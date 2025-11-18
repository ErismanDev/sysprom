# 📁 Conectar ao Servidor Digital Ocean via WinSCP

**IP do Servidor:** 64.23.185.235

## 📋 Configuração Básica do WinSCP

### Passo 1: Abrir WinSCP

1. Abra o programa **WinSCP**
2. Se for a primeira vez, a janela de login aparecerá automaticamente
3. Se não aparecer, clique em **"Nova Sessão"** ou **"New Session"**

### Passo 2: Preencher Dados de Conexão

Na tela de login, preencha:

```
Protocolo: SFTP (recomendado) ou SCP
Host name: 64.23.185.235
Port number: 22
User name: root
Password: [sua senha do servidor]
```

### Passo 3: Salvar Sessão (Opcional mas Recomendado)

1. Clique em **"Salvar"** ou **"Save"**
2. Dê um nome: `Digital Ocean - SEPROM`
3. Clique em **"OK"**
4. Agora você pode usar **"Login"** para conectar rapidamente

### Passo 4: Conectar

1. Clique em **"Login"** ou **"Conectar"**
2. Na primeira vez, aparecerá uma mensagem sobre autenticidade do servidor
3. Clique em **"Sim"** ou **"Yes"** para aceitar
4. Digite a senha se solicitado
5. Aguarde a conexão ser estabelecida

---

## 🔐 Configurações Avançadas

### Usar Chave SSH (Recomendado para Segurança)

1. Na tela de login, clique em **"Avançado"** ou **"Advanced"**
2. Vá em **"SSH"** → **"Autenticação"** ou **"Authentication"**
3. Em **"Arquivo de chave privada"**, clique em **"..."**
4. Selecione sua chave privada (arquivo `.ppk` ou `.pem`)
5. Se necessário, converta `.pem` para `.ppk` usando PuTTYgen
6. Clique em **"OK"**

### Configurações de Performance

1. Clique em **"Avançado"** ou **"Advanced"**
2. Vá em **"Conexão"** ou **"Connection"**
3. Ajuste:
   - **Timeout:** 30 segundos
   - **Keepalive:** Ativar
   - **Intervalo:** 30 segundos

### Configurações de Transferência

1. Vá em **"Transferências"** ou **"Transfers"**
2. Configure:
   - **Modo de transferência:** Binário (para arquivos Python)
   - **Preservar timestamp:** Ativar
   - **Preservar permissões:** Ativar (importante para Linux)

---

## 📤 Enviar Arquivos para o Servidor

### Método 1: Arrastar e Soltar

1. **Painel Esquerdo (Local):** Navegue até a pasta do seu projeto no Windows
   - Exemplo: `C:\projetos\Sysgabom`

2. **Painel Direito (Servidor):** Navegue até o diretório destino
   - Exemplo: `/home/seprom/sepromcbmepi`

3. **Arraste os arquivos** do painel esquerdo para o direito
4. Aguarde o upload completar

### Método 2: Menu de Upload

1. Selecione os arquivos no painel esquerdo (local)
2. Clique com botão direito → **"Upload"** ou **"Enviar"**
3. Escolha o diretório destino no servidor
4. Clique em **"OK"**

### Método 3: Comando Sincronizar

1. Vá em **"Comandos"** → **"Sincronizar diretórios"** ou **"Synchronize"**
2. Escolha diretório local e remoto
3. Configure opções de sincronização
4. Clique em **"OK"**

---

## 📋 Diretórios Importantes

### No Servidor (Diretório Destino)

```
/home/seprom/sepromcbmepi/
```

### Estrutura de Pastas no Servidor

```
/home/seprom/sepromcbmepi/
├── manage.py
├── requirements.txt
├── requirements_production.txt
├── gunicorn.conf.py
├── nginx_seprom.conf
├── sepromcbmepi/
├── militares/
├── templates/
├── static/
└── ...
```

---

## ⚠️ Arquivos que NÃO devem ser Enviados

O WinSCP respeitará o `.gitignore`, mas certifique-se de NÃO enviar:

- `venv/` (ambiente virtual - será criado no servidor)
- `__pycache__/`
- `*.pyc`
- `.env` (criar no servidor com dados de produção)
- `db.sqlite3` (se usar SQLite local)
- Arquivos de backup grandes

---

## 🔧 Configurações Recomendadas

### Preservar Permissões

