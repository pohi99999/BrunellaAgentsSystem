@echo off
echo ==============================
echo   Brunella Agent System Stack
echo ==============================
cd /d G:\Brunella\BrunellaAgentSystem

echo Inditas: docker-compose up --build -d
docker-compose up --build -d

echo.
echo ==============================
echo   Stack elindult!
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo ==============================
pause
