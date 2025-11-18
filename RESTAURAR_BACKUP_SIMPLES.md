# 🔧 Restaurar Backup - Versão Simples (Sem Privilégios Especiais)

## ✅ SOLUÇÃO SIMPLES

O erro anterior foi por falta de permissão. Esta versão funciona sem privilégios especiais:

```bash
systemctl stop seprom && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && pip install -q python-dateutil==2.9.0" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python restaurar_backup_sem_signals.py" && \
systemctl start seprom && \
echo "✅ Restauração concluída!"
```

---

## 🔧 OU: Restaurar Manualmente (Passo a Passo)

```bash
# 1. Parar aplicação
systemctl stop seprom

# 2. Instalar dateutil
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && pip install python-dateutil==2.9.0"

# 3. Restaurar backup
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python restaurar_backup_sem_signals.py"

# 4. Se houver erros de foreign key, limpar dados órfãos
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py shell << 'PYEOF'
from militares.models import FichaConceitoOficiais, FichaConceitoPracas, Militar
militares_ids = set(Militar.objects.values_list('id', flat=True))
deleted_o = FichaConceitoOficiais.objects.exclude(militar_id__in=militares_ids).delete()
deleted_p = FichaConceitoPracas.objects.exclude(militar_id__in=militares_ids).delete()
print(f'✅ Removidos {deleted_o[0]} fichas de oficiais e {deleted_p[0]} fichas de praças órfãs')
PYEOF
"

# 5. Reiniciar
systemctl start seprom
```

---

## 📝 O Script Atualizado

O script `restaurar_backup_sem_signals.py` foi atualizado para:
- Usar `SET CONSTRAINTS ALL DEFERRED` (não requer privilégios especiais)
- Limpar dados órfãos automaticamente após o restore
- Continuar mesmo se houver alguns erros

---

## ✅ Verificar Restauração

```bash
# Verificar aplicação
curl http://localhost/login/ | head -10

# Verificar logs
sudo journalctl -u seprom -n 50 --no-pager

# Verificar status
sudo systemctl status seprom --no-pager
```

