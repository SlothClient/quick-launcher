# Task Plan: Quick Launcher

## Goal
Create a Windows desktop app that lets users create quick-launch commands (like `bar`) that open any program via the Explorer address bar, with conflict detection, management UI, and PATH integration.

## Current Phase
Complete

## Phases

### Phase 1: Requirements & Discovery
- [x] User intent confirmed via questions
- [x] Technology choices made: tkinter, PyInstaller, embedded config
- [x] Architecture decision: embedded config in exe (not JSON files)
- **Status:** complete

### Phase 2: Project Setup & Core Files
- [x] Create project structure (directories, requirements.txt)
- [x] Implement launcher.py (generic launcher with embedded config reading)
- [x] Implement app.py core utils (PATH detection, conflict scan, exe generation)
- [x] Implement build.py (PyInstaller packaging scripts)
- **Status:** complete

### Phase 3: GUI Implementation
- [x] Create Tab: Create launcher (command name input, browse button, conflict detection, create button)
- [x] Create Tab: Manage launchers (Treeview list, delete/edit functionality)
- [x] Create Tab: Settings (directory path config, PATH status, add to PATH button)
- **Status:** complete

### Phase 4: Testing & Verification
- [x] Build launcher base exe
- [x] Test creating a quick command (mynotepad -> notepad.exe)
- [x] Test conflict detection (found 4 python.exe in PATH)
- [x] Test launching notepad via quick command
- **Status:** complete

### Phase 5: Packaging & Delivery
- [x] Package app as QuickLauncher.exe
- [x] Create .gitignore
- [x] Initial git commit + multiple fix commits
- **Status:** complete

### Phase 6: Modernization & Enhancement
- [x] **Modern UI Design**: Create industrial-tech style interface with dark theme
- [x] **Color Scheme Optimization**: Reduce eye strain with softer, professional colors
- [x] **Code Quality**: Extract common utilities to utils.py module
- [x] **UX Improvements**: Better display of legacy launchers and error handling
- [x] **Build System**: Add force kill capability for updating running executables
- [x] **Windows Integration**: Create Start Menu shortcuts for searchability
- **Status:** complete

## Key Questions
1. How to embed config in exe without breaking it? → Append data after PE marker
2. How to refresh PATH without reboot? → SendMessageTimeout with WM_SETTINGCHANGE
3. Default directory location? → D:\.quick-launchers (user configurable)

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Embedded config in exe | No extra .json files needed, each exe is self-contained |
| tkinter for GUI | Built-in, no extra dependencies |
| D:\.quick-launchers default | D: drive likely exists, hidden folder convention |
| Subprocess spawn (not call) | Launches target app and exits immediately |
| --noconsole for PyInstaller | Proper console hiding for Windows GUI apps |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| launcher.py not found when running from temp dir | Auto-detect via build.py instead of __file__ | Fixed by calling build.py from app.py |
| Console window still shows | Changed --windowed to --noconsole | Using --noconsole flag |
| dist folder lock error | Move exe to project root first | Using temp dir + shutil.move |

## Notes
- Embedded config format: `b"__QUICK_LAUNCHER_CONFIG__" + json_config_bytes`
- PATH uses winreg for user-level modification
- Each quick command exe is a copy of base + embedded target path
- QuickLauncher.exe output to project root, only one exe file remains
