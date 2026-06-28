"""
AIA extraction and parsing utilities.

Exposes:
  read_all_aias(submissions)  — extract .aia files and populate blockly/components columns
  read_aia(dir_name)          — folder-based extract (used by extract_aias.py)
  get_comments(desc, mark, max_mark)  — format [O]/[-]/[X] feedback lines
"""

import json
import shutil
import zipfile
from os import getcwd, listdir, mkdir, path, remove

import pandas as pd
import xmltodict

import blockly_util
import components_util


def parse_blockly_and_xml(src_path):
    output = {"blockly": {}, "components": {}}
    for f in sorted(listdir(src_path)):
        if f.endswith(".bky"):
            screen_name = f.split(".")[0]
            with open(path.join(src_path, f), "r") as fh:
                data = fh.read()
            data = data.replace("&#13;", "")
            data = {} if data.strip() == "" else xmltodict.parse(data)
            output["blockly"][screen_name] = data
            with open(path.join(src_path, f"{screen_name}_blockly.json"), "w") as fh:
                fh.write(json.dumps(data))
            remove(path.join(src_path, f))

        elif f.endswith(".scm"):
            screen_name = f.split(".")[0]
            with open(path.join(src_path, f), "r") as fh:
                data = fh.read()
            data = data.replace("&#13;", "")[8:-3]
            output["components"][screen_name] = json.loads(data)
            with open(path.join(src_path, f"{screen_name}_components.json"), "w") as fh:
                fh.write(data)
            remove(path.join(src_path, f))

        elif f.endswith("_blockly.json"):
            with open(path.join(src_path, f), "r", encoding="utf-8") as fh:
                output["blockly"][f.split("_")[0]] = json.load(fh)

        elif f.endswith("_components.json"):
            with open(path.join(src_path, f), "r", encoding="utf-8") as fh:
                output["components"][f.split("_")[0]] = json.load(fh)

    return output


def parse_src(src_path):
    for f in listdir(src_path):
        if f in ("assets", "youngandroidproject"):
            continue
        if path.isdir(path.join(src_path, f)):
            return parse_src(path.join(src_path, f))
        if f.endswith((".bky", ".blk", ".json")):
            return parse_blockly_and_xml(src_path)
    return None


def _extract_aia(source_path, aia_path):
    with zipfile.ZipFile(source_path, "r") as zf:
        zf.extractall(aia_path)


def read_all_aias(submissions: pd.DataFrame) -> pd.DataFrame:
    """Extract .aia files referenced in submissions["filepath"] and fill blockly/components columns."""
    for idx, row in submissions.iterrows():
        source_path = submissions.loc[idx, "filepath"]
        if source_path is None:
            submissions.loc[idx, "blockly"] = json.dumps({})
            submissions.loc[idx, "components"] = json.dumps({})
            continue

        aia_path = (
            str(source_path)
            .replace(".aia", "")
            .replace(".zip", "")
            .replace("attachments", "aias")
        )

        if not path.exists(aia_path):
            try:
                _extract_aia(source_path, aia_path)
            except Exception:
                print(f"Error extracting {source_path}")
                submissions.loc[idx, "blockly"] = json.dumps({})
                submissions.loc[idx, "components"] = json.dumps({})
                continue

        output = parse_src(aia_path)
        submissions.loc[idx, "blockly"] = json.dumps(output["blockly"]) if output else json.dumps({})
        submissions.loc[idx, "components"] = json.dumps(output["components"]) if output else json.dumps({})

    return submissions


def _parse_aia_folder(dir_name):
    aia_path = path.join(getcwd(), "aias", dir_name)
    output = []
    for file in listdir(aia_path):
        if file.endswith(".aia"):
            with zipfile.ZipFile(path.join(aia_path, file), "r") as zf:
                zf.extractall(aia_path)
            src_path = path.join(aia_path, file.split(".")[0])
            shutil.move(path.join(aia_path, "src"), src_path)
            remove(path.join(aia_path, file))
            output.append(parse_src(src_path))
    return output


def _clear_aia(dir_name):
    import os
    aia_path = path.join(getcwd(), "aias", dir_name)
    if path.exists(aia_path):
        shutil.rmtree(aia_path)
    os.mkdir(aia_path)


def _move_aia(folder):
    src_dir = path.join(getcwd(), "attachments", folder)
    dst_dir = path.join(getcwd(), "aias", folder)
    for file in listdir(src_dir):
        if file.endswith((".aia", ".json")):
            shutil.copy(path.join(src_dir, file), dst_dir)


def read_aia(dir_name: str) -> pd.DataFrame:
    """Copy .aia files from attachments/<dir_name> to aias/<dir_name> and extract them."""
    _clear_aia(dir_name)
    _move_aia(dir_name)
    return pd.DataFrame(_parse_aia_folder(dir_name))


def get_comments(section_description: str, section_mark: int, max_mark: int = 2) -> str:
    if section_mark == 0:
        return f"[X] {section_description}\n"
    if section_mark < max_mark:
        return f"[-] {section_description}\n"
    return f"[O] {section_description}\n"


def check_copycat(submissions: pd.DataFrame) -> None:
    print("Detecting copycat in components...")
    components_util.assert_no_copycat_components(submissions)
    print("Detecting copycat in blockly...")
    blockly_util.assert_no_copycat_blockly(submissions)
    print("Done.")
