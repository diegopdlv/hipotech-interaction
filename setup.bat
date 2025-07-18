@echo off
setlocal

REM Check if Python is available
where python >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found. Please install Python and add it to PATH.
    pause
    exit /b
)

REM Define venv path
set VENV_DIR=venv

IF EXIST "%VENV_DIR%\Scripts\activate.bat" (
    echo [OK] Virtual environment already exists. Activating...
    call "%VENV_DIR%\Scripts\activate.bat"
) ELSE (
    echo [NEW] Creating virtual environment...
    python -m venv "%VENV_DIR%"
    IF ERRORLEVEL 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )

    echo [OK] Virtual environment created.
    echo [*] Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"

    pip show hipotech_analysis >nul 2>&1
    IF ERRORLEVEL 1 (
        echo [*] Installing wheel package...
        pip install dist\hipotech_analysis-0.1.0-py3-none-any.whl
    ) ELSE (
        echo [OK] hipotech_analysis wheel already installed.
    )

    echo [*] Installing Python requirements...
    pip install -r requirements.txt

    echo [*] Installing Playwright browsers...
    playwright install
)

echo [GO] Running the Streamlit app...
streamlit run app.py

pause
endlocal
