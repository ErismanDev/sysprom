# 📊 Exportar e Importar Banco via Excel

## 📤 PASSO 1: Exportar do Banco Local (PC)

### 1. Instalar dependências (se necessário)

```bash
pip install pandas openpyxl
```

### 2. Executar script de exportação

```bash
python exportar_banco_excel.py
```

O script criará um arquivo `backup_sepromcbmepi_YYYYMMDD_HHMMSS.xlsx` com os dados principais:
- Usuários
- Militares
- Quadro de Acesso
- Promoções

---

## 📤 PASSO 2: Enviar Excel para o Servidor

### Via WinSCP:

1. Conecte ao servidor (64.23.185.235)
2. Navegue até `/home/seprom/sepromcbmepi/` no servidor
3. Envie o arquivo `backup_sepromcbmepi_*.xlsx` do PC local para o servidor

---

## 📥 PASSO 3: Importar no Servidor

### 1. Instalar dependências no servidor

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
pip install pandas openpyxl
EOF
```

### 2. Enviar script de importação

Envie o arquivo `importar_banco_excel.py` para `/home/seprom/sepromcbmepi/` via WinSCP

### 3. Executar importação

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python importar_banco_excel.py
EOF
```

---

## 🔧 Comandos Rápidos

### No PC Local (Exportar):

```bash
# Instalar dependências
pip install pandas openpyxl

# Executar exportação
python exportar_banco_excel.py
```

### No Servidor (Importar):

```bash
# Instalar dependências
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && pip install pandas openpyxl"

# Executar importação
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python importar_banco_excel.py"
```

---

## ⚠️ Observações

1. **Backup antes de importar**: Sempre faça backup do banco no servidor antes de importar
2. **Dados duplicados**: O script usa `update_or_create`, então atualiza registros existentes
3. **Relacionamentos**: Alguns relacionamentos podem precisar ser ajustados manualmente
4. **Fotos**: As fotos dos militares precisam ser enviadas separadamente via WinSCP para `/home/seprom/sepromcbmepi/media/`

---

## 📋 Verificar Importação

```bash
# Verificar usuários importados
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py shell -c \"from django.contrib.auth.models import User; print(f'Total de usuários: {User.objects.count()}')\""

# Verificar militares importados
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py shell -c \"from militares.models import Militar; print(f'Total de militares: {Militar.objects.count()}')\""
```

