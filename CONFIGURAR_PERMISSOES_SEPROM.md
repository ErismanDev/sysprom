# 🔐 Configurar Permissões do Usuário seprom

## ⚠️ Problema
O usuário `seprom` não tem permissão sudo ou não tem senha configurada.

## ✅ SOLUÇÃO 1: Adicionar seprom ao grupo sudo (Recomendado)

Execute como **root**:

```bash
# Sair do usuário seprom (se estiver logado)
exit

# Como root, adicionar seprom ao grupo sudo
sudo usermod -aG sudo seprom

# Configurar senha para seprom (opcional, mas recomendado)
sudo passwd seprom
# Digite a senha quando solicitado

# Verificar
groups seprom
```

## ✅ SOLUÇÃO 2: Executar Comandos como Root

Se não quiser configurar sudo, execute os comandos diretamente como root:

```bash
# Sair do usuário seprom
exit

# Agora você está como root
# Executar comandos sem sudo
systemctl status seprom --no-pager -l
systemctl status nginx --no-pager -l
systemctl status postgresql --no-pager -l
journalctl -u seprom -n 30 --no-pager
curl http://localhost
curl http://64.23.185.235
```

## ✅ SOLUÇÃO 3: Configurar sudo sem senha (Menos seguro)

Execute como **root**:

```bash
# Adicionar seprom ao grupo sudo
usermod -aG sudo seprom

# Configurar sudo sem senha (apenas para comandos específicos)
echo "seprom ALL=(ALL) NOPASSWD: /usr/bin/systemctl, /usr/bin/journalctl" | tee /etc/sudoers.d/seprom
```

---

## 🔧 COMANDO RÁPIDO - Configurar Tudo

Execute como **root**:

```bash
# Adicionar ao grupo sudo
usermod -aG sudo seprom

# Configurar senha (você escolhe a senha)
passwd seprom

# Verificar
groups seprom
id seprom
```

---

## 📋 Após Configurar, Testar

```bash
# Como usuário seprom, testar sudo
sudo whoami
# Deve mostrar: root

# Agora os comandos anteriores funcionarão
sudo systemctl status seprom
```

---

## 🚀 Continuar Instalação

Após configurar permissões, continue com:

```bash
# Como root, verificar serviços
systemctl status seprom --no-pager -l
systemctl status nginx --no-pager -l
systemctl status postgresql --no-pager -l

# Ver logs
journalctl -u seprom -n 30 --no-pager

# Testar aplicação
curl http://localhost
curl http://64.23.185.235
```

