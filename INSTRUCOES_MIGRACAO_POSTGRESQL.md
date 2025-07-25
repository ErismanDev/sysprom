# Guia de Migração: SQLite → PostgreSQL

Este guia irá te ajudar a migrar o banco de dados do SQLite para PostgreSQL no seu projeto Django.

## 📋 Pré-requisitos

### 1. Instalar PostgreSQL

**Windows:**
- Baixe o instalador em: https://www.postgresql.org/download/windows/
- Durante a instalação, anote a senha do usuário `postgres`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

### 2. Verificar Instalação
```bash
psql --version
```

## 🚀 Processo de Migração

### Passo 1: Fazer Backup
Antes de começar, faça um backup do seu banco atual:
```bash
cp db.sqlite3 db_backup.sqlite3
```

### Passo 2: Instalar Dependências Python
```bash
pip install psycopg2-binary
```

### Passo 3: Criar Banco PostgreSQL
```bash
# Conectar ao PostgreSQL
psql -U postgres

# Criar banco de dados
CREATE DATABASE sepromcbmepi;

# Sair
\q
```

### Passo 4: Atualizar Configurações Django

Edite o arquivo `sepromcbmepi/settings.py` e substitua a seção `DATABASES`:

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

### Passo 5: Exportar Dados do SQLite
```bash
python manage.py dumpdata --exclude contenttypes --exclude auth.Permission --indent 2 -o dados_sqlite.json
```

### Passo 6: Aplicar Migrações no PostgreSQL
```bash
python manage.py migrate
```

### Passo 7: Importar Dados
```bash
python manage.py loaddata dados_sqlite.json
```

### Passo 8: Verificar Migração
```bash
python manage.py shell
```

No shell do Django:
```python
from django.contrib.auth.models import User
from militares.models import Militar

print(f"Usuários: {User.objects.count()}")
print(f"Militares: {Militar.objects.count()}")
```

## 🔧 Script Automatizado

Para facilitar o processo, use o script `migrar_para_postgresql.py`:

```bash
python migrar_para_postgresql.py
```

Este script irá:
- Verificar se o PostgreSQL está instalado
- Instalar dependências necessárias
- Fazer backup do SQLite
- Criar o banco PostgreSQL
- Atualizar as configurações
- Migrar os dados
- Verificar se tudo funcionou

## ⚠️ Problemas Comuns

### Erro de Conexão
```
django.db.utils.OperationalError: could not connect to server
```
**Solução:** Verifique se o PostgreSQL está rodando:
```bash
# Windows
net start postgresql

# Linux
sudo systemctl start postgresql

# macOS
brew services start postgresql
```

### Erro de Autenticação
```
django.db.utils.OperationalError: FATAL: password authentication failed
```
**Solução:** Verifique a senha no `settings.py` e certifique-se de que está correta.

### Erro de Permissão
```
django.db.utils.OperationalError: permission denied for database
```
**Solução:** Conceda permissões ao usuário:
```sql
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO postgres;
```

## 🧹 Limpeza (Opcional)

Após confirmar que tudo está funcionando:

1. Remover arquivos temporários:
```bash
rm dados_sqlite.json
rm db_backup.sqlite3
rm db.sqlite3
```

2. Atualizar `.gitignore`:
```
# Adicionar ao .gitignore
*.sqlite3
dados_sqlite.json
```

## 📊 Vantagens do PostgreSQL

- **Performance:** Melhor para aplicações com muitos dados
- **Concorrência:** Suporte a múltiplos usuários simultâneos
- **Recursos Avançados:** Índices, views, stored procedures
- **Escalabilidade:** Adequado para produção
- **Integridade:** Melhor controle de transações

## 🔍 Verificação Final

Teste o sistema:
```bash
python manage.py runserver
```

Acesse http://localhost:8000 e verifique se:
- Login funciona
- Dados estão presentes
- Funcionalidades principais operam normalmente

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do Django
2. Consulte a documentação do PostgreSQL
3. Verifique se todas as dependências estão instaladas
4. Confirme se as configurações estão corretas 