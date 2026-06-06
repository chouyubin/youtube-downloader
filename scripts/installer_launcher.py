"""YouTube Downloader Installer with GUI progress."""

import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import ttk
import threading
import urllib.request
import zipfile
from pathlib import Path

APP_NAME = "YouTubeDownloader"
DISPLAY_NAME = "YouTube Downloader"
APP_ZIP_URL = ""
ARIA2_URL = "https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip"
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
LOG_PATH = Path(tempfile.gettempdir()) / "YouTubeDownloaderSetup.log"


def log(message: str):
    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(message + "\n")


def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


def download_file(url: str, destination: Path):
    log(f"Downloading {url}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "YouTubeDownloaderSetup"})
    with urllib.request.urlopen(request, timeout=300) as response:
        with destination.open("wb") as file:
            shutil.copyfileobj(response, file)


def extract_zip(zip_path: Path, destination: Path):
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(destination)


def copy_first_match(search_root: Path, filename: str, destination: Path):
    match = next(search_root.rglob(filename), None)
    if not match:
        raise FileNotFoundError(f"Cannot find {filename} in {search_root}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(match, destination)


class InstallerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{DISPLAY_NAME} Setup")
        self.root.geometry("480x320")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d1117")

        # Center on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 480) // 2
        y = (self.root.winfo_screenheight() - 320) // 2
        self.root.geometry(f"+{x}+{y}")

        self._build_ui()
        self.error = None

    def _build_ui(self):
        bg = "#0d1117"
        fg = "#e6edf3"
        accent = "#3fb950"
        bg2 = "#161b22"

        # Title
        tk.Label(self.root, text=f"🎬 {DISPLAY_NAME}", fg=fg, bg=bg,
                 font=("Segoe UI", 18, "bold")).pack(pady=(24, 4))
        tk.Label(self.root, text="正在安装，请稍候...", fg="#8b949e", bg=bg,
                 font=("Segoe UI", 10)).pack()

        # Progress frame
        pf = tk.Frame(self.root, bg=bg2, highlightbackground="#30363d", highlightthickness=1)
        pf.pack(fill="x", padx=32, pady=(20, 8))

        self.step_label = tk.Label(pf, text="准备中...", fg=fg, bg=bg2,
                                   font=("Segoe UI", 10), anchor="w")
        self.step_label.pack(fill="x", padx=16, pady=(12, 4))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Install.Horizontal.TProgressbar",
                        background=accent, troughcolor="#21262d",
                        borderwidth=0, thickness=8)

        self.progress = ttk.Progressbar(pf, style="Install.Horizontal.TProgressbar",
                                        mode="determinate", length=400)
        self.progress.pack(fill="x", padx=16, pady=(0, 12))

        # Status label
        self.status_label = tk.Label(self.root, text="", fg="#8b949e", bg=bg,
                                     font=("Segoe UI", 9), anchor="w")
        self.status_label.pack(fill="x", padx=32)

        # Error area (hidden by default)
        self.error_frame = tk.Frame(self.root, bg=bg)
        self.error_text = tk.Text(self.error_frame, bg="#1c1305", fg="#f85149",
                                  font=("Consolas", 9), height=4, relief="flat",
                                  wrap="word", padx=8, pady=4)
        self.error_text.pack(fill="x")

    def set_step(self, text: str, progress_val: float):
        self.step_label.config(text=text)
        self.progress["value"] = progress_val
        self.root.update_idletasks()

    def set_status(self, text: str):
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def show_error(self, message: str):
        self.error_frame.pack(fill="x", padx=32, pady=(8, 12))
        self.error_text.config(state="normal")
        self.error_text.insert("1.0", message)
        self.error_text.config(state="disabled")
        self.set_step("安装失败", 0)
        # Add close button
        btn = tk.Button(self.root, text="关闭", command=self.root.destroy,
                        bg="#f85149", fg="white", font=("Segoe UI", 10, "bold"),
                        relief="flat", padx=24, pady=4, cursor="hand2")
        btn.pack(pady=(0, 16))

    def show_success(self):
        self.set_step("安装完成！", 100)
        self.set_status("应用已启动，可以关闭此窗口")
        btn = tk.Button(self.root, text="完成", command=self.root.destroy,
                        bg="#3fb950", fg="white", font=("Segoe UI", 10, "bold"),
                        relief="flat", padx=24, pady=4, cursor="hand2")
        btn.pack(pady=(12, 16))


def install_app(install_dir: Path, temp_dir: Path, gui: InstallerGUI):
    gui.set_step("解压应用文件...", 10)
    log("Installing app payload")
    app_zip = resource_path("app.zip")
    if APP_ZIP_URL:
        app_zip = temp_dir / "app.zip"
        download_file(APP_ZIP_URL, app_zip)
    elif not app_zip.exists():
        raise FileNotFoundError(f"Missing installer payload: {app_zip}")

    extract_dir = temp_dir / "app"
    extract_zip(app_zip, extract_dir)
    install_dir.mkdir(parents=True, exist_ok=True)

    items = list(extract_dir.iterdir())
    for i, item in enumerate(items):
        gui.set_status(f"复制: {item.name}")
        destination = install_dir / item.name
        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination)
        gui.set_step("解压应用文件...", 10 + 20 * (i + 1) / max(len(items), 1))


