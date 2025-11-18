#!/bin/bash

# Script de Deploy para Servidor Linux - SEPROM CBMEPI
# Execute como: chmod +x deploy_linux.sh && ./deploy_linux.sh

echo "🚀 Iniciando deploy do SEPROM CBMEPI em servidor Linux..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ Não execute este script como root!${NC}"
   exit 1
fi

# Atualizar sistema
echo -e "${YELLOW}📦 Atualizando sistema...${NC}"
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
echo -e "${YELLOW}🔧 Instalando dependências do sistema...${NC}"
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl wget unzip

# Instalar Node.js (para build de assets se necessário)
echo -e "${YELLOW}📦 Instalando Node.js...${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Criar usuário para a aplicação
echo -e "${YELLOW}👤 Criando usuário para aplicação...${NC}"
sudo useradd -m -s /bin/bash seprom
sudo usermod -aG sudo seprom

# Configurar PostgreSQL
echo -e "${YELLOW}🗄️ Configurando PostgreSQL...${NC}"
sudo -u postgres createuser seprom
sudo -u postgres createdb seprom_db
sudo -u postgres psql -c "ALTER USER seprom PASSWORD 'senha_segura_aqui';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE seprom_db TO seprom;"

# Mudar para usuário seprom
sudo su - seprom << 'EOF'

# Clonar repositório (substitua pela URL do seu repo)
echo "📥 Clonando repositório..."
git clone https://github.com/seu-usuario/sepromcbmepi.git
cd sepromcbmepi

# Criar ambiente virtual
echo "🐍 Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements_production.txt

# Configurar variáveis de ambiente
echo "⚙️ Configurando variáveis de ambiente..."
cp env_example.txt .env
# Edite o arquivo .env com suas configurações reais

# Executar migrações
echo "🔄 Executando migrações..."
python manage.py migrate

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Criar superusuário
echo "👑 Criando superusuário..."
python manage.py createsuperuser

# Testar aplicação
echo "🧪 Testando aplicação..."
python manage.py check

EOF

# Configurar Gunicorn
echo -e "${YELLOW}🔧 Configurando Gunicorn...${NC}"
sudo tee /etc/systemd/system/seprom.service > /dev/null <<EOF
[Unit]
Description=SEPROM CBMEPI Gunicorn daemon
After=network.target

[Service]
User=seprom
Group=www-data
WorkingDirectory=/home/seprom/sepromcbmepi
Environment="PATH=/home/seprom/sepromcbmepi/venv/bin"
ExecStart=/home/seprom/sepromcbmepi/venv/bin/gunicorn --workers 3 --bind unix:/home/seprom/sepromcbmepi/seprom.sock sepromcbmepi.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
echo -e "${YELLOW}🌐 Configurando Nginx...${NC}"
sudo tee /etc/nginx/sites-available/seprom > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/seprom/sepromcbmepi;
    }
    
    location /media/ {
        root /home/seprom/sepromcbmepi;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/seprom/sepromcbmepi/seprom.sock;
    }
}
EOF

# Ativar site e reiniciar serviços
echo -e "${YELLOW}🔄 Ativando serviços...${NC}"
sudo ln -s /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl daemon-reload
sudo systemctl start seprom
sudo systemctl enable seprom
sudo systemctl restart nginx

# Configurar firewall
echo -e "${YELLOW}🔥 Configurando firewall...${NC}"
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable

# Verificar status
echo -e "${YELLOW}📊 Verificando status dos serviços...${NC}"
sudo systemctl status seprom --no-pager -l
sudo systemctl status nginx --no-pager -l

echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}"
echo -e "${GREEN}🌐 Acesse: http://$(curl -s ifconfig.me)${NC}"
echo -e "${YELLOW}📝 Lembre-se de:${NC}"
echo -e "${YELLOW}   1. Editar o arquivo .env com suas configurações reais${NC}"
echo -e "${YELLOW}   2. Configurar SSL/HTTPS${NC}"
echo -e "${YELLOW}   3. Configurar backup do banco de dados${NC}"
echo -e "${YELLOW}   4. Monitorar logs: sudo journalctl -u seprom -f${NC}"
