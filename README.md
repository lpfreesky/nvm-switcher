# nvm-switcher

**一个简洁的 nvm-windows Node.js 版本切换 GUI 工具。**

支持一键切换、安装 Node 版本，无需记忆命令，适合日常开发使用。

![screenshot](https://raw.githubusercontent.com/lpfreesky/nvm-switcher/main/screenshot.png)

---

## 功能特性

- **版本切换** — 双击列表或点击按钮，一键切换已安装的 Node.js 版本
- **版本安装** — 一键安装最新的 LTS 版本
- **自动探测** — 自动在 PATH / 环境变量 / 常见目录中查找 nvm.exe，覆盖 99% 安装场景
- **手动指定** — 菜单栏提供手动选择 nvm.exe 的入口，适配所有特殊路径
- **无需重启** — 基于 nvm-windows 的 symlink 机制，切换后立即生效
- **零依赖** — 使用 Python 内置 tkinter 编写，无需安装任何额外包

---

## 环境要求

- Windows 10 / Windows 11
- [nvm-windows](https://github.com/coreybutler/nvm-windows)（安装后确保 `nvm` 在 PATH 中）
- Python 3.8+

---

## 快速开始

### 运行

```powershell
# 克隆仓库
git clone https://github.com/lpfreesky/nvm-switcher.git
cd nvm-switcher

# 直接运行
python nvm_switcher.py
```

### 打包为 exe（可选）

```powershell
pip install pyinstaller
pyinstaller -F -w nvm_switcher.py
```

打包后的文件在 `dist/` 目录下，可独立分发给任何人使用。

---

## 使用方法

1. 启动程序后，左侧显示当前激活的 Node.js 版本
2. 列表中显示所有已安装的版本，`>>` 标记的为当前使用的版本
3. **切换版本**：选中目标版本后点击「切换版本」按钮，或直接双击列表项
4. **安装 LTS**：点击「安装 LTS」按钮，自动下载安装最新长期支持版
5. **刷新列表**：点击「刷新列表」按钮重新检测已安装版本
6. **手动指定 nvm.exe**：菜单栏 → 帮助 → 手动选择 nvm.exe

---

## 自动探测路径

程序按以下顺序自动查找 nvm.exe：

1. 系统 PATH 中的 `nvm` 命令
2. 环境变量 `NVM_HOME` / `NVM_DIR`
3. 常见安装目录：
   - `%APPDATA%\nvm`
   - `%USERPROFILE%\nvm`
   - `C:\nvm`
   - `D:\nvm`
   - `C:\ProgramData\nvm`
   - `%LOCALAPPDATA%\nvm`

---

## 项目结构

```
nvm-switcher/
├── nvm_switcher.py    # 主程序
├── generate_icon.py   # 图标生成脚本（如需换图标可修改后重新生成）
├── icon.ico           # 程序图标
├── README.md          # 本文件
└── LICENSE            # MIT License
```

---

## 版本历史

### v1.0.0 (2026-04-13)
- 初始版本发布
- 支持版本切换、LTS 安装、nvm.exe 自动探测

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## License

MIT License — 详见 [LICENSE](LICENSE) 文件。
