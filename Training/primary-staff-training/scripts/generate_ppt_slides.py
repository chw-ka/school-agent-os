#!/usr/bin/env python3
"""
Generate 16:9 PPT slide images from docs/ppt-slides-gemini-prompts.md using Gemini API.

Usage:
  cp .env.example .env   # add GEMINI_API_KEY
  pip install -r requirements.txt
  python scripts/generate_ppt_slides.py
  python scripts/generate_ppt_slides.py --slide 14
  python scripts/generate_ppt_slides.py --dry-run

Requires: pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv() -> None:
    """Load project-root .env into os.environ (does not override existing vars)."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    try:
        from dotenv import load_dotenv as _load

        _load(env_file, override=False)
        return
    except ImportError:
        pass
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value
PROMPTS_MD = ROOT / "docs" / "ppt-slides-gemini-prompts.md"
OUTPUT_DIR = ROOT / "docs" / "ppt-output"

STYLE_SUFFIX = (
    "Clean modern educational presentation slide, mandatory 16:9 landscape aspect ratio, "
    "1920x1080 composition, flat vector illustration, bold readable sans-serif typography, "
    "high contrast text, kid-friendly but professional, STEAM color palette (deep blue, teal, warm orange), "
    "minimal clutter, no watermarks, no realistic human faces, crisp edges."
)

# Default Imagen model (override: --model or IMAGEN_MODEL in .env)
DEFAULT_MODEL = "imagen-4.0-generate-001"
DEFAULT_REFERENCE_MODEL = "gemini-2.5-flash-image"
PRODUCT_REFERENCE = ROOT / "docs" / "assets" / "m5sticks3-product-reference.png"


def parse_filename_index(md_text: str) -> dict[int, str]:
    """Parse | 03 | `slide-03-foo.png` | rows from slide index table."""
    index: dict[int, str] = {}
    for m in re.finditer(r"\|\s*(\d{2})\s*\|\s*`(slide-\d{2}-[^`]+\.png)`", md_text):
        index[int(m.group(1))] = m.group(2)
    return index


def parse_slides(md_text: str) -> list[dict]:
    """Extract slide blocks from markdown."""
    filename_index = parse_filename_index(md_text)
    slides: list[dict] = []
    pattern = re.compile(
        r"### Slide (\d+) — ([^\n]+)\n\n"
        r"(?:\*\*On-slide text(?: \(English only\))?:\*\*[^\n]*\n(?:`[^`]*`[^\n]*\n)*\n)?"
        r"(?:\*\*REFERENCE:\*\* ([^\n]+)\n)?"
        r"(?:\*\*MODEL:\*\* ([^\n]+)\n\n)?"
        r"\*\*PROMPT:\*\*\n```\n(.*?)\n```",
        re.DOTALL,
    )
    for m in pattern.finditer(md_text):
        num = int(m.group(1))
        title = m.group(2).strip()
        reference = (m.group(3) or "").strip()
        model = (m.group(4) or "").strip()
        prompt = m.group(5).strip()
        filename = filename_index.get(num)
        if not filename:
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            filename = f"slide-{num:02d}-{slug}.png"
        slides.append(
            {
                "num": num,
                "title": title,
                "prompt": prompt,
                "filename": filename,
                "reference": reference,
                "model": model,
            }
        )
    return sorted(slides, key=lambda s: s["num"])


def generate_one(client, model: str, full_prompt: str, out_path: Path) -> None:
    """Call Imagen image generation."""
    response = client.models.generate_images(
        model=model,
        prompt=full_prompt,
        config={
            "number_of_images": 1,
            "aspect_ratio": "16:9",
            "output_mime_type": "image/png",
        },
    )
    if not response.generated_images:
        raise RuntimeError("No images returned")
    img = response.generated_images[0].image
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(img, "save"):
        img.save(str(out_path))
    elif hasattr(img, "image_bytes"):
        out_path.write_bytes(img.image_bytes)
    else:
        raise RuntimeError("Unknown image response format")


def generate_with_reference(
    client, model: str, full_prompt: str, reference_path: Path, out_path: Path
) -> None:
    """Call Gemini image model with a product reference photo."""
    from google.genai import types

    if not reference_path.exists():
        raise FileNotFoundError(f"Reference image not found: {reference_path}")

    ref_bytes = reference_path.read_bytes()
    response = client.models.generate_content(
        model=model,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=ref_bytes, mime_type="image/png"),
                    types.Part.from_text(text=full_prompt),
                ],
            )
        ],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="16:9"),
        ),
    )
    if not response.candidates:
        raise RuntimeError("No response candidates")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            out_path.write_bytes(part.inline_data.data)
            return
    raise RuntimeError("No image in response")


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Generate PPT slides via Gemini API")
    parser.add_argument("--slide", type=int, help="Generate only this slide number")
    parser.add_argument("--model", default=None, help="Imagen model id")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts only")
    parser.add_argument("--delay", type=float, default=2.0, help="Seconds between API calls")
    args = parser.parse_args()
    model = args.model or os.environ.get("IMAGEN_MODEL", DEFAULT_MODEL)

    if not PROMPTS_MD.exists():
        print(f"Missing {PROMPTS_MD}", file=sys.stderr)
        return 1

    slides = parse_slides(PROMPTS_MD.read_text(encoding="utf-8"))
    if not slides:
        print("No slides parsed from markdown", file=sys.stderr)
        return 1

    if args.slide:
        slides = [s for s in slides if s["num"] == args.slide]
        if not slides:
            print(f"Slide {args.slide} not found", file=sys.stderr)
            return 1

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not args.dry_run and not api_key:
        print(
            "Missing API key. Add GEMINI_API_KEY to .env in the project root:\n"
            "  cp .env.example .env\n"
            "  # edit .env and set GEMINI_API_KEY=...\n"
            "Or export GEMINI_API_KEY in your shell.",
            file=sys.stderr,
        )
        return 1

    client = None
    if not args.dry_run:
        try:
            from google import genai
        except ImportError:
            print("Install: pip install google-genai", file=sys.stderr)
            return 1
        client = genai.Client(api_key=api_key)

    print(f"Slides to generate: {len(slides)} → {OUTPUT_DIR} (model: {model})\n")

    for i, slide in enumerate(slides):
        full_prompt = f"{slide['prompt']}\n\n{STYLE_SUFFIX}"
        out_path = OUTPUT_DIR / slide["filename"]
        slide_model = slide.get("model") or model
        reference_rel = slide.get("reference") or ""
        reference_path = ROOT / reference_rel if reference_rel else None
        mode = "ref+gemini" if reference_path else "imagen"
        print(f"[{slide['num']:02d}] {slide['title']} → {out_path.name} ({mode})")

        if args.dry_run:
            print(f"  PROMPT ({len(full_prompt)} chars): {full_prompt[:120]}…\n")
            continue

        try:
            if reference_path:
                generate_with_reference(
                    client,
                    slide_model or DEFAULT_REFERENCE_MODEL,
                    full_prompt,
                    reference_path,
                    out_path,
                )
            elif full_prompt.strip().startswith("(Skip AI generation"):
                print("  SKIP (blank placeholder — use build_pptx.py)")
                continue
            else:
                generate_one(client, slide_model or model, full_prompt, out_path)
            print(f"  OK ({out_path.stat().st_size // 1024} KB)")
        except Exception as e:
            print(f"  FAILED: {e}", file=sys.stderr)
            return 1

        if i < len(slides) - 1 and args.delay > 0:
            time.sleep(args.delay)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
