#!/bin/bash

# Script de Deploy Simplificado - SEPROM CBMEPI (Amazon Linux 2023)
# Domínio: sysprom.cbmepi.gov.br
# Repositório: https://github.com/ErismanDev/sysprom.git

set -e

echo "=== INICIANDO DEPLOY DO SISTEMA SEPROM CBMEPI ==="
echo "Domínio: sysprom.cbmepi.gov.br"
echo "IP: 18.230.255.20"
echo "Sistema: Amazon Linux 2023"

# Atualizar sistema
echo "Atualizando sistema..."
sudo dnf update -y

# Instalar dependências básicas
echo "Instalando dependências..."
sudo dnf install -y python3 python3-pip python3-devel nginx git gcc

# Instalar PostgreSQL
echo "Instalando PostgreSQL..."
sudo dnf install -y postgresql15 postgresql15-server postgresql15-contrib

# Inicializar PostgreSQL
echo "Inicializando PostgreSQL..."
sudo postgresql15-setup initdb
sudo systemctl enable postgresql15
sudo systemctl start postgresql15

# Criar usuário para o aplicativo
echo "Criando usuário para o aplicativo..."
sudo useradd -m -s /bin/bash seprom || true
sudo usermod -aG wheel seprom

# Configurar PostgreSQL
echo "Configurando PostgreSQL..."
sudo -u postgres createuser --interactive --pwprompt seprom || true
sudo -u postgres createdb seprom_db || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE seprom_db TO seprom;"

# Criar diretório do projeto
echo "Criando diretório do projeto..."
sudo mkdir -p /opt/seprom
sudo chown seprom:seprom /opt/seprom

# Clonar repositório
echo "Clonando repositório..."
cd /opt/seprom
sudo -u seprom git clone https://github.com/ErismanDev/sysprom.git . || (sudo -u seprom git pull)

# Configurar ambiente virtual
echo "Configurando ambiente virtual..."
sudo -u seprom python3 -m venv venv
sudo -u seprom /opt/seprom/venv/bin/pip install --upgrade pip
sudo -u seprom /opt/seprom/venv/bin/pip install -r requirements.txt

# Configurar variáveis de ambiente
echo "Configurando variáveis de ambiente..."
sudo -u seprom tee /opt/seprom/.env > /dev/null <<EOF
DEBUG=False
SECRET_KEY=django-insecure-change-this-in-production
DATABASE_URL=postgresql://seprom:senha123@localhost/seprom_db
ALLOWED_HOSTS=sysprom.cbmepi.gov.br,www.sysprom.cbmepi.gov.br,18.230.255.20
STATIC_ROOT=/opt/seprom/staticfiles
MEDIA_ROOT=/opt/seprom/media
EOF

# Configurar Django
echo "Configurando Django..."
cd /opt/seprom
sudo -u seprom /opt/seprom/venv/bin/python manage.py collectstatic --noinput
sudo -u seprom /opt/seprom/venv/bin/python manage.py migrate
sudo -u seprom /opt/seprom/venv/bin/python manage.py createsuperuser --noinput --username admin --email admin@sysprom.cbmepi.gov.br || true

# Configurar Gunicorn
echo "Configurando Gunicorn..."
sudo -u seprom /opt/seprom/venv/bin/pip install gunicorn

# Criar arquivo de serviço do Gunicorn
sudo tee /etc/systemd/system/seprom.service > /dev/null <<EOF
[Unit]
Description=SEPROM CBMEPI Gunicorn daemon
After=network.target

[Service]
User=seprom
Group=seprom
WorkingDirectory=/opt/seprom
Environment="PATH=/opt/seprom/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=sepromcbmepi.settings"
ExecStart=/opt/seprom/venv/bin/gunicorn --workers 3 --bind unix:/opt/seprom/seprom.sock --timeout 120 sepromcbmepi.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
echo "Configurando Nginx..."
sudo tee /etc/nginx/conf.d/seprom.conf > /dev/null <<EOF
server {
    listen 80;
    server_name sysprom.cbmepi.gov.br www.sysprom.cbmepi.gov.br 18.230.255.20;

    # Logs
    access_log /var/log/nginx/seprom_access.log;
    error_log /var/log/nginx/seprom_error.log;

    # Favicon
    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    # Arquivos estáticos
    location /static/ {
        alias /opt/seprom/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Arquivos de mídia
    location /media/ {
        alias /opt/seprom/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Proxy para o Django
    location / {
        proxy_pass http://unix:/opt/seprom/seprom.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Configurações de segurança
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
EOF

# Remover configuração padrão do Nginx
sudo rm -f /etc/nginx/conf.d/default.conf

# Iniciar serviços
echo "Iniciando serviços..."
sudo systemctl daemon-reload
sudo systemctl enable seprom
sudo systemctl start seprom
sudo systemctl enable nginx
sudo systemctl start nginx

# Configurar firewall
echo "Configurando firewall..."
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload

echo "=== DEPLOY CONCLUÍDO ==="
echo "Sistema disponível em: http://18.230.255.20"
echo "Para verificar status: sudo systemctl status seprom"
echo "Para ver logs: sudo journalctl -u seprom -f"
echo "Para configurar SSL manualmente: sudo dnf install -y certbot python3-certbot-nginx"
echo "Depois: sudo certbot --nginx -d sysprom.cbmepi.gov.br" 