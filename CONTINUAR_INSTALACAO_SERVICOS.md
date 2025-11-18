# 🚀 Continuar Instalação - Configurar Serviços

## 📋 ETAPA 1: Instalar PostgreSQL

```bash
# Como root
apt update
apt install -y postgresql postgresql-contrib
systemctl start postgresql
systemctl enable postgresql

# Verificar
systemctl status postgresql
```

---

## 📋 ETAPA 2: Criar Banco de Dados

```bash
# Criar usuário e banco
su - postgres -c "psql -c \"DROP USER IF EXISTS seprom;\""
su - postgres -c "psql -c \"CREATE USER seprom WITH PASSWORD 'Seprom2024!@#';\""
su - postgres -c "psql -c \"DROP DATABASE IF EXISTS sepromcbmepi;\""
su - postgres -c "psql -c \"CREATE DATABASE sepromcbmepi OWNER seprom;\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;\""
su - postgres -c "psql -c \"ALTER USER seprom CREATEDB;\""

# Verificar
su - postgres -c "psql -l" | grep sepromcbmepi
```

---

## 📋 ETAPA 3: Configurar .env e Executar Migrações

```bash
# Mudar para usuário seprom
su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate

# Gerar SECRET_KEY
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo "SECRET_KEY gerada"

# Criar arquivo .env
cat > .env << EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=64.23.185.235
DATABASE_NAME=sepromcbmepi
DATABASE_USER=seprom
DATABASE_PASSWORD=Seprom2024!@#
DATABASE_HOST=localhost
DATABASE_PORT=5432
EOF

# Verificar .env
cat .env

# Verificar configuração Django
python manage.py check

# Executar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar superusuário
python manage.py createsuperuser
```

---

## 📋 ETAPA 4: Configurar Gunicorn

```bash
# Sair do usuário seprom
exit

# Como root, criar serviço systemd
tee /etc/systemd/system/seprom.service > /dev/null << 'EOF'
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

# Recarregar systemd
systemctl daemon-reload

# Iniciar serviço
systemctl start seprom
systemctl enable seprom

# Verificar status
systemctl status seprom
```

---

## 📋 ETAPA 5: Instalar e Configurar Nginx

```bash
# Instalar Nginx
apt install -y nginx

# Copiar configuração
cp /home/seprom/sepromcbmepi/nginx_seprom.conf /etc/nginx/sites-available/seprom

# Ativar site
ln -s /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar configuração
nginx -t

# Iniciar Nginx
systemctl start nginx
systemctl enable nginx

# Verificar status
systemctl status nginx
```

---

## 📋 ETAPA 6: Configurar Firewall

```bash
# Permitir serviços
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Verificar
ufw status
```

---

## ✅ VERIFICAÇÃO FINAL

```bash
# Verificar todos os serviços
systemctl status seprom --no-pager -l
systemctl status nginx --no-pager -l
systemctl status postgresql --no-pager -l

# Ver logs
journalctl -u seprom -n 30 --no-pager

# Testar aplicação
curl http://localhost
curl http://64.23.185.235
```

---

## 🆘 Troubleshooting

### Se Gunicorn não iniciar
```bash
# Ver logs detalhados
journalctl -u seprom -n 50 --no-pager

# Verificar se arquivo de configuração existe
ls -la /home/seprom/sepromcbmepi/gunicorn.conf.py

# Testar manualmente
su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate
gunicorn --config gunicorn.conf.py sepromcbmepi.wsgi:application
```

### Se Nginx não iniciar
```bash
# Ver logs
tail -50 /var/log/nginx/error.log

# Testar configuração
nginx -t

# Verificar se socket existe
ls -la /home/seprom/sepromcbmepi/seprom.sock
```

