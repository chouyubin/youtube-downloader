@echo off
chcp 65001 >nul 2>nul
pushd "%~dp0"

:: 设置本地工具路径（优先使用打包的 FFmpeg + Aria2）
if exist "%~dp0tools\bin" set "PATH=%~dp0tools\bin;%PATH%"

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

:: 启动应用（无控制台窗口）
echo 启动 YouTube 下载器...
if exist "%~dp0main.pyw" (
    "%PYEXE%" "%~dp0main.pyw"
) else (
    "%PYEXE%" "%~dp0main.py"
)
popd