#!/usr/bin/env python3
"""Parse ESP32 partition tables and drive esptool read/write for M5StickS3 cloning."""

from __future__ import annotations

import argparse
import json
import re
import struct
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

FLASH_SIZE = 0x800000  # 8 MB
PARTITION_TABLE_OFFSET = 0x8000
PARTITION_TABLE_SIZE = 0x1000
BOOTLOADER_MAX = 0x10000

APP_TYPE = 0x00
DATA_TYPE = 0x01

SUBTYPE_NAMES = {
    (APP_TYPE, 0x00): "factory",
    (APP_TYPE, 0x10): "ota_0",
    (APP_TYPE, 0x11): "ota_1",
    (APP_TYPE, 0x20): "ota_2",
    (APP_TYPE, 0x21): "ota_3",
    (APP_TYPE, 0x01): "test",
    (DATA_TYPE, 0x00): "otadata",
    (DATA_TYPE, 0x01): "phy",
    (DATA_TYPE, 0x02): "nvs",
    (DATA_TYPE, 0x03): "coredump",
    (DATA_TYPE, 0x81): "fat",
    (DATA_TYPE, 0x82): "spiffs",
    (DATA_TYPE, 0x04): "nvs_keys",
    (DATA_TYPE, 0x05): "efuse",
}


@dataclass
class Partition:
    name: str
    type: int
    subtype: int
    offset: int
    size: int
    flags: int

    @property
    def subtype_name(self) -> str:
        return SUBTYPE_NAMES.get((self.type, self.subtype), f"0x{self.subtype:02x}")

    @property
    def safe_filename(self) -> str:
        slug = re.sub(r"[^A-Za-z0-9._-]+", "_", self.name.strip()) or "unnamed"
        return f"{slug}__{self.subtype_name}__0x{self.offset:x}.bin"


PARTITION_MAGIC = 0x50AA
PARTITION_ENTRY_SIZE = 32


def parse_partition_table(data: bytes) -> list[Partition]:
    """Parse ESP-IDF partition table (magic-first 32-byte entries)."""
    entries: list[Partition] = []
    pos = 0
    while pos + PARTITION_ENTRY_SIZE <= len(data):
        magic, ptype, subtype, offset, size, name_raw = struct.unpack_from(
            "<HBBII16s", data, pos
        )
        if magic != PARTITION_MAGIC:
            break
        name = name_raw.split(b"\x00", 1)[0].decode("ascii", errors="replace").strip()
        entries.append(
            Partition(
                name=name,
                type=ptype,
                subtype=subtype,
                offset=offset,
                size=size,
                flags=0,
            )
        )
        pos += PARTITION_ENTRY_SIZE
    return entries


def esptool_cmd(root: Path, port: str | None, *args: str) -> list[str]:
    esptool = root / ".venv" / "bin" / "python"
    cmd = [str(esptool), "-m", "esptool", "--chip", "esp32s3"]
    if port:
        cmd.extend(["--port", port])
    cmd.extend(["--baud", "460800"])
    cmd.extend(args)
    return cmd


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd))
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if check and result.returncode != 0:
        raise SystemExit(result.returncode)
    return result


