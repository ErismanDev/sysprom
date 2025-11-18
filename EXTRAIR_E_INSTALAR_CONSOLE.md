# 📦 Extrair ZIP e Instalar Sistema - Console Digital Ocean

**IP:** 64.23.185.235

## 🔍 ETAPA 1: Localizar e Verificar o Arquivo ZIP

Execute no console do Digital Ocean:

```bash
# Verificar se o arquivo ZIP existe
ls -lh /root/*.zip
ls -lh /home/seprom/*.zip
ls -lh /tmp/*.zip

# Ou procurar em todo o sistema
find / -name "*.zip" -type f 2>/dev/null | head -10
```

---

## 📋 ETAPA 2: Criar Diretório e Extrair ZIP

```bash
# Criar usuário seprom (se não existir)
sudo useradd -m -s /bin/bash seprom 2>/dev/null || echo "Usuário já existe"

# Criar diretório da aplicação
sudo mkdir -p /home/seprom/sepromcbmepi
sudo chown -R seprom:seprom /home/seprom/sepromcbmepi

# Ir para o diretório (como root primeiro)
cd /home/seprom/sepromcbmepi

# Se o ZIP estiver em /root, copiar para o diretório
# (Substitua nome_do_arquivo.zip pelo nome real do seu arquivo)
sudo cp /root/*.zip /home/seprom/sepromcbmepi/ 2>/dev/null || \
sudo cp /tmp/*.zip /home/seprom/sepromcbmepi/ 2>/dev/null || \
echo "Localize o arquivo ZIP primeiro"

# Listar arquivos ZIP no diretório
ls -lh *.zip

# Extrair ZIP (substitua pelo nome real do arquivo)
# Exemplo: unzip sepromcbmepi.zip ou unzip Sysgabom.zip
unzip *.zip

# Ou se tiver nome específico:
# unzip nome_do_arquivo.zip

# Verificar conteúdo extraído
ls -la
```

---

## ⚡ COMANDO ÚNICO - Extração Completa

Copie e cole tudo de uma vez (ajuste o nome do arquivo ZIP):

```bash
# Criar estrutura
sudo useradd -m -s /bin/bash seprom 2>/dev/null || true
sudo mkdir -p /home/seprom/sepromcbmepi
sudo chown -R seprom:seprom /home/seprom/sepromcbmepi

# Encontrar e copiar ZIP
ZIP_FILE=$(find /root /home /tmp -name "*.zip" -type f 2>/dev/null | head -1)
if [ -n "$ZIP_FILE" ]; then
    echo "📦 Arquivo ZIP encontrado: $ZIP_FILE"
    sudo cp "$ZIP_FILE" /home/seprom/sepromcbmepi/
    cd /home/seprom/sepromcbmepi
    sudo unzip -q *.zip
    sudo chown -R seprom:seprom /home/seprom/sepromcbmepi
    echo "✅ Arquivo extraído com sucesso!"
    ls -la
else
    echo "❌ Arquivo ZIP não encontrado. Verifique onde você enviou."
    echo "Procure manualmente: find / -name '*.zip' 2>/dev/null"
fi
```

---

## 📋 ETAPA 3: Verificar Estrutura Extraída

```bash
cd /home/seprom/sepromcbmepi

# Verificar se manage.py existe
ls -la manage.py

# Verificar estrutura de pastas
ls -la

# Verificar se requirements.txt existe
ls -la requirements*.txt

# Ver estrutura completa
tree -L 2 2>/dev/null || find . -maxdepth 2 -type d
```

---

## 📋 ETAPA 4: Ajustar Permissões

```bash
# Ajustar proprietário
sudo chown -R seprom:seprom /home/seprom/sepromcbmepi

# Ajustar permissões
sudo chmod -R 755 /home/seprom/sepromcbmepi
sudo chmod +x /home/seprom/sepromcbmepi/manage.py

# Criar diretórios necessários
sudo -u seprom mkdir -p /home/seprom/sepromcbmepi/{logs,media,staticfiles}
sudo chmod -R 755 /home/seprom/sepromcbmepi/{logs,media,staticfiles}
```

---

## 📋 ETAPA 5: Instalar Python 3.11 (se ainda não instalado)

```bash
# Verificar se Python 3.11 está instalado
python3.11 --version || /usr/local/bin/python3.11 --version

# Se não estiver, instalar (isso leva alguns minutos)
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

## 📋 ETAPA 6: Criar Ambiente Virtual e Instalar Dependências

```bash
# Mudar para usuário seprom
sudo su - seprom

# Ir para o diretório
cd /home/seprom/sepromcbmepi

# Verificar Python disponível
which python3.11 || which /usr/local/bin/python3.11

# Criar ambiente virtual
python3.11 -m venv venv 2>/dev/null || \
/usr/local/bin/python3.11 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Verificar versão do Python no venv
python --version

# Atualizar pip
pip install --upgrade pip setuptools wheel

# Instalar dependências
pip install -r requirements_production.txt

# Verificar instalação
pip list | head -20
```

---

## 📋 ETAPA 7: Configurar Banco de Dados

```bash
# Ainda como usuário seprom, com venv ativado

# Instalar PostgreSQL (se não estiver instalado)
sudo apt install -y postgresql postgresql-contrib

