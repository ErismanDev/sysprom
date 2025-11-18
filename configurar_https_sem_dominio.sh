#!/bin/bash
# Script para configurar HTTPS sem domínio usando Cloudflare Tunnel
# Ou certificado auto-assinado como alternativa

set -e

echo "=========================================="
echo "🔒 CONFIGURAR HTTPS SEM DOMÍNIO"
echo "=========================================="
echo ""
echo "Escolha uma opção:"
echo "1. Cloudflare Tunnel (Recomendado - Gratuito, HTTPS real)"
echo "2. Certificado Auto-Assinado (Apenas para teste - Aviso no navegador)"
echo ""
read -p "Digite a opção (1 ou 2): " OPCAO

if [ "$OPCAO" = "1" ]; then
    echo ""
    echo "🌐 Configurando Cloudflare Tunnel..."
    echo ""
    
    # Verificar se cloudflared está instalado
    if ! command -v cloudflared &> /dev/null; then
        echo "📦 Instalando cloudflared..."
        
        # Detectar arquitetura
        ARCH=$(uname -m)
        if [ "$ARCH" = "x86_64" ]; then
            ARCH="amd64"
        elif [ "$ARCH" = "aarch64" ]; then
            ARCH="arm64"
        else
            echo "❌ Arquitetura não suportada: $ARCH"
            exit 1
        fi
        
        # Baixar e instalar
        wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${ARCH}.deb -O /tmp/cloudflared.deb
        dpkg -i /tmp/cloudflared.deb || apt-get install -f -y
        rm /tmp/cloudflared.deb
    fi
    
    echo "✅ cloudflared instalado!"
    echo ""
    echo "📋 Próximos passos:"
    echo ""
    echo "1. Crie uma conta gratuita em: https://dash.cloudflare.com/sign-up"
    echo "2. Execute o comando de autenticação:"
    echo "   cloudflared tunnel login"
    echo ""
    echo "3. Crie um tunnel:"
    echo "   cloudflared tunnel create seprom"
    echo ""
    echo "4. Configure o tunnel:"
    echo "   cloudflared tunnel route dns seprom seprom-tunnel.cf"
    echo ""
    echo "5. Execute o tunnel:"
    echo "   cloudflared tunnel run seprom"
    echo ""
    echo "📖 Guia completo: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/"
    
elif [ "$OPCAO" = "2" ]; then
    echo ""
    echo "🔐 Gerando certificado auto-assinado..."
    echo ""
    echo "⚠️  ATENÇÃO: Navegadores mostrarão aviso de segurança!"
    echo "   Use apenas para testes internos."
    echo ""
    
    # Criar diretório para certificados
    mkdir -p /etc/ssl/private
    mkdir -p /etc/ssl/certs
    
    # Gerar certificado auto-assinado
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/ssl/private/seprom-selfsigned.key \
        -out /etc/ssl/certs/seprom-selfsigned.crt \
        -subj "/C=BR/ST=CE/L=Fortaleza/O=SEPROM/CN=64.23.185.235" \
        2>/dev/null
    
    echo "✅ Certificado gerado!"
    echo ""
    echo "📝 Atualizando configuração do Nginx..."
    
    # Backup
    cp /etc/nginx/sites-available/seprom /etc/nginx/sites-available/seprom.backup.$(date +%Y%m%d_%H%M%S)
    
    # Criar configuração com HTTPS auto-assinado
    cat > /etc/nginx/sites-available/seprom << 'NGINX_EOF'
# Configuração Nginx para SEPROM CBMEPI com HTTPS (Auto-Assinado)
# ⚠️ Certificado auto-assinado - Navegadores mostrarão aviso

# Servidor HTTP (redireciona para HTTPS)
server {
    listen 80;
    server_name 64.23.185.235;
    
    # Redirecionar para HTTPS
    return 301 https://$server_name$request_uri;
}

# Servidor HTTPS
server {
    listen 443 ssl http2;
    server_name 64.23.185.235;
    
    # Certificados auto-assinados
    ssl_certificate /etc/ssl/certs/seprom-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/seprom-selfsigned.key;
    
    # Configurações SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Headers de segurança
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline' 'unsafe-eval'" always;
    
    # Configurações de performance
    client_max_body_size 100M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Arquivos estáticos
    location /static/ {
        alias /home/seprom/sepromcbmepi/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Arquivos de mídia
    location /media/ {
        alias /home/seprom/sepromcbmepi/media/;
        expires 1y;
        add_header Cache-Control "public";
        access_log off;
    }
    
    # Favicon
    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }
    
    # Robots.txt
    location = /robots.txt {
        access_log off;
        log_not_found off;
    }
    
    # Aplicação principal
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
    
    # Health check
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Logs
    access_log /var/log/nginx/seprom_access.log;
    error_log /var/log/nginx/seprom_error.log;
}
NGINX_EOF
    
    # Testar configuração
    echo ""
    echo "🔍 Testando configuração do Nginx..."
    nginx -t
    
    if [ $? -eq 0 ]; then
        echo "✅ Configuração válida!"
        
        # Reiniciar Nginx
        echo ""
        echo "🔄 Reiniciando Nginx..."
        systemctl reload nginx
        
        echo ""
        echo "=========================================="
        echo "✅ HTTPS CONFIGURADO (Auto-Assinado)!"
        echo "=========================================="
        echo "🌐 Acesse: https://64.23.185.235"
        echo ""
        echo "⚠️  IMPORTANTE:"
        echo "   - O navegador mostrará aviso de segurança"
        echo "   - Clique em 'Avançado' > 'Continuar para o site'"
        echo "   - Isso é normal para certificados auto-assinados"
        echo ""
        echo "💡 Para HTTPS sem avisos, use Cloudflare Tunnel ou registre um domínio"
        echo "=========================================="
    else
        echo "❌ Erro na configuração do Nginx!"
        exit 1
    fi
    
else
    echo "❌ Opção inválida!"
    exit 1
fi

