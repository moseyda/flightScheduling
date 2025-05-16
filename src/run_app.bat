@echo off
REM Batch file to run Streamlit application
REM Ensure Python and Streamlit are installed

:: Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Install Python from https://www.python.org/downloads/
    pause
    exit /b
)

:: Check if Streamlit is installed
pip show streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo Streamlit is not installed. Installing now...
    pip install streamlit
)

:: Check if Pandas is installed
pip show pandas >nul 2>&1
if %errorlevel% neq 0 (
    echo Pandas is not installed. Installing now...
    pip install pandas
)

:: Navigate to script directory (adjust if needed)
cd /d "%~dp0"

:: Launch Streamlit app
echo Starting Flight Scheduling Dashboard...
streamlit run app_04.py

:: Keep window open after exit
pause