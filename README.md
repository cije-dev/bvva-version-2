# Data Analyzer Pro - Web Version

A professional-grade data analysis web application built with Streamlit.

## Features

- 📊 Load and analyze Excel/CSV files
- 📈 View analytics and statistics dashboard
- 🔍 Search through data with partial matching
- 🔗 Combine base names for analysis
- 📍 Filter by base names with detailed statistics
- Support for multi-sheet Excel files
- Base name grouping (e.g., "20221-US-LY" and "20232-US-LY" grouped as "LY")

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### With Password Protection (Recommended)

1. **Using PowerShell script:**
   ```powershell
   .\run.ps1 -Password "your_password_here"
   ```

2. **Using Batch script:**
   ```cmd
   run.bat your_password_here
   ```

3. **Using environment variable:**
   ```powershell
   $env:DATA_ANALYZER_PASSWORD="your_password_here"
   streamlit run app.py
   ```

4. **Using command line argument:**
   ```bash
   streamlit run app.py -- --password=your_password_here
   ```

5. **Direct Streamlit command:**
   ```bash
   streamlit run app.py
   ```
   (Shows a warning if no password is set)

2. The application will open in your default web browser at `http://localhost:8501`

3. Enter the password on the login screen to access the application

### Without Password Protection

If no password is set, the application will show a warning but allow access (not recommended for production).

## Usage

1. **Load a File**: 
   - **Upload**: Use "📤 Upload File" to upload an Excel (.xlsx, .xls) or CSV file
   - **From Data Folder**: Use "📁 Load from Data Folder" to select from existing files in the `data` directory
2. **Select Sheets**: If your Excel file has multiple sheets, select which ones to load
3. **View Data**: Navigate to "📋 Data View" to see the loaded data
4. **Analytics**: Check "📈 Analytics" for statistics on approval status
5. **Search**: Use "🔍 Search" to find specific records
6. **Combine Bases**: Use "🔗 Combine" to analyze multiple base names together
7. **Base Statistics**: Use "📍 Bases" to filter and view statistics by base name

## Data Folder

The application includes a `data` folder where you can store Excel and CSV files for quick access:
- Place your files in the `web-version/data/` directory
- Files will automatically appear in the "📁 Load from Data Folder" option
- Supported formats: .xlsx, .xls, .csv

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- OpenPyXL (for Excel file support)

