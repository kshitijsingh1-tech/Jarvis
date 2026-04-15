import os
import subprocess
import psutil
import screen_brightness_control as sbc
from git import Repo

# Jarvis Tools for Engineering OS

def set_brightness(level: int) -> str:
    """Set the screen brightness (0-100)."""
    try:
        sbc.set_brightness(level)
        return f"Brightness set to {level}%"
    except Exception as e:
        return f"Error setting brightness: {str(e)}"

def get_system_stats() -> dict:
    """Returns CPU, RAM, and Disk usage stats."""
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else "AC"
        }
    except Exception as e:
        return {"error": str(e)}

def open_app(app_name: str) -> str:
    """
    Attempts to launch an application on Windows.
    Supports clear aliases for engineering students.
    """
    app_map = {
        "code": "code",
        "vs code": "code",
        "browser": "start chrome",
        "chrome": "start chrome",
        "firefox": "start firefox",
        "matlab": "start matlab",
        "calculator": "calc",
        "terminal": "start powershell",
        "explorer": "start explorer ."
    }

    cmd = app_map.get(app_name.lower())
    if not cmd:
        # Try direct execution if name is provided
        cmd = f"start {app_name}"

    try:
        subprocess.Popen(cmd, shell=True)
        return f"Requesting open for: {app_name}"
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"

def git_repo_sync(commit_message: str = "JARVIS: Automated engineering sync") -> str:
    """
    Performs standard Git workflow: add all, commit, and push.
    Assumes current workspace is a Git repository.
    """
    try:
        repo_path = os.path.abspath("D:/lucky-ai")
        repo = Repo(repo_path)
        
        if not repo.is_dirty(untracked_files=True):
            return "Repository is clean. No sync needed."

        repo.git.add(A=True)
        repo.index.commit(commit_message)
        
        # Pull first to avoid conflicts before pushing
        origin = repo.remotes.origin
        origin.pull()
        origin.push()
        
        return f"JARVIS: Workspace synced. Commit: '{commit_message}'"
    except Exception as e:
        return f"Git Sync Error: {str(e)}"
