# 🎬 YouTube Video Downloader

一个基于 yt-dlp + Tkinter 的高颜值 YouTube 视频下载器，支持多线程加速、GPU 硬件加速、种子生成、中英文切换等多个实用功能。

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/yt--dlp-2025+-red.svg" alt="yt-dlp">
</p>

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🎯 **视频解析** | 粘贴 YouTube 链接一键解析，显示标题、作者、时长、播放量、可用画质 |
| 📥 **画质选择** | 支持 4K / 1440p / 1080p / 720p / 480p / 360p 多档画质 + best 自动最佳 |
| 🎵 **仅音频** | 提取音频流并转为 MP3，适合播客/音乐 |
| 📝 **字幕下载** | 下载中英文字幕并嵌入视频文件 |
| 📋 **播放列表** | 支持下载完整播放列表或仅下载当前单集 |
| 🧲 **种子生成** | 下载完成后自动生成 .torrent 文件和磁力链接 |
| ⚡ **多线程加速** | 最高 16 路并发分片下载 |
| 🚀 **GPU 硬件加速** | 自动识别 NVIDIA / AMD / Intel 显卡，视频转码时使用硬件编码器 (NVENC/AMF/QSV) |
| 🌐 **代理支持** | 内置代理配置与测试，轻松访问受限内容 |
| 🍪 **Cookie 认证** | 支持从 Chrome / Firefox / Edge / Brave / Opera 读取登录态，绕过 YouTube 人机验证 |
| 🎨 **主题切换** | 内置 9 款 VS Code 风格主题（暗黑/亮色），一键切换 |
| 🌍 **中英文切换** | 界面完整支持中文 / English 实时切换 |
| 📋 **内置控制台** | GUI 内嵌日志面板 + 可切换 yt-dlp 原生控制台输出 |
| 🔧 **aria2 支持** | 可选启用 aria2 外部下载器 |

---

## 📸 界面预览

> 暗黑主题 + 中文界面，支持多种 VS Code 风格主题

---

## 🚀 快速开始

### 环境要求

- **Python** >= 3.9
- **FFmpeg**（可选，但强烈推荐 — 用于音视频合并、GPU 加速、字幕嵌入）
- **aria2**（可选 — 用于加速下载）

### 安装

```bash
# 1. 克隆项目
git clone https://github.com/your-username/youtube-downloader.git
cd youtube-downloader

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动
python main.py
```

### Windows 一键启动

双击 `启动.bat` 即可运行。

### Windows 安装包

提供 `release/YouTubeDownloaderSetup.exe` 安装包，安装时会自动配置 FFmpeg 和 aria2。安装后桌面和开始菜单会创建快捷方式。

### FFmpeg 安装

