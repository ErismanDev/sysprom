# Script para rodar o servidor Django com PostgreSQL
Write-Host "🚀 Iniciando servidor Django com PostgreSQL..." -ForegroundColor Green
Write-Host ""

# Adicionar PostgreSQL ao PATH
$env:PATH += ";C:\Program Files\PostgreSQL\17\bin"

# Definir senha do PostgreSQL
$env:PGPASSWORD = "postgres123"

# Rodar servidor
python manage.py runserver

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 