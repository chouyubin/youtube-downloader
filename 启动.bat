@echo off
chcp 65001 >nul 2>nul
pushd "%~dp0"

:: 设置工具路径（按需修改）
if exist "D:\Tool\ffmpeg\bin" set "PATH=D:\Tool\ffmpeg\bin;%PATH%"
if exist "D:\Tool\aria2" set "PATH=D:\Tool\aria2;%PATH%"

:: 查找 Python
set "PYEXE="
if exist ".venv\Scripts\pythonw.exe" (
    set "PYEXE=.venv\Scripts\pythonw.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PYEXE=.venv\Scripts\python.exe"
) else (
    where pythonw.exe >nul 2>nul && set "PYEXE=pythonw.exe"
    if "%PYEXE%"=="" where python.exe >nul 2>nul && set "PYEXE=python.exe"
)

if "%PYEXE%"=="" (
    echo [错误] 未找到 Python，请安装 Python 3.9+ 或创建 .venv 虚拟环境
    pause
    popd
    exit /b 1
)

:: 检查依赖
"%PYEXE%" -c "import yt_dlp" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [提示] 正在安装依赖...
    if exist ".venv\Scripts\pip.exe" (
        .venv\Scripts\pip.exe install -r requirements.txt
    ) else (
        pip install -r requirements.txt
    )
)

:: 启动应用
echo 启动 YouTube 下载器...
start "" "%PYEXE%" "%~dp0main.py"
popd
