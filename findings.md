# Findings & Decisions

## Requirements
- GUI desktop app (tkinter)
- User inputs: command name + target program path
- Detect conflicts if command name already exists in PATH
- Generate .exe launchers that open target programs
- Manage launchers (list, delete)
- Configurable launcher directory (default D:\.quick-launchers)
- Add launcher directory to PATH
- Package app itself as .exe

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Embedded config via file append | PyInstaller exe ignores trailing data, self-contained |
| tkinter (built-in) | No extra dependencies |
| D:\.quick-launchers default | D: typically exists, dot prefix = hidden convention |
| subprocess.Popen (spawn, not call) | Target app runs independently, launcher exits |
| shutil.which() + PATH scan | Double-check for conflict detection |

## Architecture
```
launcher.py → PyInstaller → _ql_base.exe
                               ↓ copy + embed config
                          notepad.exe (self-contained)
```

## Key Implementation Details
- MARKER = b"__QUICK_LAUNCHER_CONFIG__"
- Config stored as JSON: {"target": "C:\\path\\to\\app.exe"}
- Config appended to exe file, read via rfind(MARKER)
- PATH refresh via: SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, "Environment")
- User PATH stored in: HKEY_CURRENT_USER\Environment (not system-wide)

## Modernization Findings

### Console Window Fix
- PyInstaller --noconsole is REQUIRED for both base launcher AND app
- Removing print()/input() from launcher.py prevents console allocation
- subprocess.Popen should use CREATE_NO_WINDOW flag

### Code Quality Improvements
- utils.py module reduces code duplication by ~200 lines
- _extract_config_from_exe() unified config extraction across app.py and launcher.py
- get_hidden_startupinfo() and get_subprocess_env() standardize subprocess calls
- kill_process() utility handles force-kill for updating running executables

### UI Design Decisions
| Decision | Rationale |
|----------|-----------|
| Dark theme (#0A0E1A) | Reduces eye strain, professional appearance |
| Blue accent (#3B82F6) | Softer than cyan, better text contrast |
| Status indicators | Visual feedback for PATH and base launcher status |
| Custom ttk styles | Consistent look across all widgets |

### Windows Integration
- Start Menu shortcuts required for Win+S search
- PowerShell + WScript.Shell.CreateShortcut is reliable method
- Shortcuts should point to working directory for relative paths
- Windows search index may need time to recognize new shortcuts

## Resources
- PyInstaller docs: https://pyinstaller.org/
- winreg Python docs: https://docs.python.org/3/library/winreg.html
- Windows API: SendMessageTimeout with WM_SETTINGCHANGE
- ttk styling: https://docs.python.org/3/library/tkinter.ttk.html