def install_tools(install_dir: Path, temp_dir: Path, gui: InstallerGUI):
    log("Installing aria2 and FFmpeg")
    tools_bin = install_dir / "_internal" / "tools" / "bin"
    tools_bin.mkdir(parents=True, exist_ok=True)

    gui.set_step("下载 aria2...", 35)
    gui.set_status("正在下载 aria2 下载加速器...")
    aria_zip = temp_dir / "aria2.zip"
    aria_extract = temp_dir / "aria2"
    download_file(ARIA2_URL, aria_zip)
    gui.set_step("安装 aria2...", 45)
    extract_zip(aria_zip, aria_extract)
    copy_first_match(aria_extract, "aria2c.exe", tools_bin / "aria2c.exe")
    gui.set_status("aria2 安装完成")

    gui.set_step("下载 FFmpeg...", 55)
    gui.set_status("正在下载 FFmpeg (约 100MB)...")
    ffmpeg_zip = temp_dir / "ffmpeg.zip"
    ffmpeg_extract = temp_dir / "ffmpeg"
    download_file(FFMPEG_URL, ffmpeg_zip)
    gui.set_step("安装 FFmpeg...", 75)
    extract_zip(ffmpeg_zip, ffmpeg_extract)
    copy_first_match(ffmpeg_extract, "ffmpeg.exe", tools_bin / "ffmpeg.exe")
    copy_first_match(ffmpeg_extract, "ffprobe.exe", tools_bin / "ffprobe.exe")
    gui.set_status("FFmpeg 安装完成")


def create_shortcut(shortcut_path: Path, target_path: Path, working_dir: Path):
    ps_script = f"""
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{target_path}'
$Shortcut.WorkingDirectory = '{working_dir}'
$Shortcut.IconLocation = '{target_path},0'
$Shortcut.Description = '{DISPLAY_NAME}'
$Shortcut.Save()
"""
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        check=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def create_shortcuts(exe_path: Path, install_dir: Path, gui: InstallerGUI):
    gui.set_step("创建快捷方式...", 90)
    log("Creating shortcuts")
    desktop = Path(os.path.join(os.environ["USERPROFILE"], "Desktop"))
    create_shortcut(desktop / f"{DISPLAY_NAME}.lnk", exe_path, install_dir)

    programs = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / DISPLAY_NAME
    programs.mkdir(parents=True, exist_ok=True)
    create_shortcut(programs / f"{DISPLAY_NAME}.lnk", exe_path, install_dir)
    gui.set_status("桌面和开始菜单快捷方式已创建")


def do_install(gui: InstallerGUI):
    try:
        LOG_PATH.write_text("", encoding="utf-8")
        log("Installation started")

        gui.set_step("准备安装...", 5)
        subprocess.run(
            ["taskkill.exe", "/IM", f"{APP_NAME}.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

        install_dir = Path(os.environ["LOCALAPPDATA"]) / APP_NAME
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            install_app(install_dir, temp_dir, gui)
            install_tools(install_dir, temp_dir, gui)

        exe_path = install_dir / f"{APP_NAME}.exe"
        if not exe_path.exists():
            raise FileNotFoundError(f"Installed executable not found: {exe_path}")

        create_shortcuts(exe_path, install_dir, gui)

        gui.set_step("启动应用...", 95)
        gui.set_status("正在启动 YouTube Downloader...")
        log("Starting app")
        subprocess.Popen([str(exe_path)], cwd=str(install_dir))

        gui.show_success()
        log("Installation completed successfully")

    except Exception as exc:
        log(f"Install failed: {exc}")
        gui.show_error(str(exc))


def main():
    gui = InstallerGUI()

    def run():
        do_install(gui)

    threading.Thread(target=run, daemon=True).start()
    gui.root.mainloop()


if __name__ == "__main__":
    main()
