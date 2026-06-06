"""YouTube 视频下载核心模块 - 基于 yt-dlp"""

import os, subprocess, sys, time
from pathlib import Path
import yt_dlp


def _prepend_local_tool_paths():
    bases = [Path(__file__).resolve().parent]
    if getattr(sys, "frozen", False):
        bases.append(Path(sys.executable).resolve().parent)
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        bases.append(Path(bundle_dir).resolve())

    candidates = []
    for base in bases:
        candidates.extend([
            base / "tools" / "bin",
            base / "tools" / "aria2",
            base / "tools" / "ffmpeg" / "bin",
        ])

    existing = [str(path) for path in candidates if path.is_dir()]
    if not existing:
        return

    path_parts = os.environ.get("PATH", "").split(os.pathsep)
    for tool_dir in reversed(existing):
        if tool_dir not in path_parts:
            path_parts.insert(0, tool_dir)
    os.environ["PATH"] = os.pathsep.join(path_parts)


_prepend_local_tool_paths()


def check_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except: return False


def check_aria2() -> bool:
    try:
        subprocess.run(["aria2c", "--version"], capture_output=True, check=True)
        return True
    except: return False


def detect_gpu() -> dict:
    """检测所有 GPU 类型和型号"""
    result = {"type": None, "name": "", "encoders": {}}

    # 1. NVIDIA via nvidia-smi
    try:
        nv = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=5)
        if nv.returncode == 0 and nv.stdout.strip():
            result["type"] = "nvidia"
            name = nv.stdout.strip().split(chr(10))[0]
            # 格式: "GPU 0: NVIDIA GeForce RTX 3050 Laptop GPU (UUID: ...)"
            if ": " in name:
                name = name.split(": ", 1)[1]
            # 去掉 UUID 部分
            if "(UUID:" in name:
                name = name.split("(UUID:")[0].strip()
            result["name"] = name[:80]
            result["encoders"] = {"h264": "h264_nvenc", "hevc": "hevc_nvenc", "av1": "av1_nvenc"}
            return result
    except Exception:
        pass

    # 2. Fallback: 通过 ffmpeg 编码器判断
    try:
        enc = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True, text=True, timeout=5
        )
        out = enc.stdout + enc.stderr
        if "h264_amf" in out:
            result["type"] = "amd"
            result["name"] = "AMD Radeon GPU"
            result["encoders"] = {"h264": "h264_amf", "hevc": "hevc_amf", "av1": "av1_amf"}
        elif "h264_qsv" in out:
            result["type"] = "intel"
            result["name"] = "Intel Graphics"
            result["encoders"] = {"h264": "h264_qsv", "hevc": "hevc_qsv", "av1": "av1_qsv"}
        elif "h264_nvenc" in out:
            result["type"] = "nvidia"
            result["name"] = "NVIDIA GPU"
            result["encoders"] = {"h264": "h264_nvenc", "hevc": "hevc_nvenc", "av1": "av1_nvenc"}
    except Exception:
        pass

    # 3. 尝试通过 WMI 获取实际型号（Windows 通用）
    if result["type"]:
        try:
            import subprocess as sp
            r = sp.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True, text=True, timeout=8
            )
            if r.returncode == 0:
                lines = [l.strip() for l in r.stdout.splitlines() if l.strip() and "Name" not in l]
                for line in lines:
                    # 匹配 GPU 类型
                    if result["type"] == "nvidia" and "nvidia" in line.lower():
                        result["name"] = line[:80]; break
                    elif result["type"] == "amd" and ("amd" in line.lower() or "radeon" in line.lower()):
                        result["name"] = line[:80]; break
                    elif result["type"] == "intel" and ("intel" in line.lower() or "arc" in line.lower() or "iris" in line.lower()):
                        result["name"] = line[:80]; break
        except Exception:
            pass

    return result


