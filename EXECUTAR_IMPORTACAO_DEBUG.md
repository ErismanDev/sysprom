# 🔍 Executar Importação com Debug

## 🚀 Comando para Executar

### 1. Enviar Script de Debug

Envie o arquivo `importar_banco_excel_debug.py` para `/home/seprom/sepromcbmepi/` via WinSCP

### 2. Executar com Debug

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python importar_banco_excel_debug.py
EOF
```

---

## 📋 Ou Usar o Script Original com Mais Informações

Execute o script original novamente e veja a saída completa:

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python importar_banco_excel.py 2>&1 | tee /tmp/importacao.log
EOF

# Ver o log
cat /tmp/importacao.log
```