# Configurar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar usuário e banco (como root)
exit  # Sair do usuário seprom
sudo -u postgres psql << EOF
CREATE USER seprom WITH PASSWORD 'Seprom2024!@#';
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
ALTER USER seprom CREATEDB;
\q
EOF

# Voltar para usuário seprom
sudo su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate
```

---

## 📋 ETAPA 8: Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
cat > .env << 'EOF'
SECRET_KEY=ALTERE-ESTA-CHAVE-GERE-UMA-NOVA-AQUI
DEBUG=False
ALLOWED_HOSTS=64.23.185.235
DATABASE_NAME=sepromcbmepi
DATABASE_USER=seprom
DATABASE_PASSWORD=Seprom2024!@#
DATABASE_HOST=localhost
DATABASE_PORT=5432
EOF

# Gerar SECRET_KEY segura
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo "SECRET_KEY gerada: $SECRET_KEY"

# Atualizar .env com a chave gerada
sed -i "s/ALTERE-ESTA-CHAVE-GERE-UMA-NOVA-AQUI/$SECRET_KEY/" .env

# Verificar .env
cat .env
```

---

## 📋 ETAPA 9: Executar Migrações e Coletar Estáticos

```bash
# Ainda como seprom, com venv ativado

# Executar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar superusuário
python manage.py createsuperuser
# (Siga as instruções na tela)
```

---

## 📋 ETAPA 10: Configurar Gunicorn

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

# Recarregar systemd
sudo systemctl daemon-reload

# Iniciar serviço
sudo systemctl start seprom
sudo systemctl enable seprom

# Verificar status
sudo systemctl status seprom
```

---

## 📋 ETAPA 11: Configurar Nginx

```bash
# Instalar Nginx (se não estiver instalado)
sudo apt install -y nginx

# Copiar configuração
sudo cp /home/seprom/sepromcbmepi/nginx_seprom.conf /etc/nginx/sites-available/seprom

# Editar configuração (ajustar caminhos se necessário)
sudo nano /etc/nginx/sites-available/seprom

# Ativar site
sudo ln -s /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx

# Verificar status
sudo systemctl status nginx
```

---

## 📋 ETAPA 12: Configurar Firewall

```bash
# Permitir SSH
sudo ufw allow OpenSSH

# Permitir HTTP e HTTPS
sudo ufw allow 'Nginx Full'

# Ativar firewall
sudo ufw --force enable

# Verificar
sudo ufw status
```

---

## ✅ VERIFICAÇÃO FINAL

```bash
# Verificar serviços
sudo systemctl status seprom
sudo systemctl status nginx
sudo systemctl status postgresql

# Verificar logs
sudo journalctl -u seprom -n 50
sudo tail -n 50 /var/log/nginx/seprom_error.log

# Testar aplicação
curl http://localhost
curl http://64.23.185.235
```

---

## 🚀 COMANDO COMPLETO - Tudo de Uma Vez

**ATENÇÃO:** Execute passo a passo, não tudo de uma vez. Este é apenas um guia de referência.

```bash
# 1. Extrair ZIP
sudo useradd -m -s /bin/bash seprom 2>/dev/null || true
sudo mkdir -p /home/seprom/sepromcbmepi
ZIP_FILE=$(find /root /home /tmp -name "*.zip" -type f 2>/dev/null | head -1)
sudo cp "$ZIP_FILE" /home/seprom/sepromcbmepi/ && \
cd /home/seprom/sepromcbmepi && \
sudo unzip -q *.zip && \
sudo chown -R seprom:seprom /home/seprom/sepromcbmepi && \
sudo chmod -R 755 /home/seprom/sepromcbmepi && \
echo "✅ ZIP extraído!"

# 2. Continuar com instalação Python, venv, etc...
```

---

## 🆘 Troubleshooting

### Arquivo ZIP não encontrado
```bash
# Procurar em todos os lugares
find / -name "*.zip" -type f 2>/dev/null

# Verificar diretório home do root
ls -la /root/

# Verificar diretório atual
pwd
ls -la
```

### Erro ao extrair
```bash
# Instalar unzip se necessário
sudo apt install -y unzip

# Tentar extrair manualmente
unzip -l nome_do_arquivo.zip  # Listar conteúdo
unzip nome_do_arquivo.zip      # Extrair
```

### Permissões negadas
```bash
# Ajustar todas as permissões
sudo chown -R seprom:seprom /home/seprom/sepromcbmepi
sudo chmod -R 755 /home/seprom/sepromcbmepi
```

---

## 📝 Checklist de Instalação

- [ ] ZIP localizado e extraído
- [ ] Estrutura de pastas verificada
- [ ] Permissões ajustadas
- [ ] Python 3.11 instalado
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] Banco de dados configurado
- [ ] Arquivo .env criado
- [ ] Migrações executadas
- [ ] Arquivos estáticos coletados
- [ ] Superusuário criado
- [ ] Gunicorn configurado e rodando
- [ ] Nginx configurado e rodando
- [ ] Firewall configurado
- [ ] Aplicação acessível

---

## 🎯 Próximos Passos Após Instalação

1. Acessar aplicação: http://64.23.185.235
2. Fazer login com superusuário criado
3. Configurar SSL/HTTPS (Let's Encrypt)
4. Configurar backup automático
5. Monitorar logs: `sudo journalctl -u seprom -f`

