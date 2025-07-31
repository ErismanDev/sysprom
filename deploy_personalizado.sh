#!/bin/bash

# Script de Deploy Personalizado - SEPROM CBMEPI
# Domínio: sysprom.cbmepi.gov.br
# Repositório: https://github.com/ErismanDev/sysprom.git

set -e

echo "=== INICIANDO DEPLOY DO SISTEMA SEPROM CBMEPI ==="
echo "Domínio: sysprom.cbmepi.gov.br"
echo "IP: 18.230.255.20"

# Atualizar sistema
echo "Atualizando sistema..."
sudo apt update
sudo apt upgrade -y

# Instalar dependências
echo "Instalando dependências..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl

# Criar usuário para o aplicativo
echo "Criando usuário para o aplicativo..."
sudo useradd -m -s /bin/bash seprom || true
sudo usermod -aG sudo seprom

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

# Copiar arquivo .env
echo "Configurando variáveis de ambiente..."
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

# Copiar arquivo de serviço
sudo cp seprom.service /etc/systemd/system/

# Copiar configuração do Nginx
sudo cp nginx_seprom.conf /etc/nginx/sites-available/seprom

# Ativar site
sudo ln -sf /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Configurar SSL
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

# Configurar SSL com Certbot
echo "Configurando certificado SSL..."
sudo certbot --nginx -d sysprom.cbmepi.gov.br -d www.sysprom.cbmepi.gov.br --non-interactive --agree-tos --email admin@sysprom.cbmepi.gov.br

echo "=== DEPLOY CONCLUÍDO ==="
echo "Sistema disponível em: https://sysprom.cbmepi.gov.br"
echo "Para verificar status: sudo systemctl status seprom"
echo "Para ver logs: sudo journalctl -u seprom -f"
