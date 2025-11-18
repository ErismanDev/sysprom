# 📦 Extrair Sysgabom.zip - Comandos Rápidos

## ⚡ COMANDO COMPLETO - Copiar e Extrair

Execute no console do Digital Ocean:

```bash
# Instalar unzip
sudo apt update && sudo apt install -y unzip

# Copiar ZIP do /root para o diretório da aplicação
sudo cp /root/Sysgabom.zip /home/seprom/sepromcbmepi/

# Ir para o diretório
cd /home/seprom/sepromcbmepi

# Extrair ZIP
sudo unzip -q Sysgabom.zip

# Ajustar permissões
sudo chown -R seprom:seprom /home/seprom/sepromcbmepi
sudo chmod -R 755 /home/seprom/sepromcbmepi

# Verificar se manage.py existe agora
ls -la manage.py

# Ver estrutura de pastas
ls -la
```

---

## 📋 Se o ZIP Extrair em Subpasta

Se o ZIP extrair em uma subpasta (ex: `Sysgabom/`), mova os arquivos:

```bash
cd /home/seprom/sepromcbmepi

# Verificar se há subpasta
ls -la

# Se houver subpasta Sysgabom, mover conteúdo para o diretório atual
if [ -d "Sysgabom" ]; then
    sudo mv Sysgabom/* .
    sudo mv Sysgabom/.* . 2>/dev/null || true
    sudo rmdir Sysgabom
    echo "✅ Arquivos movidos da subpasta"
fi

# Verificar estrutura
ls -la
ls -la manage.py
```

---

## 🔍 Verificar Conteúdo do ZIP Antes de Extrair

```bash
# Listar conteúdo do ZIP sem extrair
unzip -l /root/Sysgabom.zip | head -30
```

---

## ✅ COMANDO ÚNICO COMPLETO

Copie e cole tudo de uma vez:

```bash
# Instalar unzip
sudo apt install -y unzip

# Copiar e extrair
sudo cp /root/Sysgabom.zip /home/seprom/sepromcbmepi/ && \
cd /home/seprom/sepromcbmepi && \
sudo unzip -q Sysgabom.zip && \
if [ -d "Sysgabom" ]; then sudo mv Sysgabom/* . && sudo mv Sysgabom/.* . 2>/dev/null; sudo rmdir Sysgabom; fi && \
sudo chown -R seprom:seprom /home/seprom/sepromcbmepi && \
sudo chmod -R 755 /home/seprom/sepromcbmepi && \
sudo chmod +x manage.py 2>/dev/null || echo "manage.py será criado após ajustes" && \
echo "✅ ZIP extraído!" && \
ls -la | head -20
```

---

## 📋 Verificar Estrutura Após Extração

```bash
cd /home/seprom/sepromcbmepi

# Ver arquivos principais
ls -la manage.py requirements*.txt gunicorn.conf.py nginx_seprom.conf

# Ver estrutura de pastas
ls -d */ | head -10

# Verificar se pastas importantes existem
[ -d "sepromcbmepi" ] && echo "✅ Pasta sepromcbmepi existe" || echo "❌ Pasta sepromcbmepi não encontrada"
[ -d "militares" ] && echo "✅ Pasta militares existe" || echo "❌ Pasta militares não encontrada"
[ -f "manage.py" ] && echo "✅ manage.py existe" || echo "❌ manage.py não encontrado"
```

---

## 🆘 Se Ainda Não Funcionar

### Verificar conteúdo do ZIP
```bash
unzip -l /root/Sysgabom.zip | less
```

### Extrair manualmente passo a passo
```bash
cd /home/seprom/sepromcbmepi
sudo unzip /root/Sysgabom.zip

# Ver o que foi extraído
ls -la

# Se houver subpasta, mover arquivos
# (ajuste o nome da subpasta se for diferente)
```

