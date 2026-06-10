# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os, glob

SPEC_DIR = os.path.dirname(os.path.abspath(SPECPATH or __file__))
datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('yt_dlp')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('torf')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Bundle tools (FFmpeg + Aria2)
tools_dir = os.path.join(SPEC_DIR, 'tools', 'bin')
for exe in glob.glob(os.path.join(tools_dir, '*.exe')):
    name = os.path.basename(exe)
    binaries.append((exe, os.path.join('tools', 'bin', name), 'BINARY'))


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
