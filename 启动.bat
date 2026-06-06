@echo off
set "PATH=D:\Tool\ffmpeg\bin;D:\Tool\aria2;%PATH%"
pushd "%~dp0"
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0main.py"
) else (
    where pythonw.exe >nul 2>nul
    if %ERRORLEVEL%==0 (
    start "" pythonw.exe "%~dp0main.py"
    ) else (
    start "" python.exe "%~dp0main.py"
    )
)
popd
