#!/usr/bin/env python3
"""
Script de Configuração de Deploy - SEPROM CBMEPI
Este script gera os arquivos de configuração personalizados para o deploy
"""

import os
import secrets
import sys

def generate_secret_key():
    """Gera uma chave secreta segura para o Django"""
    return secrets.token_urlsafe(50)

def create_env_file(domain, db_password):
    """Cria o arquivo .env com as configurações"""
    secret_key = generate_secret_key()
    
    env_content = f"""# Configurações do Django
DEBUG=False
SECRET_KEY={secret_key}
DATABASE_URL=postgresql://seprom:{db_password}@localhost/seprom_db
ALLOWED_HOSTS={domain},www.{domain},18.230.255.20
STATIC_ROOT=/opt/seprom/staticfiles
MEDIA_ROOT=/opt/seprom/media

# Configurações de Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app

# Configurações AWS (se necessário)
AWS_ACCESS_KEY_ID=sua-access-key
AWS_SECRET_ACCESS_KEY=sua-secret-key
AWS_STORAGE_BUCKET_NAME=seu-bucket
AWS_S3_REGION_NAME=sa-east-1
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado com sucesso!")

def create_nginx_config(domain):
    """Cria a configuração do Nginx"""
    nginx_config = f"""server {{
    listen 80;
    server_name {domain} www.{domain} 18.230.255.20;

    # Logs
    access_log /var/log/nginx/seprom_access.log;
    error_log /var/log/nginx/seprom_error.log;

    # Favicon
    location = /favicon.ico {{ 
        access_log off; 
        log_not_found off; 
    }}
    
    # Arquivos estáticos
    location /static/ {{
        alias /opt/seprom/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}

    # Arquivos de mídia
    location /media/ {{
        alias /opt/seprom/media/;
        expires 30d;
        add_header Cache-Control "public";
    }}

    # Proxy para o Django
    location / {{
        include proxy_params;
        proxy_pass http://unix:/opt/seprom/seprom.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    # Configurações de segurança
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}}
"""
    
    with open('nginx_seprom.conf', 'w') as f:
        f.write(nginx_config)
    
    print("✅ Configuração do Nginx criada!")

def create_systemd_service():
    """Cria o arquivo de serviço do systemd"""
    service_content = """[Unit]
Description=SEPROM CBMEPI Gunicorn daemon
After=network.target

[Service]
User=seprom
Group=seprom
WorkingDirectory=/opt/seprom
Environment="PATH=/opt/seprom/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=sepromcbmepi.settings"
ExecStart=/opt/seprom/venv/bin/gunicorn --workers 3 --bind unix:/opt/seprom/seprom.sock --timeout 120 sepromcbmepi.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
"""
    
    with open('seprom.service', 'w') as f:
        f.write(service_content)
    
    print("✅ Arquivo de serviço systemd criado!")

def create_deploy_script(domain, repo_url):
    """Cria o script de deploy personalizado"""
    deploy_script = f"""#!/bin/bash

# Script de Deploy Personalizado - SEPROM CBMEPI
# Domínio: {domain}
# Repositório: {repo_url}

set -e

echo "=== INICIANDO DEPLOY DO SISTEMA SEPROM CBMEPI ==="
echo "Domínio: {domain}"
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
sudo -u seprom git clone {repo_url} . || (sudo -u seprom git pull)

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
sudo -u seprom /opt/seprom/venv/bin/python manage.py createsuperuser --noinput --username admin --email admin@{domain} || true

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
sudo certbot --nginx -d {domain} -d www.{domain} --non-interactive --agree-tos --email admin@{domain}

echo "=== DEPLOY CONCLUÍDO ==="
echo "Sistema disponível em: https://{domain}"
echo "Para verificar status: sudo systemctl status seprom"
echo "Para ver logs: sudo journalctl -u seprom -f"
"""
    
    with open('deploy_personalizado.sh', 'w') as f:
        f.write(deploy_script)
    
    # Tornar executável
    os.chmod('deploy_personalizado.sh', 0o755)
    print("✅ Script de deploy personalizado criado!")

def main():
    print("=== CONFIGURADOR DE DEPLOY - SEPROM CBMEPI ===")
    print()
    
    # Solicitar informações
    domain = input("Digite o domínio (ex: seprom.cbmepi.gov.br): ").strip()
    if not domain:
        print("❌ Domínio é obrigatório!")
        sys.exit(1)
    
    repo_url = input("Digite a URL do repositório Git: ").strip()
    if not repo_url:
        repo_url = "https://github.com/seu-usuario/sepromcbmepi.git"
    
    db_password = input("Digite a senha do banco de dados (ou pressione Enter para gerar): ").strip()
    if not db_password:
        db_password = secrets.token_urlsafe(16)
    
    print(f"\n📋 Configurações:")
    print(f"   Domínio: {domain}")
    print(f"   Repositório: {repo_url}")
    print(f"   Senha do banco: {db_password}")
    print()
    
    # Criar arquivos
    create_env_file(domain, db_password)
    create_nginx_config(domain)
    create_systemd_service()
    create_deploy_script(domain, repo_url)
    
    print("\n🎉 Configuração concluída!")
    print("\n📁 Arquivos criados:")
    print("   - .env (variáveis de ambiente)")
    print("   - nginx_seprom.conf (configuração do Nginx)")
    print("   - seprom.service (serviço systemd)")
    print("   - deploy_personalizado.sh (script de deploy)")
    print()
    print("🚀 Para fazer o deploy:")
    print("   1. Faça commit dos arquivos no Git")
    print("   2. Execute: ./deploy_personalizado.sh")
    print("   3. Configure o DNS para apontar para 18.230.255.20")

if __name__ == "__main__":
    main() 