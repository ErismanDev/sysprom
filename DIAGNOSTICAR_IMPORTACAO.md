# 🔍 Diagnosticar Problema na Importação

## 🚀 Comandos de Diagnóstico

### 1. Verificar se o Arquivo Excel Existe

```bash
ls -lh /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.xlsx
```

### 2. Verificar se o Script Existe

```bash
ls -lh /home/seprom/sepromcbmepi/importar_banco_excel.py
```

### 3. Executar o Script com Debug

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python importar_banco_excel.py
EOF
```

### 4. Verificar Erros no Python

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python -c "import pandas; import openpyxl; print('✅ Dependências OK')"
EOF
```

### 5. Testar Abertura do Excel Manualmente

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python << 'PYEOF'
import glob
from openpyxl import load_workbook

arquivos = glob.glob("/home/seprom/sepromcbmepi/backup_sepromcbmepi_*.xlsx")
if arquivos:
    arquivo = sorted(arquivos, reverse=True)[0]
    print(f"📁 Arquivo encontrado: {arquivo}")
    try:
        wb = load_workbook(arquivo, data_only=True)
        print(f"✅ Arquivo pode ser aberto")
        print(f"📊 Planilhas disponíveis: {wb.sheetnames}")
    except Exception as e:
        print(f"❌ Erro ao abrir: {e}")
else:
    print("❌ Nenhum arquivo Excel encontrado!")
PYEOF
EOF
```

