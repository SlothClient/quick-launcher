import subprocess
import sys
import json
import os

MARKER = b"__QUICK_LAUNCHER_CONFIG__"

def get_embedded_config():
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
    else:
        exe_path = os.path.abspath(sys.argv[0])
    
    with open(exe_path, 'rb') as f:
        data = f.read()
    
    idx = data.rfind(MARKER)
    if idx == -1:
        return None
    
    config_bytes = data[idx + len(MARKER):]
    try:
        return json.loads(config_bytes.decode('utf-8').strip('\x00'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

def main():
    config = get_embedded_config()

    if config is None:
        sys.exit(1)

    target = config.get("target", "")

    if not target:
        sys.exit(1)

    if not os.path.exists(target):
        sys.exit(1)

    args = sys.argv[1:] if len(sys.argv) > 1 else []
    subprocess.Popen([target] + args)
    sys.exit(0)

if __name__ == "__main__":
    main()
