"""i18n - 中英文语言包"""

import json, os

TRANSLATIONS = {
    "zh": {
        "app_title": "YouTube 视频下载器",
        "ready": "就绪 — 粘贴 YouTube 链接开始",
        "ffmpeg_ok": "FFmpeg 就绪",
        "ffmpeg_no": "无 FFmpeg",
        "gpu_none": "GPU: 无",
        "settings": "设置",
        "video_url": "视频链接",
        "parse": "解析",
        "parsing": "正在解析...",
        "extracting": "正在提取视频信息...",
        "parse_fail": "解析失败 — 请检查链接或代理",
        "invalid_url": "请输入有效的 YouTube 链接",
        "conn_busy": "连接繁忙，请稍后重试",
        "options": "下载选项",
        "multi_thread": "多线程加速",
        "quality": "画质",
        "format": "格式",
        "audio_only": "仅音频",
        "subtitles": "字幕",
        "playlist": "播放列表",
        "torrent": "生成种子",
        "progress": "下载进度",
        "log": "日志",
        "clear": "清空",
        "open_folder": "打开文件夹",
        "download": "开始下载",
        "downloading": "下载中...",
        "retry": "重试",
        "connecting": "正在连接...",
        "merging": "正在合并音视频...",
        "creating_torrent": "正在生成种子...",
        "download_complete": "下载完成!",
        "open_folder_q": "是否打开文件夹?",
        "video_info": "视频信息",
        "parsing_url": "正在解析: {}",
        "parse_ok": "解析成功: {}",
        "parse_error": "解析错误: {}",
        "download_start": "开始下载: {}",
        "download_done": "下载完成: {} ({})",
        "download_fail": "下载失败: {}",
        "torrent_done": "种子: {}",
        "magnet_done": "磁力: {}",
        "all_resolutions": "可用画质: {}",
        "speed": "速度",
        "eta": "剩余",
        "downloaded": "已下载",
        "total": "总计",
        "info_title": "标题",
        "info_author": "作者",
        "info_duration": "时长",
        "info_views": "播放",

        # Settings dialog
        "settings_title": "设置",
        "proxy": "代理地址",
        "proxy_hint": "例: http://127.0.0.1:7890",
        "test_proxy": "测试",
        "test_ok": "代理连接正常",
        "test_fail": "代理连接失败",
        "test_enter": "请先输入代理地址",
        "download_settings": "下载设置",
        "default_quality": "默认画质",
        "default_format": "默认格式",
        "threads": "并发线程",
        "use_aria2": "使用 aria2 加速",
        "aria2_missing": "(未安装)",
        "force_ipv4": "强制 IPv4",
        "gpu_accel": "GPU 加速",
        "output_dir": "输出目录",
        "browse": "浏览",
        "reset": "恢复默认",
        "save": "保存设置",
        "saved": "设置已保存",
        "reset_done": "已恢复默认设置",

        # Language
        "language": "语言",

        # Cookies
        "cookies": "Cookie 认证",
        "cookies_hint": "选择已登录 YouTube 的浏览器，用于绕过人机验证（使用前需关闭该浏览器）",
    },
    "en": {
        "app_title": "YouTube Downloader",
        "ready": "Ready — Paste a YouTube link",
        "ffmpeg_ok": "FFmpeg OK",
        "ffmpeg_no": "No FFmpeg",
        "gpu_none": "GPU: None",
        "settings": "Settings",
        "video_url": "Video URL",
        "parse": "Parse",
        "parsing": "Parsing...",
        "extracting": "Extracting video info...",
        "parse_fail": "Parse failed — check link or proxy",
        "invalid_url": "Please enter a valid YouTube URL",
        "conn_busy": "Connection busy, please try again later",
        "options": "Options",
        "multi_thread": "Multi-thread",
        "quality": "Quality",
        "format": "Format",
        "audio_only": "Audio only",
        "subtitles": "Subtitles",
        "playlist": "Playlist",
        "torrent": "Torrent",
        "progress": "Progress",
        "log": "Log",
        "clear": "Clear",
        "open_folder": "Open Folder",
        "download": "Download",
        "downloading": "Downloading...",
        "retry": "Retry",
        "connecting": "Connecting...",
        "merging": "Merging audio/video...",
        "creating_torrent": "Creating torrent...",
        "download_complete": "Download complete!",
        "open_folder_q": "Open folder?",
        "video_info": "Video Info",
        "parsing_url": "Parsing: {}",
        "parse_ok": "Parsed: {}",
        "parse_error": "Parse error: {}",
        "download_start": "Download: {}",
        "download_done": "Done: {} ({})",
        "download_fail": "Failed: {}",
        "torrent_done": "Torrent: {}",
        "magnet_done": "Magnet: {}",
        "all_resolutions": "Resolutions: {}",
        "speed": "Speed",
        "eta": "ETA",
        "downloaded": "Downloaded",
        "total": "Total",
        "info_title": "Title",
        "info_author": "Author",
        "info_duration": "Duration",
        "info_views": "Views",

        # Settings dialog
        "settings_title": "Settings",
        "proxy": "Proxy",
        "proxy_hint": "e.g. http://127.0.0.1:7890",
        "test_proxy": "Test",
        "test_ok": "Proxy works!",
        "test_fail": "Proxy connection failed",
        "test_enter": "Enter proxy address first",
        "download_settings": "Download Settings",
        "default_quality": "Default Quality",
        "default_format": "Default Format",
        "threads": "Threads",
        "use_aria2": "Use aria2",
        "aria2_missing": "(not installed)",
        "force_ipv4": "Force IPv4",
        "gpu_accel": "GPU Accel",
        "output_dir": "Output",
        "browse": "Browse",
        "reset": "Reset",
        "save": "Save",
        "saved": "Settings saved",
        "reset_done": "Reset to defaults",

        # Language
        "language": "Language",

        # Cookies
        "cookies": "Cookie Auth",
        "cookies_hint": "Select the browser logged into YouTube to bypass bot verification (close the browser first)",
    },
}

# Save config path
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lang_config")


def load_lang() -> str:
    """加载保存的语言设置"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("lang", "zh")
    except Exception:
        return "zh"


def save_lang(lang: str):
    """保存语言设置"""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"lang": lang}, f)
    except Exception:
        pass


class I18n:
    """国际化翻译器"""

    def __init__(self, lang: str = None):
        self.lang = lang or load_lang()
        self._callbacks = []

    def t(self, key: str, *args) -> str:
        """获取翻译文本"""
        text = TRANSLATIONS.get(self.lang, {}).get(key)
        if text is None:
            text = TRANSLATIONS.get("zh", {}).get(key, key)
        if args:
            text = text.format(*args)
        return text

    def switch(self, lang: str):
        """切换语言"""
        self.lang = lang
        save_lang(lang)
        for cb in self._callbacks:
            cb()

    def on_change(self, callback):
        """注册语言变更回调"""
        self._callbacks.append(callback)
