@echo off
echo Instalando dependencias para self-bot de Discord...
echo.

echo Creando entorno virtual...
py -m venv venv

echo Activando entorno virtual...
call venv\Scripts\activate

echo Instalando discord.py-self con soporte de voz...
py -m pip install "discord.py-self[voice]"

echo Instalando python-dotenv...
py -m pip install python-dotenv

echo.
echo Instalación completada.
echo.
echo Verificando instalación...
py src\test_imports.py
echo.
echo Para ejecutar el bot, ejecuta: run.bat
pause