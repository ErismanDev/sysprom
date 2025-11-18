# 📥 Importar Excel no Servidor Digital Ocean

## 🚀 Comandos para Executar no Console

### PASSO 1: Instalar Dependências

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
pip install pandas openpyxl
EOF
```

---

### PASSO 2: Verificar se os Arquivos Foram Enviados

```bash
# Verificar se o Excel está no servidor
ls -lh /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.xlsx

# Verificar se o script de importação está no servidor
ls -lh /home/seprom/sepromcbmepi/importar_banco_excel.py
```

---

### PASSO 3: Executar Importação

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python importar_banco_excel.py
EOF
```

---

## 📋 Comando Único (Tudo em Um)

```bash
# Instalar dependências e executar importação
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
pip install -q pandas openpyxl && \
python importar_banco_excel.py
EOF
```

---

## ✅ Verificar Importação

```bash
# Verificar usuários importados
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python manage.py shell -c "from django.contrib.auth.models import User; print(f'✅ Total de usuários: {User.objects.count()}')"
EOF

# Verificar militares importados
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python manage.py shell -c "from militares.models import Militar; print(f'✅ Total de militares: {Militar.objects.count()}')"
EOF

# Verificar quadros de acesso
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python manage.py shell -c "from militares.models import QuadroAcesso; print(f'✅ Total de quadros: {QuadroAcesso.objects.count()}')"
EOF

# Verificar promoções
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python manage.py shell -c "from militares.models import Promocao; print(f'✅ Total de promoções: {Promocao.objects.count()}')"
EOF
```

---

## 🔧 Se Der Erro

### Erro: Arquivo não encontrado

```bash
# Listar arquivos Excel disponíveis
ls -la /home/seprom/sepromcbmepi/*.xlsx

# Se não houver, você precisa enviar via WinSCP primeiro
```

### Erro: Módulo não encontrado

```bash
# Reinstalar dependências
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
pip install --upgrade pandas openpyxl
EOF
```

### Erro: Permissão negada

```bash
# Corrigir permissões
sudo chown seprom:seprom /home/seprom/sepromcbmepi/importar_banco_excel.py
sudo chmod +x /home/seprom/sepromcbmepi/importar_banco_excel.py
```

---

## 📤 Checklist Antes de Executar

- [ ] Arquivo Excel enviado via WinSCP para `/home/seprom/sepromcbmepi/`
- [ ] Arquivo `importar_banco_excel.py` enviado via WinSCP para `/home/seprom/sepromcbmepi/`
- [ ] Servidor acessível via console do Digital Ocean
- [ ] Backup do banco atual feito (opcional, mas recomendado)

