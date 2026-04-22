import os
import sys
import json
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import winreg
from ctypes import windll, c_long, byref, wintypes

MARKER = b"__QUICK_LAUNCHER_CONFIG__"
DEFAULT_DIR = r"D:\.quick-launchers"
BASE_EXE_NAME = "_ql_base.exe"
SETTINGS_FILE = "settings.json"

def get_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"launcher_dir": DEFAULT_DIR}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

def get_user_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
        try:
            path_val, _ = winreg.QueryValueEx(key, "Path")
            return path_val
        finally:
            winreg.CloseKey(key)
    except:
        return ""

def set_user_path(path_str):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, path_str)
        winreg.CloseKey(key)
        refresh_environment()
        return True
    except Exception as e:
        return str(e)

def refresh_environment():
    try:
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SendMessageTimeoutW = windll.user32.SendMessageTimeoutW
        SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 0x0002, 5000, byref(c_long()))
    except:
        pass

def ensure_launcher_dir():
    settings = get_settings()
    launcher_dir = settings.get("launcher_dir", DEFAULT_DIR)
    if not os.path.exists(launcher_dir):
        os.makedirs(launcher_dir)
    return launcher_dir

def get_base_exe_path():
    settings = get_settings()
    launcher_dir = settings.get("launcher_dir", DEFAULT_DIR)
    return os.path.join(launcher_dir, BASE_EXE_NAME)

def is_in_path(command_name):
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    for directory in path_dirs:
        exe_path = os.path.join(directory, command_name + ".exe")
        if os.path.exists(exe_path):
            return True, exe_path
    return False, None

def scan_all_path_for_conflict(command_name):
    user_path = get_user_path()
    all_dirs = user_path.split(os.pathsep) if user_path else []
    all_dirs.extend(os.environ.get("PATH", "").split(os.pathsep))
    
    conflicts = []
    for directory in all_dirs:
        if directory.strip():
            exe_path = os.path.join(directory, command_name + ".exe")
            if os.path.exists(exe_path):
                conflicts.append(exe_path)
    return conflicts

def get_launchers_in_dir():
    settings = get_settings()
    launcher_dir = settings.get("launcher_dir", DEFAULT_DIR)
    launchers = []

    if not os.path.exists(launcher_dir):
        return launchers

    for filename in os.listdir(launcher_dir):
        if filename.endswith(".exe") and filename != BASE_EXE_NAME:
            exe_path = os.path.join(launcher_dir, filename)
            target = get_target_from_exe(exe_path)

            # 提供更有用的显示信息
            if target is None:
                target = "<Legacy launcher - target unknown>"
            elif not target:
                target = "<Invalid configuration>"

            launchers.append({
                "name": filename[:-4],
                "exe_path": exe_path,
                "target": target
            })
    return launchers

def get_launcher_info(exe_path):
    """Get detailed information about a launcher file"""
    try:
        with open(exe_path, 'rb') as f:
            data = f.read()

        idx = data.rfind(MARKER)
        if idx == -1:
            return {"status": "invalid", "reason": "No configuration marker found"}

        config_bytes = data[idx + len(MARKER):]
        config_str = config_bytes.decode('utf-8').strip('\x00')

        if not config_str:
            return {"status": "invalid", "reason": "Empty configuration data"}

        config = json.loads(config_str)
        target = config.get("target", "")

        if not target:
            return {"status": "invalid", "reason": "Empty target path"}

        return {
            "status": "valid",
            "target": target,
            "config_size": len(config_str),
            "file_size": len(data)
        }

    except json.JSONDecodeError as e:
        return {"status": "invalid", "reason": f"Invalid JSON: {str(e)}"}
    except UnicodeDecodeError as e:
        return {"status": "invalid", "reason": f"Encoding error: {str(e)}"}
    except Exception as e:
        return {"status": "invalid", "reason": f"Error: {str(e)}"}

