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

def run_pyinstaller(args):
    result = subprocess.run([sys.executable, "-m", "PyInstaller"] + args, cwd=SCRIPT_DIR)
    return result.returncode == 0

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
    
    dist_dir = os.path.join(SCRIPT_DIR, "dist")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    build_dir = os.path.join(SCRIPT_DIR, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    
    spec_file = os.path.join(SCRIPT_DIR, "_ql_base.spec")
    if os.path.exists(spec_file):
        os.remove(spec_file)
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "_ql_base",
        "--distpath", launcher_dir,
        "--workpath", build_dir,
        "--specpath", SCRIPT_DIR,
        "launcher.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=SCRIPT_DIR)
    
    if result.returncode != 0:
        print("Build failed!")
        return False
    
    if os.path.exists(spec_file):
        os.remove(spec_file)
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    
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
    
    dist_dir = os.path.join(SCRIPT_DIR, "dist")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    build_dir = os.path.join(SCRIPT_DIR, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    
    spec_file = os.path.join(SCRIPT_DIR, "QuickLauncher.spec")
    if os.path.exists(spec_file):
        os.remove(spec_file)
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "QuickLauncher",
        "--windowed",
        "--distpath", dist_dir,
        "--workpath", build_dir,
        "--specpath", SCRIPT_DIR,
        "app.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=SCRIPT_DIR)
    
    if result.returncode != 0:
        print("Build failed!")
        return False
    
    if os.path.exists(spec_file):
        os.remove(spec_file)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    
    output_exe = os.path.join(dist_dir, "QuickLauncher.exe")
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
