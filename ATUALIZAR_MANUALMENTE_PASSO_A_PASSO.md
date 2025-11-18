# 📤 COMO ATUALIZAR chat-calls.js NO SERVIDOR - PASSO A PASSO

## ⚠️ PROBLEMA ATUAL
O arquivo no servidor está desatualizado. O log mostra linha 221, mas deveria mostrar linha 329.

## ✅ SOLUÇÃO: Atualizar Manualmente

### OPÇÃO 1: Usar WinSCP (RECOMENDADO - Mais Fácil)

1. **Baixar WinSCP** (se não tiver):
   - Acesse: https://winscp.net/eng/download.php
   - Baixe e instale

2. **Conectar ao servidor**:
   - Abra o WinSCP
   - Clique em "Nova Sessão"
   - Preencha:
     - **Protocolo**: SFTP
     - **Nome do host**: `64.23.185.235`
     - **Nome de usuário**: `root`
     - **Senha**: `erismaN@193a`
   - Clique em "Login"

3. **Navegar até a pasta**:
   - No painel direito (servidor), navegue até:
     `/home/seprom/sepromcbmepi/static/js/`

4. **Fazer backup** (IMPORTANTE):
   - Clique com botão direito em `chat-calls.js`
   - Escolha "Renomear"
   - Renomeie para: `chat-calls.js.backup_20241116`

5. **Copiar arquivo local**:
   - No painel esquerdo (seu computador), navegue até:
     `C:\projetos\Sysgabom\static\js\`
   - Arraste o arquivo `chat-calls.js` do painel esquerdo para o painel direito
   - Confirme a substituição

6. **Verificar se foi atualizado**:
   - Clique com botão direito no arquivo `chat-calls.js` no servidor
   - Escolha "Editar"
   - Procure por: `Exibindo video remoto (condicoes atendidas)`
   - Se encontrar, o arquivo foi atualizado! ✅
   - Feche o editor

---

### OPÇÃO 2: Usar PowerShell (Linha de Comando)

1. **Abrir PowerShell**

2. **Navegar até a pasta do projeto**:
   ```powershell
   cd C:\projetos\Sysgabom
   ```

3. **Copiar arquivo para o servidor**:
   ```powershell
   scp static/js/chat-calls.js root@64.23.185.235:/home/seprom/sepromcbmepi/static/js/chat-calls.js
   ```
   - Quando pedir a senha, digite: `erismaN@193a`

4. **Verificar se foi atualizado**:
   ```powershell
   ssh root@64.23.185.235 "grep -n 'Exibindo video remoto (condicoes atendidas)' /home/seprom/sepromcbmepi/static/js/chat-calls.js"
   ```
   - Se mostrar uma linha (ex: `329:...`), o arquivo foi atualizado! ✅

---

## 🔍 COMO VERIFICAR SE O ARQUIVO FOI ATUALIZADO

### No Servidor (via SSH):
```bash
ssh root@64.23.185.235
grep -n "Exibindo video remoto" /home/seprom/sepromcbmepi/static/js/chat-calls.js
```

**Resultado esperado**:
- ✅ Se mostrar linha ~329 com "(condicoes atendidas)": Arquivo atualizado!
- ❌ Se mostrar linha ~221 sem "(condicoes atendidas)": Arquivo ainda desatualizado

### No Navegador (após limpar cache):

1. **Limpar cache do navegador** (OBRIGATÓRIO):
   - Chrome/Edge: `Ctrl+Shift+Delete` → Marcar "Imagens e arquivos em cache" → Limpar dados
   - Ou: `Ctrl+Shift+R` (hard refresh)
   - Ou: Abrir em modo anônimo (`Ctrl+Shift+N`)

2. **Verificar no console**:
   - Abrir console (F12)
   - Ir para aba "Sources" ou "Fontes"
   - Navegar até: `static/js/chat-calls.js`
   - Procurar por: `Exibindo video remoto`
   - Se encontrar na linha ~329 com "(condicoes atendidas)": Arquivo atualizado! ✅
   - Se encontrar na linha ~221 sem "(condicoes atendidas)": Cache não foi limpo ou arquivo não foi atualizado

---

## ⚠️ SE O ARQUIVO AINDA NÃO ATUALIZAR

1. **Verificar permissões**:
   ```bash
   ssh root@64.23.185.235 "ls -la /home/seprom/sepromcbmepi/static/js/chat-calls.js"
   ```
   - Deve mostrar: `-rw-r--r--` (644)

2. **Corrigir permissões se necessário**:
   ```bash
   ssh root@64.23.185.235 "chmod 644 /home/seprom/sepromcbmepi/static/js/chat-calls.js"
   ```

3. **Reiniciar Nginx** (se necessário):
   ```bash
   ssh root@64.23.185.235 "systemctl reload nginx"
   ```

4. **Limpar cache do navegador novamente**

---

## 📋 APÓS ATUALIZAR

1. ✅ **Limpar cache do navegador** (OBRIGATÓRIO)
2. ✅ **Verificar no console** se o arquivo foi atualizado
3. ✅ **Testar novamente** com duas pessoas
4. ✅ **Verificar logs** quando o outro lado aceitar a chamada

---

**Última atualização**: 2024-11-16

