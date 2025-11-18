# ✅ Verificar Importação do Excel

## 🔍 Comandos para Verificar se a Importação Funcionou

### Verificar Quantos Registros Foram Importados

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python manage.py shell << 'PYEOF'
from django.contrib.auth.models import User
from militares.models import Militar, QuadroAcesso, Promocao

print("📊 Verificando importação...")
print("")
print(f"✅ Usuários: {User.objects.count()}")
print(f"✅ Militares: {Militar.objects.count()}")
print(f"✅ Quadros de Acesso: {QuadroAcesso.objects.count()}")
print(f"✅ Promoções: {Promocao.objects.count()}")
print("")
print("✅ Verificação concluída!")
PYEOF
EOF
```

---

### Verificar um Usuário Específico

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.filter(username='33888647304').first(); print(f'Usuário encontrado: {u.username if u else \"Não encontrado\"}'); print(f'Superusuário: {u.is_superuser if u else False}')"
EOF
```

---

### Verificar um Militar Específico

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python manage.py shell -c "from militares.models import Militar; m = Militar.objects.first(); print(f'Primeiro militar: {m.nome_completo if m else \"Nenhum militar\"}')"
EOF
```

---

## 🔧 Se Houver Erros

### Verificar Logs do Script

```bash
# Se o script gerou algum erro, verifique
cat /home/seprom/sepromcbmepi/importar_banco_excel.py | head -20
```

### Verificar se o Arquivo Excel Existe

```bash
ls -lh /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.xlsx
```

### Verificar Dependências

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
pip list | grep -E "pandas|openpyxl"
EOF
```

---

## 📋 Comando Completo de Verificação

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate

echo "📊 Verificando importação..."
echo ""

python manage.py shell << 'PYEOF'
from django.contrib.auth.models import User
from militares.models import Militar, QuadroAcesso, Promocao

usuarios = User.objects.count()
militares = Militar.objects.count()
quadros = QuadroAcesso.objects.count()
promocoes = Promocao.objects.count()

print(f"✅ Usuários: {usuarios}")
print(f"✅ Militares: {militares}")
print(f"✅ Quadros de Acesso: {quadros}")
print(f"✅ Promoções: {promocoes}")
print("")

if usuarios > 0 and militares > 0:
    print("✅ Importação parece ter funcionado!")
else:
    print("⚠️ Poucos registros encontrados. Verifique se a importação funcionou corretamente.")
PYEOF
EOF
```

