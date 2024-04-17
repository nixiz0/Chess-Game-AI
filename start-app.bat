@echo off
IF NOT EXIST .env (
    python -m venv .env
    cd .env\Scripts
    cd ../..
    pip install -r requirements.txt
) ELSE (
    cd .env\Scripts
    cd ../..
)
python.exe menu.py