class _ConsoleLogger:
    def __init__(self, callback): self._cb = callback
    def debug(self, msg): self._send(msg)
    def info(self, msg): self._send(msg)
    def warning(self, msg): self._send(msg, "warn")
    def error(self, msg): self._send(msg, "err")
    def _send(self, msg, level="info"):
        if self._cb and msg.strip():
            try: self._cb(msg.strip(), level)
            except: pass


class YouTubeDownloader:
    def __init__(self, output_dir=None, proxy=""):
        self.output_dir = output_dir or str(Path.home() / "Downloads" / "YouTube")
        os.makedirs(self.output_dir, exist_ok=True)
        self.has_ffmpeg = check_ffmpeg()
        self.has_aria2 = check_aria2()
        self.gpu_info = detect_gpu()
        self.gpu_enabled = False
        self.proxy = proxy.strip() if proxy else ""
        self.cookies_from_browser = ""  # e.g. "chrome", "firefox", "edge"
        self.cookies_file = ""  # path to cookies.txt
        self._multi_thread = True
        self._threads = 8
        self._use_aria2 = False
        self._force_ipv4 = True
        self._progress_callback = None
        self._console_callback = None
        self._console_enabled = False

    def set_proxy(self, proxy): self.proxy = proxy.strip() if proxy else ""
    def set_console(self, enabled, callback=None): self._console_enabled = enabled; self._console_callback = callback
    def set_gpu(self, enabled): self.gpu_enabled = enabled and bool(self.gpu_info["type"])
    def set_options(self, multi_thread=True, threads=8, use_aria2=False, force_ipv4=True):
        self._multi_thread = multi_thread
        self._threads = threads
        self._use_aria2 = use_aria2
        self._force_ipv4 = force_ipv4
    def on_progress(self, callback): self._progress_callback = callback

    def _progress_hook(self, d):
        if not self._progress_callback: return
        s = d["status"]
        if s == "downloading":
            self._progress_callback({
                "type": "download",
                "percent": float(d.get("_percent_str", "0%").strip("%") or 0),
                "downloaded": d.get("downloaded_bytes", 0),
                "total": d.get("total_bytes") or d.get("total_bytes_estimate", 0),
                "speed": d.get("speed", 0), "eta": d.get("eta", 0),
            })
        elif s == "finished":
            self._progress_callback({"type": "processing", "message": "Merging..."})

    def _build_options(self, quality, format_type, audio_only, subtitles, subtitle_langs, playlist):
        fmt_map = {
            "best": "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best",
            "4k": "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best",
            "1440p": "bestvideo[height<=1440]+bestaudio/best[height<=1440]/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
        }
        outtmpl = os.path.join(self.output_dir, "%(title).100s [%(id)s].%(ext)s")
        # Dynamic downloader settings
        external_dl = "aria2c" if (self._use_aria2 and self.has_aria2) else "native"
        concurrent = self._threads if self._multi_thread else 1
        opts = {
            "outtmpl": outtmpl, "progress_hooks": [self._progress_hook],
            "quiet": not self._console_enabled, "noprogress": True,
            "no_warnings": not self._console_enabled,
            "retries": 10, "fragment_retries": 10, "extractor_retries": 5,
            "external_downloader": external_dl,
            "socket_timeout": 30, "concurrent_fragment_downloads": concurrent,
            "force_ipv4": self._force_ipv4,
            "logger": _ConsoleLogger(self._console_callback) if self._console_enabled else None,
        }
        if self.proxy: opts["proxy"] = self.proxy
        # Cookies for authentication
        if self.cookies_from_browser:
            opts["cookiesfrombrowser"] = self.cookies_from_browser
        elif self.cookies_file:
            opts["cookiefile"] = self.cookies_file
        # aria2 默认不启用，避免网络不稳定时失败
            # 用户可在 GUI Settings 中手动开启
        if not playlist: opts["playlistend"] = 1
        if audio_only:
            opts["format"] = "bestaudio/best"
            if self.has_ffmpeg:
                opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": format_type if format_type != "mp4" else "mp3", "preferredquality": "192"}]
        else:
            opts["format"] = fmt_map.get(quality, fmt_map["best"])
            if self.has_ffmpeg:
                opts["merge_output_format"] = format_type
                if self.gpu_enabled and self.gpu_info["type"]:
                    auto_codec = "h264" if format_type == "mp4" else "hevc"
                    gpu_encoder = self.gpu_info["encoders"].get(auto_codec, next(iter(self.gpu_info["encoders"].values()), ""))
                    if gpu_encoder:
                        is_nv = self.gpu_info["type"] == "nvidia"
                        args = ["-c:v", gpu_encoder, "-preset", "p1" if is_nv else "fast"]
                        if is_nv: args += ["-rc", "vbr", "-cq", "23"]
                        opts.setdefault("postprocessor_args", {})["ffmpeg"] = args
            else:
                h = quality.replace("p", "")
                opts["format"] = f"best[height<=?{h}]/best"
        if subtitles:
            opts["writesubtitles"] = True; opts["writeautomaticsub"] = True
            opts["subtitleslangs"] = [l.strip() for l in subtitle_langs.split(",") if l.strip()]
            if self.has_ffmpeg: opts["embedsubtitles"] = True
        return opts

    def _base_opts(self):
        opts = {"quiet": True, "no_warnings": True, "socket_timeout": 30, "retries": 5, "extractor_retries": 3, "force_ipv4": True}
        if self.proxy: opts["proxy"] = self.proxy
        if self.cookies_from_browser:
            opts["cookiesfrombrowser"] = self.cookies_from_browser
        elif self.cookies_file:
            opts["cookiefile"] = self.cookies_file
        return opts

    def get_video_info(self, url):
        opts = self._base_opts(); opts["extract_flat"] = False
        for attempt in range(2):
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if not info: return None
                    formats, seen = [], set()
                    for f in info.get("formats", []):
                        h = f.get("height")
                        # 只保留有效画质 (>=144p 且去重)
                        if h and isinstance(h, int) and h >= 144 and h not in seen:
                            seen.add(h)
                            formats.append({
                                "format_id": f.get("format_id"),
                                "ext": f.get("ext"),
                                "height": h,
                                "resolution": f"{h}p",
                                "filesize": f.get("filesize"),
                                "fps": f.get("fps"),
                            })
                    # 按高度降序排列
                    formats.sort(key=lambda x: -x["height"])
                    return {
                        "title": info.get("title", "?"), "duration": info.get("duration", 0),
                        "uploader": info.get("uploader", "?"), "thumbnail": info.get("thumbnail", ""),
                        "description": (info.get("description") or "")[:500],
                        "view_count": info.get("view_count", 0), "formats": formats,
                        "webpage_url": info.get("webpage_url", url),
                    }
            except Exception as e:
                if attempt >= 1: return {"error": str(e)}
                time.sleep(3)

    def download(self, url, quality="best", format_type="mp4", audio_only=False, subtitles=False, subtitle_langs="zh-Hans,en", playlist=False):
        opts = self._build_options(quality, format_type, audio_only, subtitles, subtitle_langs, playlist)
        last_err = None
        for attempt in range(3):
            try:
                if self._progress_callback:
                    self._progress_callback({"type": "extracting", "message": "Extracting video info..."})
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if not info: continue
                    if playlist and "entries" in info: return self.output_dir
                    filename = ydl.prepare_filename(info)
                    base = os.path.splitext(filename)[0]
                    for ext in [format_type, "mkv", "webm", "mp4", "mp3", "m4a", "opus"]:
                        candidate = f"{base}.{ext}"
                        if os.path.exists(candidate): return candidate
                    return filename
            except yt_dlp.utils.DownloadError as e:
                last_err = e
                if attempt < 2: time.sleep(2 * (attempt + 1))
            except Exception as e:
                last_err = e
                if attempt < 2: time.sleep(2 * (attempt + 1))
        raise RuntimeError(f"Download failed after 3 retries: {last_err}")
