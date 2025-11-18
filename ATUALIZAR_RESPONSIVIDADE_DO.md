# 📱 Atualizar Responsividade no Digital Ocean

Este guia mostra como atualizar o arquivo `base.html` com as melhorias de responsividade para smartphones no servidor Digital Ocean.

## 📋 Informações do Servidor

- **IP**: 64.23.185.235
- **Usuário**: root
- **Caminho**: `/home/seprom/sepromcbmepi/templates/base.html`

---

## 🚀 OPÇÃO 1: Usar Script Automático (Recomendado)

### Windows (PowerShell)

```powershell
# Execute o script PowerShell
.\ATUALIZAR_BASE_HTML_DO.ps1
```

### Windows (CMD/Batch)

```cmd
# Execute o arquivo batch
ATUALIZAR_BASE_HTML_DO.bat
```

### Linux/Mac/Git Bash

```bash
# Dar permissão de execução
chmod +x ATUALIZAR_BASE_HTML_DO.sh

# Executar
./ATUALIZAR_BASE_HTML_DO.sh
```

---

## 📤 OPÇÃO 2: Upload Manual via WinSCP

1. **Abrir WinSCP** e conectar ao servidor:
   - Host: `64.23.185.235`
   - Usuário: `root`
   - Senha: (sua senha SSH)

2. **Navegar até o diretório**:
   ```
   /home/seprom/sepromcbmepi/templates/
   ```

3. **Fazer backup do arquivo atual**:
   - Clique com botão direito em `base.html`
   - Selecione "Renomear"
   - Renomeie para `base.html.backup_YYYYMMDD_HHMMSS`

4. **Fazer upload do novo arquivo**:
   - Arraste o arquivo `templates/base.html` do seu computador
   - Para a pasta `/home/seprom/sepromcbmepi/templates/` no servidor

---

## 📤 OPÇÃO 3: Upload Manual via SCP (PowerShell/CMD)

```powershell
# No PowerShell ou CMD, no diretório do projeto
scp templates/base.html root@64.23.185.235:/home/seprom/sepromcbmepi/templates/base.html
```

---

## 🔄 APÓS FAZER O UPLOAD - Comandos no Servidor

### Passo 1: Conectar ao Servidor

```bash
ssh root@64.23.185.235
```

### Passo 2: Executar Comandos de Atualização

```bash
# Ir para o diretório do projeto
cd /home/seprom/sepromcbmepi

# Ativar ambiente virtual
source venv/bin/activate

# Coletar arquivos estáticos (importante para templates)
python manage.py collectstatic --noinput

# Reiniciar o serviço Gunicorn
sudo systemctl restart seprom

# Verificar se reiniciou corretamente
sudo systemctl status seprom
```

### ⚡ COMANDO ÚNICO (Copie e Cole Tudo de Uma Vez)

```bash
cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py collectstatic --noinput && sudo systemctl restart seprom && sudo systemctl status seprom
```

---

## ✅ Verificação

### 1. Verificar Status do Serviço

```bash
sudo systemctl status seprom
```

Deve mostrar: `Active: active (running)`

### 2. Verificar Logs (se houver erro)

```bash
# Logs do Gunicorn
sudo journalctl -u seprom -n 50 --no-pager

# Logs do Nginx
sudo tail -n 50 /var/log/nginx/seprom_error.log
```

### 3. Testar no Navegador

1. **Limpar cache do navegador**:
   - Chrome/Edge: `Ctrl + Shift + Delete`
   - Ou usar modo anônimo: `Ctrl + Shift + N`

2. **Acessar o sistema** e verificar:
   - Em smartphone ou redimensionando a janela do navegador
   - A sidebar deve aparecer como menu hambúrguer
   - O layout deve se adaptar ao tamanho da tela

---

## 🆘 Troubleshooting

### Problema: Serviço não inicia

```bash
# Verificar erros detalhados
sudo journalctl -u seprom -n 100 --no-pager

# Verificar permissões
ls -la /home/seprom/sepromcbmepi/templates/base.html

# Verificar se o arquivo foi atualizado
grep -n "RESPONSIVIDADE PARA SMARTPHONES" /home/seprom/sepromcbmepi/templates/base.html
```

### Problema: Mudanças não aparecem no navegador

1. **Limpar cache do navegador** completamente
2. **Verificar se os arquivos estáticos foram coletados**:
   ```bash
   ls -la /home/seprom/sepromcbmepi/staticfiles/
   ```
3. **Forçar recarregamento do Nginx**:
   ```bash
   sudo systemctl reload nginx
   ```

### Problema: Erro de permissão

```bash
# Corrigir permissões
sudo chown -R seprom:seprom /home/seprom/sepromcbmepi
sudo chmod -R 755 /home/seprom/sepromcbmepi
```

---

## 📝 Notas Importantes

- ⚠️ **Sempre faça backup** antes de atualizar arquivos em produção
- 🔄 **Reinicie o serviço** após atualizar templates
- 🧹 **Limpe o cache** do navegador para ver as mudanças
- 📱 **Teste em diferentes dispositivos** para garantir a responsividade

---

## 🎯 O Que Foi Atualizado

As melhorias de responsividade incluem:

- ✅ Sidebar responsiva com menu hambúrguer em mobile
- ✅ Navbar otimizado para telas pequenas
- ✅ Cards e informações ajustados para mobile
- ✅ Tabelas com scroll horizontal suave
- ✅ Formulários otimizados para toque
- ✅ Modais ajustados para mobile
- ✅ Media queries para diferentes tamanhos de tela

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs do servidor
2. Confirme que o arquivo foi copiado corretamente
3. Verifique as permissões dos arquivos
4. Teste em modo anônimo do navegador