def get_target_from_exe(exe_path):
    try:
        with open(exe_path, 'rb') as f:
            data = f.read()
        idx = data.rfind(MARKER)
        if idx == -1:
            # No configuration marker found - might be an old launcher or not created by this tool
            return None
        config_bytes = data[idx + len(MARKER):]
        config_str = config_bytes.decode('utf-8').strip('\x00')
        if not config_str:
            return None
        config = json.loads(config_str)
        return config.get("target", "")
    except json.JSONDecodeError as e:
        # Config data is corrupted or invalid JSON
        return None
    except UnicodeDecodeError as e:
        # Config data has encoding issues
        return None
    except Exception as e:
        # Other unexpected errors
        return None

def create_launcher(command_name, target_path):
    settings = get_settings()
    launcher_dir = settings.get("launcher_dir", DEFAULT_DIR)
    
    base_exe = get_base_exe_path()
    if not os.path.exists(base_exe):
        return False, f"Base launcher not found: {base_exe}\nPlease run 'python build.py launcher' first."
    
    if not os.path.exists(target_path):
        return False, f"Target program not found: {target_path}"
    
    output_exe = os.path.join(launcher_dir, command_name + ".exe")
    config_json = json.dumps({"target": target_path}, ensure_ascii=False)
    config_bytes = config_json.encode('utf-8')
    
    try:
        with open(base_exe, 'rb') as f:
            base_data = f.read()
        
        with open(output_exe, 'wb') as f:
            f.write(base_data)
            f.write(MARKER)
            f.write(config_bytes)
        
        return True, f"Created: {output_exe}"
    except Exception as e:
        return False, str(e)

def delete_launcher(command_name):
    settings = get_settings()
    launcher_dir = settings.get("launcher_dir", DEFAULT_DIR)
    exe_path = os.path.join(launcher_dir, command_name + ".exe")
    
    if os.path.exists(exe_path):
        os.remove(exe_path)
        return True
    return False

def is_dir_in_path(launcher_dir):
    user_path = get_user_path()
    if not user_path:
        return False
    path_dirs = [d.strip() for d in user_path.split(os.pathsep) if d.strip()]
    return any(os.path.normpath(d) == os.path.normpath(launcher_dir) for d in path_dirs)

def add_dir_to_path(launcher_dir):
    user_path = get_user_path()
    if user_path:
        path_dirs = [d.strip() for d in user_path.split(os.pathsep) if d.strip()]
    else:
        path_dirs = []
    
    normalized_dir = os.path.normpath(launcher_dir)
    if normalized_dir not in [os.path.normpath(d) for d in path_dirs]:
        if user_path:
            new_path = user_path + os.pathsep + launcher_dir
        else:
            new_path = launcher_dir
        
        error = set_user_path(new_path)
        if error is True or error == "":
            return True, "PATH updated. You may need to restart terminals."
        else:
            return False, f"Failed to update PATH: {error}"
    return True, "Directory already in PATH."


class QuickLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Launcher")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        self.settings = get_settings()
        
        self.create_widgets()
        self.refresh_launcher_list()
        self.update_path_status()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        save_settings(self.settings)
        self.root.destroy()
    
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab_create = ttk.Frame(self.notebook)
        self.tab_manage = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_create, text="Create Launcher")
        self.notebook.add(self.tab_manage, text="Manage Launchers")
        self.notebook.add(self.tab_settings, text="Settings")
        
        self.create_create_tab()
        self.create_manage_tab()
        self.create_settings_tab()
    
    def create_create_tab(self):
        frame = ttk.LabelFrame(self.tab_create, text="Create New Launcher", padding=15)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Command Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.cmd_name_var = tk.StringVar()
        cmd_entry = ttk.Entry(frame, textvariable=self.cmd_name_var, width=40)
        cmd_entry.grid(row=0, column=1, sticky='we', pady=5, padx=5)
        cmd_entry.focus()
        
        ttk.Label(frame, text="Target Program:").grid(row=1, column=0, sticky='w', pady=5)
        target_frame = ttk.Frame(frame)
        target_frame.grid(row=1, column=1, sticky='we', pady=5, padx=5)
        
        self.target_var = tk.StringVar()
        ttk.Entry(target_frame, textvariable=self.target_var, width=35).pack(side='left', fill='x', expand=True)
        ttk.Button(target_frame, text="Browse", command=self.browse_target).pack(side='left', padx=5)
        
        ttk.Button(frame, text="Create Launcher", command=self.create_launcher_action).grid(
            row=2, column=0, columnspan=2, pady=20
        )
        
        self.status_var = tk.StringVar(value="Enter command name and target program")
        ttk.Label(frame, textvariable=self.status_var, foreground="blue").grid(
            row=3, column=0, columnspan=2, sticky='w'
        )
    
    def create_manage_tab(self):
        frame = ttk.Frame(self.tab_manage)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('name', 'target')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        self.tree.heading('name', text='Command')
        self.tree.heading('target', text='Target Program')
        self.tree.column('name', width=150)
        self.tree.column('target', width=500)
        
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=10)
        
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_launcher_list).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Open Target Folder", command=self.open_target_folder).pack(side='left', padx=5)
    
    def create_settings_tab(self):
        frame = ttk.LabelFrame(self.tab_settings, text="Settings", padding=15)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Launcher Directory:").grid(row=0, column=0, sticky='w', pady=5)
        
        dir_frame = ttk.Frame(frame)
        dir_frame.grid(row=1, column=0, columnspan=2, sticky='we', pady=5)
        
        self.launcher_dir_var = tk.StringVar(value=self.settings.get("launcher_dir", DEFAULT_DIR))
        ttk.Entry(dir_frame, textvariable=self.launcher_dir_var, width=50).pack(side='left', fill='x', expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_launcher_dir).pack(side='left', padx=5)
        ttk.Button(dir_frame, text="Save", command=self.save_launcher_dir).pack(side='left', padx=5)
        
        ttk.Separator(frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='we', pady=15)
        
        ttk.Label(frame, text="PATH Status:").grid(row=3, column=0, sticky='w', pady=5)
        self.path_status_var = tk.StringVar(value="Checking...")
        ttk.Label(frame, textvariable=self.path_status_var, foreground="gray").grid(row=3, column=1, sticky='w', pady=5)
        
        self.path_dir_status_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.path_dir_status_var).grid(row=4, column=1, sticky='w', pady=2)
        
        ttk.Button(frame, text="Add Directory to PATH", command=self.add_to_path).grid(
            row=5, column=0, columnspan=2, pady=10
        )
        
        ttk.Separator(frame, orient='horizontal').grid(row=6, column=0, columnspan=2, sticky='we', pady=15)
        
        ttk.Label(frame, text="Base Launcher:").grid(row=7, column=0, sticky='w', pady=5)
        self.base_exe_status_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.base_exe_status_var).grid(row=7, column=1, sticky='w', pady=5)
        
        ttk.Button(frame, text="Build / Rebuild Base Launcher", command=self.build_base_launcher).grid(
            row=8, column=0, columnspan=2, pady=10
        )
    
    def browse_target(self):
        filename = filedialog.askopenfilename(
            title="Select Target Program",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if filename:
            self.target_var.set(filename)
    
    def browse_launcher_dir(self):
        directory = filedialog.askdirectory(title="Select Launcher Directory")
        if directory:
            self.launcher_dir_var.set(directory)
    
    def save_launcher_dir(self):
        new_dir = self.launcher_dir_var.get().strip()
        if new_dir:
            if not os.path.exists(new_dir):
                try:
                    os.makedirs(new_dir)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create directory:\n{e}")
                    return
            self.settings["launcher_dir"] = new_dir
            save_settings(self.settings)
            self.update_path_status()
            self.refresh_launcher_list()
            messagebox.showinfo("Saved", f"Launcher directory set to:\n{new_dir}")
    
    def create_launcher_action(self):
        command_name = self.cmd_name_var.get().strip()
        target_path = self.target_var.get().strip()
        
        if not command_name:
            self.status_var.set("Error: Command name is required")
            self.status_var.set("Error: Command name is required")
            return
        
        if not target_path:
            self.status_var.set("Error: Target program is required")
            return
        
        if not command_name.replace('_', '').replace('-', '').isalnum():
            self.status_var.set("Error: Command name must be alphanumeric (underscores and hyphens allowed)")
            return
        
        conflicts = scan_all_path_for_conflict(command_name)
        
        if conflicts:
            conflict_list = "\n".join(conflicts)
            response = messagebox.askyesno(
                "Conflict Detected",
                f"The command '{command_name}' already exists in:\n{conflict_list}\n\nDo you want to overwrite it in the launcher directory?"
            )
            if not response:
                self.status_var.set("Cancelled: Command name conflicts with existing PATH entries")
                return
        
        success, message = create_launcher(command_name, target_path)
        
        if success:
            self.status_var.set(f"Success: Created '{command_name}' -> {target_path}")
            self.cmd_name_var.set("")
            self.target_var.set("")
            self.refresh_launcher_list()
        else:
            self.status_var.set(f"Error: {message}")
    
    def refresh_launcher_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        launchers = get_launchers_in_dir()
        for launcher in launchers:
            self.tree.insert('', 'end', values=(launcher['name'], launcher['target']))

        self.update_base_exe_status()
    
    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a launcher to delete")
            return
        
        for item in selection:
            values = self.tree.item(item)['values']
            command_name = values[0]
            
            response = messagebox.askyesno(
                "Confirm Delete",
                f"Delete launcher '{command_name}'?"
            )
            
            if response:
                if delete_launcher(command_name):
                    self.tree.delete(item)
        
        self.update_base_exe_status()
    
    def open_target_folder(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a launcher")
            return

        values = self.tree.item(selection[0])['values']
        target = values[1]

        # 检查是否为遗留启动器或无效配置
        if target.startswith('<') and target.endswith('>'):
            messagebox.showinfo("Legacy Launcher",
                "This is a legacy launcher with unknown target.\n"
                "The target program cannot be determined from the launcher file.")
            return

        if target:
            folder = os.path.dirname(target)
            if os.path.exists(folder):
                os.startfile(folder)
            else:
                messagebox.showwarning("Folder Not Found",
                    f"Target folder does not exist:\n{folder}")
        else:
            messagebox.showwarning("No Target", "This launcher has no target configured.")
    
    def update_path_status(self):
        launcher_dir = self.settings.get("launcher_dir", DEFAULT_DIR)
        
        if is_dir_in_path(launcher_dir):
            self.path_status_var.set("Added to PATH")
            self.path_status_var.set("In PATH (OK)")
            self.path_dir_status_var.set("")
        else:
            self.path_status_var.set("Not in PATH")
            self.path_dir_status_var.set(f"'{launcher_dir}' not found in user PATH")
    
    def add_to_path(self):
        launcher_dir = self.settings.get("launcher_dir", DEFAULT_DIR)
        success, message = add_dir_to_path(launcher_dir)
        
        if success:
            messagebox.showinfo("Success", message)
            self.update_path_status()
        else:
            messagebox.showerror("Error", message)
    
    def update_base_exe_status(self):
        base_exe = get_base_exe_path()
        if os.path.exists(base_exe):
            size = os.path.getsize(base_exe)
            self.base_exe_status_var.set(f"Found ({size:,} bytes)")
        else:
            self.base_exe_status_var.set("Not found - click 'Build Base Launcher' below")
    
    def build_base_launcher(self):
        import subprocess
        import sys
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        build_py = os.path.join(script_dir, "build.py")
        
        if not os.path.exists(build_py):
            messagebox.showerror("Error", f"build.py not found in:\n{script_dir}")
            return
        
        messagebox.showinfo("Building", "Building base launcher, please wait...")
        
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        
        python_exe = sys.executable.replace('python.exe', 'pythonw.exe')
        if not os.path.exists(python_exe):
            python_exe = sys.executable
        
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "0"
        
        with open(os.devnull, 'w') as devnull:
            result = subprocess.run(
                [python_exe, build_py, "launcher"],
                cwd=script_dir,
                stdin=devnull,
                stdout=devnull,
                stderr=subprocess.STDOUT,
                startupinfo=si,
                creationflags=subprocess.CREATE_NO_WINDOW,
                env=env
            )
        
        if result.returncode == 0:
            messagebox.showinfo("Success", "Base launcher built successfully!")
            self.update_base_exe_status()
        else:
            messagebox.showerror("Build Failed", "Build failed. Check build.py output.")


def main():
    ensure_launcher_dir()
    root = tk.Tk()
    app = QuickLauncherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
