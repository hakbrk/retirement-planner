@echo off
cd /d "%~dp0retirement_dashboard"
uv run streamlit run app/main.py
pause