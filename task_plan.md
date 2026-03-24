# Task Plan: Quick Launcher

## Goal
Create a Windows desktop app that lets users create quick-launch commands (like `bar`) that open any program via the Explorer address bar, with conflict detection, management UI, and PATH integration.

## Current Phase
Phase 1

## Phases

### Phase 1: Requirements & Discovery
- [x] User intent confirmed via questions
- [x] Technology choices made: tkinter, PyInstaller, embedded config
- [x] Architecture decision: embedded config in exe (not JSON files)
- **Status:** complete

### Phase 2: Project Setup & Core Files
- [ ] Create project structure (directories, requirements.txt)
- [ ] Implement launcher.py (generic launcher with embedded config reading)
- [ ] Implement app.py core utils (PATH detection, conflict scan, exe generation)
- [ ] Implement build.py (PyInstaller packaging scripts)
- **Status:** pending

### Phase 3: GUI Implementation
- [ ] Create Tab: Create launcher (command name input, browse button, conflict detection, create button)
- [ ] Create Tab: Manage launchers (Treeview list, delete/edit functionality)
- [ ] Create Tab: Settings (directory path config, PATH status, add to PATH button)
- **Status:** pending

### Phase 4: Testing & Verification
- [ ] Build launcher base exe
- [ ] Test creating a quick command (e.g., `notepad`)
- [ ] Test conflict detection
- [ ] Test management features (list, delete)
- [ ] Test PATH addition
- **Status:** pending

### Phase 5: Packaging & Delivery
- [ ] Package app as QuickLauncher.exe
- [ ] Create .gitignore
- [ ] Initial git commit
- **Status:** pending

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

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       |         |            |

## Notes
- Embedded config format: `b"__QUICK_LAUNCHER_CONFIG__" + json_config_bytes`
- PATH uses winreg for user-level modification
- Each quick command exe is a copy of base + embedded target path
