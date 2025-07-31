#!/bin/bash

# Script de Deploy - Sistema SEPROM CBMEPI
# Este script configura o ambiente completo no servidor

set -e  # Para o script se houver erro

echo "=== INICIANDO DEPLOY DO SISTEMA SEPROM CBMEPI ==="

# Atualizar sistema
echo "Atualizando sistema..."
sudo apt update
sudo apt upgrade -y

# Instalar dependências
echo "Instalando dependências..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl

# Criar usuário para o aplicativo
echo "Criando usuário para o aplicativo..."
sudo useradd -m -s /bin/bash seprom
sudo usermod -aG sudo seprom

# Configurar PostgreSQL
echo "Configurando PostgreSQL..."
sudo -u postgres createuser --interactive --pwprompt seprom
sudo -u postgres createdb seprom_db
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE seprom_db TO seprom;"

# Criar diretório do projeto
echo "Criando diretório do projeto..."
sudo mkdir -p /opt/seprom
sudo chown seprom:seprom /opt/seprom

# Clonar repositório (substitua pela URL do seu repositório)
echo "Clonando repositório..."
cd /opt/seprom
sudo -u seprom git clone https://github.com/seu-usuario/sepromcbmepi.git .

# Configurar ambiente virtual
echo "Configurando ambiente virtual..."
sudo -u seprom python3 -m venv venv
sudo -u seprom /opt/seprom/venv/bin/pip install --upgrade pip
sudo -u seprom /opt/seprom/venv/bin/pip install -r requirements.txt

# Configurar variáveis de ambiente
echo "Configurando variáveis de ambiente..."
sudo -u seprom tee /opt/seprom/.env > /dev/null <<EOF
DEBUG=False
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=postgresql://seprom:senha-do-banco@localhost/seprom_db
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com,18.230.255.20
STATIC_ROOT=/opt/seprom/staticfiles
MEDIA_ROOT=/opt/seprom/media
EOF

# Configurar Django
echo "Configurando Django..."
cd /opt/seprom
sudo -u seprom /opt/seprom/venv/bin/python manage.py collectstatic --noinput
sudo -u seprom /opt/seprom/venv/bin/python manage.py migrate
sudo -u seprom /opt/seprom/venv/bin/python manage.py createsuperuser --noinput --username admin --email admin@seu-dominio.com

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
ExecStart=/opt/seprom/venv/bin/gunicorn --workers 3 --bind unix:/opt/seprom/seprom.sock sepromcbmepi.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
echo "Configurando Nginx..."
sudo tee /etc/nginx/sites-available/seprom > /dev/null <<EOF
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com 18.230.255.20;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /opt/seprom;
    }

    location /media/ {
        root /opt/seprom;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/seprom/seprom.sock;
    }
}
EOF

# Ativar site
sudo ln -s /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled
sudo rm -f /etc/nginx/sites-enabled/default

# Configurar SSL (opcional - para HTTPS)
echo "Configurando SSL..."
sudo apt install -y certbot python3-certbot-nginx

# Iniciar serviços
echo "Iniciando serviços..."
sudo systemctl daemon-reload
sudo systemctl enable seprom
sudo systemctl start seprom
sudo systemctl restart nginx

# Configurar firewall
echo "Configurando firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable

echo "=== DEPLOY CONCLUÍDO ==="
echo "Sistema disponível em: http://18.230.255.20"
echo "Para configurar domínio, execute: sudo certbot --nginx -d seu-dominio.com"
echo "Para verificar status: sudo systemctl status seprom" 