# 🚀 COMANDOS RÁPIDOS - Digital Ocean Console

**IP:** 64.23.185.235

## ⚡ COMANDO ÚNICO - Preparação Completa

Copie e cole tudo de uma vez no console do Digital Ocean:

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências para compilação Python
sudo apt install -y software-properties-common build-essential zlib1g-dev \
    libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev \
    libffi-dev libsqlite3-dev wget libbz2-dev

# Adicionar repositório para Python 3.11 (se necessário)
sudo add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null || echo "Repositório já existe ou não disponível"

# Atualizar após adicionar repositório
sudo apt update

# Instalar Python 3.11 e ferramentas
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Instalar pip para Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
python3.11 -m pip install --upgrade pip setuptools wheel

# Verificar instalação Python 3.11
python3.11 --version
python3.11 -m pip --version

# Instalar outras dependências do sistema
sudo apt install -y postgresql postgresql-contrib nginx git curl wget unzip \
    libpq-dev libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev \
    libopenjp2-7 libtiff5-dev

# Configurar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres psql -c "CREATE USER seprom WITH PASSWORD 'Seprom2024!@#';"
sudo -u postgres psql -c "CREATE DATABASE sepromcbmepi OWNER seprom;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;"
sudo -u postgres psql -c "ALTER USER seprom CREATEDB;"

# Criar usuário e diretórios
sudo useradd -m -s /bin/bash seprom 2>/dev/null || true
sudo usermod -aG sudo seprom
sudo mkdir -p /home/seprom/sepromcbmepi/{logs,media,staticfiles}
sudo chown -R seprom:seprom /home/seprom/sepromcbmepi
sudo chmod -R 755 /home/seprom/sepromcbmepi

# Configurar firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "✅ Preparação concluída! Agora envie os arquivos via WinSCP para: /home/seprom/sepromcbmepi/"
```

---

## 📤 APÓS ENVIAR ARQUIVOS VIA WINSCP

Execute estes comandos após enviar todos os arquivos:

```bash
# Mudar para usuário seprom
sudo su - seprom

# Ir para o diretório
cd /home/seprom/sepromcbmepi

# Criar venv com Python 3.11
python3.11 -m venv venv

# Ativar venv
source venv/bin/activate

# Verificar versão do Python no venv (deve ser 3.11.x)
python --version

# Atualizar pip
pip install --upgrade pip setuptools wheel

# Instalar dependências
pip install -r requirements_production.txt

# Criar arquivo .env (você edita depois)
cat > .env << 'EOF'
SECRET_KEY=ALTERE-ESTA-CHAVE-GERE-UMA-NOVA
DEBUG=False
ALLOWED_HOSTS=64.23.185.235
DATABASE_NAME=sepromcbmepi
DATABASE_USER=seprom
DATABASE_PASSWORD=Seprom2024!@#
DATABASE_HOST=localhost
DATABASE_PORT=5432
EOF

# Migrações e static
python manage.py migrate
python manage.py collectstatic --noinput

# Criar superusuário (siga as instruções)
python manage.py createsuperuser

# Sair do usuário seprom
exit
```

---

## 🔧 CONFIGURAR SERVIÇOS (como root)

```bash
# Criar serviço Gunicorn
sudo tee /etc/systemd/system/seprom.service > /dev/null << 'EOF'
[Unit]
Description=SEPROM CBMEPI Gunicorn daemon
After=network.target

[Service]
User=seprom
Group=www-data
WorkingDirectory=/home/seprom/sepromcbmepi
Environment="PATH=/home/seprom/sepromcbmepi/venv/bin"
ExecStart=/home/seprom/sepromcbmepi/venv/bin/gunicorn \
    --config /home/seprom/sepromcbmepi/gunicorn.conf.py \
    sepromcbmepi.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
sudo cp /home/seprom/sepromcbmepi/nginx_seprom.conf /etc/nginx/sites-available/seprom
sudo ln -s /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Testar e iniciar
sudo nginx -t
sudo systemctl daemon-reload
sudo systemctl start seprom
sudo systemctl enable seprom
sudo systemctl restart nginx

# Verificar status
sudo systemctl status seprom
sudo systemctl status nginx
```

---

## 🔑 GERAR SECRET_KEY

```bash
sudo su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copie a chave gerada e cole no arquivo `.env` substituindo `ALTERE-ESTA-CHAVE-GERE-UMA-NOVA`

---

## 📋 VERIFICAÇÕES FINAIS

```bash
# Verificar serviços
sudo systemctl status seprom
sudo systemctl status nginx
sudo systemctl status postgresql

# Verificar logs
sudo journalctl -u seprom -n 50
sudo tail -n 50 /var/log/nginx/seprom_error.log

# Testar acesso
curl http://localhost
```

---

## 🆘 COMANDOS DE TROUBLESHOOTING

```bash
# Reiniciar tudo
sudo systemctl restart seprom
sudo systemctl restart nginx

# Ver processos
ps aux | grep gunicorn

# Verificar permissões
ls -la /home/seprom/sepromcbmepi/
ls -la /home/seprom/sepromcbmepi/seprom.sock

# Testar banco
sudo -u postgres psql -d sepromcbmepi -c "SELECT 1;"
```

