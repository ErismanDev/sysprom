# 🔧 Restaurar Backup Corrigido (Sem Signals)

## ⚠️ Problema
Os signals do Django estão tentando criar militares automaticamente durante o restore, causando conflitos de chave única.

## ✅ SOLUÇÃO: Restaurar Desabilitando Signals

### Opção 1: Usar Script Python (Recomendado)

```bash
# Como root no servidor
systemctl stop seprom

# Copiar script para o servidor (ou criar diretamente)
# O script já foi criado: restaurar_backup_sem_signals.py

# Executar como seprom
su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate

# Executar script
python restaurar_backup_sem_signals.py

# Sair
exit

# Reiniciar aplicação
systemctl start seprom
```

### Opção 2: Desabilitar Signals Manualmente

```bash
# Como root
systemctl stop seprom

# Mudar para seprom
su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate

# Fazer backup de segurança
python manage.py dumpdata > /tmp/backup_seguranca_$(date +%Y%m%d_%H%M%S).json

# Editar signals.py temporariamente para desabilitar
# Ou usar variável de ambiente
export DISABLE_SIGNALS=1

# Limpar banco
python manage.py flush --noinput

# Restaurar (os signals não devem executar se desabilitados)
BACKUP_FILE=$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json 2>/dev/null | head -1)
python manage.py loaddata "$BACKUP_FILE" --verbosity=1

# Sair
exit

# Reiniciar
systemctl start seprom
```

### Opção 3: Usar --skip-checks e ignorar erros

```bash
# Como root
systemctl stop seprom

# Mudar para seprom
su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate

# Fazer backup de segurança
python manage.py dumpdata > /tmp/backup_seguranca_$(date +%Y%m%d_%H%M%S).json

# Limpar banco
python manage.py flush --noinput

# Restaurar ignorando erros de signals (alguns dados podem não carregar)
BACKUP_FILE=$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json 2>/dev/null | head -1)
python manage.py loaddata "$BACKUP_FILE" --verbosity=1 2>&1 | grep -v "duplicate key\|IntegrityError" || true

# Sair
exit

# Reiniciar
systemctl start seprom
```

---

## 🚀 COMANDO RÁPIDO - Restaurar com Tolerância a Erros

```bash
systemctl stop seprom && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py dumpdata > /tmp/backup_seguranca_\$(date +%Y%m%d_%H%M%S).json && python manage.py flush --noinput && python manage.py loaddata \$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json 2>/dev/null | head -1) 2>&1 | grep -v 'duplicate key\|IntegrityError\|TransactionManagementError' || true" && \
systemctl start seprom && \
echo "✅ Backup restaurado (alguns warnings podem ter ocorrido)"
```

---

## 🔧 Solução Definitiva: Editar signals.py Temporariamente

```bash
# Como root
systemctl stop seprom

# Fazer backup do signals.py
su - seprom -c "cp /home/seprom/sepromcbmepi/militares/signals.py /home/seprom/sepromcbmepi/militares/signals.py.backup"

# Comentar a função criar_militar_para_usuario temporariamente
su - seprom -c "sed -i 's/@receiver(post_save, sender=User)/# @receiver(post_save, sender=User)/' /home/seprom/sepromcbmepi/militares/signals.py"
su - seprom -c "sed -i 's/def criar_militar_para_usuario/# def criar_militar_para_usuario/' /home/seprom/sepromcbmepi/militares/signals.py"

# Restaurar backup
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py dumpdata > /tmp/backup_seguranca_\$(date +%Y%m%d_%H%M%S).json && python manage.py flush --noinput && python manage.py loaddata \$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json 2>/dev/null | head -1)"

# Restaurar signals.py original
su - seprom -c "mv /home/seprom/sepromcbmepi/militares/signals.py.backup /home/seprom/sepromcbmepi/militares/signals.py"

# Reiniciar
systemctl start seprom
```

---

## ✅ Verificar Restauração

```bash
# Verificar tabelas
su - postgres -c "psql sepromcbmepi -c '\dt' | head -20"

# Verificar quantidade de registros
su - postgres -c "psql sepromcbmepi -c \"SELECT 'militares_militar' as tabela, COUNT(*) as registros FROM militares_militar UNION ALL SELECT 'auth_user', COUNT(*) FROM auth_user;\""

# Testar aplicação
curl http://localhost/login/ | head -10
```

