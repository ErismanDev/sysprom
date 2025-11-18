# 💾 Backup Completo e Restauração no Digital Ocean

## 📋 Informações do Servidor

- **IP**: 64.23.185.235
- **Usuário SSH**: root
- **Banco de Dados**: sepromcbmepi
- **Usuário do Banco**: seprom

---

## 🚀 ETAPA 1: Fazer Backup no PC Local

### Opção 1: Usando o Script Python (Recomendado)

```powershell
# No PowerShell, no diretório do projeto
cd C:\projetos\Sysgabom

# Executar script de backup
python fazer_backup_completo_do.py
```

O script irá:
- ✅ Criar backup completo do banco local
- ✅ Validar o arquivo de backup
- ✅ Comprimir o backup (opcional)
- ✅ Criar script de restauração automático

### Opção 2: Usando pg_dump Diretamente

```powershell
# Definir senha do PostgreSQL
$env:PGPASSWORD="11322361"

# Criar backup
pg_dump -h localhost -U postgres -d sepromcbmepi -F p -b -v --clean --if-exists -f backup_sepromcbmepi_completo_$(Get-Date -Format "yyyyMMdd_HHmmss").sql
```

---

## 📤 ETAPA 2: Enviar Backup para o Servidor

### Opção A: Usando WinSCP (Recomendado para Windows)

1. Abra o WinSCP
2. Conecte ao servidor:
   - **Host**: 64.23.185.235
   - **Usuário**: root
   - **Senha**: (sua senha SSH)
3. Navegue até: `/home/seprom/sepromcbmepi/`
4. Arraste o arquivo de backup para o servidor
   - Exemplo: `backup_sepromcbmepi_completo_20241115_143000.sql`
   - Ou o arquivo comprimido: `backup_sepromcbmepi_completo_20241115_143000.sql.gz`
5. Se tiver o script de restauração, envie também: `restaurar_backup_do_*.sh`

### Opção B: Usando PowerShell (SCP)

```powershell
# Enviar arquivo de backup
scp backup_sepromcbmepi_completo_*.sql root@64.23.185.235:/home/seprom/sepromcbmepi/

# Ou se for comprimido
scp backup_sepromcbmepi_completo_*.sql.gz root@64.23.185.235:/home/seprom/sepromcbmepi/

# Enviar script de restauração (se tiver)
scp restaurar_backup_do_*.sh root@64.23.185.235:/home/seprom/sepromcbmepi/
```

---

## 🔄 ETAPA 3: Restaurar no Servidor Digital Ocean

### Opção A: Usando Script Automático (Recomendado)

```bash
# Conectar ao servidor
ssh root@64.23.185.235

# Ir para o diretório do projeto
cd /home/seprom/sepromcbmepi

# Tornar script executável
chmod +x restaurar_backup_do_*.sh

# Executar script de restauração
./restaurar_backup_do_*.sh
```

O script irá automaticamente:
- ✅ Parar a aplicação
- ✅ Fazer backup de segurança do banco atual
- ✅ Limpar o banco atual
- ✅ Restaurar o novo backup
- ✅ Verificar a restauração
- ✅ Reiniciar a aplicação

### Opção B: Comandos Manuais

```bash
# 1. Conectar ao servidor
ssh root@64.23.185.235

# 2. Ir para o diretório do projeto
cd /home/seprom/sepromcbmepi

# 3. Parar aplicação
systemctl stop seprom

# 4. Fazer backup de segurança do banco atual
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql"

# 5. Limpar banco atual
su - postgres << 'EOF'
psql << SQL
-- Terminar conexões ativas
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'sepromcbmepi' AND pid <> pg_backend_pid();

-- Dropar e recriar banco
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF

# 6. Restaurar backup
# Se o arquivo estiver comprimido:
gunzip -c backup_sepromcbmepi_completo_*.sql.gz | su - postgres -c "psql sepromcbmepi"

# Se o arquivo NÃO estiver comprimido:
su - postgres -c "psql sepromcbmepi < backup_sepromcbmepi_completo_*.sql"

# 7. Verificar restauração
su - postgres -c "psql sepromcbmepi -c '\dt' | head -20"

# 8. Reiniciar aplicação
systemctl start seprom

# 9. Verificar status
systemctl status seprom
```

