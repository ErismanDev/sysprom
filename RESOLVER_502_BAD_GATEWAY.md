# 🔧 Resolver Erro 502 Bad Gateway

## ⚠️ Problema
Nginx não consegue se conectar ao Gunicorn.

## ✅ DIAGNÓSTICO E SOLUÇÃO

### Passo 1: Verificar Status dos Serviços

```bash
# Verificar status do Gunicorn
sudo systemctl status seprom --no-pager

# Verificar status do Nginx
sudo systemctl status nginx --no-pager
```

### Passo 2: Verificar Logs

```bash
# Logs do Gunicorn (últimas 50 linhas)
sudo journalctl -u seprom -n 50 --no-pager

# Logs de erro do Nginx
sudo tail -n 50 /var/log/nginx/error.log
```

### Passo 3: Verificar Configuração

```bash
# Verificar se o serviço está configurado corretamente
cat /etc/systemd/system/seprom.service

# Verificar configuração do Nginx
sudo nginx -t
cat /etc/nginx/sites-enabled/seprom
```

---

## 🔧 SOLUÇÕES COMUNS

### Solução 1: Reiniciar Serviços

```bash
# Reiniciar Gunicorn
sudo systemctl restart seprom

# Reiniciar Nginx
sudo systemctl restart nginx

# Verificar status
sudo systemctl status seprom --no-pager
```

### Solução 2: Verificar se Gunicorn está escutando

```bash
# Verificar se Gunicorn está rodando na porta 8000
sudo netstat -tlnp | grep 8000
# OU
sudo ss -tlnp | grep 8000

# Testar conexão direta
curl http://127.0.0.1:8000
```

### Solução 3: Verificar Permissões e Arquivos

```bash
# Verificar se o arquivo .env existe
ls -la /home/seprom/sepromcbmepi/.env

# Verificar permissões do diretório
ls -la /home/seprom/sepromcbmepi/

# Verificar se o socket/porta está acessível
ls -la /home/seprom/sepromcbmepi/seprom.sock 2>/dev/null || echo "Socket não encontrado (usando TCP)"
```

### Solução 4: Verificar Configuração do Gunicorn

```bash
# Verificar arquivo de configuração
cat /home/seprom/sepromcbmepi/gunicorn.conf.py

# Verificar se está usando TCP (127.0.0.1:8000) ou socket
grep -E "bind|socket" /home/seprom/sepromcbmepi/gunicorn.conf.py
```

---

## 🚀 COMANDO RÁPIDO - Diagnóstico Completo

```bash
echo "=== STATUS DOS SERVIÇOS ===" && \
sudo systemctl status seprom --no-pager -l | head -20 && \
echo -e "\n=== LOGS DO GUNICORN (últimas 30 linhas) ===" && \
sudo journalctl -u seprom -n 30 --no-pager && \
echo -e "\n=== LOGS DO NGINX (erros) ===" && \
sudo tail -n 30 /var/log/nginx/error.log && \
echo -e "\n=== TESTE DE CONEXÃO ===" && \
curl -v http://127.0.0.1:8000 2>&1 | head -20
```

---

## 🔧 Solução: Reiniciar e Verificar

Execute este comando para reiniciar tudo e verificar:

```bash
# Parar serviços
sudo systemctl stop seprom
sudo systemctl stop nginx

# Verificar se há processos antigos
sudo pkill -f gunicorn

# Reiniciar Gunicorn
sudo systemctl start seprom
sleep 3

# Verificar se iniciou
sudo systemctl status seprom --no-pager

# Reiniciar Nginx
sudo systemctl start nginx

# Testar
curl -I http://localhost
curl -I http://64.23.185.235
```

