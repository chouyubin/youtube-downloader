"""YouTube 视频下载器 - 命令行入口"""
import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# 修复 Windows GBK 编码问题
if sys.platform == "win32":
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
from downloader import YouTubeDownloader, check_ffmpeg
from torrent_maker import TorrentMaker


def main():
    parser = argparse.ArgumentParser(
        description="YouTube 视频下载器 (基于 yt-dlp)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cli.py https://www.youtube.com/watch?v=xxxxx
  python cli.py https://youtu.be/xxxxx -q 1080p -f mp4
  python cli.py https://www.youtube.com/playlist?list=xxxx --playlist
  python cli.py https://youtu.be/xxxxx --audio -f mp3
  python cli.py https://youtu.be/xxxxx --torrent
        """,
    )

    parser.add_argument("url", nargs="?", help="YouTube 视频或播放列表链接")
    parser.add_argument("-o", "--output", help="输出目录", default=None)
    parser.add_argument("-q", "--quality", default="best",
                        choices=["best", "4k", "1440p", "1080p", "720p", "480p", "360p"],
                        help="画质 (默认: best)")
    parser.add_argument("-f", "--format", default="mp4",
                        choices=["mp4", "mkv", "webm", "mp3", "m4a", "opus"],
                        help="输出格式；音频模式支持 mp3/m4a/opus (默认: mp4)")
    parser.add_argument("--audio", action="store_true", help="仅下载音频")
    parser.add_argument("--subtitle", action="store_true", help="下载字幕")
    parser.add_argument("--sub-lang", default="zh-Hans,en", help="字幕语言 (默认: zh-Hans,en)")
    parser.add_argument("--playlist", action="store_true", help="下载整个播放列表")
    parser.add_argument("--torrent", action="store_true", help="下载后生成种子文件")
    parser.add_argument("--info", action="store_true", help="仅查看视频信息，不下载")
    parser.add_argument("--proxy", default="", help="代理地址，例: http://127.0.0.1:7890")

    args = parser.parse_args()

    video_formats = {"mp4", "mkv", "webm"}
    if not args.audio and args.format not in video_formats:
        parser.error("-f/--format 只有在 --audio 模式下才支持 mp3/m4a/opus")

    if not args.url:
        # 交互模式
        args.url = input("请输入 YouTube 链接: ").strip()
        if not args.url:
            print("未输入链接，退出。")
            return

    downloader = YouTubeDownloader(output_dir=args.output, proxy=args.proxy)
    torrent_maker = TorrentMaker()

    # 检查 ffmpeg
    if not check_ffmpeg() and not args.audio:
        print("⚠ 未检测到 ffmpeg，高画质视频可能需要 ffmpeg 合并音视频流。")
        print("  下载地址: https://ffmpeg.org/download.html\n")

    # 信息模式
    if args.info:
        print("正在获取视频信息...")
        info = downloader.get_video_info(args.url)
        if info is None or "error" in info:
            err = info.get("error", "Unknown") if info else "Unknown"
            print(f"获取失败: {err}")
            return
        dur = info.get("duration", 0)
        print(f"\n  标题: {info['title']}")
        print(f"  作者: {info['uploader']}")
        print(f"  时长: {dur // 60}:{dur % 60:02d}")
        print(f"  播放: {info.get('view_count', 'N/A'):,}")
        if info.get("formats"):
            print(f"  画质: {', '.join(f['resolution'] for f in info['formats'])}")
        return

    # 下载模式
    print(f"\n[⬇] 开始下载...")
    print(f"  链接: {args.url}")
    print(f"  画质: {args.quality}  格式: {args.format}")
    if args.audio:
        print(f"  模式: 仅音频")

    def progress(data):
        if data["type"] == "download":
            pct = data["percent"]
            bar_len = 40
            filled = int(bar_len * pct / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            speed = f"{data['speed'] / 1024 / 1024:.1f} MiB/s" if data.get("speed") else "N/A"
            eta = f"{data['eta']}s" if data.get("eta") else "?"
            print(f"\r  [{bar}] {pct:.0f}%  {speed}  ETA: {eta}", end="", flush=True)
        elif data["type"] == "processing":
            print(f"\n  [⏳] {data['message']}")

    downloader.on_progress(progress)

    try:
        result = downloader.download(
            url=args.url,
            quality=args.quality,
            format_type=args.format,
            audio_only=args.audio,
            subtitles=args.subtitle,
            subtitle_langs=args.sub_lang,
            playlist=args.playlist,
        )
        print()  # 换行

        if result and os.path.isfile(result):
            print(f"\n[✓] 下载完成: {result}")
        elif result:
            print(f"\n[✓] 下载完成到目录: {result}")

        # 生成种子
        if args.torrent and result and os.path.isfile(result):
            print("\n[🌱] 正在生成种子文件...")
            torrent_path = torrent_maker.create(result)
            magnet = torrent_maker.create_magnet(torrent_path)
            print(f"[✓] 种子: {torrent_path}")
            print(f"[🧲] 磁力: {magnet}")

    except Exception as e:
        print(f"\n[✗] 下载失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
