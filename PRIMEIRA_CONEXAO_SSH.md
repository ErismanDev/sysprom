# 🔐 Primeira Conexão SSH - O Que Fazer

## ⚠️ Mensagem de Verificação

Quando você conecta pela primeira vez via SSH, o sistema pergunta se você confia no servidor. Isso é **NORMAL** e **SEGURO**.

## ✅ O Que Fazer

Quando aparecer esta mensagem:

```
The authenticity of host '64.23.185.235 (64.23.185.235)' can't be established.
ED25519 key fingerprint is SHA256:JdD2O4O5zwsBsTSrscSnZ6YvTHKG9/A+0cbZDdUFzbo.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

**Digite:** `yes` e pressione **Enter**

## 🔍 Verificação

O fingerprint mostrado (`SHA256:JdD2O4O5zwsBsTSrscSnZ6YvTHKG9/A+0cbZDdUFzbo`) é a "impressão digital" do servidor. 

Se você tem certeza de que está conectando ao servidor correto (64.23.185.235), digite `yes`.

## 📝 Próximos Passos

Após digitar `yes`:
1. O sistema salvará a chave do servidor
2. Você será solicitado a digitar a senha
3. Depois poderá executar o script `./configurar_https.sh`

## ⚠️ Importante

- **Só digite `yes` se você tem certeza** de que está conectando ao servidor correto
- Esta verificação acontece **apenas na primeira vez**
- Nas próximas conexões, não aparecerá mais esta mensagem

---

**Resumo:** Digite `yes` e continue! ✅

