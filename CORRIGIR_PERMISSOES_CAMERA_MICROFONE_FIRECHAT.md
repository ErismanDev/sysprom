# 🔧 Corrigir Permissões de Câmera e Microfone no Firechat

## ⚠️ Problema

O Firechat não está permitindo acesso à câmera e microfone. Isso geralmente ocorre por:

1. **Site não está usando HTTPS** (obrigatório para getUserMedia)
2. **Permissões bloqueadas no navegador**
3. **Dispositivos não encontrados ou em uso**

---

## ✅ Soluções Implementadas

O código foi atualizado para:
- ✅ Verificar se `getUserMedia` está disponível
- ✅ Tratar erros de permissão com mensagens claras
- ✅ Orientar o usuário sobre como resolver

---

## 🔍 Verificar o Problema

### 1. Verificar se está usando HTTPS

O `getUserMedia` **requer HTTPS** em produção (exceto localhost).

**No servidor Digital Ocean:**
- Verifique se o site está acessível via `https://`
- Se estiver usando `http://`, o navegador bloqueará o acesso à mídia

### 2. Verificar Permissões no Navegador

**Chrome/Edge:**
1. Clique no ícone de cadeado na barra de endereço
2. Vá em "Configurações do site"
3. Verifique "Câmera" e "Microfone"
4. Altere para "Permitir"

**Firefox:**
1. Clique no ícone de cadeado
2. Clique em "Mais informações"
3. Vá na aba "Permissões"
4. Configure "Acessar sua câmera" e "Acessar seu microfone"

**Safari:**
1. Safari > Preferências > Websites
2. Configure "Câmera" e "Microfone"

---

## 🛠️ Configurar HTTPS no Servidor

Se o site não está usando HTTPS, configure:

### Opção 1: Usar Certbot (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com

# Renovar automaticamente
sudo certbot renew --dry-run
```

### Opção 2: Configurar Nginx com SSL

```nginx
server {
    listen 443 ssl http2;
    server_name seu-dominio.com;
    
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    # ... resto da configuração
}

# Redirecionar HTTP para HTTPS
server {
    listen 80;
    server_name seu-dominio.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 🧪 Testar Permissões

### Teste Manual no Console do Navegador

Abra o console (F12) e execute:

```javascript
// Testar acesso ao microfone
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        console.log('✅ Microfone acessível!');
        stream.getTracks().forEach(track => track.stop());
    })
    .catch(error => {
        console.error('❌ Erro:', error.name, error.message);
    });

// Testar acesso à câmera
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        console.log('✅ Câmera acessível!');
        stream.getTracks().forEach(track => track.stop());
    })
    .catch(error => {
        console.error('❌ Erro:', error.name, error.message);
    });
```

---

## 📋 Mensagens de Erro e Soluções

### "NotAllowedError" ou "PermissionDeniedError"
**Solução:** Permitir acesso nas configurações do navegador

### "NotFoundError" ou "DevicesNotFoundError"
**Solução:** Verificar se há câmera/microfone conectados

### "NotReadableError" ou "TrackStartError"
**Solução:** Fechar outros aplicativos que usam o dispositivo

### "getUserMedia não está disponível"
**Solução:** Site precisa estar em HTTPS ou localhost

---

## 🔄 Atualizar Código no Servidor

Após fazer as alterações, atualize os arquivos no servidor:

```bash
# No servidor
cd /home/seprom/sepromcbmepi

# Fazer backup
cp static/js/chat-calls.js static/js/chat-calls.js.backup
cp static/js/chat-voice-message.js static/js/chat-voice-message.js.backup

# Enviar novos arquivos via WinSCP ou git pull
# Depois coletar arquivos estáticos
python manage.py collectstatic --noinput
```

---

## ✅ Checklist

- [ ] Site está usando HTTPS
- [ ] Permissões de câmera/microfone permitidas no navegador
- [ ] Dispositivos estão conectados e funcionando
- [ ] Nenhum outro aplicativo está usando os dispositivos
- [ ] Código atualizado no servidor
- [ ] Arquivos estáticos coletados

---

## 🆘 Se Ainda Não Funcionar

1. **Limpar cache do navegador**
2. **Testar em outro navegador**
3. **Verificar logs do console (F12)**
4. **Testar em modo anônimo/privado**
5. **Verificar se o dispositivo funciona em outros sites (ex: Google Meet)**

---

**Última atualização**: 2024-11-16

