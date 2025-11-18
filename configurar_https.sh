#!/bin/bash
# Script para configurar HTTPS no servidor Digital Ocean
# IP: 64.23.185.235

set -e

echo "=========================================="
echo "🔒 CONFIGURANDO HTTPS NO SERVIDOR"
echo "=========================================="

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Por favor, execute como root (sudo)"
    exit 1
fi

# Verificar se tem domínio configurado
read -p "Você tem um domínio apontando para este servidor? (s/n): " TEM_DOMINIO

if [ "$TEM_DOMINIO" = "s" ] || [ "$TEM_DOMINIO" = "S" ]; then
    read -p "Digite o domínio (ex: exemplo.com): " DOMINIO
    
    echo ""
    echo "📋 Configurando HTTPS para: $DOMINIO"
    echo ""
    
    # Atualizar sistema
    echo "📦 Atualizando sistema..."
    apt update
    apt upgrade -y
    
    # Instalar Certbot
    echo ""
    echo "📦 Instalando Certbot..."
    apt install -y certbot python3-certbot-nginx
    
    # Parar Nginx temporariamente para validação
    echo ""
    echo "⏸️  Parando Nginx..."
    systemctl stop nginx
    
    # Obter certificado
    echo ""
    echo "🔐 Obtendo certificado SSL..."
    certbot certonly --standalone -d $DOMINIO --non-interactive --agree-tos --email admin@$DOMINIO
    
    # Atualizar configuração do Nginx
    echo ""
    echo "📝 Atualizando configuração do Nginx..."
    
    # Backup da configuração atual
    cp /etc/nginx/sites-available/seprom /etc/nginx/sites-available/seprom.backup.$(date +%Y%m%d_%H%M%S)
    
    # Criar nova configuração com HTTPS
    cat > /etc/nginx/sites-available/seprom << 'NGINX_EOF'
# Configuração Nginx para SEPROM CBMEPI com HTTPS
# Gerado automaticamente

# Redirecionar HTTP para HTTPS
server {
    listen 80;
    server_name DOMINIO_AQUI;
    
    # Permitir validação do Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirecionar todo o resto para HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# Servidor HTTPS
server {
    listen 443 ssl http2;
    server_name DOMINIO_AQUI;
    
    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/DOMINIO_AQUI/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/DOMINIO_AQUI/privkey.pem;
    
    # Configurações SSL modernas
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/DOMINIO_AQUI/chain.pem;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    # Headers de segurança
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
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

    # Substituir DOMINIO_AQUI pelo domínio real
    sed -i "s/DOMINIO_AQUI/$DOMINIO/g" /etc/nginx/sites-available/seprom
    
    # Testar configuração
    echo ""
    echo "🔍 Testando configuração do Nginx..."
    nginx -t
    
    if [ $? -eq 0 ]; then
        echo "✅ Configuração válida!"
        
        # Reiniciar Nginx
        echo ""
        echo "🔄 Reiniciando Nginx..."
        systemctl start nginx
        systemctl reload nginx
        
        # Configurar renovação automática
        echo ""
        echo "⏰ Configurando renovação automática do certificado..."
        systemctl enable certbot.timer
        systemctl start certbot.timer
        
        echo ""
        echo "=========================================="
        echo "✅ HTTPS CONFIGURADO COM SUCESSO!"
        echo "=========================================="
        echo "🌐 Acesse: https://$DOMINIO"
        echo "🔄 O certificado será renovado automaticamente"
        echo "=========================================="
    else
        echo "❌ Erro na configuração do Nginx!"
        echo "Restaurando backup..."
        cp /etc/nginx/sites-available/seprom.backup.* /etc/nginx/sites-available/seprom
        systemctl start nginx
        exit 1
    fi
    
else
    echo ""
    echo "⚠️  Para usar HTTPS, você precisa de um domínio."
    echo ""
    echo "Opções:"
    echo "1. Registrar um domínio (ex: no Registro.br, GoDaddy, etc)"
    echo "2. Apontar o domínio para o IP: 64.23.185.235"
    echo "3. Executar este script novamente"
    echo ""
    echo "Ou use um serviço como:"
    echo "- Cloudflare (gratuito, com SSL)"
    echo "- Let's Encrypt (requer domínio)"
    echo ""
    echo "Para usar apenas IP, você pode:"
    echo "- Usar um certificado auto-assinado (não recomendado)"
    echo "- Usar Cloudflare Tunnel (recomendado)"
    exit 0
fi