---

## 🔍 Verificar Restauração

```bash
# Verificar tabelas
su - postgres -c "psql sepromcbmepi -c '\dt'"

# Contar tabelas
su - postgres -c "psql sepromcbmepi -t -c \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';\""

# Verificar algumas tabelas importantes
su - postgres -c "psql sepromcbmepi -c \"SELECT COUNT(*) FROM militares_militar;\""
su - postgres -c "psql sepromcbmepi -c \"SELECT COUNT(*) FROM auth_user;\""

# Verificar logs da aplicação
journalctl -u seprom -f

# Testar aplicação
curl http://localhost/ | head -20
```

---

## ⚠️ Troubleshooting

### Erro: "permission denied"

```bash
# Ajustar permissões do arquivo de backup
chmod 644 /home/seprom/sepromcbmepi/backup_*.sql
chown seprom:seprom /home/seprom/sepromcbmepi/backup_*.sql
```

### Erro: "database does not exist"

```bash
# Criar banco se não existir
su - postgres -c "psql -c 'CREATE DATABASE sepromcbmepi OWNER seprom;'"
```

### Erro: "database is being accessed by other users"

```bash
# Terminar todas as conexões
su - postgres -c "psql -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'sepromcbmepi' AND pid <> pg_backend_pid();\""
```

### Backup muito grande

Se o backup for muito grande, use compressão:

```powershell
# No Windows, comprimir antes de enviar
Compress-Archive -Path backup_sepromcbmepi_completo_*.sql -DestinationPath backup_sepromcbmepi_completo_*.zip
```

No servidor:

```bash
# Descomprimir
unzip backup_sepromcbmepi_completo_*.zip
```

### Restauração lenta

Para bancos muito grandes, pode levar vários minutos. Monitore o progresso:

```bash
# Em outro terminal, verificar progresso
watch -n 1 "su - postgres -c \"psql sepromcbmepi -c 'SELECT COUNT(*) FROM information_schema.tables;'\""
```

---

## 📝 Notas Importantes

1. **Sempre faça backup antes de restaurar** - O script faz backup automático, mas é bom ter um manual também
2. **Formato recomendado**: Use `.sql` (texto) para maior compatibilidade
3. **Tamanho do arquivo**: Se for muito grande (>100MB), use compressão
4. **Tempo**: A restauração pode levar alguns minutos dependendo do tamanho
5. **Downtime**: A aplicação ficará offline durante a restauração
6. **Teste primeiro**: Se possível, teste a restauração em um ambiente de desenvolvimento antes

---

## 🆘 Comandos de Emergência

### Restaurar backup de segurança

```bash
# Se algo der errado, restaurar backup de segurança
BACKUP_SEGURANCA=$(ls -t /tmp/sepromcbmepi_backup_seguranca_*.sql | head -1)
if [ -n "$BACKUP_SEGURANCA" ]; then
    systemctl stop seprom
    su - postgres -c "psql -c 'DROP DATABASE IF EXISTS sepromcbmepi;'"
    su - postgres -c "psql -c 'CREATE DATABASE sepromcbmepi OWNER seprom;'"
    su - postgres -c "psql sepromcbmepi < $BACKUP_SEGURANCA"
    systemctl start seprom
fi
```

### Verificar espaço em disco

```bash
# Verificar espaço disponível
df -h

# Verificar tamanho do backup
ls -lh /home/seprom/sepromcbmepi/backup_*.sql
```

---

## ✅ Checklist de Restauração

- [ ] Backup criado no PC local
- [ ] Arquivo enviado para o servidor
- [ ] Backup de segurança do banco atual feito
- [ ] Aplicação parada
- [ ] Banco limpo e recriado
- [ ] Backup restaurado com sucesso
- [ ] Tabelas verificadas
- [ ] Aplicação reiniciada
- [ ] Aplicação testada e funcionando

---

**Última atualização**: 2024-11-15

