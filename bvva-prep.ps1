# Script to set up virtual environment and install requirements
# Usage: .\bvva-prep.ps1

Write-Host "Creating virtual environment..." -ForegroundColor Green

# Create virtual environment
python -m venv venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to create virtual environment. Make sure Python is installed." -ForegroundColor Red
    exit 1
}

Write-Host "Virtual environment created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Green

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to activate virtual environment." -ForegroundColor Red
    exit 1
}

Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "Installing requirements from requirements.txt..." -ForegroundColor Green

# Install requirements
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install requirements." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setup complete! Virtual environment is ready." -ForegroundColor Green
Write-Host "To activate the virtual environment in the future, run: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan

