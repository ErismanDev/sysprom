# 🔧 Resolver "Connection refused" - SSH Digital Ocean

## 🔍 Diagnóstico do Problema

O erro "Connection refused" significa que:
- O serviço SSH não está rodando no servidor
- O firewall está bloqueando a porta 22
- O servidor está offline ou não acessível

## ✅ SOLUÇÃO 1: Verificar via Console Web do Digital Ocean

O Digital Ocean tem um console web que permite acessar o servidor mesmo sem SSH.

### Passos:

1. **Acesse o painel do Digital Ocean**
   - Vá para: https://cloud.digitalocean.com
   - Faça login na sua conta

2. **Acesse seu Droplet**
   - Clique em "Droplets" no menu lateral
   - Clique no seu droplet (IP: 64.23.185.235)

3. **Abra o Console Web**
   - Clique no botão "Access" ou "Console"
   - Ou use o ícone de terminal no canto superior direito
   - Isso abre um console web no navegador

4. **No console web, execute:**

```bash
# Verificar se SSH está instalado
which sshd
sshd -v

# Verificar se serviço SSH está rodando
sudo systemctl status ssh

# Se não estiver rodando, iniciar
sudo systemctl start ssh
sudo systemctl enable ssh

# Verificar se está escutando na porta 22
sudo netstat -tlnp | grep :22
# ou
sudo ss -tlnp | grep :22

# Verificar firewall
sudo ufw status

# Se firewall estiver ativo, permitir SSH
sudo ufw allow 22/tcp
sudo ufw allow OpenSSH
```

## ✅ SOLUÇÃO 2: Verificar e Iniciar SSH via Console Web

Execute no console web do Digital Ocean:

```bash
# Instalar OpenSSH Server (se não estiver instalado)
sudo apt update
sudo apt install -y openssh-server

# Iniciar serviço SSH
sudo systemctl start ssh
sudo systemctl enable ssh

# Verificar status
sudo systemctl status ssh

# Verificar se está escutando
sudo netstat -tlnp | grep :22
```

## ✅ SOLUÇÃO 3: Configurar Firewall

```bash
# Verificar status do firewall
sudo ufw status verbose

# Se estiver ativo, permitir SSH ANTES de fazer qualquer coisa
sudo ufw allow 22/tcp
sudo ufw allow OpenSSH

# Verificar regras
sudo ufw status numbered

# Se necessário, recarregar
sudo ufw reload
```

## ✅ SOLUÇÃO 4: Verificar Configuração SSH

```bash
# Verificar se sshd_config está correto
sudo nano /etc/ssh/sshd_config

# Verificar estas linhas (devem estar assim):
# Port 22
# PermitRootLogin yes (ou PermitRootLogin prohibit-password)
# PasswordAuthentication yes

# Após editar, reiniciar SSH
sudo systemctl restart ssh

# Verificar se reiniciou corretamente
sudo systemctl status ssh
```

## ✅ SOLUÇÃO 5: Verificar se Servidor está Online

No PowerShell do Windows, teste:

```powershell
# Testar conectividade
Test-NetConnection -ComputerName 64.23.185.235 -Port 22

# Testar ping
ping 64.23.185.235
```

## 🔧 COMANDOS COMPLETOS PARA EXECUTAR NO CONSOLE WEB

Copie e cole tudo de uma vez no console web do Digital Ocean:

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar OpenSSH Server
sudo apt install -y openssh-server

# Iniciar e habilitar SSH
sudo systemctl start ssh
sudo systemctl enable ssh

# Configurar firewall
sudo ufw allow 22/tcp
sudo ufw allow OpenSSH
sudo ufw --force enable

# Verificar status
sudo systemctl status ssh
sudo netstat -tlnp | grep :22

echo "✅ SSH configurado! Tente conectar novamente via PowerShell: ssh root@64.23.185.235"
```

## 📋 VERIFICAÇÃO FINAL

Após executar os comandos acima, no PowerShell do Windows:

```powershell
# Testar conexão
Test-NetConnection -ComputerName 64.23.185.235 -Port 22

# Se mostrar "TcpTestSucceeded : True", tente conectar:
ssh root@64.23.185.235
```

## 🆘 Se Ainda Não Funcionar

### Verificar Logs SSH

No console web do Digital Ocean:

```bash
# Ver logs do SSH
sudo journalctl -u ssh -n 50
sudo tail -f /var/log/auth.log
```

### Verificar se porta está aberta externamente

```bash
# No servidor, verificar o que está escutando
sudo netstat -tlnp | grep sshd
sudo ss -tlnp | grep :22
```

### Verificar configuração de rede do Digital Ocean

1. No painel do Digital Ocean
2. Vá em "Networking" → "Firewalls"
3. Verifique se há firewall configurado
4. Se houver, adicione regra para porta 22 (SSH)

## 📝 NOTAS IMPORTANTES

1. **Sempre use o Console Web** do Digital Ocean se SSH não funcionar
2. **Firewall UFW** pode estar bloqueando - sempre permita SSH primeiro
3. **Serviço SSH** precisa estar rodando: `sudo systemctl start ssh`
4. **Porta 22** precisa estar aberta no firewall

## 🚀 Comando Rápido de Recuperação

Se você tiver acesso ao console web, execute:

```bash
sudo apt install -y openssh-server && \
sudo systemctl start ssh && \
sudo systemctl enable ssh && \
sudo ufw allow 22/tcp && \
sudo ufw allow OpenSSH && \
sudo systemctl restart ssh && \
echo "✅ SSH configurado! Tente conectar: ssh root@64.23.185.235"
```

