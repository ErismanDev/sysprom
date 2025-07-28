# Script para abrir o site no navegador com HTTP
Write-Host "🌐 Abrindo SEPROM CBMEPI no navegador..." -ForegroundColor Green

# URL correta (HTTP)
$url = "http://127.0.0.1:8000"

# Abrir no navegador padrão
Start-Process $url

Write-Host "✅ Site aberto em: $url" -ForegroundColor Cyan
Write-Host "📋 Credenciais: admin / admin123" -ForegroundColor Yellow 