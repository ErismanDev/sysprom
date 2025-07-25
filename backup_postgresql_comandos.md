# Backup do Banco de Dados PostgreSQL - SEPROMCBMEPI

## Configurações do Banco
- **Nome do banco**: sepromcbmepi
- **Usuário**: postgres
- **Senha**: postgres123
- **Host**: localhost
- **Porta**: 5432

## Comandos para Backup

### 1. Backup Completo (Estrutura + Dados)
```bash
# Criar diretório de backup
mkdir backups

# Fazer backup completo
pg_dump --host=localhost --port=5432 --username=postgres --dbname=sepromcbmepi --verbose --clean --no-owner --no-privileges --file=backups/sepromcbmepi_backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Backup Apenas dos Dados
```bash
pg_dump --host=localhost --port=5432 --username=postgres --dbname=sepromcbmepi --data-only --verbose --file=backups/sepromcbmepi_dados_$(date +%Y%m%d_%H%M%S).sql
```

### 3. Backup Apenas da Estrutura (Schema)
```bash
pg_dump --host=localhost --port=5432 --username=postgres --dbname=sepromcbmepi --schema-only --verbose --file=backups/sepromcbmepi_schema_$(date +%Y%m%d_%H%M%S).sql
```

### 4. Backup Compactado (Gzip)
```bash
pg_dump --host=localhost --port=5432 --username=postgres --dbname=sepromcbmepi --verbose --clean --no-owner --no-privileges | gzip > backups/sepromcbmepi_backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

## Comandos para Restauração

### 1. Restaurar Backup Completo
```bash
psql --host=localhost --port=5432 --username=postgres --dbname=sepromcbmepi --file=backups/nome_do_arquivo_backup.sql
```

### 2. Restaurar Backup Compactado
```bash
gunzip -c backups/nome_do_arquivo_backup.sql.gz | psql --host=localhost --port=5432 --username=postgres --dbname=sepromcbmepi
```

## Usando o Script Python

### Backup Completo
```bash
python backup_postgresql.py backup
```

### Backup Apenas dos Dados
```bash
python backup_postgresql.py dados
```

### Listar Backups Existentes
```bash
python backup_postgresql.py listar
```

### Restaurar Backup
```bash
python backup_postgresql.py restaurar backups/nome_do_arquivo.sql
```

## Dicas Importantes

1. **Sempre faça backup antes de atualizações importantes**
2. **Mantenha múltiplas versões de backup**
3. **Teste a restauração em ambiente de desenvolvimento**
4. **Configure backups automáticos se possível**
5. **Monitore o espaço em disco dos backups**

## Backup Automático (Cron - Linux/Mac)

Adicione ao crontab para backup diário às 2h da manhã:
```bash
0 2 * * * /usr/bin/pg_dump --host=localhost --port=5432 --username=postgres --dbname=sepromcbmepi --file=/caminho/para/backups/sepromcbmepi_backup_$(date +\%Y\%m\%d).sql
```

## Backup Automático (Windows - Task Scheduler)

Crie uma tarefa agendada executando:
```cmd
pg_dump --host=localhost --port=5432 --username=postgres --dbname=sepromcbmepi --file=C:\backups\sepromcbmepi_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.sql
``` 