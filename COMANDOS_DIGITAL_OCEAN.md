# Comandos para Preparar Digital Ocean - SEPROM CBMEPI

**IP do Servidor:** 64.23.185.235

## 📋 ETAPA 1: Atualizar Sistema e Instalar Dependências Básicas

```bash
# Atualizar lista de pacotes
sudo apt update && sudo apt upgrade -y

# Instalar dependências essenciais
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip \
    postgresql postgresql-contrib nginx git curl wget unzip \
    build-essential libpq-dev libjpeg-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5-dev \
    libffi-dev libssl-dev
```

## 📋 ETAPA 2: Configurar PostgreSQL

```bash
# Iniciar e habilitar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar usuário e banco de dados
sudo -u postgres psql << EOF
CREATE USER seprom WITH PASSWORD 'SuaSenhaSegura123!';
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
ALTER USER seprom CREATEDB;
\q
EOF

# Verificar se foi criado
sudo -u postgres psql -l | grep sepromcbmepi
```

## 📋 ETAPA 3: Criar Usuário e Estrutura de Diretórios

```bash
# Criar usuário para a aplicação
sudo useradd -m -s /bin/bash seprom
sudo usermod -aG sudo seprom

# Criar diretório da aplicação
sudo mkdir -p /home/seprom/sepromcbmepi
sudo mkdir -p /home/seprom/sepromcbmepi/logs
sudo mkdir -p /home/seprom/sepromcbmepi/media
sudo mkdir -p /home/seprom/sepromcbmepi/staticfiles

# Definir proprietário
sudo chown -R seprom:seprom /home/seprom/sepromcbmepi

# Dar permissões
sudo chmod -R 755 /home/seprom/sepromcbmepi
```

## 📋 ETAPA 4: Configurar Firewall

```bash
# Verificar status do firewall
sudo ufw status

# Permitir SSH (IMPORTANTE - não feche a conexão!)
sudo ufw allow OpenSSH

# Permitir HTTP e HTTPS
sudo ufw allow 'Nginx Full'

# Ativar firewall
sudo ufw --force enable

# Verificar regras
sudo ufw status numbered
```

## 📋 ETAPA 5: Preparar para Receber Arquivos via WinSCP

```bash
# Garantir que o usuário seprom pode receber arquivos
sudo chown -R seprom:seprom /home/seprom

# Criar diretório .ssh se não existir (para chaves SSH)
sudo mkdir -p /home/seprom/.ssh
sudo chmod 700 /home/seprom/.ssh
sudo chown seprom:seprom /home/seprom/.ssh
```

## 📋 ETAPA 6: Verificar Configurações

```bash
# Verificar Python
python3.11 --version

# Verificar PostgreSQL
sudo systemctl status postgresql

# Verificar Nginx
sudo systemctl status nginx

# Verificar usuário
id seprom

# Verificar diretórios
ls -la /home/seprom/sepromcbmepi/
```

---

## 📤 APÓS ENVIAR ARQUIVOS VIA WINSCP

Após enviar todos os arquivos para `/home/seprom/sepromcbmepi/`, execute:

### 1. Criar Ambiente Virtual

```bash
# Fazer login como usuário seprom
sudo su - seprom

# Ir para o diretório do projeto
cd /home/seprom/sepromcbmepi

# Criar ambiente virtual
python3.11 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip setuptools wheel
```

### 2. Instalar Dependências Python

```bash
# Ainda com venv ativado
pip install -r requirements_production.txt
```

### 3. Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env (você precisará editar com suas configurações)
nano .env
```

**Conteúdo do .env:**
```
SECRET_KEY=sua-chave-secreta-aqui-gerada-aleatoriamente
DEBUG=False
ALLOWED_HOSTS=64.23.185.235,seu-dominio.com
DATABASE_NAME=sepromcbmepi
DATABASE_USER=seprom
DATABASE_PASSWORD=SuaSenhaSegura123!
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### 4. Executar Migrações

```bash
# Com venv ativado
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar superusuário
python manage.py createsuperuser
```

### 5. Configurar Gunicorn

```bash
# Criar arquivo de serviço systemd
sudo nano /etc/systemd/system/seprom.service
```

**Conteúdo do arquivo:**
```ini
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
```

### 6. Configurar Nginx

```bash
# Copiar configuração do projeto
sudo cp /home/seprom/sepromcbmepi/nginx_seprom.conf /etc/nginx/sites-available/seprom

# Editar para ajustar caminhos
sudo nano /etc/nginx/sites-available/seprom
```

**Ajustar no arquivo:**
- Verificar se os caminhos estão corretos: `/home/seprom/sepromcbmepi/`
- Se tiver domínio, substituir `server_name _;` por `server_name seu-dominio.com;`

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/

# Remover default se existir
sudo rm -f /etc/nginx/sites-enabled/default

# Testar configuração do Nginx
sudo nginx -t

# Se estiver OK, recarregar
sudo systemctl reload nginx
```

### 7. Iniciar Serviços

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Iniciar e habilitar serviço Gunicorn
sudo systemctl start seprom
sudo systemctl enable seprom

# Reiniciar Nginx
sudo systemctl restart nginx

# Verificar status
sudo systemctl status seprom
sudo systemctl status nginx
```

### 8. Verificar Logs

```bash
# Logs do Gunicorn
sudo journalctl -u seprom -f

# Logs do Nginx
sudo tail -f /var/log/nginx/seprom_error.log
sudo tail -f /var/log/nginx/seprom_access.log

# Logs do Gunicorn (arquivo)
tail -f /home/seprom/sepromcbmepi/logs/gunicorn_error.log
```

---

## 🔧 Comandos Úteis para Manutenção

```bash
# Reiniciar aplicação
sudo systemctl restart seprom

# Recarregar Nginx
sudo systemctl reload nginx

# Ver status dos serviços
sudo systemctl status seprom
sudo systemctl status nginx
sudo systemctl status postgresql

# Ver processos Gunicorn
ps aux | grep gunicorn

# Parar aplicação
sudo systemctl stop seprom

# Iniciar aplicação
sudo systemctl start seprom
```

---

## ⚠️ IMPORTANTE - Configurações de Segurança

1. **Altere a senha do PostgreSQL** no comando da ETAPA 2
2. **Gere uma SECRET_KEY** segura para o Django:
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```
3. **Configure ALLOWED_HOSTS** no .env com seu domínio/IP
4. **Desabilite DEBUG** em produção (DEBUG=False)
5. **Configure SSL/HTTPS** depois (Let's Encrypt)

---

## 📝 Notas

- **Usuário WinSCP:** root ou seprom (depende da configuração SSH)
- **Diretório destino:** `/home/seprom/sepromcbmepi/`
- **Porta SSH:** 22 (padrão)
- **Porta HTTP:** 80
- **Porta HTTPS:** 443 (após configurar SSL)

---

## 🆘 Em caso de problemas

```bash
# Verificar se o socket do Gunicorn foi criado
ls -la /home/seprom/sepromcbmepi/seprom.sock

# Verificar permissões
ls -la /home/seprom/sepromcbmepi/

# Verificar se o banco está acessível
sudo -u postgres psql -d sepromcbmepi -c "SELECT version();"

# Testar conexão Django com banco
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python manage.py dbshell
```

