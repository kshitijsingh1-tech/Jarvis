import os

BASE_DIR = "D:/lucky-ai/data"

def create_file(filename, content):
    os.makedirs(BASE_DIR, exist_ok=True)  # create folder if missing

    path = os.path.join(BASE_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"File '{filename}' created successfully at {path}"


def read_file(filename):
    path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(path):
        return f"File '{filename}' does not exist."

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    return f"CONTENT OF {filename}:\n{content}"