"""种子文件生成模块 - 基于 torf"""

import os
from pathlib import Path
from typing import Optional, List


class TorrentMaker:
    """将本地文件/目录生成 .torrent 种子文件"""

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or str(Path.home() / "Downloads" / "Torrents")
        os.makedirs(self.output_dir, exist_ok=True)

    def create(self, file_path: str,
               trackers: List[str] = None,
               comment: str = "",
               piece_size: int = None,
               private: bool = False) -> str:
        """
        创建种子文件

        Args:
            file_path: 要分发的文件或目录路径
            trackers: tracker URL 列表 (默认使用公共 tracker)
            comment: 种子备注
            piece_size: 分块大小 (自动选择)
            private: 是否私有种子

        Returns:
            生成的 .torrent 文件路径
        """
        from torf import Torrent

        if trackers is None:
            trackers = [
                "udp://tracker.opentrackr.org:1337/announce",
                "udp://tracker.openbittorrent.com:6969/announce",
                "udp://open.stealth.si:80/announce",
                "udp://tracker.torrent.eu.org:451/announce",
                "udp://tracker.moeking.me:6969/announce",
                "udp://explodie.org:6969/announce",
                "udp://exodus.desync.com:6969/announce",
                "http://tracker.openbittorrent.com:80/announce",
            ]

        # 自动选择合适的分块大小
        if piece_size is None:
            total_size = self._get_size(file_path)
            if total_size < 50 * 1024 * 1024:  # < 50MB
                piece_size = 256 * 1024  # 256KB
            elif total_size < 500 * 1024 * 1024:  # < 500MB
                piece_size = 512 * 1024  # 512KB
            elif total_size < 2 * 1024 * 1024 * 1024:  # < 2GB
                piece_size = 1024 * 1024  # 1MB
            else:
                piece_size = 2 * 1024 * 1024  # 2MB

        path = Path(file_path)
        torrent = Torrent(
            path=file_path,
            trackers=trackers,
            comment=comment or f"Created from {path.name}",
            piece_size=piece_size,
            private=private,
        )
        torrent.generate()

        torrent_path = os.path.join(
            self.output_dir,
            f"{path.stem}.torrent"
        )
        torrent.write(torrent_path)

        return torrent_path

    def _get_size(self, path: str) -> int:
        """获取文件/目录大小"""
        p = Path(path)
        if p.is_file():
            return p.stat().st_size
        elif p.is_dir():
            return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
        return 0

    def create_magnet(self, torrent_path: str) -> str:
        """从种子文件生成磁力链接"""
        from torf import Torrent
        torrent = Torrent.read(torrent_path)
        magnet = torrent.magnet()
        return str(magnet)
