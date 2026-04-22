import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import winreg
from ctypes import windll, c_long, byref, wintypes

from utils import get_settings, save_settings, ensure_launcher_dir, DEFAULT_DIR

MARKER = b"__QUICK_LAUNCHER_CONFIG__"
BASE_EXE_NAME = "_ql_base.exe"
SETTINGS_FILE = "settings.json"

# ====================
# 现代化设计系统
# ====================

class DesignSystem:
    """工业科技风格设计系统"""

    # 颜色方案 - 深色工业科技风（调整版）
    COLORS = {
        'bg_dark': '#0A0E1A',           # 深空蓝背景
        'bg_card': '#1A1F2E',           # 卡片背景
        'bg_sidebar': '#0F1419',        # 侧边栏背景
        'accent_blue': '#3B82F6',       # 柔和蓝色强调色（原为#00D4FF）
        'accent_green': '#10B981',      # 柔和绿色强调色（原为#00FF88）
        'accent_orange': '#F97316',     # 柔和橙色警告（原为#FF6B35）
        'text_primary': '#F1F5F9',      # 主要文本（提高亮度）
        'text_secondary': '#94A3B8',    # 次要文本（提高亮度）
        'border': '#334155',            # 边框（稍微提亮）
        'hover': '#2563EB',             # 悬停效果
        'success': '#059669',           # 成功状态（柔和绿色）
        'warning': '#D97706',           # 警告状态（柔和橙色）
        'error': '#DC2626'              # 错误状态（柔和红色）
    }

    # 字体系统
    FONTS = {
        'title': ('Segoe UI', 16, 'bold'),
        'heading': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'code': ('Consolas', 9),
        'small': ('Segoe UI', 8)
    }

    # 尺寸系统
    SIZES = {
        'padding_small': 8,
        'padding_medium': 16,
        'padding_large': 24,
        'border_radius': 8,
        'border_width': 1,
        'icon_size': 16
    }

# ====================
# 自定义样式组件
# ====================

class ModernButton(ttk.Button):
    """现代化按钮组件"""

    def __init__(self, master, **kwargs):
        # 设置默认样式
        if 'style' not in kwargs:
            kwargs['style'] = 'Modern.TButton'

        super().__init__(master, **kwargs)

class ModernEntry(ttk.Entry):
    """现代化输入框组件"""

    def __init__(self, master, **kwargs):
        if 'style' not in kwargs:
            kwargs['style'] = 'Modern.TEntry'
        super().__init__(master, **kwargs)

class ModernLabel(ttk.Label):
    """现代化标签组件"""

    def __init__(self, master, **kwargs):
        # 自动设置字体
        if 'font' not in kwargs:
            kwargs['font'] = DesignSystem.FONTS['body']

        # 自动设置前景色
        if 'foreground' not in kwargs:
            kwargs['foreground'] = DesignSystem.COLORS['text_primary']

        # 自动设置背景色
        if 'background' not in kwargs:
            kwargs['background'] = DesignSystem.COLORS['bg_card']

        super().__init__(master, **kwargs)

class StatusIndicator(tk.Canvas):
    """状态指示器组件"""

    def __init__(self, master, status='neutral', **kwargs):
        super().__init__(master, width=12, height=12, bg=DesignSystem.COLORS['bg_card'],
                        highlightthickness=0, **kwargs)
        self.status = status
        self.draw_indicator()

    def draw_indicator(self):
        self.delete('all')
        colors = {
            'success': DesignSystem.COLORS['success'],
            'warning': DesignSystem.COLORS['warning'],
            'error': DesignSystem.COLORS['error'],
            'neutral': DesignSystem.COLORS['text_secondary']
        }

        center_x, center_y = 6, 6
        radius = 4

        # 绘制外圈光晕
        self.create_oval(center_x-radius-1, center_y-radius-1,
                        center_x+radius+1, center_y+radius+1,
                        fill=colors[self.status], outline='', stipple='gray50')

        # 绘制内圈
        self.create_oval(center_x-radius, center_y-radius,
                        center_x+radius, center_y+radius,
                        fill=colors[self.status], outline='')

    def set_status(self, status):
        self.status = status
        self.draw_indicator()

# ====================
# 业务逻辑函数
# ====================

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

def get_base_exe_path():
    settings = get_settings()
    launcher_dir = settings.get("launcher_dir", DEFAULT_DIR)
    return os.path.join(launcher_dir, BASE_EXE_NAME)

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

