import os
import re

PROJECT_ROOT = "D:/lucky-ai"

def list_files_recursive(directory: str = ".", max_depth: int = 2) -> str:
    """
    Lists files in a directory tree up to a certain depth.
    Ignores common noisy directories like .venv, __pycache__, .git.
    """
    ignore_dirs = {".venv", "__pycache__", ".git", "node_modules", ".gemini", "temp"}
    
    start_path = os.path.abspath(os.path.join(PROJECT_ROOT, directory))
    if not start_path.startswith(os.path.abspath(PROJECT_ROOT)):
        return "Error: Cannot list files outside the project root."

    output = []
    start_level = start_path.count(os.sep)

    for root, dirs, files in os.walk(start_path):
        # Filter directories in-place to prevent walking into ignored ones
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        current_level = root.count(os.sep) - start_level
        if current_level >= max_depth:
            dirs[:] = [] # stop going deeper
            continue

        indent = "  " * current_level
        rel_path = os.path.relpath(root, start_path)
        if rel_path == ".":
            output.append(f"{os.path.basename(start_path)}/")
        else:
            output.append(f"{indent}{os.path.basename(root)}/")
        
        sub_indent = "  " * (current_level + 1)
        for f in files:
            output.append(f"{sub_indent}{f}")

    return "\n".join(output) if output else "No files found."

def search_code(pattern: str, directory: str = ".") -> str:
    """
    Searches for a regex pattern in the codebase.
    Returns matching lines with filename and line numbers.
    """
    search_path = os.path.abspath(os.path.join(PROJECT_ROOT, directory))
    if not search_path.startswith(os.path.abspath(PROJECT_ROOT)):
         return "Error: Cannot search outside the project root."

    results = []
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return f"Invalid regex pattern: {str(e)}"

    ignore_dirs = {".venv", "__pycache__", ".git", "node_modules", ".gemini", "temp", "ffmpeg.zip"}
    
    match_count = 0
    max_matches = 30 # safety limit

    for root, dirs, files in os.walk(search_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file.endswith((".py", ".html", ".css", ".js", ".md", ".txt", ".sh")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            if regex.search(line):
                                rel_file = os.path.relpath(file_path, PROJECT_ROOT)
                                results.append(f"{rel_file}:{i}: {line.strip()}")
                                match_count += 1
                                if match_count >= max_matches:
                                    results.append("\n--- Match limit reached ---")
                                    return "\n".join(results)
                except Exception:
                    continue
                    
    return "\n".join(results) if results else "No matches found."

def read_project_file(filename: str) -> str:
    """
    Reads a file from anywhere within the project root.
    """
    path = os.path.abspath(os.path.join(PROJECT_ROOT, filename))

    if not path.startswith(os.path.abspath(PROJECT_ROOT)):
        return f"Access Denied: Path '{filename}' is outside the project root."

    if not os.path.exists(path):
        return f"File '{filename}' does not exist."
    
    if os.path.isdir(path):
        return f"'{filename}' is a directory. Use list_files_recursive instead."

    try:
        # Check file size to avoid crashing on large binaries
        if os.path.getsize(path) > 500000: # 500KB limit
            return f"File '{filename}' is too large to read directly ({os.path.getsize(path)} bytes)."

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return f"CONTENT OF {filename}:\n{content}"
    except Exception as e:
        return f"Read Error: {str(e)}"
