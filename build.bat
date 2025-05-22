@echo off
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b 1
)

echo Running tests...
pytest test_bot.py
if errorlevel 1 (
    echo Tests failed.
    exit /b 1
)

echo Starting bot...
python bot.py