def get_target_from_exe(exe_path):
    """Extract target path from launcher executable"""
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
        config = json.loads(config_str)
        return config.get("target", "")
    except:
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

# ====================
# 主应用程序类
# ====================

class QuickLauncherApp:
    """现代化快速启动器应用程序"""

    def __init__(self, root):
        self.root = root
        self.root.title("QuickLauncher Pro")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)

        # 设置应用程序样式
        self.setup_styles()

        # 加载设置
        self.settings = get_settings()

        # 创建界面
        self.create_widgets()
        self.refresh_launcher_list()
        self.update_path_status()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 应用深色主题
        self.root.configure(bg=DesignSystem.COLORS['bg_dark'])

    def setup_styles(self):
        """设置ttk样式"""
        style = ttk.Style()

        # 配置主题
        style.theme_use('default')

        # 按钮样式
        style.configure('Modern.TButton',
                       font=DesignSystem.FONTS['body'],
                       background=DesignSystem.COLORS['accent_blue'],
                       foreground='white',
                       borderwidth=0,
                       focusthickness=0,
                       focuscolor='none')
        style.map('Modern.TButton',
                  background=[('active', DesignSystem.COLORS['hover'])],
                  foreground=[('active', 'white')])

        # 输入框样式
        style.configure('Modern.TEntry',
                       fieldbackground=DesignSystem.COLORS['bg_card'],
                       foreground=DesignSystem.COLORS['text_primary'],
                       insertcolor=DesignSystem.COLORS['accent_blue'],
                       bordercolor=DesignSystem.COLORS['border'])

        # 标签样式
        style.configure('Modern.TLabel',
                       background=DesignSystem.COLORS['bg_card'],
                       foreground=DesignSystem.COLORS['text_primary'],
                       font=DesignSystem.FONTS['body'])

        # Notebook样式
        style.configure('Modern.TNotebook',
                       background=DesignSystem.COLORS['bg_dark'],
                       borderwidth=0)
        style.configure('Modern.TNotebook.Tab',
                       background=DesignSystem.COLORS['bg_card'],
                       foreground=DesignSystem.COLORS['text_secondary'],
                       borderwidth=0,
                       padding=[16, 8],
                       font=DesignSystem.FONTS['body'])
        style.map('Modern.TNotebook.Tab',
                  background=[('selected', DesignSystem.COLORS['accent_blue'])],
                  foreground=[('selected', 'white')])

        # Treeview样式
        style.configure('Modern.Treeview',
                       background=DesignSystem.COLORS['bg_card'],
                       foreground=DesignSystem.COLORS['text_primary'],
                       fieldbackground=DesignSystem.COLORS['bg_card'],
                       borderwidth=0,
                       font=DesignSystem.FONTS['body'])
        style.configure('Modern.Treeview.Heading',
                       background=DesignSystem.COLORS['bg_sidebar'],
                       foreground=DesignSystem.COLORS['accent_blue'],
                       font=DesignSystem.FONTS['heading'],
                       borderwidth=0)
        style.map('Modern.Treeview',
                  background=[('selected', DesignSystem.COLORS['accent_blue'])],
                  foreground=[('selected', 'white')])

    def create_widgets(self):
        """创建主界面"""
        # 主容器
        self.main_container = tk.Frame(self.root, bg=DesignSystem.COLORS['bg_dark'])
        self.main_container.pack(fill='both', expand=True, padx=DesignSystem.SIZES['padding_large'],
                                pady=DesignSystem.SIZES['padding_large'])

        # 标题栏
        self.create_header()

        # 主要内容区域
        self.create_main_content()

    def create_header(self):
        """创建标题栏"""
        header_frame = tk.Frame(self.main_container, bg=DesignSystem.COLORS['bg_dark'])
        header_frame.pack(fill='x', pady=(0, DesignSystem.SIZES['padding_large']))

        # 应用图标和标题
        title_frame = tk.Frame(header_frame, bg=DesignSystem.COLORS['bg_dark'])
        title_frame.pack(side='left')

        # 应用图标（使用Unicode字符）
        icon_label = tk.Label(title_frame, text="🚀", font=('Segoe UI', 24),
                             fg=DesignSystem.COLORS['accent_blue'],
                             bg=DesignSystem.COLORS['bg_dark'])
        icon_label.pack(side='left', padx=(0, DesignSystem.SIZES['padding_medium']))

        # 应用标题
        title_label = tk.Label(title_frame, text="QuickLauncher Pro",
                              font=DesignSystem.FONTS['title'],
                              fg=DesignSystem.COLORS['text_primary'],
                              bg=DesignSystem.COLORS['bg_dark'])
        title_label.pack(side='left')

        # 副标题
        subtitle_label = tk.Label(header_frame,
                                 text="Professional Windows Launcher Manager",
                                 font=DesignSystem.FONTS['small'],
                                 fg=DesignSystem.COLORS['text_secondary'],
                                 bg=DesignSystem.COLORS['bg_dark'])
        subtitle_label.pack(side='right')

    def create_main_content(self):
        """创建主要内容区域"""
        content_frame = tk.Frame(self.main_container, bg=DesignSystem.COLORS['bg_dark'])
        content_frame.pack(fill='both', expand=True)

        # 创建Notebook（选项卡）
        self.notebook = ttk.Notebook(content_frame, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True)

        # 创建各个选项卡
        self.create_create_tab()
        self.create_manage_tab()
        self.create_settings_tab()

    def create_create_tab(self):
        """创建'创建启动器'选项卡"""
        tab_frame = tk.Frame(self.notebook, bg=DesignSystem.COLORS['bg_card'])
        self.notebook.add(tab_frame, text="  Create Launcher  ")

        # 主要内容容器
        main_frame = tk.Frame(tab_frame, bg=DesignSystem.COLORS['bg_card'])
        main_frame.pack(fill='both', expand=True, padx=DesignSystem.SIZES['padding_large'],
                       pady=DesignSystem.SIZES['padding_large'])

        # 标题
        title_label = ModernLabel(main_frame, text="Create New Launcher",
                                 font=DesignSystem.FONTS['title'])
        title_label.pack(anchor='w', pady=(0, DesignSystem.SIZES['padding_large']))

        # 创建表单
        form_frame = tk.Frame(main_frame, bg=DesignSystem.COLORS['bg_card'])
        form_frame.pack(fill='x', pady=DesignSystem.SIZES['padding_medium'])

        # 命令名称输入
        cmd_frame = tk.Frame(form_frame, bg=DesignSystem.COLORS['bg_card'])
        cmd_frame.pack(fill='x', pady=DesignSystem.SIZES['padding_small'])

        cmd_label = ModernLabel(cmd_frame, text="Command Name",
                               font=DesignSystem.FONTS['heading'])
        cmd_label.pack(anchor='w', pady=(0, DesignSystem.SIZES['padding_small']))

        self.cmd_name_var = tk.StringVar()
        cmd_entry = ModernEntry(cmd_frame, textvariable=self.cmd_name_var, width=50)
        cmd_entry.pack(fill='x', ipady=8)

        # 目标程序输入
        target_frame = tk.Frame(form_frame, bg=DesignSystem.COLORS['bg_card'])
        target_frame.pack(fill='x', pady=DesignSystem.SIZES['padding_small'])

        target_label = ModernLabel(target_frame, text="Target Program",
                                  font=DesignSystem.FONTS['heading'])
        target_label.pack(anchor='w', pady=(0, DesignSystem.SIZES['padding_small']))

        target_input_frame = tk.Frame(target_frame, bg=DesignSystem.COLORS['bg_card'])
        target_input_frame.pack(fill='x')

        self.target_var = tk.StringVar()
        target_entry = ModernEntry(target_input_frame, textvariable=self.target_var)
        target_entry.pack(side='left', fill='x', expand=True, ipady=8)

        browse_btn = ModernButton(target_input_frame, text="Browse",
                                 command=self.browse_target, width=10)
        browse_btn.pack(side='left', padx=(DesignSystem.SIZES['padding_small'], 0))

        # 创建按钮
        create_btn = ModernButton(form_frame, text="Create Launcher",
                                 command=self.create_launcher_action)
        create_btn.pack(pady=DesignSystem.SIZES['padding_large'], ipadx=20, ipady=8)

        # 状态显示
        self.status_var = tk.StringVar(value="Enter command name and target program")
        status_label = ModernLabel(form_frame, textvariable=self.status_var,
                                  foreground=DesignSystem.COLORS['text_secondary'])
        status_label.pack(anchor='w')

    def create_manage_tab(self):
        """创建'管理启动器'选项卡"""
        tab_frame = tk.Frame(self.notebook, bg=DesignSystem.COLORS['bg_card'])
        self.notebook.add(tab_frame, text="  Manage Launchers  ")

        # 主要内容容器
        main_frame = tk.Frame(tab_frame, bg=DesignSystem.COLORS['bg_card'])
        main_frame.pack(fill='both', expand=True, padx=DesignSystem.SIZES['padding_large'],
                       pady=DesignSystem.SIZES['padding_large'])

        # 标题和工具栏
        header_frame = tk.Frame(main_frame, bg=DesignSystem.COLORS['bg_card'])
        header_frame.pack(fill='x', pady=(0, DesignSystem.SIZES['padding_medium']))

        title_label = ModernLabel(header_frame, text="Installed Launchers",
                                 font=DesignSystem.FONTS['title'])
        title_label.pack(side='left')

        # 工具栏按钮
        toolbar_frame = tk.Frame(header_frame, bg=DesignSystem.COLORS['bg_card'])
        toolbar_frame.pack(side='right')

        refresh_btn = ModernButton(toolbar_frame, text="Refresh",
                                  command=self.refresh_launcher_list, width=10)
        refresh_btn.pack(side='left', padx=(0, DesignSystem.SIZES['padding_small']))

        delete_btn = ModernButton(toolbar_frame, text="Delete Selected",
                                 command=self.delete_selected, width=15)
        delete_btn.pack(side='left', padx=(0, DesignSystem.SIZES['padding_small']))

        folder_btn = ModernButton(toolbar_frame, text="Open Folder",
                                 command=self.open_target_folder, width=12)
        folder_btn.pack(side='left')

        # 启动器列表
        list_frame = tk.Frame(main_frame, bg=DesignSystem.COLORS['bg_card'])
        list_frame.pack(fill='both', expand=True)

        # 创建Treeview
        columns = ('name', 'target')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                height=15, style='Modern.Treeview')

        self.tree.heading('name', text='Command Name')
        self.tree.heading('target', text='Target Program')
        self.tree.column('name', width=200, anchor='w')
        self.tree.column('target', width=400, anchor='w')

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_settings_tab(self):
        """创建'设置'选项卡"""
        tab_frame = tk.Frame(self.notebook, bg=DesignSystem.COLORS['bg_card'])
        self.notebook.add(tab_frame, text="  Settings  ")

        # 主要内容容器
        main_frame = tk.Frame(tab_frame, bg=DesignSystem.COLORS['bg_card'])
        main_frame.pack(fill='both', expand=True, padx=DesignSystem.SIZES['padding_large'],
                       pady=DesignSystem.SIZES['padding_large'])

        # 标题
        title_label = ModernLabel(main_frame, text="Application Settings",
                                 font=DesignSystem.FONTS['title'])
        title_label.pack(anchor='w', pady=(0, DesignSystem.SIZES['padding_large']))

        # 设置项容器
        settings_frame = tk.Frame(main_frame, bg=DesignSystem.COLORS['bg_card'])
        settings_frame.pack(fill='x', pady=DesignSystem.SIZES['padding_medium'])

        # 启动器目录设置
        dir_frame = tk.Frame(settings_frame, bg=DesignSystem.COLORS['bg_card'])
        dir_frame.pack(fill='x', pady=DesignSystem.SIZES['padding_small'])

        dir_label = ModernLabel(dir_frame, text="Launcher Directory",
                               font=DesignSystem.FONTS['heading'])
        dir_label.pack(anchor='w', pady=(0, DesignSystem.SIZES['padding_small']))

        dir_input_frame = tk.Frame(dir_frame, bg=DesignSystem.COLORS['bg_card'])
        dir_input_frame.pack(fill='x')

        self.launcher_dir_var = tk.StringVar(value=self.settings.get("launcher_dir", DEFAULT_DIR))
        dir_entry = ModernEntry(dir_input_frame, textvariable=self.launcher_dir_var)
        dir_entry.pack(side='left', fill='x', expand=True, ipady=8)

        dir_browse_btn = ModernButton(dir_input_frame, text="Browse",
                                       command=self.browse_launcher_dir, width=10)
        dir_browse_btn.pack(side='left', padx=(DesignSystem.SIZES['padding_small'], 0))

        dir_save_btn = ModernButton(dir_input_frame, text="Save",
                                   command=self.save_launcher_dir, width=8)
        dir_save_btn.pack(side='left', padx=(DesignSystem.SIZES['padding_small'], 0))

        # PATH状态
        path_frame = tk.Frame(settings_frame, bg=DesignSystem.COLORS['bg_card'])
        path_frame.pack(fill='x', pady=DesignSystem.SIZES['padding_small'])

        path_label = ModernLabel(path_frame, text="PATH Status",
                                font=DesignSystem.FONTS['heading'])
        path_label.pack(anchor='w', pady=(0, DesignSystem.SIZES['padding_small']))

        path_status_frame = tk.Frame(path_frame, bg=DesignSystem.COLORS['bg_card'])
        path_status_frame.pack(fill='x')

        self.path_status_indicator = StatusIndicator(path_status_frame, status='neutral')
        self.path_status_indicator.pack(side='left', padx=(0, DesignSystem.SIZES['padding_small']))

        self.path_status_var = tk.StringVar(value="Checking...")
        path_status_label = ModernLabel(path_status_frame, textvariable=self.path_status_var)
        path_status_label.pack(side='left')

        path_btn = ModernButton(path_frame, text="Add Directory to PATH",
                               command=self.add_to_path)
        path_btn.pack(anchor='w', pady=(DesignSystem.SIZES['padding_small'], 0))

        # 基础启动器状态
        base_frame = tk.Frame(settings_frame, bg=DesignSystem.COLORS['bg_card'])
        base_frame.pack(fill='x', pady=DesignSystem.SIZES['padding_small'])

        base_label = ModernLabel(base_frame, text="Base Launcher",
                                font=DesignSystem.FONTS['heading'])
        base_label.pack(anchor='w', pady=(0, DesignSystem.SIZES['padding_small']))

        base_status_frame = tk.Frame(base_frame, bg=DesignSystem.COLORS['bg_card'])
        base_status_frame.pack(fill='x')

        self.base_exe_indicator = StatusIndicator(base_status_frame, status='neutral')
        self.base_exe_indicator.pack(side='left', padx=(0, DesignSystem.SIZES['padding_small']))

        self.base_exe_status_var = tk.StringVar(value="Checking...")
        base_status_label = ModernLabel(base_status_frame, textvariable=self.base_exe_status_var)
        base_status_label.pack(side='left')

        build_btn = ModernButton(base_frame, text="Build / Rebuild Base Launcher",
                                command=self.build_base_launcher)
        build_btn.pack(anchor='w', pady=(DesignSystem.SIZES['padding_small'], 0))

    # ====================
    # 事件处理方法
    # ====================

    def on_closing(self):
        """窗口关闭事件"""
        save_settings(self.settings)
        self.root.destroy()

    def browse_target(self):
        """浏览目标程序"""
        filename = filedialog.askopenfilename(
            title="Select Target Program",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if filename:
            self.target_var.set(filename)

    def browse_launcher_dir(self):
        """浏览启动器目录"""
        directory = filedialog.askdirectory(title="Select Launcher Directory")
        if directory:
            self.launcher_dir_var.set(directory)

    def save_launcher_dir(self):
        """保存启动器目录设置"""
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
        """创建启动器操作"""
        command_name = self.cmd_name_var.get().strip()
        target_path = self.target_var.get().strip()

        if not command_name:
            self.status_var.set("Error: Command name is required")
            return

        if not target_path:
            self.status_var.set("Error: Target program is required")
            return

        if not command_name.replace('_', '').replace('-', '').isalnum():
            self.status_var.set("Error: Command name must be alphanumeric (underscores and hyphens allowed)")
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
        """刷新启动器列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        launchers = get_launchers_in_dir()
        for launcher in launchers:
            self.tree.insert('', 'end', values=(launcher['name'], launcher['target']))

        self.update_base_exe_status()

    def delete_selected(self):
        """删除选中的启动器"""
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
        """打开目标文件夹"""
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
        """更新PATH状态"""
        launcher_dir = self.settings.get("launcher_dir", DEFAULT_DIR)

        if is_dir_in_path(launcher_dir):
            self.path_status_var.set("In PATH (OK)")
            self.path_status_indicator.set_status('success')
        else:
            self.path_status_var.set("Not in PATH")
            self.path_status_indicator.set_status('warning')

    def add_to_path(self):
        """添加到PATH"""
        launcher_dir = self.settings.get("launcher_dir", DEFAULT_DIR)
        success, message = add_dir_to_path(launcher_dir)

        if success:
            messagebox.showinfo("Success", message)
            self.update_path_status()
        else:
            messagebox.showerror("Error", message)

    def update_base_exe_status(self):
        """更新基础启动器状态"""
        base_exe = get_base_exe_path()
        if os.path.exists(base_exe):
            size = os.path.getsize(base_exe)
            self.base_exe_status_var.set(f"Found ({size:,} bytes)")
            self.base_exe_indicator.set_status('success')
        else:
            self.base_exe_status_var.set("Not found - click 'Build Base Launcher' below")
            self.base_exe_indicator.set_status('error')

    def build_base_launcher(self):
        """构建基础启动器"""
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