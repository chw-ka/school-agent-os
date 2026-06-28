"""Load Arduino (.ino / .cpp) submission files."""

import os


def load_file(file_path):
    """Return file contents as a string, or None if file does not exist."""
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
