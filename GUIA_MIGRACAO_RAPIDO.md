# 🚀 Guia Rápido de Migração SQLite → PostgreSQL

## 📋 Passos para Migração

### 1. Instalar PostgreSQL
- **Windows:** Baixe em https://www.postgresql.org/download/windows/
- Durante a instalação, anote a senha do usuário `postgres`
- Reinicie o terminal após a instalação

### 2. Verificar Instalação
```bash
psql --version
```

### 3. Executar Migração Automatizada
```bash
python migrar_para_postgresql.py
```

### 4. Se houver problemas, execute manualmente:

#### A. Exportar dados (já feito)
```bash
python exportar_dados_utf8.py
```

#### B. Instalar dependências
```bash
pip install psycopg2-binary
```

#### C. Criar banco PostgreSQL
```bash
psql -U postgres -c "CREATE DATABASE sepromcbmepi;"
```

#### D. Atualizar settings.py
Edite `sepromcbmepi/settings.py` e substitua:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "sepromcbmepi",
        "USER": "postgres",
        "PASSWORD": "sua_senha_aqui",  # Altere para sua senha
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

#### E. Aplicar migrações
```bash
python manage.py migrate
```

#### F. Importar dados
```bash
python manage.py loaddata dados_sqlite_utf8.json
```

#### G. Verificar migração
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from militares.models import Militar
print(f"Usuários: {User.objects.count()}")
print(f"Militares: {Militar.objects.count()}")
```

## ⚠️ Problemas Comuns

### PostgreSQL não encontrado
- Verifique se está instalado
- Reinicie o terminal
- Adicione ao PATH se necessário

### Erro de conexão
- Verifique se o PostgreSQL está rodando
- Confirme a senha no settings.py
- Teste: `psql -U postgres`

### Erro de codificação
- Use o arquivo `dados_sqlite_utf8.json` (já criado)
- Execute: `python exportar_dados_utf8.py`

## 🎯 Próximos Passos

1. **Teste o sistema:**
   ```bash
   python manage.py runserver
   ```

2. **Acesse:** http://localhost:8000

3. **Verifique se tudo funciona**

4. **Limpeza (após confirmar):**
   ```bash
   rm db.sqlite3
   rm dados_sqlite_utf8.json
   rm db_backup.sqlite3
   ```

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do Django
2. Confirme se o PostgreSQL está rodando
3. Verifique a senha no settings.py
4. Use o script automatizado: `python migrar_para_postgresql.py` 