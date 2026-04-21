@echo off
cd /d "H:\Meu Drive\Cyber Trade\Winfut"
echo Starting Cyber Trade WIN v3.0 Dashboard...
python -m streamlit run dashboard.py --server.headless=false --server.port=8501
pause