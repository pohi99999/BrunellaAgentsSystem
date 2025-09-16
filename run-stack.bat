@echo off
echo ==============================
echo   Brunella Agent System Stack
echo ==============================
cd /d G:\Brunella\projects\BrunellaAgentSystem

rem Engedelyezzuk a BuildKitet es elokeszitjuk a lokalis build cache-t (G: meghajto)
set DOCKER_BUILDKIT=1

echo Kepek epitese BuildX + lokalis cache hasznalataval...
powershell -NoProfile -ExecutionPolicy Bypass -File .\build-images.ps1
if errorlevel 1 (
	echo HIBA: A kepek epitesi leallt. Ellenorizd a hibauzenetet fentebb.
	echo Probalhatod kezzel is futtatni:
	echo   powershell -NoProfile -ExecutionPolicy Bypass -File .\build-images.ps1 -CacheDir ".buildx-cache"
	exit /b 1
)

echo Inditas: docker compose up -d (ha nem megy, docker-compose up -d)
docker compose up -d
if errorlevel 1 (
	echo docker compose nem elerheto, probalkozas docker-compose v1-el...
	docker-compose up -d
	if errorlevel 1 (
		echo HIBA: A docker compose inditas sikertelen.
		echo Ellenorizd, hogy a Docker Desktop fut-e, es az env valtozok be vannak allitva (.env).
		exit /b 1
	)
)

echo.
echo ==============================
echo   Stack elindult!
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo ==============================
pause
