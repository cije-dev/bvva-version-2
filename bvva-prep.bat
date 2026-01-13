@echo off
REM Script to set up virtual environment and install requirements
REM Usage: bvva-prep.bat

echo Creating virtual environment...
python -m venv venv

if errorlevel 1 (
    echo Error: Failed to create virtual environment. Make sure Python is installed.
    exit /b 1
)

echo Virtual environment created successfully!
echo.
echo Activating virtual environment...

call venv\Scripts\activate.bat

if errorlevel 1 (
    echo Error: Failed to activate virtual environment.
    exit /b 1
)

echo Virtual environment activated!
echo.
echo Installing requirements from requirements.txt...

pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install requirements.
    exit /b 1
)

echo.
echo Setup complete! Virtual environment is ready.
echo To activate the virtual environment in the future, run: venv\Scripts\activate.bat
pause

