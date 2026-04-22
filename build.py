import os
import sys
import shutil
import subprocess
import json

from utils import get_settings, ensure_launcher_dir, DEFAULT_DIR, get_hidden_startupinfo, get_subprocess_env, kill_process

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LAUNCHER_DIR = os.path.join(SCRIPT_DIR)
BASE_EXE_NAME = "_ql_base.exe"
APP_EXE_NAME = "QuickLauncher.exe"
SETTINGS_FILE = "settings.json"

PYTHON_EXE = sys.executable.replace('python.exe', 'pythonw.exe')
if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = sys.executable

si = get_hidden_startupinfo()
env = get_subprocess_env()

# _kill_process moved to utils.py


def _cleanup_build_dirs(dist_dir, build_dir, spec_file):
    """Clean up build directories and files"""
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir, ignore_errors=True)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)
    if spec_file and os.path.exists(spec_file):
        try:
            os.remove(spec_file)
        except:
            pass


def _run_pyinstaller(script_path, output_name, dist_dir, build_dir):
    """Run PyInstaller with common settings"""
    cmd = [
        PYTHON_EXE, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name", output_name,
        "--distpath", dist_dir,
        "--workpath", build_dir,
        "--specpath", SCRIPT_DIR,
        script_path
    ]

    print(f"Running: {' '.join(cmd)}")
    with open(os.devnull, 'w') as devnull:
        return subprocess.run(
            cmd,
            cwd=SCRIPT_DIR,
            stdin=devnull,
            stdout=devnull,
            stderr=subprocess.STDOUT,
            startupinfo=si,
            creationflags=subprocess.CREATE_NO_WINDOW,
            env=env
        )


def _move_built_exe(src_exe, dest_exe, process_name=None):
    """Move built executable to final location, handling file locks"""
    if not os.path.exists(src_exe):
        return False, "Source executable not found"

    # Try direct move first
    try:
        if os.path.exists(dest_exe):
            os.remove(dest_exe)
        shutil.move(src_exe, dest_exe)
        return True, "Success"
    except (PermissionError, FileExistsError):
        # If file is locked, try to kill process and retry
        if process_name:
            _kill_process(process_name)
            try:
                if os.path.exists(dest_exe):
                    os.remove(dest_exe)
                shutil.move(src_exe, dest_exe)
                return True, "Success (after killing process)"
            except Exception:
                pass

        # If still failing, copy to .new file
        temp_output = dest_exe + ".new"
        try:
            shutil.copy2(src_exe, temp_output)
            return False, f"File locked, saved as {temp_output}"
        except Exception as e:
            return False, f"Failed to copy: {str(e)}"


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

    _cleanup_build_dirs(temp_dist, build_dir, spec_file)

    result = _run_pyinstaller("launcher.py", "_ql_base", temp_dist, build_dir)

    if result.returncode != 0:
        print("Build failed!")
        _cleanup_build_dirs(temp_dist, build_dir, spec_file)
        return False

    src_exe = os.path.join(temp_dist, BASE_EXE_NAME)
    success, message = _move_built_exe(src_exe, output_exe)

    _cleanup_build_dirs(temp_dist, build_dir, spec_file)

    if success or os.path.exists(output_exe):
        size = os.path.getsize(output_exe)
        print(f"Success! Built {BASE_EXE_NAME} ({size:,} bytes)")
        return True
    else:
        print(f"Error: {message}")
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

    kill_process("QuickLauncher.exe")
    _cleanup_build_dirs(temp_dist, build_dir, spec_file)

    if os.path.exists(output_exe):
        try:
            os.remove(output_exe)
        except PermissionError:
            print(f"Warning: Could not remove {output_exe} (file in use)")

    result = _run_pyinstaller("app.py", "QuickLauncher", temp_dist, build_dir)

    if result.returncode != 0:
        print("Build failed!")
        _cleanup_build_dirs(temp_dist, build_dir, spec_file)
        return False

    src_exe = os.path.join(temp_dist, "QuickLauncher.exe")
    success, message = _move_built_exe(src_exe, output_exe, "QuickLauncher.exe")

    _cleanup_build_dirs(temp_dist, build_dir, spec_file)

    if success and os.path.exists(output_exe):
        size = os.path.getsize(output_exe)
        print(f"Success! Built QuickLauncher.exe ({size:,} bytes)")
        print(f"Location: {output_exe}")
        return True
    else:
        if "saved as" in message:
            print(f"Warning: {message}")
            print("Please replace the old file manually when the application is not running.")
            return True
        else:
            print(f"Error: {message}")
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
