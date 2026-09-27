@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creando ambiente virtual...
    python -m venv .venv
)

if not exist ".env" (
    echo Creando archivo .env desde .env.example...
    copy ".env.example" ".env" >nul
)

echo Instalando/verificando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Error instalando dependencias.
    pause
    exit /b 1
)

echo Preparando base de datos PostgreSQL...
".venv\Scripts\python.exe" ".\scripts\init_db.py"
if errorlevel 1 (
    echo Error preparando la base de datos. Revise DATABASE_URL en .env.
    pause
    exit /b 1
)

echo Creando/verificando tablas iniciales...
".venv\Scripts\python.exe" ".\scripts\create_tables.py"
if errorlevel 1 (
    echo Error creando o verificando tablas.
    pause
    exit /b 1
)

echo Actualizando esquema de base de datos...
".venv\Scripts\python.exe" ".\scripts\update_schema.py"
if errorlevel 1 (
    echo Error actualizando el esquema de base de datos.
    pause
    exit /b 1
)

echo.
echo Aplicativo disponible en http://127.0.0.1:5000
echo Presione Ctrl+C para detener el servidor.
echo.

".venv\Scripts\python.exe" ".\run.py"

endlocal
