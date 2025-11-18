# 🔌 Conectar ao Servidor Digital Ocean via PowerShell

**IP do Servidor:** 64.23.185.235

## 📋 Método 1: SSH com PowerShell (Recomendado)

### Conectar como root (padrão Digital Ocean)

```powershell
ssh root@64.23.185.235
```

### Conectar como usuário seprom (após criar)

```powershell
ssh seprom@64.23.185.235
```

### Conectar com porta específica (se necessário)

```powershell
ssh -p 22 root@64.23.185.235
```

---

## 📋 Método 2: SSH com Chave Privada

Se você configurou chave SSH:

```powershell
ssh -i C:\caminho\para\sua\chave_privada root@64.23.185.235
```

---

## 📋 Método 3: SSH com Opções Adicionais

### Conectar e manter conexão ativa

```powershell
ssh -o ServerAliveInterval=60 root@64.23.185.235
```

### Conectar com verbose (para debug)

```powershell
ssh -v root@64.23.185.235
```

---

## 🔑 Primeira Conexão

Na primeira vez, você verá uma mensagem sobre autenticidade do host:

```
The authenticity of host '64.23.185.235 (64.23.185.235)' can't be established.
ECDSA key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Digite `yes` e pressione Enter.

---

## 🔐 Autenticação

### Com senha
- Digite a senha quando solicitado
- A senha não aparece enquanto você digita (por segurança)

### Com chave SSH
- Se configurou chave SSH, não precisará de senha
- Certifique-se de que a chave está no caminho correto

---

## 📤 Comandos Úteis

### Sair do servidor
```bash
exit
```
ou pressione `Ctrl + D`

### Desconectar sem fechar sessão
```bash
# Pressione: Ctrl + A, depois D
# Ou use screen/tmux se instalado
```

---

## 🛠️ Configurar SSH no PowerShell (Opcional)

### Criar arquivo de configuração SSH

No PowerShell, edite ou crie o arquivo:
```
C:\Users\SeuUsuario\.ssh\config
```

Adicione:

```
Host digitalocean
    HostName 64.23.185.235
    User root
    Port 22
    IdentityFile C:\caminho\para\chave_privada
```

Depois você pode conectar apenas com:
```powershell
ssh digitalocean
```

---

## 🔧 Troubleshooting

### Erro: "ssh: command not found"
```powershell
# Instalar OpenSSH no Windows
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

### Erro: "Permission denied"
- Verifique se a senha está correta
- Verifique se a chave SSH tem permissões corretas
- Verifique se o usuário existe no servidor

### Erro: "Connection refused"
- Verifique se o servidor está online
- Verifique se a porta 22 está aberta no firewall
- Verifique se o serviço SSH está rodando no servidor

### Verificar se servidor está acessível
```powershell
Test-NetConnection -ComputerName 64.23.185.235 -Port 22
```

---

## 📋 Comando Completo com Exemplo

```powershell
# Conectar ao servidor
ssh root@64.23.185.235

# Após conectar, você verá algo como:
# root@ubuntu-s-1vcpu-1gb-sfo3-01:~#
```

---

## 🔐 Segurança

### Desabilitar autenticação por senha (após configurar chave SSH)

No servidor, edite:
```bash
sudo nano /etc/ssh/sshd_config
```

Altere:
```
PasswordAuthentication no
PubkeyAuthentication yes
```

Reinicie SSH:
```bash
sudo systemctl restart sshd
```

---

## 📝 Notas

- **Usuário padrão Digital Ocean:** `root`
- **Porta padrão SSH:** `22`
- **Senha:** A senha que você configurou ao criar o droplet
- **Chave SSH:** Se você adicionou chave SSH ao criar o droplet, use ela

---

## 🚀 Exemplo Prático

```powershell
# 1. Abrir PowerShell
# 2. Conectar
ssh root@64.23.185.235

# 3. Digitar senha quando solicitado
# 4. Após conectar, você estará no servidor!

# 5. Verificar Python (após instalar)
/usr/local/bin/python3.11 --version

# 6. Sair quando terminar
exit
```

