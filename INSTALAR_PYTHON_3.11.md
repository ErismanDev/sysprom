# 🐍 Instalar Python 3.11 no Digital Ocean (Ubuntu/Debian)

**IP:** 64.23.185.235

## ⚡ COMANDO COMPLETO - Instalação Python 3.11

Copie e cole tudo de uma vez no console do Digital Ocean:

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências necessárias
sudo apt install -y software-properties-common build-essential zlib1g-dev \
    libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev \
    libffi-dev libsqlite3-dev wget libbz2-dev

# Adicionar repositório deadsnakes (para Python 3.11)
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Se não estiver disponível, instalar de fonte alternativa
sudo add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null || \
    (echo "Repositório não disponível, usando instalação direta")

# Atualizar após adicionar repositório
sudo apt update

# Instalar Python 3.11 e ferramentas
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Instalar pip para Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Verificar instalação
python3.11 --version
python3.11 -m pip --version

# Criar link simbólico (opcional, se quiser usar python3.11 como python3)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Verificar
python3 --version

echo "✅ Python 3.11 instalado com sucesso!"
```

---

## 🔄 ALTERNATIVA: Instalação Manual (se o método acima falhar)

Se o repositório não funcionar, use esta alternativa:

```bash
# Baixar e compilar Python 3.11 do código fonte
cd /tmp
wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz
tar -xzf Python-3.11.7.tgz
cd Python-3.11.7

# Configurar e compilar
./configure --enable-optimizations --with-ensurepip=install
make -j $(nproc)
sudo make altinstall

# Verificar
python3.11 --version
python3.11 -m pip --version
```

---

## ✅ VERIFICAÇÃO PÓS-INSTALAÇÃO

```bash
# Verificar versão
python3.11 --version
# Deve mostrar: Python 3.11.x

# Verificar pip
python3.11 -m pip --version

# Testar criação de ambiente virtual
python3.11 -m venv /tmp/test_venv
rm -rf /tmp/test_venv
echo "✅ Ambiente virtual funciona!"
```

---

## 🔧 CONFIGURAR PARA USO COM O PROJETO

```bash
# Garantir que o usuário seprom pode usar Python 3.11
sudo su - seprom
python3.11 --version
python3.11 -m pip --version
exit

# Se necessário, instalar pip novamente para o usuário
sudo -u seprom python3.11 -m ensurepip --upgrade
```

---

## 📝 NOTAS IMPORTANTES

1. **Não remova Python 3.10 ou 3.9** se já estiver instalado - o sistema pode depender dele
2. **Use `python3.11` explicitamente** nos comandos para garantir a versão correta
3. **Ambientes virtuais** criados com `python3.11 -m venv` usarão Python 3.11 automaticamente

---

## 🆘 TROUBLESHOOTING

### Problema: "python3.11: command not found"

```bash
# Verificar se está instalado
which python3.11
ls -la /usr/bin/python3.11

# Se não existir, reinstalar
sudo apt install --reinstall python3.11
```

### Problema: "pip não encontrado"

```bash
# Instalar pip manualmente
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
python3.11 -m pip install --upgrade pip
```

### Problema: "módulo não encontrado após instalação"

```bash
# Garantir que está usando o pip correto
python3.11 -m pip install nome-do-modulo
```

