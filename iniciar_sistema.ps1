# Script para iniciar o SEPROM CBMEPI com ambiente virtual ativo
Write-Host "🚀 Iniciando SEPROM CBMEPI..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

# Ativar ambiente virtual
Write-Host "📦 Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Verificar se o dotenv está instalado
Write-Host "🔍 Verificando dependências..." -ForegroundColor Yellow
try {
    python -c "import dotenv; print('✅ python-dotenv OK')" 2>$null
} catch {
    Write-Host "❌ python-dotenv não encontrado. Instalando..." -ForegroundColor Red
    pip install python-dotenv==1.0.0
}

# Verificar configurações Django
Write-Host "🔧 Verificando configurações Django..." -ForegroundColor Yellow
python manage.py check --settings=sepromcbmepi.settings_supabase

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Configurações OK" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "📋 Informações de Acesso:" -ForegroundColor White
    Write-Host "   • URL Principal: http://127.0.0.1:8000" -ForegroundColor Cyan
    Write-Host "   • URL Admin: http://127.0.0.1:8000/admin" -ForegroundColor Cyan
    Write-Host "   • Usuário Admin: admin" -ForegroundColor Cyan
    Write-Host "   • Senha Admin: admin123" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "🔄 Para parar o servidor, pressione Ctrl+C" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Cyan
    
    # Iniciar servidor
    python iniciar_supabase_dev.py
} else {
    Write-Host "❌ Erro nas configurações Django" -ForegroundColor Red
    exit 1
} 