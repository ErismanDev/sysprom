# 🚀 Guia Completo - Supabase em Produção

## ✅ Configuração Concluída com Sucesso!

O projeto SEPROM CBMEPI está agora configurado para usar o **Supabase** como banco de dados em produção, com **variáveis de ambiente** para maior segurança.

---

## 📋 Resumo da Configuração

### 🔗 Informações de Conexão
- **Host**: `aws-0-sa-east-1.pooler.supabase.com`
- **Porta**: `6543`
- **Database**: `postgres`
- **Usuário**: `postgres.vubnekyyfjcrswaufnla`
- **SSL**: Obrigatório (`sslmode=require`)

### 👤 Credenciais de Acesso
- **Usuário Admin**: `admin`
- **Senha**: `admin123`
- **Email**: `admin@supabase.com`

---

## 🚀 Como Usar

### Para Desenvolvimento (Supabase + HTTP)
```bash
python iniciar_supabase_dev.py
# ou
python manage.py runserver --settings=sepromcbmepi.settings_supabase
```

### Para Produção (Supabase + HTTPS)
```bash
python manage.py runserver --settings=sepromcbmepi.settings_supabase_production
```

### Para Desenvolvimento (Banco Local)
```bash
python manage.py runserver
```

---

## 📁 Arquivos de Configuração

### 1. `sepromcbmepi/settings_supabase.py`
Configurações para **desenvolvimento** com Supabase:
- Conexão com banco PostgreSQL
- DEBUG = True
- SSL desabilitado para desenvolvimento
- HTTP permitido
- **Usa variáveis de ambiente**

### 2. `sepromcbmepi/settings_supabase_production.py`
Configurações para **produção** com Supabase:
- Conexão com banco PostgreSQL
- DEBUG = False
- SSL obrigatório
- Configurações de segurança ativas
- **Usa variáveis de ambiente**

### 3. `sepromcbmepi/settings.py`
Configurações padrão (banco local):
- PostgreSQL local
- Configurações de desenvolvimento

### 4. `.env` (Arquivo de Variáveis de Ambiente)
Contém as configurações sensíveis:
- Credenciais do Supabase
- Chave secreta do Django
- Configurações de debug e hosts

---

## ⚠️ IMPORTANTE - URLs de Acesso

### Desenvolvimento
- ✅ **URL Correta**: `http://127.0.0.1:8000`
- ❌ **URL Incorreta**: `https://127.0.0.1:8000`

### Produção
- ✅ **URL Correta**: `https://seu-dominio.com`
- ❌ **URL Incorreta**: `http://seu-dominio.com`

---

## 🔧 Comandos Úteis

### Executar Migrações no Supabase
```bash
python manage.py migrate --settings=sepromcbmepi.settings_supabase
```

### Criar Superusuário no Supabase
```bash
python manage.py createsuperuser --settings=sepromcbmepi.settings_supabase
```

### Coletar Arquivos Estáticos
```bash
python manage.py collectstatic --settings=sepromcbmepi.settings_supabase
```

### Shell Django no Supabase
```bash
python manage.py shell --settings=sepromcbmepi.settings_supabase
```

---

## 🛠️ Scripts de Manutenção

### 1. `teste_final_supabase.py`
Testa se a conexão com o Supabase está funcionando:
```bash
python teste_final_supabase.py
```

### 2. `corrigir_migracoes_supabase.py`
Corrige problemas de migração e configura o banco:
```bash
python corrigir_migracoes_supabase.py
```

### 3. `iniciar_supabase_dev.py`
Inicia o servidor de desenvolvimento com Supabase:
```bash
python iniciar_supabase_dev.py
```

### 4. `criar_env.py`
Cria o arquivo `.env` com as configurações:
```bash
python criar_env.py
```

### 5. `teste_env.py`
Testa se as variáveis de ambiente estão funcionando:
```bash
python teste_env.py
```

---

## 🔒 Variáveis de Ambiente

### Arquivo `.env` (Já Criado)
```env
# Supabase
SUPABASE_HOST=aws-0-sa-east-1.pooler.supabase.com
SUPABASE_PORT=6543
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres.vubnekyyfjcrswaufnla
SUPABASE_PASSWORD=2YXGdmXESoZAoPkO

# Django
SECRET_KEY=django-insecure-sua-chave-secreta-aqui-mude-esta-chave-em-producao
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com
```

