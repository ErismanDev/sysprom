#!/bin/bash

# Script de Deploy Personalizado - SEPROM CBMEPI
# Dom�nio: sysprom.cbmepi.gov.br
# Reposit�rio: https://github.com/ErismanDev/sysprom.git

set -e

echo "=== INICIANDO DEPLOY DO SISTEMA SEPROM CBMEPI ==="
echo "Dom�nio: sysprom.cbmepi.gov.br"
echo "IP: 18.230.255.20"

# Atualizar sistema
echo "Atualizando sistema..."
sudo apt update
sudo apt upgrade -y

# Instalar depend�ncias
echo "Instalando depend�ncias..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl

# Criar usu�rio para o aplicativo
echo "Criando usu�rio para o aplicativo..."
sudo useradd -m -s /bin/bash seprom || true
sudo usermod -aG sudo seprom

# Configurar PostgreSQL
echo "Configurando PostgreSQL..."
sudo -u postgres createuser --interactive --pwprompt seprom || true
sudo -u postgres createdb seprom_db || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE seprom_db TO seprom;"

# Criar diret�rio do projeto
echo "Criando diret�rio do projeto..."
sudo mkdir -p /opt/seprom
sudo chown seprom:seprom /opt/seprom

# Clonar reposit�rio
echo "Clonando reposit�rio..."
cd /opt/seprom
sudo -u seprom git clone https://github.com/ErismanDev/sysprom.git . || (sudo -u seprom git pull)

# Configurar ambiente virtual
echo "Configurando ambiente virtual..."
sudo -u seprom python3 -m venv venv
sudo -u seprom /opt/seprom/venv/bin/pip install --upgrade pip
sudo -u seprom /opt/seprom/venv/bin/pip install -r requirements.txt

# Copiar arquivo .env
echo "Configurando vari�veis de ambiente..."
sudo -u seprom cp .env /opt/seprom/.env

# Configurar Django
echo "Configurando Django..."
cd /opt/seprom
sudo -u seprom /opt/seprom/venv/bin/python manage.py collectstatic --noinput
sudo -u seprom /opt/seprom/venv/bin/python manage.py migrate
sudo -u seprom /opt/seprom/venv/bin/python manage.py createsuperuser --noinput --username admin --email admin@sysprom.cbmepi.gov.br || true

# Configurar Gunicorn
echo "Configurando Gunicorn..."
sudo -u seprom /opt/seprom/venv/bin/pip install gunicorn

# Copiar arquivo de servi�o
sudo cp seprom.service /etc/systemd/system/

# Copiar configura��o do Nginx
sudo cp nginx_seprom.conf /etc/nginx/sites-available/seprom

# Ativar site
sudo ln -sf /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Configurar SSL
echo "Configurando SSL..."
sudo apt install -y certbot python3-certbot-nginx

# Iniciar servi�os
echo "Iniciando servi�os..."
sudo systemctl daemon-reload
sudo systemctl enable seprom
sudo systemctl start seprom
sudo systemctl restart nginx

# Configurar firewall
echo "Configurando firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable

# Configurar SSL com Certbot
echo "Configurando certificado SSL..."
sudo certbot --nginx -d sysprom.cbmepi.gov.br -d www.sysprom.cbmepi.gov.br --non-interactive --agree-tos --email admin@sysprom.cbmepi.gov.br

echo "=== DEPLOY CONCLU�DO ==="
echo "Sistema dispon�vel em: https://sysprom.cbmepi.gov.br"
echo "Para verificar status: sudo systemctl status seprom"
echo "Para ver logs: sudo journalctl -u seprom -f"
