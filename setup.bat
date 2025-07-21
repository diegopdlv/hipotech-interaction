@echo off
setlocal

REM === 1. Check if Python is available ===
where python >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found. Please install Python and add it to PATH.
    pause
    exit /b
)

REM === 2. Define venv path ===
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

REM === 3. Check for AWS CLI ===
where aws >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] AWS CLI not found. Please install AWS CLI and add it to PATH.
    pause
    exit /b
)

REM === 4. Check if AWS credentials exist ===
set AWS_CREDENTIALS_FILE=%USERPROFILE%\.aws\credentials

IF NOT EXIST "%AWS_CREDENTIALS_FILE%" (
    echo [*] AWS credentials not found.
    goto ConfigureAWS
) ELSE (
    findstr /C:"aws_access_key_id" "%AWS_CREDENTIALS_FILE%" >nul 2>&1
    IF ERRORLEVEL 1 (
        echo [*] AWS credentials file exists but no access key found.
        goto ConfigureAWS
    ) ELSE (
        echo [OK] AWS credentials already configured.
    )
)

goto RunApp

:ConfigureAWS
echo [*] Running aws configure...
aws configure

:RunApp
echo [GO] Running the Streamlit app...
streamlit run app.py

pause
endlocal
