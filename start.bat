@echo off

REM Check if virtual environment folder exists
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
echo Activating virtual environment...
CALL venv\Scripts\activate

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Start the application
echo Starting the application...
python app.py

REM Deactivate the virtual environment
echo Deactivating virtual environment...
deactivate