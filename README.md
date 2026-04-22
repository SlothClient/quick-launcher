# Quick Launcher - Windows 快速启动器

一个现代化的 Windows 桌面应用程序，让您通过资源管理器地址栏快速启动任何程序。只需输入简短命令（如 `npd`），即可打开对应的程序，无需记忆完整路径。

![create](README.assets\image-20260422204650166.png)

![manage](README.assets\image-20260422204717933.png)

![settings](README.assets\image-20260422204734627.png)

## ✨ 主要功能

### 🚀 快速启动
- **地址栏启动**: 在 Windows 资源管理器地址栏输入命令即可启动程序
- **命令简洁**: 使用简短易记的命令名（如 `npd`）
- **即时响应**: 毫秒级启动速度

### 🛡️ 冲突检测
- **智能检测**: 自动扫描 PATH 环境变量中的命令冲突
- **风险提示**: 发现冲突时提供详细警告信息
- **安全创建**: 避免覆盖系统重要命令

### 🎨 现代界面
- **工业科技风格**: 深色主题，现代化 UI 设计
- **直观管理**: 三个标签页分别管理创建、列表和设置
- **护眼配色**: 经过优化的柔和色彩方案，减少视觉疲劳

### ⚙️ 高级功能
- **PATH 集成**: 自动检测和管理 PATH 环境变量
- **批量管理**: 查看、编辑、删除已创建的启动器
- **便携配置**: 嵌入式配置，无需额外文件
- **强制更新**: 支持打包更新正在运行的程序

## 📋 系统要求

- Windows 10/11 (64位)
- Python 3.8+ (仅开发环境)
- 管理员权限 (用于修改 PATH 环境变量)

## 🚀 快速开始

### 方法一：直接使用 (推荐)
1. 下载 `QuickLauncherPro.exe`
2. 双击运行程序
3. 点击 "创建启动器" 标签页
4. 输入命令名（如 `npd`）
5. 点击 "浏览" 选择程序（如 `notepad.exe`）
6. 点击 "创建启动器"
7. 打开资源管理器，在地址栏输入 `npd` 回车即可启动记事本

### 方法二：从源码运行
```bash
# 克隆仓库
git clone <repository-url>
cd quick-launcher

# 安装依赖
pip install -r requirements.txt

# 运行程序
python app_modern.py
```

### 方法三：构建可执行文件
```bash
# 使用现代版本构建
python build_modern.py

# 生成的可执行文件在 dist/ 目录
```

## 📖 使用指南

### 创建启动器
1. 切换到 "创建启动器" 标签页
2. 输入您想要的命令名称（如 `chrome`, `vscode`）
3. 点击 "浏览" 按钮选择目标程序
4. 系统会自动检测 PATH 冲突并提示
5. 点击 "创建启动器" 完成创建

### 管理启动器
1. 切换到 "管理启动器" 标签页
2. 查看所有已创建的启动器
3. 可以编辑或删除不需要的启动器

### 系统设置
1. 切换到 "设置" 标签页
2. 查看启动器目录路径
3. 检查 PATH 环境变量状态
4. 一键添加到 PATH（需要管理员权限）

## 🔧 技术特性

### 架构设计
- **模块化设计**: 分离 GUI、核心逻辑和构建系统
- **嵌入式配置**: 配置信息直接嵌入到可执行文件中
- **无依赖运行**: 单个 EXE 文件，无需额外配置文件

### 核心组件
- **launcher.py**: 通用启动器核心，负责读取嵌入式配置并启动目标程序
- **app_modern.py**: 现代化 GUI 界面，使用 tkinter 实现
- **build_modern.py**: PyInstaller 构建脚本，支持高级功能
- **utils.py**: 通用工具函数，提供设置管理和目录操作

### 安全特性
- **冲突检测**: 防止覆盖系统命令
- **路径验证**: 确保目标程序存在且可执行
- **权限管理**: 安全的 PATH 环境变量操作

## 📁 文件结构

```
quick-launcher/
├── QuickLauncherPro.exe      # 主程序（现代版本）
├── app_modern.py             # 现代化 GUI 应用程序
├── launcher.py               # 启动器核心逻辑
├── build_modern.py           # 构建脚本（现代版本）
├── utils.py                  # 通用工具函数
├── requirements.txt          # Python 依赖
├── README.md                 # 项目文档
└── .gitignore               # Git 忽略文件
```

## 🔄 更新机制

### 打包更新
程序支持强制更新模式，可以安全地替换正在运行的可执行文件：
1. 程序会自动终止相关进程
2. 移动旧版本到临时位置
3. 清理临时文件
4. 完成更新

### 手动更新
1. 下载最新版本的 `QuickLauncherPro.exe`
2. 关闭正在运行的 Quick Launcher
3. 替换旧版本文件
4. 重新运行程序

## 🐛 故障排除

### 常见问题

**Q: 启动器创建后无法使用？**
A: 确保已将启动器目录添加到 PATH 环境变量。在设置页面点击 "添加到 PATH"。

**Q: 提示权限不足？**
A: 修改 PATH 环境变量需要管理员权限，请右键以管理员身份运行程序。

**Q: 如何删除启动器？**
A: 在 "管理启动器" 标签页选择要删除的启动器，点击删除按钮。

### 错误代码

- **ERROR_PATH_NOT_FOUND**: 目标程序路径不存在
- **ERROR_CONFLICT_DETECTED**: 检测到命令冲突
- **ERROR_PERMISSION_DENIED**: 权限不足，需要管理员权限
- **ERROR_EXE_IN_USE**: 可执行文件正在使用，无法更新

## 🤝 贡献指南

1. Fork 项目到您的账户
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- Tkinter - Python GUI 工具包
- PyInstaller - 应用程序打包工具
- Windows API - 系统级功能支持

## 📞 联系方式

如有问题或建议，请通过以下方式联系我们：
- 项目主页: [GitHub Repository](https://github.com/SlothClient/quick-launcher)
- 问题反馈: [GitHub Issues](https://github.com/SlothClient/quick-launcher/issues)

**让 Windows 启动程序变得更加简单快捷！** 🚀
