#!/usr/bin/env python3
"""
Run an exam generator recipe, then compare output against template + past papers.

Usage:
  python run.py f5_ict_blueprint_db_web [-- extra args for recipe]
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path


RECIPES: dict[str, str] = {
    "f5_ict_blueprint_db_web": "f5_ict_blueprint_db_web",
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run exam generator recipe with post-check.")
    ap.add_argument("recipe", choices=sorted(RECIPES.keys()), help="Generator recipe name")
    ap.add_argument("recipe_args", nargs=argparse.REMAINDER, help="Arguments passed to the recipe")
    args = ap.parse_args(argv)

    mod_name = RECIPES[args.recipe]
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    mod = importlib.import_module(mod_name)

    recipe_argv = list(args.recipe_args)
    if recipe_argv and recipe_argv[0] == "--":
        recipe_argv = recipe_argv[1:]

    return int(mod.main(recipe_argv))


if __name__ == "__main__":
    raise SystemExit(main())
