# 🚀 Continuar Instalação - Após Extrair ZIP

## ✅ Status Atual
- ✅ ZIP extraído
- ✅ manage.py existe
- ✅ Estrutura de pastas criada

## 📋 ETAPA 1: Verificar Estrutura e Arquivos

```bash
cd /home/seprom/sepromcbmepi

# Verificar arquivos principais
ls -la manage.py requirements*.txt gunicorn.conf.py nginx_seprom.conf

# Verificar pastas importantes
ls -d sepromcbmepi/ militares/ templates/ static/ 2>/dev/null

# Verificar se requirements existe
[ -f "requirements_production.txt" ] && echo "✅ requirements_production.txt existe" || echo "❌ requirements_production.txt não encontrado"
[ -f "requirements.txt" ] && echo "✅ requirements.txt existe" || echo "❌ requirements.txt não encontrado"
```

---

## 📋 ETAPA 2: Ajustar Permissões Finais

```bash
# Ajustar todas as permissões
sudo chown -R seprom:seprom /home/seprom/sepromcbmepi
sudo chmod -R 755 /home/seprom/sepromcbmepi
sudo chmod +x manage.py

# Criar diretórios necessários
sudo -u seprom mkdir -p /home/seprom/sepromcbmepi/{logs,media,staticfiles}
sudo chmod -R 755 /home/seprom/sepromcbmepi/{logs,media,staticfiles}
```

---

## 📋 ETAPA 3: Verificar Python 3.11

```bash
# Verificar se Python 3.11 está disponível
python3.11 --version || /usr/local/bin/python3.11 --version

# Se não estiver instalado, instalar (leva alguns minutos)
if ! command -v python3.11 &> /dev/null && [ ! -f /usr/local/bin/python3.11 ]; then
    echo "📦 Instalando Python 3.11.7..."
    sudo apt update && \
    sudo apt install -y build-essential zlib1g-dev libncurses5-dev \
        libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev \
        libsqlite3-dev libbz2-dev liblzma-dev wget && \
    cd /tmp && \
    wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz && \
    tar -xzf Python-3.11.7.tgz && \
    cd Python-3.11.7 && \
    ./configure --enable-optimizations --with-ensurepip=install \
        --prefix=/usr/local --enable-shared && \
    make -j $(nproc) && \
    sudo make altinstall && \
    sudo ldconfig && \
    /usr/local/bin/python3.11 -m pip install --upgrade pip setuptools wheel
fi
```

---

## 📋 ETAPA 4: Criar Ambiente Virtual

```bash
# Mudar para usuário seprom
sudo su - seprom

# Ir para o diretório
cd /home/seprom/sepromcbmepi

# Verificar qual Python usar
PYTHON_CMD=$(which python3.11 2>/dev/null || echo "/usr/local/bin/python3.11")
echo "Usando: $PYTHON_CMD"
$PYTHON_CMD --version

# Criar ambiente virtual
$PYTHON_CMD -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Verificar versão do Python no venv
python --version

# Atualizar pip
pip install --upgrade pip setuptools wheel
```

---

## 📋 ETAPA 5: Instalar Dependências

```bash
# Ainda como seprom, com venv ativado

# Verificar qual arquivo de requirements usar
if [ -f "requirements_production.txt" ]; then
    REQUIREMENTS_FILE="requirements_production.txt"
elif [ -f "requirements.txt" ]; then
    REQUIREMENTS_FILE="requirements.txt"
else
    echo "❌ Nenhum arquivo requirements encontrado!"
    exit 1
fi

echo "📦 Instalando dependências de: $REQUIREMENTS_FILE"
pip install -r $REQUIREMENTS_FILE

# Verificar instalação
pip list | head -20
```

---

## 📋 ETAPA 6: Configurar Banco de Dados

```bash
# Sair do usuário seprom
exit

# Instalar PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar usuário e banco
sudo -u postgres psql << EOF
DROP USER IF EXISTS seprom;
CREATE USER seprom WITH PASSWORD 'Seprom2024!@#';
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
ALTER USER seprom CREATEDB;
\q
EOF

# Verificar se banco foi criado
sudo -u postgres psql -l | grep sepromcbmepi
```

---

## 📋 ETAPA 7: Configurar .env

```bash
# Voltar para usuário seprom
sudo su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate

# Gerar SECRET_KEY
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo "SECRET_KEY gerada: $SECRET_KEY"

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
```

---

## 📋 ETAPA 8: Executar Migrações

```bash
# Ainda como seprom, com venv ativado

# Verificar configuração Django
python manage.py check

# Executar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar superusuário
python manage.py createsuperuser
# (Siga as instruções na tela)
```

---

## 📋 ETAPA 9: Configurar Gunicorn

```bash
# Sair do usuário seprom
exit

# Criar serviço systemd
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

# Recarregar e iniciar
sudo systemctl daemon-reload
sudo systemctl start seprom
sudo systemctl enable seprom
sudo systemctl status seprom
```

---

## 📋 ETAPA 10: Configurar Nginx

```bash
# Instalar Nginx
sudo apt install -y nginx

# Copiar configuração
sudo cp /home/seprom/sepromcbmepi/nginx_seprom.conf /etc/nginx/sites-available/seprom

# Ativar site
sudo ln -s /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
sudo systemctl status nginx
```

---

## 📋 ETAPA 11: Configurar Firewall

```bash
# Permitir serviços
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Verificar
sudo ufw status
```

---

## ✅ VERIFICAÇÃO FINAL

```bash
# Verificar todos os serviços
sudo systemctl status seprom
sudo systemctl status nginx
sudo systemctl status postgresql

# Verificar logs
sudo journalctl -u seprom -n 50 --no-pager

# Testar aplicação
curl http://localhost
curl http://64.23.185.235
```

---

## 🚀 COMANDO RÁPIDO - Verificar Estrutura

```bash
cd /home/seprom/sepromcbmepi && \
echo "=== Arquivos principais ===" && \
ls -la manage.py requirements*.txt gunicorn.conf.py nginx_seprom.conf 2>/dev/null && \
echo "" && \
echo "=== Pastas ===" && \
ls -d sepromcbmepi/ militares/ templates/ static/ 2>/dev/null
```

