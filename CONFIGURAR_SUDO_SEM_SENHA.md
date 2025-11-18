# 🔓 Configurar Sudo Sem Senha para seprom

## ⚡ COMANDO ÚNICO - Configurar Sudo Sem Senha

Execute como **root**:

```bash
# Adicionar seprom ao grupo sudo
usermod -aG sudo seprom

# Configurar sudo sem senha
echo "seprom ALL=(ALL) NOPASSWD: ALL" | tee /etc/sudoers.d/seprom

# Ajustar permissões do arquivo
chmod 0440 /etc/sudoers.d/seprom

# Verificar
cat /etc/sudoers.d/seprom
```

---

## ✅ Verificar se Funcionou

```bash
# Testar como usuário seprom
su - seprom
sudo whoami
# Deve mostrar: root (sem pedir senha)

# Testar comandos
sudo systemctl status seprom
sudo systemctl status nginx
```

---

## 🔧 Comando Completo (Copie e Cole)

```bash
usermod -aG sudo seprom && \
echo "seprom ALL=(ALL) NOPASSWD: ALL" | tee /etc/sudoers.d/seprom && \
chmod 0440 /etc/sudoers.d/seprom && \
echo "✅ Sudo sem senha configurado para seprom!" && \
cat /etc/sudoers.d/seprom
```

---

## 📋 Após Configurar

Agora você pode usar sudo sem senha:

```bash
# Como usuário seprom
sudo systemctl status seprom
sudo systemctl status nginx
sudo journalctl -u seprom -n 30
```

---

## ⚠️ Nota de Segurança

Configurar sudo sem senha é menos seguro, mas útil para servidores de desenvolvimento. Para produção, considere usar senha ou chaves SSH.

