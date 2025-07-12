@echo off
REM AGP Power Monitor
REM Copyright (C) 2025 - tehsiggi

set VENV_DIR=.venv

if "%1"=="install" goto install
if "%1"=="activate-venv" goto activate_venv
if "%1"=="start" goto start

echo Usage: %0 ^<install^|activate-venv^|start^>
exit /b 1

:install
python -m venv %VENV_DIR%
call %VENV_DIR%\Scripts\activate
python -m pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
)
echo Installation complete.
exit /b

:activate_venv
if exist %VENV_DIR% (
    echo Run: call %VENV_DIR%\Scripts\activate
) else (
    echo Virtual environment not found. Run "setup.bat install" first.
    exit /b 1
)
exit /b

:start
shift
set ARGS=
:loop
if "%1"=="" goto afterloop
set ARGS=%ARGS% %1
shift
goto loop
:afterloop

if exist %VENV_DIR% (
    call %VENV_DIR%\Scripts\activate
    if exist src\main.py (
        python src\main.py %ARGS%
    ) else (
        echo main.py not found.
        exit /b 1
    )
) else (
    echo Virtual environment not found. Run "setup.bat install" first.
    exit /b 1
)
exit /b

