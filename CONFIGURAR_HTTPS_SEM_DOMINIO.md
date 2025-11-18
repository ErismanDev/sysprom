# 🔒 Configurar HTTPS Sem Domínio

## 🎯 Duas Opções Disponíveis

### Opção 1: Cloudflare Tunnel (Recomendado) ⭐

**Vantagens:**
- ✅ HTTPS real (sem avisos no navegador)
- ✅ Gratuito
- ✅ Fácil de configurar
- ✅ Não precisa de domínio próprio

**Desvantagens:**
- ⚠️ Requer conta no Cloudflare
- ⚠️ URL será algo como: `seprom-tunnel.cf`

### Opção 2: Certificado Auto-Assinado

**Vantagens:**
- ✅ Não precisa de conta externa
- ✅ Funciona imediatamente
- ✅ HTTPS funcional

**Desvantagens:**
- ⚠️ Navegadores mostrarão aviso de segurança
- ⚠️ Usuários precisam aceitar o aviso
- ⚠️ Não recomendado para produção

---

## 🚀 Opção 1: Cloudflare Tunnel

### Passo 1: Executar Script

```bash
cd /home/seprom/sepromcbmepi
chmod +x configurar_https_sem_dominio.sh
./configurar_https_sem_dominio.sh
# Escolha opção 1
```

### Passo 2: Criar Conta Cloudflare

1. Acesse: https://dash.cloudflare.com/sign-up
2. Crie uma conta gratuita
3. Não precisa adicionar domínio

### Passo 3: Autenticar

```bash
cloudflared tunnel login
```

Isso abrirá o navegador para autenticar.

### Passo 4: Criar Tunnel

```bash
cloudflared tunnel create seprom
```

### Passo 5: Configurar DNS

```bash
cloudflared tunnel route dns seprom seprom-tunnel.cf
```

### Passo 6: Criar Arquivo de Configuração

```bash
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << EOF
tunnel: seprom
credentials-file: /root/.cloudflared/SEU_TUNNEL_ID.json

ingress:
  - hostname: seprom-tunnel.cf
    service: http://localhost:8000
  - service: http_status:404
EOF
```

### Passo 7: Executar Tunnel

```bash
# Executar manualmente (teste)
cloudflared tunnel run seprom

# Ou criar serviço systemd (permanente)
cat > /etc/systemd/system/cloudflared.service << EOF
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/cloudflared tunnel run seprom
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cloudflared
systemctl start cloudflared
```

### Passo 8: Acessar

Acesse: `https://seprom-tunnel.cf`

---

## 🔐 Opção 2: Certificado Auto-Assinado

### Executar Script

```bash
cd /home/seprom/sepromcbmepi
chmod +x configurar_https_sem_dominio.sh
./configurar_https_sem_dominio.sh
# Escolha opção 2
```

### Acessar

1. Acesse: `https://64.23.185.235`
2. O navegador mostrará aviso de segurança
3. Clique em "Avançado" ou "Advanced"
4. Clique em "Continuar para o site" ou "Proceed to site"
5. Pronto! ✅

---

## ⚠️ Importante

### Para Firechat Funcionar

Após configurar HTTPS (qualquer opção), o Firechat terá acesso à câmera e microfone!

### Aviso do Navegador (Auto-Assinado)

Se usar certificado auto-assinado:
- Chrome/Edge: "Sua conexão não é privada" → Avançado → Continuar
- Firefox: "Aviso de Segurança" → Avançado → Aceitar o Risco
- Safari: "Este site pode não ser seguro" → Mostrar Detalhes → Visitar Site

Isso é **normal** e **seguro** para uso interno.

---

## 🔄 Comparação

| Recurso | Cloudflare Tunnel | Auto-Assinado |
|---------|-------------------|---------------|
| HTTPS Real | ✅ Sim | ⚠️ Sim, mas com aviso |
| Aviso no Navegador | ❌ Não | ✅ Sim |
| Gratuito | ✅ Sim | ✅ Sim |
| Requer Conta Externa | ✅ Sim (Cloudflare) | ❌ Não |
| Configuração | ⚠️ Média | ✅ Fácil |
| Recomendado para Produção | ✅ Sim | ❌ Não |

---

## 💡 Recomendação

**Para uso interno/teste:** Use certificado auto-assinado (Opção 2)
**Para produção/público:** Use Cloudflare Tunnel (Opção 1) ou registre um domínio

---

**Última atualização**: 2024-11-16

