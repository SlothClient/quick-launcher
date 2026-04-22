import os
import sys
import shutil
import subprocess
import json

from utils import get_settings, ensure_launcher_dir, DEFAULT_DIR, get_hidden_startupinfo, get_subprocess_env, kill_process

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LAUNCHER_DIR = os.path.join(SCRIPT_DIR)
BASE_EXE_NAME = "_ql_base.exe"
APP_EXE_NAME = "QuickLauncherPro.exe"
SETTINGS_FILE = "settings.json"

PYTHON_EXE = sys.executable.replace('python.exe', 'pythonw.exe')
if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = sys.executable

si = get_hidden_startupinfo()
env = get_subprocess_env()

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
            kill_process(process_name)
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

def build_modern_app():
    """Build the modern QuickLauncher interface"""
    print("=" * 60)
    print("Building QuickLauncher Pro (Modern Interface)...")
    print("=" * 60)

    app_py = os.path.join(SCRIPT_DIR, "app_modern.py")
    if not os.path.exists(app_py):
        print(f"Error: app_modern.py not found in {SCRIPT_DIR}")
        return False

    output_exe = os.path.join(SCRIPT_DIR, APP_EXE_NAME)
    temp_dist = os.path.join(SCRIPT_DIR, "_build_modern_temp")
    build_dir = os.path.join(SCRIPT_DIR, "build")
    spec_file = os.path.join(SCRIPT_DIR, "QuickLauncherPro.spec")

    # Kill any running instances
    kill_process("QuickLauncherPro.exe")
    kill_process("QuickLauncher.exe")
    _cleanup_build_dirs(temp_dist, build_dir, spec_file)

    if os.path.exists(output_exe):
        try:
            os.remove(output_exe)
        except PermissionError:
            print(f"Warning: Could not remove {output_exe} (file in use)")

    result = _run_pyinstaller("app_modern.py", "QuickLauncherPro", temp_dist, build_dir)

    if result.returncode != 0:
        print("Build failed!")
        _cleanup_build_dirs(temp_dist, build_dir, spec_file)
        return False

    src_exe = os.path.join(temp_dist, "QuickLauncherPro.exe")
    success, message = _move_built_exe(src_exe, output_exe, "QuickLauncherPro.exe")

    _cleanup_build_dirs(temp_dist, build_dir, spec_file)

    if success and os.path.exists(output_exe):
        size = os.path.getsize(output_exe)
        print(f"Success! Built {APP_EXE_NAME} ({size:,} bytes)")
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
    if len(sys.argv) > 1 and sys.argv[1].lower() == "modern":
        success = build_modern_app()
        sys.exit(0 if success else 1)
    else:
        print("Usage: python build_modern.py modern")
        print("  modern - Build the modern GUI app (QuickLauncherPro.exe)")
        sys.exit(1)

if __name__ == "__main__":
    main()