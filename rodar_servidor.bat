@echo off
echo Iniciando servidor Django com PostgreSQL...
echo.

REM Adicionar PostgreSQL ao PATH
set PATH=%PATH%;C:\Program Files\PostgreSQL\17\bin

REM Definir senha do PostgreSQL
set PGPASSWORD=postgres123

REM Rodar servidor
python manage.py runserver

pause 