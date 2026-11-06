@echo off
title ACL - Streamlit Native Frontend
echo ========================================================
echo   ACL - Automated Comic Localization (Streamlit Native)
echo   Opening frontend on http://localhost:8501
echo ========================================================
python -m streamlit run app.py --server.port 8501
pause
