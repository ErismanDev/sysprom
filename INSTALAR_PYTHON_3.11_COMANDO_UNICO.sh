#!/bin/bash
# Comando único para instalar Python 3.11 no Digital Ocean
# Copie e cole tudo no console do Digital Ocean

echo "🚀 Iniciando instalação do Python 3.11..."

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências para compilação Python
sudo apt install -y software-properties-common build-essential zlib1g-dev \
    libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev \
    libffi-dev libsqlite3-dev wget libbz2-dev

# Tentar adicionar repositório deadsnakes
if ! sudo add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null; then
    echo "⚠️  Repositório ppa:deadsnakes/ppa não disponível, tentando instalação direta..."
fi

# Atualizar após adicionar repositório
sudo apt update

# Instalar Python 3.11 e ferramentas
echo "📦 Instalando Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Instalar pip para Python 3.11
echo "📦 Instalando pip para Python 3.11..."
if ! python3.11 -m pip --version 2>/dev/null; then
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
fi

# Atualizar pip
python3.11 -m pip install --upgrade pip setuptools wheel

# Verificar instalação
echo ""
echo "✅ Verificando instalação..."
echo "Python versão:"
python3.11 --version

echo ""
echo "Pip versão:"
python3.11 -m pip --version

echo ""
echo "✅ Python 3.11 instalado com sucesso!"
echo "📍 Use 'python3.11' para executar comandos Python"
echo "📍 Use 'python3.11 -m venv nome_venv' para criar ambientes virtuais"

