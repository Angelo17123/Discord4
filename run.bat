@echo off
echo Iniciando self-bot de Discord...
echo.

echo Activando entorno virtual...
call venv\Scripts\activate

echo Verificando dependencias...
py src\test_imports.py
if %errorlevel% neq 0 (
    echo Error: Faltan dependencias. Ejecuta install.bat primero.
    pause
    exit /b 1
)

echo Ejecutando bot...
py src\bot.py

pause