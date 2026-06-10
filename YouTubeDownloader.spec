# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os

SPEC_DIR = os.path.dirname(os.path.abspath(SPECPATH or r"D:\Project\youtube-downloader\YouTubeDownloader.spec"))
datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('yt_dlp')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('torf')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Bundle tools (FFmpeg + Aria2)
TOOLS_DIR = os.path.join(SPEC_DIR, 'tools', 'bin')
if os.path.isdir(TOOLS_DIR):
    for f in os.listdir(TOOLS_DIR):
        fp = os.path.join(TOOLS_DIR, f)
        if os.path.isfile(fp):
            binaries.append((fp, os.path.join('tools', 'bin', f), 'BINARY'))


a = Analysis(
    ['D:\\Project\\youtube-downloader\\main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YouTubeDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=['ffmpeg.exe', 'ffprobe.exe', 'aria2c.exe'],
    name='YouTubeDownloader',
)
