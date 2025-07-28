# 🚀 Guia de Configuração do Supabase - SEPROM CBMEPI

Este guia irá ajudá-lo a conectar seu projeto Django SEPROM CBMEPI ao Supabase.

## 📋 Pré-requisitos

- Python 3.8+
- Django 5.2.3
- Conta no Supabase
- Credenciais do banco de dados PostgreSQL do Supabase

## 🔧 Configuração Inicial

### 1. Obter Credenciais do Supabase

1. Acesse o [Supabase Dashboard](https://supabase.com/dashboard)
2. Selecione seu projeto
3. Vá para **Settings** > **Database**
4. Copie a **Connection string** ou as credenciais individuais

### 2. Configurar a Senha do Banco

**IMPORTANTE**: Você precisa substituir `[YOUR-PASSWORD]` pela senha real do seu banco Supabase nos seguintes arquivos:

- `sepromcbmepi/settings_supabase.py`
- `conectar_supabase.py`
- `migrar_para_supabase.py`

### 3. Estrutura de Arquivos Criada

```
sepromcbmepi/
├── settings_supabase.py    # Configurações específicas do Supabase
├── conectar_supabase.py    # Script de teste de conexão
├── migrar_para_supabase.py # Script de migração de dados
└── GUIA_SUPABASE.md        # Este arquivo
```

## 🚀 Passos para Conectar ao Supabase

### Passo 1: Configurar a Senha

Edite o arquivo `sepromcbmepi/settings_supabase.py` e substitua `[YOUR-PASSWORD]` pela senha real:

```python
DATABASE_URL = "postgresql://postgres:SUA_SENHA_REAL@db.vubnekyyfjcrswaufnla.supabase.co:5432/postgres"
```

### Passo 2: Testar a Conexão

Execute o script de teste de conexão:

```bash
python conectar_supabase.py
```

### Passo 3: Migrar Dados (Opcional)

Se você quiser migrar os dados do banco local para o Supabase:

```bash
python migrar_para_supabase.py
```

### Passo 4: Executar o Servidor com Supabase

```bash
python manage.py runserver --settings=sepromcbmepi.settings_supabase
```

## 📊 Comandos Úteis

### Executar Migrações no Supabase

```bash
python manage.py migrate --settings=sepromcbmepi.settings_supabase
```

### Criar Superusuário no Supabase

```bash
python manage.py createsuperuser --settings=sepromcbmepi.settings_supabase
```

### Fazer Backup dos Dados

```bash
python manage.py dumpdata --settings=sepromcbmepi.settings_supabase --output backup_supabase.json
```

### Carregar Dados no Supabase

```bash
python manage.py loaddata backup_supabase.json --settings=sepromcbmepi.settings_supabase
```

### Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --settings=sepromcbmepi.settings_supabase
```

## 🔍 Verificação da Conexão

### Testar via Django Shell

```bash
python manage.py shell --settings=sepromcbmepi.settings_supabase
```

```python
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT version();")
    print(cursor.fetchone())
```

### Verificar Tabelas

```python
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])
```

## ⚠️ Configurações de Segurança

### SSL (Recomendado para Produção)

O arquivo `settings_supabase.py` já inclui configurações SSL:

```python
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
}
```

### Variáveis de Ambiente (Recomendado)

Para maior segurança, use variáveis de ambiente:

```bash
export DATABASE_URL="postgresql://postgres:SENHA@db.vubnekyyfjcrswaufnla.supabase.co:5432/postgres"
export DJANGO_SETTINGS_MODULE="sepromcbmepi.settings_supabase"
```

## 🐛 Solução de Problemas

### Erro de Conexão

1. Verifique se a senha está correta
2. Verifique se o host e porta estão corretos
3. Verifique se o banco de dados existe no Supabase

### Erro de SSL

Se houver problemas com SSL, remova ou modifique:

```python
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'prefer',  # ou 'disable' para desenvolvimento
}
```

### Erro de Migração

1. Verifique se todas as migrações estão aplicadas localmente
2. Execute `python manage.py makemigrations` se necessário
3. Verifique se não há conflitos de dependências

### Erro de Permissões

1. Verifique se o usuário do banco tem permissões adequadas
2. Verifique se as tabelas foram criadas corretamente

## 📈 Monitoramento

### Logs do Django

Os logs são configurados para arquivo e console:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Dashboard do Supabase

- Acesse o dashboard do Supabase para monitorar:
  - Uso do banco de dados
  - Performance das queries
  - Logs de acesso
  - Backup automático

## 🔄 Alternância entre Ambientes

### Para usar o banco local:

```bash
python manage.py runserver --settings=sepromcbmepi.settings
```

### Para usar o Supabase:

```bash
python manage.py runserver --settings=sepromcbmepi.settings_supabase
```

## 📞 Suporte

Se você encontrar problemas:

1. Verifique os logs do Django (`django.log`)
2. Verifique os logs do Supabase no dashboard
3. Teste a conexão com `psql` ou outro cliente PostgreSQL
4. Verifique se todas as dependências estão instaladas

## 🎯 Próximos Passos

Após a configuração bem-sucedida:

1. Configure backups automáticos no Supabase
2. Configure monitoramento de performance
3. Configure alertas para problemas de conexão
4. Considere usar o Supabase Auth para autenticação
5. Configure o Supabase Storage para arquivos

---

**Desenvolvido por: Erisman Org**  
**Projeto: SEPROM CBMEPI**  
**Data: Julho 2025** 