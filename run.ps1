# Run script for Data Analyzer Pro Web Version
param(
    [string]$Password = $env:DATA_ANALYZER_PASSWORD
)

Write-Host "Starting Data Analyzer Pro Web Version..." -ForegroundColor Cyan

if ($Password) {
    Write-Host "Password protection is enabled." -ForegroundColor Green
    streamlit run app.py -- --password=$Password
} else {
    Write-Host "Warning: No password set. Use -Password parameter or set DATA_ANALYZER_PASSWORD environment variable." -ForegroundColor Yellow
    Write-Host "Example: .\run.ps1 -Password 'your_password'" -ForegroundColor Yellow
    $proceed = Read-Host "Continue without password protection? (y/n)"
    if ($proceed -eq 'y') {
        streamlit run app.py
    } else {
        Write-Host "Exiting. Please set a password." -ForegroundColor Red
    }
}

