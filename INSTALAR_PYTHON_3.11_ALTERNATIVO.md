# 🔧 Instalar Python 3.11 - Método Alternativo (Ubuntu 24.04)

O repositório ppa:deadsnakes não está funcionando. Vamos usar método alternativo.

## 📋 ETAPA 1: Verificar Python Atual

```bash
python3 --version
which python3
```

## 📋 ETAPA 2: Instalar Python 3.11 do Código Fonte

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências de compilação
sudo apt install -y build-essential zlib1g-dev libncurses5-dev \
    libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev \
    libsqlite3-dev libbz2-dev liblzma-dev

# Baixar Python 3.11.7 (versão estável)
cd /tmp
wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz

# Extrair
tar -xzf Python-3.11.7.tgz
cd Python-3.11.7

# Configurar (com otimizações)
./configure --enable-optimizations --with-ensurepip=install \
    --prefix=/usr/local --enable-shared

# Compilar (isso pode levar 5-10 minutos)
make -j $(nproc)

# Instalar
sudo make altinstall

# Criar link simbólico
sudo ln -sf /usr/local/bin/python3.11 /usr/local/bin/python3.11

# Atualizar bibliotecas
sudo ldconfig

# Verificar instalação
/usr/local/bin/python3.11 --version
/usr/local/bin/python3.11 -m pip --version
```

## 📋 ETAPA 3: Instalar pip se necessário

```bash
# Se pip não estiver instalado
/usr/local/bin/python3.11 -m ensurepip --upgrade

# Ou baixar get-pip.py
curl -sS https://bootstrap.pypa.io/get-pip.py | /usr/local/bin/python3.11

# Atualizar pip
/usr/local/bin/python3.11 -m pip install --upgrade pip setuptools wheel
```

## 📋 ETAPA 4: Verificar e Testar

```bash
# Verificar versão
/usr/local/bin/python3.11 --version

# Verificar pip
/usr/local/bin/python3.11 -m pip --version

# Testar criação de venv
/usr/local/bin/python3.11 -m venv /tmp/test_venv
/tmp/test_venv/bin/python --version
rm -rf /tmp/test_venv

echo "✅ Python 3.11 instalado em /usr/local/bin/python3.11"
```

## 📋 ETAPA 5: Criar Alias (Opcional)

```bash
# Adicionar ao PATH (temporário)
export PATH="/usr/local/bin:$PATH"

# Adicionar permanentemente ao .bashrc
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Agora você pode usar python3.11 diretamente
python3.11 --version
```

---

## ⚡ COMANDO ÚNICO COMPLETO

Copie e cole tudo de uma vez:

```bash
sudo apt update && sudo apt upgrade -y && \
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
/usr/local/bin/python3.11 -m pip install --upgrade pip setuptools wheel && \
echo "✅ Python 3.11 instalado!" && \
/usr/local/bin/python3.11 --version && \
/usr/local/bin/python3.11 -m pip --version
```

---

## 🔄 ALTERNATIVA: Usar Python 3.12 (já disponível no Ubuntu 24.04)

Se Python 3.11 não for estritamente necessário, você pode usar Python 3.12 que já vem no Ubuntu 24.04:

```bash
# Verificar se Python 3.12 está disponível
apt list python3.12* 2>/dev/null

# Instalar Python 3.12
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Verificar
python3.12 --version
```

---

## 📝 NOTAS IMPORTANTES

1. **Compilação leva tempo**: O comando `make -j $(nproc)` pode levar 5-10 minutos
2. **Uso de memória**: Certifique-se de ter pelo menos 1GB de RAM disponível
3. **Caminho**: Python 3.11 será instalado em `/usr/local/bin/python3.11`
4. **Não sobrescreve**: O Python 3.12 do sistema permanece intacto

---

## 🆘 TROUBLESHOOTING

### Erro: "make: command not found"
```bash
sudo apt install -y build-essential
```

### Erro: "configure: error"
```bash
# Instalar todas as dependências
sudo apt install -y build-essential zlib1g-dev libncurses5-dev \
    libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev \
    libsqlite3-dev libbz2-dev liblzma-dev libffi-dev
```

### Erro de memória durante compilação
```bash
# Compilar com menos processos (usa menos memória)
make -j 1
```

### Verificar se está instalado
```bash
ls -la /usr/local/bin/python3.11
/usr/local/bin/python3.11 --version
```