- **Windows**: 下载 [FFmpeg](https://ffmpeg.org/download.html)，解压后将 `bin` 目录加入系统 PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `apt install ffmpeg` / `dnf install ffmpeg`

GUI 顶部状态栏会显示 FFmpeg 是否就绪，未安装时会提示并提供下载链接。

### aria2 安装（可选）

下载 [aria2](https://github.com/aria2/aria2/releases)，将 `aria2c.exe` 加入 PATH。启用后可在设置中勾选 aria2 加速。

---

## 📖 使用说明

### 基本流程

1. 粘贴 YouTube 链接 → 点击 **解析**
2. 查看视频信息和可用画质
3. 选择画质、格式、勾选需要的选项
4. 点击 **开始下载**

### 设置说明

| 设置项 | 说明 |
|--------|------|
| **代理 (Proxy)** | 格式 `http://127.0.0.1:7890`，用于访问受限网络 |
| **Cookie 认证** | 选择已登录 YouTube 的浏览器（**需先关闭该浏览器**），用于绕过人机验证 |
| **多线程加速** | 启用并发分片下载，线程数可调 1-16 |
| **GPU 加速** | 自动识别显卡型号，勾选后在视频转码时使用硬件编码器 |
| **强制 IPv4** | 避免 IPv6 网络问题 |
| **使用 aria2** | 启用 aria2 作为外部下载器 |

### 下载选项

每个选项旁有 `?` 图标，鼠标悬停可查看说明。

| 选项 | 说明 |
|------|------|
| **仅音频** | 只下载音频，转 MP3 |
| **字幕** | 下载中英文字幕嵌入视频 |
| **播放列表** | 勾选下载整个播放列表，不勾选仅下载当前视频 |
| **生成种子** | 下载后自动创建 .torrent + 磁力链接 |

### 命令行模式

项目也提供 CLI 版本：

```bash
python cli.py "https://www.youtube.com/watch?v=VIDEO_ID" --quality 1080p --format mp4 --proxy http://127.0.0.1:7897
```

---

## 🏗️ 项目结构

```
youtube-downloader/
├── main.py                # GUI 主程序 (Tkinter, ~810 行)
├── main.pyw               # Windows 无控制台启动入口
├── downloader.py          # 下载核心模块 (基于 yt-dlp)
├── i18n.py                # 中英文语言包
├── themes.py              # VS Code 风格主题系统 (9 款主题)
├── torrent_maker.py       # 种子文件生成模块 (基于 torf)
├── cli.py                 # 命令行工具
├── requirements.txt       # Python 依赖 (yt-dlp, torf)
├── 启动.bat               # Windows 一键启动脚本
├── LICENSE                # MIT 许可证
├── scripts/
│   ├── build_installer.ps1    # PowerShell 安装包构建脚本
│   └── installer_launcher.py  # 安装程序入口 (自动下载 FFmpeg/aria2)
└── release/
    └── YouTubeDownloaderSetup.exe  # 安装包
```

运行时自动生成的配置文件（已加入 .gitignore）：
- `.theme_config` — 主题配置
- `.lang_config` — 语言配置

---

## 🔧 技术栈

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — YouTube 视频提取与下载引擎
- **[Tkinter](https://docs.python.org/3/library/tkinter.html)** — Python 标准 GUI 库
- **[torf](https://github.com/rndusr/torf)** — Torrent 文件生成
- **[PyInstaller](https://pyinstaller.org/)** — 打包为独立可执行文件
- **FFmpeg** — 音视频合并、转码、GPU 硬件加速
- **aria2** — 多线程外部下载器

### 构建安装包

```powershell
# 在项目根目录执行
.\scripts\build_installer.ps1
```

构建完成后，安装包位于 `release/YouTubeDownloaderSetup.exe`。

---

## ❓ 常见问题

<details>
<summary><b>解析提示 SSL 错误？</b></summary>

需要配置代理。点击右上角 **设置** → 填入代理地址（如 `http://127.0.0.1:7890`）→ 保存。
</details>

<details>
<summary><b>提示 "Sign in to confirm you're not a bot"？</b></summary>

YouTube 人机验证。关闭浏览器 → 打开设置 → Cookie 认证中选择已登录 YouTube 的浏览器 → 保存 → 重新解析。
</details>

<details>
<summary><b>下载的视频没有声音？</b></summary>

YouTube 高清视频音视频分离存储，需要 FFmpeg 合并。请安装 FFmpeg 并将 bin 目录加入 PATH。
</details>

<details>
<summary><b>下载速度慢？</b></summary>

- 启用 **多线程加速**，调高线程数
- 启用 **aria2** 外部下载器
- 配置好代理以提高与 YouTube 服务器的连接质量
</details>

<details>
<summary><b>GPU 加速不生效？</b></summary>

需要 FFmpeg 支持对应编码器：
- NVIDIA → `h264_nvenc` / `hevc_nvenc`
- AMD → `h264_amf` / `hevc_amf`  
- Intel → `h264_qsv` / `hevc_qsv`

程序会自动检测显卡型号和可用编码器。
</details>

---

## 📄 License

MIT © 2025

---

## ⭐ Star History

如果这个项目对你有帮助，请给一个 ⭐ Star 支持一下！

---

*Built with ❤️ using Python, yt-dlp, and Tkinter*
