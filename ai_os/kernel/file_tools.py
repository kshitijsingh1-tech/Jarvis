# tools/file_tools.py

import os

BASE_DIR = "workspace"

os.makedirs(BASE_DIR, exist_ok=True)


def create_file(filename: str, content: str):
    path = os.path.join(BASE_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"File '{filename}' created successfully."


def read_file(filename: str):
    path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(path):
        return "File does not exist."

    with open(path, "r", encoding="utf-8") as f:
        return f.read()