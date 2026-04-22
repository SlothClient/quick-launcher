"""Common utilities shared between app.py and build.py"""

import os
import json
import subprocess
import sys
from ctypes import windll, c_long, byref

# Constants
MARKER = b"__QUICK_LAUNCHER_CONFIG__"

# Subprocess utilities
def get_hidden_startupinfo():
    """Get subprocess startup info to hide console window"""
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    return si

def get_subprocess_env():
    """Get environment variables for subprocess calls"""
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "0"
    env["PYTHON_CLOSESTDIO"] = "1"
    return env

def kill_process(process_name):
    """Force kill a running process by name"""
    try:
        subprocess.run(['taskkill', '/F', '/IM', process_name],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import time
        time.sleep(1)
    except:
        pass

# Configuration utilities
def extract_config_from_exe(exe_path):
    """Extract configuration from executable file - unified version"""
    try:
        with open(exe_path, 'rb') as f:
            data = f.read()

        idx = data.rfind(MARKER)
        if idx == -1:
            return None

        config_bytes = data[idx + len(MARKER):]
        config_str = config_bytes.decode('utf-8').strip('\x00')

        if not config_str:
            return None

        return json.loads(config_str)

    except (json.JSONDecodeError, UnicodeDecodeError, IOError):
        return None

DEFAULT_DIR = r"D:\.quick-launchers"
SETTINGS_FILE = "settings.json"


def get_settings():
    """Load settings from settings.json file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"launcher_dir": DEFAULT_DIR}


def save_settings(settings):
    """Save settings to settings.json file"""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def ensure_launcher_dir():
    """Ensure launcher directory exists and return its path"""
    settings = get_settings()
    launcher_dir = settings.get("launcher_dir", DEFAULT_DIR)
    if not os.path.exists(launcher_dir):
        os.makedirs(launcher_dir)
    return launcher_dir
