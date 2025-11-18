# 🔒 Configurar HTTPS no Servidor Digital Ocean

## 📋 Pré-requisitos

1. **Domínio apontando para o servidor** (64.23.185.235)
   - Se não tiver domínio, veja a seção "Sem Domínio" abaixo

2. **Acesso root ao servidor**

3. **Portas 80 e 443 abertas no firewall**

---

## 🚀 Opção 1: Configuração Automática (Recomendado)

### Passo 1: Enviar Script para o Servidor

```bash
# No seu PC, envie o script via WinSCP ou SCP
scp configurar_https.sh root@64.23.185.235:/root/
```

### Passo 2: Executar no Servidor

```bash
# Conectar ao servidor
ssh root@64.23.185.235

# Tornar executável
chmod +x /root/configurar_https.sh

# Executar
/root/configurar_https.sh
```

O script irá:
- ✅ Instalar Certbot
- ✅ Obter certificado SSL
- ✅ Configurar Nginx com HTTPS
- ✅ Configurar renovação automática
- ✅ Redirecionar HTTP para HTTPS

---

## 🔧 Opção 2: Configuração Manual

### Passo 1: Instalar Certbot

```bash
# Atualizar sistema
apt update
apt upgrade -y

# Instalar Certbot
apt install -y certbot python3-certbot-nginx
```

### Passo 2: Obter Certificado SSL

```bash
# Substitua SEU_DOMINIO pelo seu domínio
certbot certonly --standalone -d SEU_DOMINIO --non-interactive --agree-tos --email seu-email@exemplo.com
```

### Passo 3: Configurar Nginx

```bash
# Backup da configuração atual
cp /etc/nginx/sites-available/seprom /etc/nginx/sites-available/seprom.backup

# Editar configuração
nano /etc/nginx/sites-available/seprom
```

**Substitua o conteúdo pelo arquivo `nginx_seprom_https.conf`**, mas **substitua `DOMINIO_AQUI` pelo seu domínio**.

Ou use o comando:

```bash
# Copiar configuração HTTPS
cp /home/seprom/sepromcbmepi/nginx_seprom_https.conf /etc/nginx/sites-available/seprom

# Substituir DOMINIO_AQUI pelo domínio real
sed -i "s/DOMINIO_AQUI/SEU_DOMINIO/g" /etc/nginx/sites-available/seprom
```

### Passo 4: Testar e Reiniciar

```bash
# Testar configuração
nginx -t

# Se estiver OK, recarregar
systemctl reload nginx
```

### Passo 5: Configurar Renovação Automática

```bash
# Habilitar timer do Certbot
systemctl enable certbot.timer
systemctl start certbot.timer

# Verificar status
systemctl status certbot.timer
```

---

## 🌐 Sem Domínio? Use Cloudflare

Se você não tem domínio, pode usar **Cloudflare Tunnel** (gratuito):

### Opção A: Cloudflare Tunnel

1. Crie conta no Cloudflare (gratuito)
2. Instale cloudflared no servidor
3. Configure tunnel
4. Obtenha HTTPS automático

### Opção B: Certificado Auto-Assinado (Não Recomendado)

```bash
# Gerar certificado auto-assinado
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/seprom-selfsigned.key \
    -out /etc/ssl/certs/seprom-selfsigned.crt

# Configurar Nginx para usar (aviso do navegador aparecerá)
```

---

## ✅ Verificar Configuração

### Testar HTTPS

```bash
# Testar localmente
curl -I https://SEU_DOMINIO

# Verificar certificado
openssl s_client -connect SEU_DOMINIO:443 -servername SEU_DOMINIO
```

### Verificar Renovação Automática

```bash
# Testar renovação (dry-run)
certbot renew --dry-run

# Ver status do timer
systemctl status certbot.timer
```

---

## 🔍 Troubleshooting

### Erro: "Domain not found"

**Solução:** Verifique se o domínio está apontando para o IP:
```bash
dig SEU_DOMINIO +short
# Deve retornar: 64.23.185.235
```

### Erro: "Port 80 already in use"

**Solução:** Pare o Nginx temporariamente:
```bash
systemctl stop nginx
certbot certonly --standalone -d SEU_DOMINIO
systemctl start nginx
```

### Erro: "Certificate already exists"

**Solução:** Use o certificado existente:
```bash
certbot certificates
# Use o caminho do certificado existente no Nginx
```

### Certificado não renova automaticamente

**Solução:** Verificar e corrigir timer:
```bash
systemctl status certbot.timer
systemctl enable certbot.timer
systemctl start certbot.timer
```

---

## 📝 Atualizar Django Settings

Após configurar HTTPS, atualize o Django para usar HTTPS:

```python
# Em settings.py ou settings_production.py
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## 🔄 Renovar Certificado Manualmente

```bash
# Renovar todos os certificados
certbot renew

# Renovar certificado específico
certbot renew --cert-name SEU_DOMINIO

# Forçar renovação (mesmo que não esteja próximo do vencimento)
certbot renew --force-renewal
```

---

## 📋 Checklist

- [ ] Domínio apontando para 64.23.185.235
- [ ] Certbot instalado
- [ ] Certificado SSL obtido
- [ ] Nginx configurado com HTTPS
- [ ] HTTP redirecionando para HTTPS
- [ ] Renovação automática configurada
- [ ] Testado acesso via HTTPS
- [ ] Django configurado para HTTPS

---

## 🆘 Comandos Úteis

```bash
# Ver certificados instalados
certbot certificates

# Revogar certificado
certbot revoke --cert-path /etc/letsencrypt/live/SEU_DOMINIO/cert.pem

# Ver logs do Certbot
tail -f /var/log/letsencrypt/letsencrypt.log

# Ver logs do Nginx
tail -f /var/log/nginx/seprom_error.log
tail -f /var/log/nginx/seprom_access.log

# Testar configuração SSL
ssl Labs: https://www.ssllabs.com/ssltest/
```

---

**Última atualização**: 2024-11-16