1. Vá em **"Preferências"** → **"Transferências"**
2. Marque **"Preservar permissões"**
3. Isso é importante para arquivos executáveis

### Modo de Transferência

1. Vá em **"Preferências"** → **"Transferências"**
2. Selecione **"Binário"** como padrão
3. Isso evita problemas com arquivos Python

### Mostrar Arquivos Ocultos

1. No painel do servidor, vá em **"Opções"** → **"Preferências"**
2. Marque **"Mostrar arquivos ocultos"**
3. Isso mostra arquivos como `.env`, `.gitignore`, etc.

---

## 🚀 Passo a Passo Completo

### 1. Conectar ao Servidor

```
Protocolo: SFTP
Host: 64.23.185.235
Porta: 22
Usuário: root
Senha: [sua senha]
```

### 2. Navegar até o Diretório

No servidor, vá para:
```
/home/seprom/sepromcbmepi/
```

Se o diretório não existir, crie:
- Clique com botão direito → **"Novo"** → **"Diretório"**
- Nome: `sepromcbmepi`
- Ou use o terminal integrado do WinSCP

### 3. Enviar Arquivos

- Selecione todos os arquivos do projeto no painel esquerdo
- Arraste para o painel direito (servidor)
- Aguarde o upload

### 4. Verificar Permissões (Importante!)

Após enviar, no terminal do WinSCP (ou via SSH):

```bash
cd /home/seprom/sepromcbmepi
sudo chown -R seprom:seprom .
chmod +x manage.py
```

---

## 🛠️ Terminal Integrado do WinSCP

O WinSCP tem um terminal integrado:

1. Clique em **"Terminal"** ou **"Commands"** → **"Abrir Terminal"**
2. Execute comandos diretamente no servidor
3. Útil para criar diretórios, ajustar permissões, etc.

### Comandos Úteis no Terminal do WinSCP

```bash
# Criar diretório se não existir
mkdir -p /home/seprom/sepromcbmepi

# Verificar arquivos enviados
ls -la /home/seprom/sepromcbmepi

# Ajustar permissões
chmod +x manage.py
chmod -R 755 /home/seprom/sepromcbmepi

# Verificar espaço em disco
df -h
```

---

## 🔐 Segurança

### Usar Chave SSH em vez de Senha

1. Gere chave SSH no Windows usando PuTTYgen
2. Adicione a chave pública no servidor: `~/.ssh/authorized_keys`
3. Configure WinSCP para usar a chave privada
4. Mais seguro que senha

### Desabilitar Senha após Configurar Chave

No servidor:
```bash
sudo nano /etc/ssh/sshd_config
# Altere: PasswordAuthentication no
sudo systemctl restart ssh
```

---

## 📝 Checklist de Upload

Antes de enviar, verifique:

- [ ] `.gitignore` está atualizado
- [ ] `venv/` não será enviado
- [ ] `.env` será criado no servidor (não enviar o local)
- [ ] Arquivos de backup não serão enviados
- [ ] Diretório destino existe: `/home/seprom/sepromcbmepi/`
- [ ] Permissões serão ajustadas após upload

---

## 🆘 Troubleshooting

### Erro: "Connection refused"
- Verifique se SSH está rodando no servidor
- Use o console web do Digital Ocean para iniciar SSH

### Erro: "Permission denied"
- Verifique usuário e senha
- Verifique permissões do diretório no servidor

### Upload muito lento
- Verifique conexão de internet
- Tente usar modo binário
- Desative verificação de integridade temporariamente

### Arquivos não aparecem
- Atualize a visualização (F5)
- Verifique se está no diretório correto
- Verifique filtros de exibição

---

## 📋 Resumo Rápido

1. **Abrir WinSCP**
2. **Nova Sessão:**
   - Protocolo: SFTP
   - Host: 64.23.185.235
   - Porta: 22
   - Usuário: root
   - Senha: [sua senha]
3. **Conectar**
4. **Navegar para:** `/home/seprom/sepromcbmepi/`
5. **Arrastar arquivos** do Windows para o servidor
6. **Ajustar permissões** após upload

---

## 💡 Dica Pro

Salve a sessão no WinSCP para conectar rapidamente depois:
- Clique em **"Salvar"** na tela de login
- Dê um nome: `Digital Ocean SEPROM`
- Na próxima vez, apenas selecione e clique em **"Login"**

