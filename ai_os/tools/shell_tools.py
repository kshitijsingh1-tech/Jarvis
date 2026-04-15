import os
import subprocess


WORKSPACE_DIR = os.path.abspath("D:/lucky-ai")


def run_shell(command: str) -> str:
    """
    Runs a shell command inside the workspace and returns combined output.
    The tool is intentionally constrained to the project directory.
    """

    completed = subprocess.run(
        command,
        cwd=WORKSPACE_DIR,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
    )

    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()

    parts = [f"Exit Code: {completed.returncode}"]
    if stdout:
        parts.append(f"STDOUT:\n{stdout}")
    if stderr:
        parts.append(f"STDERR:\n{stderr}")

    return "\n\n".join(parts)
