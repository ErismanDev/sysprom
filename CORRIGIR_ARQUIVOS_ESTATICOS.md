# 🔧 Corrigir Arquivos Estáticos (Imagens em /static/)

## 🔍 Problema Identificado

As imagens estão em `sepromcbmepi/static` e `staticfiles`, mas não estão carregando. Isso pode ser porque:

1. O `STATIC_URL` está como `"static/"` (sem barra inicial) - deveria ser `"/static/"`
2. O `collectstatic` pode não ter sido executado
3. Permissões incorretas nos arquivos estáticos

---

## 🚀 Solução Completa

### PASSO 1: Corrigir STATIC_URL no settings.py

```bash
# Corrigir STATIC_URL para ter barra inicial
sudo sed -i 's|STATIC_URL = "static/"|STATIC_URL = "/static/"|g' /home/seprom/sepromcbmepi/sepromcbmepi/settings.py
```

---

### PASSO 2: Executar collectstatic

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python manage.py collectstatic --noinput
EOF
```

---

### PASSO 3: Verificar e Corrigir Permissões

```bash
# Verificar permissões do diretório staticfiles
sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/staticfiles
sudo chmod -R 755 /home/seprom/sepromcbmepi/staticfiles

# Verificar permissões do diretório static (se existir)
if [ -d "/home/seprom/sepromcbmepi/static" ]; then
    sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/static
    sudo chmod -R 755 /home/seprom/sepromcbmepi/static
fi
```

---

### PASSO 4: Verificar Configuração do Nginx

```bash
# Verificar se o Nginx está configurado corretamente
grep -A 3 "location /static/" /etc/nginx/sites-available/seprom

# Se não estiver correto, o Nginx deve ter:
# location /static/ {
#     alias /home/seprom/sepromcbmepi/staticfiles/;
#     ...
# }
```

---

### PASSO 5: Reiniciar Serviços

```bash
sudo systemctl restart seprom
sudo systemctl reload nginx
```

---

## 📋 Comando Único (Tudo em Um)

```bash
# 1. Corrigir STATIC_URL
sudo sed -i 's|STATIC_URL = "static/"|STATIC_URL = "/static/"|g' /home/seprom/sepromcbmepi/sepromcbmepi/settings.py && \

# 2. Executar collectstatic
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py collectstatic --noinput" && \

# 3. Corrigir permissões
sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/staticfiles && \
sudo chmod -R 755 /home/seprom/sepromcbmepi/staticfiles && \
[ -d "/home/seprom/sepromcbmepi/static" ] && sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/static && sudo chmod -R 755 /home/seprom/sepromcbmepi/static || true && \

# 4. Reiniciar serviços
sudo systemctl restart seprom && \
sleep 2 && \
sudo systemctl reload nginx && \

# 5. Verificar
echo "✅ Correção aplicada!"
echo ""
echo "Verificando arquivos estáticos:"
find /home/seprom/sepromcbmepi/staticfiles -type f | wc -l
echo "arquivos encontrados em staticfiles"
```

---

## 🔍 Verificar se Funcionou

```bash
# Testar acesso a arquivos estáticos
curl -I http://localhost/static/ 2>&1 | head -5

# Verificar se há arquivos
find /home/seprom/sepromcbmepi/staticfiles -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" | head -10

# Verificar configuração atual
grep "STATIC_URL" /home/seprom/sepromcbmepi/sepromcbmepi/settings.py
```

---

## 📤 Se os Arquivos Não Estiverem no Servidor

Se os arquivos de `static` não foram enviados para o servidor:

1. **Via WinSCP:**
   - Conecte ao servidor
   - Envie a pasta `static` de `C:\projetos\Sysgabom\sepromcbmepi\static` para `/home/seprom/sepromcbmepi/sepromcbmepi/static`
   - Depois execute `collectstatic` novamente:
     ```bash
     su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py collectstatic --noinput"
     ```

