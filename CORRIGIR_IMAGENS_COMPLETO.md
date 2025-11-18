# 🔧 Corrigir Imagens - Solução Completa

## 🚀 PASSO 1: Diagnóstico (Execute Primeiro)

```bash
# Verificar se há arquivos de mídia
echo "=== Arquivos em /media/ ==="
find /home/seprom/sepromcbmepi/media -type f 2>/dev/null | wc -l
echo ""

# Verificar configuração atual
echo "=== Gunicorn bind ==="
grep "bind" /home/seprom/sepromcbmepi/gunicorn.conf.py
echo ""

echo "=== Nginx proxy_pass ==="
grep "proxy_pass" /etc/nginx/sites-available/seprom | grep -v "#"
echo ""

echo "=== Nginx location /media/ ==="
grep -A 3 "location /media/" /etc/nginx/sites-available/seprom
echo ""

# Testar acesso
echo "=== Testando acesso ==="
curl -I http://localhost/media/ 2>&1 | head -3
```

---

## 🔧 PASSO 2: Correção Completa

Execute este comando completo:

```bash
# 1. Corrigir Gunicorn para usar TCP
sudo sed -i 's|bind = "unix:/home/seprom/sepromcbmepi/seprom.sock"|bind = "127.0.0.1:8000"|g' /home/seprom/sepromcbmepi/gunicorn.conf.py

# 2. Criar e configurar diretório media
sudo mkdir -p /home/seprom/sepromcbmepi/media
sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/media
sudo chmod -R 755 /home/seprom/sepromcbmepi/media

# 3. Corrigir Nginx - proxy_pass
sudo sed -i 's|proxy_pass http://unix:/home/seprom/sepromcbmepi/seprom.sock;|proxy_pass http://127.0.0.1:8000;|g' /etc/nginx/sites-available/seprom

# 4. Corrigir Nginx - server_name
sudo sed -i 's|server_name _;|server_name 64.23.185.235;|g' /etc/nginx/sites-available/seprom

# 5. Garantir que o site está habilitado
sudo ln -sf /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/seprom
sudo rm -f /etc/nginx/sites-enabled/default

# 6. Testar configuração do Nginx
sudo nginx -t

# 7. Reiniciar serviços
sudo systemctl restart seprom
sudo systemctl reload nginx

# 8. Aguardar alguns segundos
sleep 3

# 9. Verificar status
echo ""
echo "=== Status dos Serviços ==="
sudo systemctl status seprom --no-pager -l | head -10
echo ""
sudo systemctl status nginx --no-pager -l | head -10
echo ""

# 10. Testar acesso
echo "=== Testando Acesso ==="
curl -I http://localhost/media/ 2>&1 | head -5
echo ""

echo "✅ Correção aplicada!"
```

---

## 📋 Comando Único (Copiar e Colar Tudo)

```bash
sudo sed -i 's|bind = "unix:/home/seprom/sepromcbmepi/seprom.sock"|bind = "127.0.0.1:8000"|g' /home/seprom/sepromcbmepi/gunicorn.conf.py && \
sudo mkdir -p /home/seprom/sepromcbmepi/media && \
sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/media && \
sudo chmod -R 755 /home/seprom/sepromcbmepi/media && \
sudo sed -i 's|proxy_pass http://unix:/home/seprom/sepromcbmepi/seprom.sock;|proxy_pass http://127.0.0.1:8000;|g' /etc/nginx/sites-available/seprom && \
sudo sed -i 's|server_name _;|server_name 64.23.185.235;|g' /etc/nginx/sites-available/seprom && \
sudo ln -sf /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/seprom && \
sudo rm -f /etc/nginx/sites-enabled/default && \
sudo nginx -t && \
sudo systemctl restart seprom && \
sleep 3 && \
sudo systemctl reload nginx && \
echo "✅ Correção aplicada! Verifique se as imagens estão carregando."
```

---

## 🔍 Se Ainda Não Funcionar - Verificar Arquivos

```bash
# Verificar se os arquivos de mídia existem no servidor
echo "Arquivos em /media/:"
find /home/seprom/sepromcbmepi/media -type f | head -20

# Se não houver arquivos, você precisa enviá-los do PC local via WinSCP
# Pasta local: C:\projetos\Sysgabom\media
# Pasta servidor: /home/seprom/sepromcbmepi/media
```

---

## 📤 Enviar Arquivos de Mídia (Se Necessário)

1. **Via WinSCP:**
   - Conecte ao servidor (64.23.185.235)
   - Navegue até `/home/seprom/sepromcbmepi/` no servidor
   - Envie a pasta `media` completa do PC local (`C:\projetos\Sysgabom\media`)
   - Após enviar, execute:
     ```bash
     sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/media
     sudo chmod -R 755 /home/seprom/sepromcbmepi/media
     ```

---

## 🐛 Verificar Logs de Erro

```bash
# Logs do Nginx
sudo tail -50 /var/log/nginx/seprom_error.log

# Logs do Gunicorn
sudo tail -50 /home/seprom/sepromcbmepi/logs/gunicorn_error.log

# Logs do sistema
sudo journalctl -u seprom -n 50 --no-pager
```

