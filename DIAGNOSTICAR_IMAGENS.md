# 🔍 Diagnosticar Problema com Imagens

## 🚀 Comandos de Diagnóstico Completo

Execute estes comandos no servidor para identificar o problema:

```bash
# 1. Verificar se o diretório media existe e tem arquivos
echo "=== 1. Verificando diretório media ==="
ls -la /home/seprom/sepromcbmepi/media/ 2>&1 | head -20
echo ""
find /home/seprom/sepromcbmepi/media -type f | head -10
echo ""

# 2. Verificar permissões
echo "=== 2. Verificando permissões ==="
ls -ld /home/seprom/sepromcbmepi/media
echo ""

# 3. Verificar configuração do Nginx
echo "=== 3. Configuração do Nginx (location /media/) ==="
grep -A 5 "location /media/" /etc/nginx/sites-available/seprom
echo ""

# 4. Verificar se o Nginx está servindo
echo "=== 4. Testando acesso via Nginx ==="
curl -I http://localhost/media/ 2>&1
echo ""

# 5. Verificar logs do Nginx
echo "=== 5. Últimos erros do Nginx ==="
sudo tail -20 /var/log/nginx/seprom_error.log 2>&1
echo ""

# 6. Verificar se o Gunicorn está rodando
echo "=== 6. Status do Gunicorn ==="
sudo systemctl status seprom --no-pager -l | head -15
echo ""

# 7. Verificar configuração do Gunicorn
echo "=== 7. Configuração do Gunicorn (bind) ==="
grep "bind" /home/seprom/sepromcbmepi/gunicorn.conf.py
echo ""

# 8. Verificar se a porta 8000 está em uso
echo "=== 8. Verificando porta 8000 ==="
sudo netstat -tlnp | grep 8000 || sudo ss -tlnp | grep 8000
echo ""

# 9. Testar acesso direto ao Gunicorn
echo "=== 9. Testando Gunicorn diretamente ==="
curl -I http://127.0.0.1:8000/ 2>&1 | head -5
echo ""

# 10. Verificar URLs de mídia no Django
echo "=== 10. Verificando configuração Django (MEDIA_URL e MEDIA_ROOT) ==="
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py shell -c \"from django.conf import settings; print('MEDIA_URL:', settings.MEDIA_URL); print('MEDIA_ROOT:', settings.MEDIA_ROOT)\"" 2>&1
echo ""

echo "✅ Diagnóstico concluído!"
```

---

## 🔧 Correção Completa (Execute Depois do Diagnóstico)

```bash
# 1. Corrigir Gunicorn para usar TCP
sudo sed -i 's|bind = "unix:/home/seprom/sepromcbmepi/seprom.sock"|bind = "127.0.0.1:8000"|g' /home/seprom/sepromcbmepi/gunicorn.conf.py

# 2. Criar diretório media se não existir
sudo mkdir -p /home/seprom/sepromcbmepi/media
sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/media
sudo chmod -R 755 /home/seprom/sepromcbmepi/media

# 3. Corrigir Nginx
sudo sed -i 's|proxy_pass http://unix:/home/seprom/sepromcbmepi/seprom.sock;|proxy_pass http://127.0.0.1:8000;|g' /etc/nginx/sites-available/seprom
sudo sed -i 's|server_name _;|server_name 64.23.185.235;|g' /etc/nginx/sites-available/seprom
sudo ln -sf /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/seprom
sudo rm -f /etc/nginx/sites-enabled/default

# 4. Reiniciar serviços
sudo systemctl restart seprom
sudo nginx -t && sudo systemctl reload nginx

# 5. Verificar status
sudo systemctl status seprom --no-pager -l | head -10
sudo systemctl status nginx --no-pager -l | head -10
```

---

## 📋 Comando Tudo em Um

```bash
sudo sed -i 's|bind = "unix:/home/seprom/sepromcbmepi/seprom.sock"|bind = "127.0.0.1:8000"|g' /home/seprom/sepromcbmepi/gunicorn.conf.py && \
sudo mkdir -p /home/seprom/sepromcbmepi/media && \
sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/media && \
sudo chmod -R 755 /home/seprom/sepromcbmepi/media && \
sudo sed -i 's|proxy_pass http://unix:/home/seprom/sepromcbmepi/seprom.sock;|proxy_pass http://127.0.0.1:8000;|g' /etc/nginx/sites-available/seprom && \
sudo sed -i 's|server_name _;|server_name 64.23.185.235;|g' /etc/nginx/sites-available/seprom && \
sudo ln -sf /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/seprom && \
sudo rm -f /etc/nginx/sites-enabled/default && \
sudo systemctl restart seprom && \
sudo nginx -t && sudo systemctl reload nginx && \
echo "✅ Correção aplicada! Teste novamente."
```

