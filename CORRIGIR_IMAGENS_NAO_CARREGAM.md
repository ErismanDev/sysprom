# 🔧 Corrigir Imagens que Não Carregam

## 🔍 Verificações e Correções

### 1. Verificar se o diretório media existe e tem permissões

```bash
# Verificar se existe
ls -la /home/seprom/sepromcbmepi/media/

# Se não existir, criar
sudo mkdir -p /home/seprom/sepromcbmepi/media
sudo chown -R seprom:seprom /home/seprom/sepromcbmepi/media
sudo chmod -R 755 /home/seprom/sepromcbmepi/media
```

---

### 2. Verificar configuração do Nginx

```bash
# Verificar se o arquivo de configuração está correto
cat /etc/nginx/sites-available/seprom | grep -A 5 "location /media/"

# Verificar se está linkado
ls -la /etc/nginx/sites-enabled/ | grep seprom

# Se não estiver linkado:
sudo ln -sf /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/seprom

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

---

### 3. Verificar se o Nginx está servindo corretamente

O problema pode ser que o Nginx está configurado para usar socket Unix, mas o Gunicorn está usando TCP. Vamos verificar:

```bash
# Verificar configuração do Gunicorn
cat /home/seprom/sepromcbmepi/gunicorn.conf.py | grep bind

# Verificar configuração do Nginx
cat /etc/nginx/sites-available/seprom | grep proxy_pass
```

**Se o Nginx estiver usando `unix:/home/seprom/sepromcbmepi/seprom.sock` mas o Gunicorn estiver usando TCP, precisamos corrigir.**

---

### 4. Corrigir configuração do Nginx (se necessário)

```bash
# Editar configuração do Nginx
sudo nano /etc/nginx/sites-available/seprom

# Verificar se está assim:
# location / {
#     proxy_pass http://127.0.0.1:8000;  # TCP
#     # OU
#     proxy_pass http://unix:/home/seprom/sepromcbmepi/seprom.sock;  # Unix socket
# }

# Se estiver usando socket Unix mas o Gunicorn está em TCP, mudar para:
# proxy_pass http://127.0.0.1:8000;

# Salvar e recarregar
sudo nginx -t
sudo systemctl reload nginx
```

---

### 5. Verificar permissões dos arquivos de mídia

```bash
# Verificar permissões
ls -la /home/seprom/sepromcbmepi/media/

# Corrigir permissões se necessário
sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/media
sudo chmod -R 755 /home/seprom/sepromcbmepi/media

# Verificar se o Nginx pode ler
sudo -u www-data ls /home/seprom/sepromcbmepi/media/
```

---

### 6. Verificar logs do Nginx para erros

```bash
# Ver logs de erro
sudo tail -50 /var/log/nginx/seprom_error.log
sudo tail -50 /var/log/nginx/error.log

# Ver logs de acesso
sudo tail -50 /var/log/nginx/seprom_access.log
```

---

### 7. Testar acesso direto aos arquivos

```bash
# Testar se consegue acessar um arquivo de mídia diretamente
curl -I http://localhost/media/teste.jpg
curl -I http://64.23.185.235/media/teste.jpg

# Se retornar 404, o problema é no Nginx
# Se retornar 403, é problema de permissão
# Se retornar 200, está funcionando
```

---

### 8. Verificar se os arquivos de mídia foram enviados

```bash
# Verificar se há arquivos no diretório media
find /home/seprom/sepromcbmepi/media -type f | head -10

# Se não houver arquivos, você precisa enviá-los do PC local via WinSCP
```

---

### 9. Comando Completo de Correção

Execute este comando completo para corrigir tudo de uma vez:

```bash
# Criar diretório media se não existir
sudo mkdir -p /home/seprom/sepromcbmepi/media
sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/media
sudo chmod -R 755 /home/seprom/sepromcbmepi/media

# Verificar e corrigir configuração do Nginx
sudo sed -i 's|proxy_pass http://unix:/home/seprom/sepromcbmepi/seprom.sock;|proxy_pass http://127.0.0.1:8000;|g' /etc/nginx/sites-available/seprom

# Garantir que o site está habilitado
sudo ln -sf /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/seprom

# Remover site padrão se existir
sudo rm -f /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx

# Verificar status
sudo systemctl status nginx
```

---

### 10. Se ainda não funcionar - Adicionar configuração de mídia no Django

Se o Nginx não estiver servindo, podemos fazer o Django servir temporariamente (não recomendado para produção, mas útil para debug):

```bash
# Editar urls.py para adicionar servir mídia em desenvolvimento
# (Isso já deve estar no código, mas vamos verificar)
```

---

## ✅ Checklist Final

- [ ] Diretório `/home/seprom/sepromcbmepi/media` existe
- [ ] Permissões corretas (seprom:www-data, 755)
- [ ] Nginx configurado para servir `/media/`
- [ ] Nginx site habilitado e linkado
- [ ] Nginx recarregado após mudanças
- [ ] Arquivos de mídia existem no diretório
- [ ] Logs do Nginx não mostram erros
- [ ] Teste direto via curl funciona

