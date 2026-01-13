@echo off
REM Run script for Data Analyzer Pro Web Version
echo Starting Data Analyzer Pro Web Version...

REM Check for password in environment variable or command line argument
set PASSWORD=%1
if "%PASSWORD%"=="" set PASSWORD=%DATA_ANALYZER_PASSWORD%

if not "%PASSWORD%"=="" (
    echo Password protection is enabled.
    streamlit run app.py -- --password=%PASSWORD%
) else (
    echo Warning: No password set. Pass password as argument or set DATA_ANALYZER_PASSWORD environment variable.
    echo Example: run.bat your_password
    set /p proceed="Continue without password protection? (y/n): "
    if /i "%proceed%"=="y" (
        streamlit run app.py
    ) else (
        echo Exiting. Please set a password.
    )
)

pause

