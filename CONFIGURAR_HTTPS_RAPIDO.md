# 🚀 Configurar HTTPS - Guia Rápido

## ⚡ Método Mais Rápido

### 1. Enviar Arquivos para o Servidor

Via WinSCP, envie para `/home/seprom/sepromcbmepi/`:
- `configurar_https.sh`
- `nginx_seprom_https.conf`

### 2. Executar no Servidor

```bash
# Conectar ao servidor
ssh root@64.23.185.235

# Ir para o diretório
cd /home/seprom/sepromcbmepi

# Tornar executável
chmod +x configurar_https.sh

# Executar
./configurar_https.sh
```

O script irá perguntar se você tem domínio. Se tiver, digite o domínio e ele configurará tudo automaticamente!

---

## 📋 Se Você TEM Domínio

1. Certifique-se de que o domínio aponta para `64.23.185.235`
2. Execute o script `configurar_https.sh`
3. Digite o domínio quando solicitado
4. Pronto! ✅

---

## 📋 Se Você NÃO TEM Domínio

### Opção 1: Registrar um Domínio (Recomendado)

1. Registre um domínio (ex: Registro.br, GoDaddy, etc)
2. Configure DNS apontando para `64.23.185.235`
3. Execute o script

### Opção 2: Usar Cloudflare Tunnel (Gratuito)

```bash
# Instalar cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared-linux-amd64.deb

# Autenticar
cloudflared tunnel login

# Criar tunnel
cloudflared tunnel create seprom

# Configurar
cloudflared tunnel route dns seprom seu-subdominio.trycloudflare.com
```

### Opção 3: Certificado Auto-Assinado (Apenas para Teste)

```bash
# Gerar certificado
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/seprom.key \
    -out /etc/ssl/certs/seprom.crt

# Configurar Nginx manualmente
# (O navegador mostrará aviso de segurança)
```

---

## ✅ Após Configurar

1. **Teste o acesso:**
   ```bash
   curl -I https://SEU_DOMINIO
   ```

2. **Atualize o Django** (se necessário):
   ```python
   # Em settings.py
   SECURE_SSL_REDIRECT = True
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
   ```

3. **Reinicie a aplicação:**
   ```bash
   systemctl restart seprom
   ```

---

## 🔍 Verificar se Funcionou

Acesse no navegador:
- `https://SEU_DOMINIO` (deve abrir sem avisos)
- `http://SEU_DOMINIO` (deve redirecionar para HTTPS)

---

**Pronto! O Firechat agora terá acesso à câmera e microfone!** 🎉

