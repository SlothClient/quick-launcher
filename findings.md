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

## Resources
- PyInstaller docs: https://pyinstaller.org/
- winreg Python docs: https://docs.python.org/3/library/winreg.html
- Windows API: SendMessageTimeout with WM_SETTINGCHANGE