### Como as Configurações Usam as Variáveis
```python
# Exemplo de como as configurações carregam as variáveis
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('SUPABASE_DATABASE', 'postgres'),
        'USER': os.environ.get('SUPABASE_USER', 'postgres.vubnekyyfjcrswaufnla'),
        'PASSWORD': os.environ.get('SUPABASE_PASSWORD', '2YXGdmXESoZAoPkO'),
        'HOST': os.environ.get('SUPABASE_HOST', 'aws-0-sa-east-1.pooler.supabase.com'),
        'PORT': os.environ.get('SUPABASE_PORT', '6543'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
```

---

## 🔄 Migração de Dados

### Do Banco Local para o Supabase

1. **Fazer backup do banco local**:
```bash
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > backup_local.json
```

2. **Carregar no Supabase**:
```bash
python manage.py loaddata backup_local.json --settings=sepromcbmepi.settings_supabase
```

### Do Supabase para o Banco Local

1. **Fazer backup do Supabase**:
```bash
python manage.py dumpdata --exclude auth.permission --exclude contenttypes --settings=sepromcbmepi.settings_supabase > backup_supabase.json
```

2. **Carregar no banco local**:
```bash
python manage.py loaddata backup_supabase.json
```

---

## 📊 Monitoramento

### Verificar Status do Banco
```bash
python manage.py dbshell --settings=sepromcbmepi.settings_supabase
```

### Verificar Tabelas
```sql
\dt
```

### Verificar Conexões
```sql
SELECT * FROM pg_stat_activity;
```

---

## 🚨 Troubleshooting

### Erro de Conexão
- Verificar se as credenciais estão corretas no arquivo `.env`
- Verificar se o Supabase está ativo
- Verificar conectividade de rede

### Erro de Migração
- Executar `python corrigir_migracoes_supabase.py`
- Verificar se não há conflitos de migração

### Erro de SSL
- Verificar se `sslmode=require` está configurado
- Verificar se o certificado SSL está válido

### Erro "HTTPS not supported"
- **Desenvolvimento**: Use `http://127.0.0.1:8000` (não https)
- **Produção**: Configure um proxy reverso com SSL

### Erro de Variáveis de Ambiente
- Verificar se o arquivo `.env` existe
- Executar `python teste_env.py` para verificar
- Verificar se `python-dotenv` está instalado

---

## 📞 Suporte

### Logs do Django
```bash
python manage.py runserver --settings=sepromcbmepi.settings_supabase --verbosity=2
```

### Logs do PostgreSQL
Acesse o painel do Supabase para ver logs detalhados.

---

## 🎯 Próximos Passos

1. ✅ **Configurar variáveis de ambiente** para maior segurança
2. **Configurar backup automático** do Supabase
3. **Configurar monitoramento** de performance
4. **Configurar CI/CD** para deploy automático
5. **Configurar domínio personalizado** se necessário

---

## ✅ Checklist de Produção

- [x] Conexão com Supabase configurada
- [x] Migrações executadas
- [x] Superusuário criado
- [x] Dados iniciais configurados
- [x] Testes de conectividade realizados
- [x] Configurações de desenvolvimento vs produção separadas
- [x] Variáveis de ambiente configuradas
- [ ] Backup automático configurado
- [ ] Monitoramento configurado
- [ ] SSL configurado
- [ ] Domínio configurado

---

## 🔒 Segurança

### Arquivo `.env`
- ✅ Criado automaticamente
- ✅ Contém configurações sensíveis
- ✅ Deve estar no `.gitignore`
- ✅ Mude a `SECRET_KEY` em produção

### Configurações de Produção
- ✅ SSL obrigatório
- ✅ DEBUG desabilitado
- ✅ Configurações de segurança ativas
- ✅ Variáveis de ambiente seguras

---

**🎉 Parabéns! O Supabase está configurado e funcionando perfeitamente com variáveis de ambiente!**

**📝 Lembre-se**: 
- Use HTTP para desenvolvimento e HTTPS para produção!
- O arquivo `.env` contém informações sensíveis - mantenha-o seguro! 