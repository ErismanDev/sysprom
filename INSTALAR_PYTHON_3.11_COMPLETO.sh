#!/bin/bash
# Instalação completa do Python 3.11.7 do código fonte
# Para Ubuntu 24.04 no Digital Ocean

set -e  # Parar em caso de erro

echo "🚀 Iniciando instalação do Python 3.11.7 do código fonte..."

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências de compilação
echo "📦 Instalando dependências de compilação..."
sudo apt install -y build-essential zlib1g-dev libncurses5-dev \
    libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev \
    libsqlite3-dev libbz2-dev liblzma-dev wget

# Limpar instalações anteriores (se houver)
cd /tmp
rm -rf Python-3.11.7 Python-3.11.7.tgz

# Baixar Python 3.11.7
echo "📥 Baixando Python 3.11.7..."
wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz

# Extrair
echo "📂 Extraindo arquivos..."
tar -xzf Python-3.11.7.tgz
cd Python-3.11.7

# Configurar
echo "⚙️ Configurando Python 3.11.7..."
echo "⏳ Isso pode levar alguns minutos..."
./configure --enable-optimizations --with-ensurepip=install \
    --prefix=/usr/local --enable-shared

# Compilar
echo "🔨 Compilando Python 3.11.7..."
echo "⏳ Isso pode levar 5-10 minutos, por favor aguarde..."
make -j $(nproc)

# Instalar
echo "📦 Instalando Python 3.11.7..."
sudo make altinstall

# Atualizar bibliotecas do sistema
echo "🔗 Atualizando bibliotecas..."
sudo ldconfig

# Instalar/atualizar pip
echo "📦 Configurando pip..."
/usr/local/bin/python3.11 -m ensurepip --upgrade || \
    curl -sS https://bootstrap.pypa.io/get-pip.py | /usr/local/bin/python3.11

# Atualizar pip
/usr/local/bin/python3.11 -m pip install --upgrade pip setuptools wheel

# Verificar instalação
echo ""
echo "✅ Verificando instalação..."
echo "Python versão:"
/usr/local/bin/python3.11 --version

echo ""
echo "Pip versão:"
/usr/local/bin/python3.11 -m pip --version

echo ""
echo "✅ Python 3.11.7 instalado com sucesso!"
echo "📍 Localização: /usr/local/bin/python3.11"
echo "📍 Use: /usr/local/bin/python3.11 -m venv nome_venv"
echo ""
echo "💡 Para usar 'python3.11' diretamente, adicione ao PATH:"
echo "   export PATH=\"/usr/local/bin:\$PATH\""

