# ✅ Criar Banco Limpo (Sem Backup)

## 🚀 Comandos para Criar Banco Limpo

Execute no servidor Digital Ocean:

```bash
# Parar serviços
systemctl stop seprom 2>/dev/null || true

# Deletar e recriar banco
su - postgres << 'EOF'
psql << SQL
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF

# Mudar para usuário seprom
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate

# Executar migrações até 0073
python manage.py migrate militares 0073

# Marcar 0074 como fake (tem problema com campo removido)
python manage.py migrate militares 0074 --fake

# Continuar com outras migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar superusuário
python manage.py createsuperuser
EOF

# Reiniciar serviços
systemctl start seprom
systemctl status seprom

echo "✅ Banco criado com sucesso!"
```

---

## 🔧 Se Der Erro na Migração 0074

Se ainda der erro, use este comando para marcar como fake diretamente no banco:

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate

# Marcar 0074 como aplicada diretamente no banco
python manage.py shell << 'PYEOF'
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("""
        INSERT INTO django_migrations (app, name, applied)
        VALUES ('militares', '0074_remove_unique_together_usuario_funcao', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("✅ Migração 0074 marcada como fake")
PYEOF

# Continuar migrações
python manage.py migrate

# Coletar estáticos
python manage.py collectstatic --noinput

# Criar superusuário
python manage.py createsuperuser
EOF
```

