import os
import sys
import shutil
import subprocess
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LAUNCHER_DIR = os.path.join(SCRIPT_DIR)
BASE_EXE_NAME = "_ql_base.exe"
APP_EXE_NAME = "QuickLauncher.exe"
SETTINGS_FILE = "settings.json"

PYTHON_EXE = sys.executable.replace('python.exe', 'pythonw.exe')
if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = sys.executable

si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
si.wShowWindow = subprocess.SW_HIDE

env = os.environ.copy()
env["PYTHONUNBUFFERED"] = "0"
env["PYTHON_CLOSESTDIO"] = "1"

def get_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"launcher_dir": r"D:\.quick-launchers"}

def ensure_launcher_dir():
    settings = get_settings()
    launcher_dir = settings.get("launcher_dir", r"D:\.quick-launchers")
    if not os.path.exists(launcher_dir):
        os.makedirs(launcher_dir)
    return launcher_dir

def build_launcher():
    print("=" * 50)
    print("Building Base Launcher...")
    print("=" * 50)
    
    launcher_py = os.path.join(SCRIPT_DIR, "launcher.py")
    if not os.path.exists(launcher_py):
        print(f"Error: launcher.py not found in {SCRIPT_DIR}")
        return False
    
    launcher_dir = ensure_launcher_dir()
    output_exe = os.path.join(launcher_dir, BASE_EXE_NAME)
    
    print(f"Building base launcher to: {launcher_dir}")
    
    temp_dist = os.path.join(SCRIPT_DIR, "dist")
    build_dir = os.path.join(SCRIPT_DIR, "build")
    spec_file = os.path.join(SCRIPT_DIR, "_ql_base.spec")
    
    if os.path.exists(temp_dist):
        shutil.rmtree(temp_dist)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(spec_file):
        os.remove(spec_file)
    
    cmd = [
        PYTHON_EXE, "-m", "PyInstaller",
        "--onefile",
        "--name", "_ql_base",
        "--distpath", temp_dist,
        "--workpath", build_dir,
        "--specpath", SCRIPT_DIR,
        "launcher.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    with open(os.devnull, 'w') as devnull:
        result = subprocess.run(cmd, cwd=SCRIPT_DIR, stdin=devnull, stdout=devnull, stderr=subprocess.STDOUT, startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW, env=env)
    
    if result.returncode != 0:
        print("Build failed!")
        shutil.rmtree(temp_dist, ignore_errors=True)
        shutil.rmtree(build_dir, ignore_errors=True)
        return False
    
    src_exe = os.path.join(temp_dist, BASE_EXE_NAME)
    if os.path.exists(src_exe):
        shutil.move(src_exe, output_exe)
    
    shutil.rmtree(temp_dist, ignore_errors=True)
    shutil.rmtree(build_dir, ignore_errors=True)
    if os.path.exists(spec_file):
        os.remove(spec_file)
    
    if os.path.exists(output_exe):
        size = os.path.getsize(output_exe)
        print(f"Success! Built {BASE_EXE_NAME} ({size:,} bytes)")
        return True
    else:
        print(f"Error: Expected output not found at {output_exe}")
        return False

def build_app():
    print("=" * 50)
    print("Building Quick Launcher App...")
    print("=" * 50)
    
    app_py = os.path.join(SCRIPT_DIR, "app.py")
    if not os.path.exists(app_py):
        print(f"Error: app.py not found in {SCRIPT_DIR}")
        return False
    
    output_exe = os.path.join(SCRIPT_DIR, "QuickLauncher.exe")
    temp_dist = os.path.join(SCRIPT_DIR, "_build_temp")
    build_dir = os.path.join(SCRIPT_DIR, "build")
    spec_file = os.path.join(SCRIPT_DIR, "QuickLauncher.spec")
    
    if os.path.exists(temp_dist):
        shutil.rmtree(temp_dist)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(spec_file):
        os.remove(spec_file)
    if os.path.exists(output_exe):
        os.remove(output_exe)
    
    cmd = [
        PYTHON_EXE, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name", "QuickLauncher",
        "--distpath", temp_dist,
        "--workpath", build_dir,
        "--specpath", SCRIPT_DIR,
        "app.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    with open(os.devnull, 'w') as devnull:
        result = subprocess.run(cmd, cwd=SCRIPT_DIR, stdin=devnull, stdout=devnull, stderr=subprocess.STDOUT, startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW, env=env)
    
    if result.returncode != 0:
        print("Build failed!")
        shutil.rmtree(temp_dist, ignore_errors=True)
        shutil.rmtree(build_dir, ignore_errors=True)
        return False
    
    src_exe = os.path.join(temp_dist, "QuickLauncher.exe")
    if os.path.exists(src_exe):
        shutil.move(src_exe, output_exe)
    
    shutil.rmtree(temp_dist, ignore_errors=True)
    shutil.rmtree(build_dir, ignore_errors=True)
    if os.path.exists(spec_file):
        os.remove(spec_file)
    
    if os.path.exists(output_exe):
        size = os.path.getsize(output_exe)
        print(f"Success! Built QuickLauncher.exe ({size:,} bytes)")
        print(f"Location: {output_exe}")
        return True
    else:
        print("Error: Expected output not found")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python build.py [launcher|app|all]")
        print("  launcher - Build the base launcher (_ql_base.exe)")
        print("  app      - Build the GUI app (QuickLauncher.exe)")
        print("  all      - Build both")
        sys.exit(1)
    
    target = sys.argv[1].lower()
    
    if target == "launcher":
        success = build_launcher()
    elif target == "app":
        success = build_app()
    elif target == "all":
        success = build_launcher()
        if success:
            success = build_app()
        else:
            print("\nSkipping app build due to launcher build failure")
    else:
        print(f"Unknown target: {target}")
        print("Use: launcher, app, or all")
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
