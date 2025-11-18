# 🔍 VERIFICAR E CORRIGIR PROBLEMA DE CACHE

## ⚠️ PROBLEMA
Mesmo após atualizar o arquivo, os logs ainda mostram linha 221 (versão antiga).

## 🔍 POSSÍVEIS CAUSAS

### 1. Cache do Navegador (Mais Comum)
O navegador está usando uma versão antiga em cache.

**Solução**:
- **Chrome/Edge**: 
  - `Ctrl+Shift+Delete` → Marcar "Imagens e arquivos em cache" → Limpar dados
  - Ou: `Ctrl+Shift+R` (hard refresh)
  - Ou: Modo anônimo (`Ctrl+Shift+N`)
  
- **Firefox**:
  - `Ctrl+Shift+Delete` → Marcar "Cache" → Limpar agora
  - Ou: `Ctrl+F5` (hard refresh)

### 2. Arquivos Estáticos Coletados (Django)
O Django pode ter coletado os arquivos estáticos para a pasta `staticfiles`, e o servidor está servindo de lá.

**Verificar**:
```bash
ssh root@64.23.185.235
cd /home/seprom/sepromcbmepi
ls -la staticfiles/js/chat-calls.js
```

**Solução**:
```bash
ssh root@64.23.185.235
cd /home/seprom/sepromcbmepi
# Copiar arquivo atualizado para staticfiles também
cp static/js/chat-calls.js staticfiles/js/chat-calls.js
# Ou recolher arquivos estáticos
python manage.py collectstatic --noinput
```

### 3. Arquivo Não Foi Atualizado no Servidor
O arquivo pode não ter sido copiado corretamente.

**Verificar**:
```bash
ssh root@64.23.185.235
grep -n "Exibindo video remoto" /home/seprom/sepromcbmepi/static/js/chat-calls.js
```

**Resultado esperado**:
- ✅ Se mostrar linha ~329 com "(condicoes atendidas)": Arquivo atualizado
- ❌ Se mostrar linha ~221 sem "(condicoes atendidas)": Arquivo não foi atualizado

### 4. Nginx Cache
O Nginx pode estar fazendo cache dos arquivos estáticos.

**Solução**:
```bash
ssh root@64.23.185.235
# Recarregar Nginx
systemctl reload nginx
# Ou reiniciar
systemctl restart nginx
```

## 📋 CHECKLIST DE VERIFICAÇÃO

Execute estes comandos para verificar:

```bash
# 1. Verificar arquivo no servidor
ssh root@64.23.185.235 "grep -n 'Exibindo video remoto (condicoes atendidas)' /home/seprom/sepromcbmepi/static/js/chat-calls.js"

# 2. Verificar se existe em staticfiles
ssh root@64.23.185.235 "ls -la /home/seprom/sepromcbmepi/staticfiles/js/chat-calls.js 2>/dev/null && echo 'EXISTE' || echo 'NAO EXISTE'"

# 3. Verificar tamanho do arquivo (deve ser ~40-50KB)
ssh root@64.23.185.235 "ls -lh /home/seprom/sepromcbmepi/static/js/chat-calls.js"
```

## ✅ SOLUÇÃO COMPLETA (Execute Todos os Passos)

```bash
# 1. Conectar ao servidor
ssh root@64.23.185.235

# 2. Atualizar arquivo principal
cd /home/seprom/sepromcbmepi
# (Copie o arquivo via WinSCP ou SCP aqui)

# 3. Verificar se foi atualizado
grep -n "Exibindo video remoto (condicoes atendidas)" static/js/chat-calls.js

# 4. Se existir staticfiles, atualizar também
if [ -f "staticfiles/js/chat-calls.js" ]; then
    cp static/js/chat-calls.js staticfiles/js/chat-calls.js
    echo "Arquivo atualizado em staticfiles também"
fi

# 5. Recarregar Nginx
systemctl reload nginx

# 6. Verificar permissões
chmod 644 static/js/chat-calls.js
if [ -f "staticfiles/js/chat-calls.js" ]; then
    chmod 644 staticfiles/js/chat-calls.js
fi
```

## 🔍 VERIFICAR NO NAVEGADOR

1. **Abrir console** (F12)
2. **Ir para aba "Network" ou "Rede"**
3. **Recarregar página** (Ctrl+R)
4. **Filtrar por "chat-calls.js"**
5. **Clicar no arquivo**
6. **Verificar conteúdo na aba "Response" ou "Resposta"**
7. **Procurar por**: `Exibindo video remoto (condicoes atendidas)`
   - ✅ Se encontrar: Arquivo atualizado, mas cache do navegador não foi limpo
   - ❌ Se não encontrar: Arquivo não foi atualizado no servidor

## 🎯 SOLUÇÃO DEFINITIVA

Se nada funcionar, tente:

1. **Atualizar arquivo no servidor** (WinSCP)
2. **Atualizar também em staticfiles** (se existir)
3. **Recarregar Nginx**: `systemctl reload nginx`
4. **Limpar cache do navegador completamente**
5. **Abrir em modo anônimo** (Ctrl+Shift+N)
6. **Testar novamente**

---

**Última atualização**: 2024-11-16

