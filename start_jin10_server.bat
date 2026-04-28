@echo off
chcp 65001 >nul
cd /d D:\练习\gold-dashboard
echo ==========================================
echo    Gold Dashboard - Jin10 Data Service
echo ==========================================
echo.
echo Data Source: Jin10 Financial Data
echo.
echo Starting server on http://localhost:8000
echo.
echo API Endpoints:
echo   - http://localhost:8000/api/dashboard
echo   - http://localhost:8000/api/jin10/gold
echo   - http://localhost:8000/api/jin10/oil
echo   - http://localhost:8000/api/jin10/flash-news
echo.
echo Press Ctrl+C to stop
echo ==========================================
echo.
python data_service_jin10.py
pause
