import os
import shutil
import subprocess
import sys
import tempfile
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
    with urllib.request.urlopen(request, timeout=120) as response:
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


def install_app(install_dir: Path, temp_dir: Path):
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

    for item in extract_dir.iterdir():
        destination = install_dir / item.name
        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination)


def install_tools(install_dir: Path, temp_dir: Path):
    log("Installing aria2 and FFmpeg")
    tools_bin = install_dir / "_internal" / "tools" / "bin"
    tools_bin.mkdir(parents=True, exist_ok=True)

    aria_zip = temp_dir / "aria2.zip"
    aria_extract = temp_dir / "aria2"
    download_file(ARIA2_URL, aria_zip)
    extract_zip(aria_zip, aria_extract)
    copy_first_match(aria_extract, "aria2c.exe", tools_bin / "aria2c.exe")

    ffmpeg_zip = temp_dir / "ffmpeg.zip"
    ffmpeg_extract = temp_dir / "ffmpeg"
    download_file(FFMPEG_URL, ffmpeg_zip)
    extract_zip(ffmpeg_zip, ffmpeg_extract)
    copy_first_match(ffmpeg_extract, "ffmpeg.exe", tools_bin / "ffmpeg.exe")
    copy_first_match(ffmpeg_extract, "ffprobe.exe", tools_bin / "ffprobe.exe")


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


def create_shortcuts(exe_path: Path, install_dir: Path):
    log("Creating shortcuts")
    desktop = Path(os.path.join(os.environ["USERPROFILE"], "Desktop"))
    create_shortcut(desktop / f"{DISPLAY_NAME}.lnk", exe_path, install_dir)

    programs = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / DISPLAY_NAME
    programs.mkdir(parents=True, exist_ok=True)
    create_shortcut(programs / f"{DISPLAY_NAME}.lnk", exe_path, install_dir)


def main() -> int:
    LOG_PATH.write_text("", encoding="utf-8")
    subprocess.run(
        ["taskkill.exe", "/IM", f"{APP_NAME}.exe", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )

    install_dir = Path(os.environ["LOCALAPPDATA"]) / APP_NAME
    with tempfile.TemporaryDirectory() as temp:
        temp_dir = Path(temp)
        install_app(install_dir, temp_dir)
        install_tools(install_dir, temp_dir)

    exe_path = install_dir / f"{APP_NAME}.exe"
    if not exe_path.exists():
        raise FileNotFoundError(f"Installed executable not found: {exe_path}")

    create_shortcuts(exe_path, install_dir)
    log("Starting app")
    subprocess.Popen([str(exe_path)], cwd=str(install_dir))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        log(f"Install failed: {exc}")
        try:
            import tkinter.messagebox as messagebox

            messagebox.showerror(DISPLAY_NAME, f"Install failed:\n{exc}")
        except Exception:
            print(f"Install failed: {exc}", file=sys.stderr)
        raise
