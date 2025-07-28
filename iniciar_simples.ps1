# Script simples para iniciar o SEPROM CBMEPI
Write-Host "🚀 Iniciando SEPROM CBMEPI..." -ForegroundColor Green

# Ativar ambiente virtual
Write-Host "📦 Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Verificar dotenv
Write-Host "🔍 Verificando python-dotenv..." -ForegroundColor Yellow
python -c "import dotenv; print('✅ python-dotenv OK')"

# Iniciar servidor
Write-Host "🌐 Iniciando servidor..." -ForegroundColor Green
python iniciar_supabase_dev.py 