def read_flash(root: Path, port: str, offset: int, size: int, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run(esptool_cmd(root, port, "read-flash", hex(offset), hex(size), str(out_path)))


def write_flash(root: Path, port: str, offset: int, in_path: Path) -> None:
    run(
        esptool_cmd(
            root,
            port,
            "write-flash",
            "--flash-size",
            "8MB",
            "--flash-mode",
            "dio",
            "--flash-freq",
            "80m",
            hex(offset),
            str(in_path),
        )
    )


def save_manifest(partitions: list[Partition], path: Path, extra: dict | None = None) -> None:
    payload = {
        "flash_size": FLASH_SIZE,
        "partitions": [asdict(p) for p in partitions],
    }
    if extra:
        payload.update(extra)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_manifest(path: Path) -> tuple[list[Partition], dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    partitions = [Partition(**item) for item in payload["partitions"]]
    return partitions, payload


def cmd_backup(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    backup_dir = root / "backups"
    part_dir = backup_dir / "partitions"
    port = args.port

    read_flash(root, port, PARTITION_TABLE_OFFSET, PARTITION_TABLE_SIZE, backup_dir / "partition-table.bin")
    table = parse_partition_table((backup_dir / "partition-table.bin").read_bytes())
    if not table:
        raise SystemExit("Partition table is empty. Is this an M5StickS3 with M5Launcher installed?")

    read_flash(root, port, 0x0, BOOTLOADER_MAX, backup_dir / "bootloader-region.bin")

    mac = run(esptool_cmd(root, port, "read-mac"), check=False).stdout.strip()
    chip = run(esptool_cmd(root, port, "chip-id"), check=False).stdout.strip()

    for part in table:
        out = part_dir / part.safe_filename
        read_flash(root, port, part.offset, part.size, out)

    save_manifest(
        table,
        backup_dir / "manifest.json",
        extra={
            "source_mac": mac,
            "source_chip": chip,
            "notes": "Backup from master M5StickS3. Do not write bootloader-region to targets unless using --include-bootloader.",
        },
    )

    print(f"\nBackup complete: {backup_dir}")
    print(f"Partitions saved: {len(table)}")
    for part in table:
        print(f"  - {part.name:12} {part.subtype_name:8} 0x{part.offset:06x} size 0x{part.size:x}")


def should_skip_partition(part: Partition, mode: str) -> bool:
    if mode == "apps-data":
        # Keep launcher + apps + filesystem + WiFi, skip RF calibration.
        if part.subtype_name == "phy":
            return True
        return False
    if mode == "full":
        return False
    raise ValueError(f"Unknown mode: {mode}")


def cmd_provision(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    backup_dir = root / "backups"
    manifest_path = backup_dir / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Missing {manifest_path}. Run backup-master.sh on the master device first.")

    partitions, _manifest = load_manifest(manifest_path)
    port = args.port

    if args.include_bootloader:
        bootloader = backup_dir / "bootloader-region.bin"
        if not bootloader.exists():
            raise SystemExit(f"Missing {bootloader}")
        write_flash(root, port, 0x0, bootloader)

    table_bin = backup_dir / "partition-table.bin"
    write_flash(root, port, PARTITION_TABLE_OFFSET, table_bin)

    part_dir = backup_dir / "partitions"
    for part in partitions:
        if should_skip_partition(part, args.mode):
            print(f"skip {part.name} ({part.subtype_name})")
            continue
        blob = part_dir / part.safe_filename
        if not blob.exists():
            raise SystemExit(f"Missing partition backup: {blob}")
        write_flash(root, port, part.offset, blob)

    mac = run(esptool_cmd(root, port, "read-mac"), check=False).stdout.strip()
    print(f"\nProvision complete for {port}")
    print(mac)
    print(
        "Next: power-cycle the StickS3. You should see the M5Launcher splash briefly, "
        "then 小智 auto-starts."
    )
    print("To open M5Launcher menu: press M5 (Enter) during the startup splash.")
    print("Then bind 小智 with this unit's verification code on the control panel.")


def cmd_fix_bootloader(args: argparse.Namespace) -> None:
    """Write only master bootloader region — fixes missing M5Launcher on already-provisioned targets."""
    root = Path(args.root).resolve()
    backup_dir = root / "backups"
    bootloader = backup_dir / "bootloader-region.bin"
    if not bootloader.exists():
        raise SystemExit(f"Missing {bootloader}. Run backup-master.sh on the master device first.")
    port = args.port
    print("Writing master bootloader (0x00000-0x0FFFF)...")
    write_flash(root, port, 0x0, bootloader)
    print("\nBootloader restored. Power-cycle the StickS3 — M5Launcher should appear at startup.")
    print("Press M5 during splash to open the Launcher menu.")


def cmd_list_ports(_args: argparse.Namespace) -> None:
    root = Path(_args.root).resolve()
    run(esptool_cmd(root, None, "read-flash", "--help"), check=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="M5StickS3 partition backup/restore helpers")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]), help="m5sticks3-clone project root")
    sub = parser.add_subparsers(dest="command", required=True)

    backup = sub.add_parser("backup", help="Read partition table and all partitions from master")
    backup.add_argument("--port", required=True, help="Serial port, e.g. /dev/cu.usbmodem1101")
    backup.set_defaults(func=cmd_backup)

    provision = sub.add_parser("provision", help="Write backup partitions to a target StickS3")
    provision.add_argument("--port", required=True, help="Serial port for target device")
    provision.add_argument(
        "--mode",
        choices=["apps-data", "full"],
        default="apps-data",
        help="apps-data (default): all partitions except phy. full: everything including phy.",
    )
    provision.add_argument(
        "--include-bootloader",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write 0x00000-0x0FFFF bootloader from master (default: on). Required for new/factory StickS3 so M5Launcher in app0 boots correctly.",
    )
    provision.set_defaults(func=cmd_provision)

    fix_boot = sub.add_parser(
        "fix-bootloader",
        help="Write only master bootloader — use if M5Launcher missing after provision",
    )
    fix_boot.add_argument("--port", required=True, help="Serial port for target device")
    fix_boot.set_defaults(func=cmd_fix_bootloader)

    sub.add_parser("help-esptool", help="Show esptool help").set_defaults(func=cmd_list_ports)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
