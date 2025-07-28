# 🚀 Guia de Deploy - AWS Elastic Beanstalk

## ✅ Por que Elastic Beanstalk?

O AWS Elastic Beanstalk é **muito melhor** para aplicações Django do que o Amplify, pois:
- ✅ Suporte nativo a Python/Django
- ✅ Servidor WSGI (Gunicorn)
- ✅ Banco de dados integrado
- ✅ Auto-scaling
- ✅ Load balancing
- ✅ SSL/HTTPS automático

## 📋 Arquivos Criados

### 1. **Procfile**
```bash
web: gunicorn sepromcbmepi.wsgi:application --bind 0.0.0.0:8000
```

### 2. **.ebextensions/django.config**
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: sepromcbmepi.wsgi:application
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: staticfiles
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: sepromcbmepi.settings_aws_production
    PYTHONPATH: /var/app/current:$PYTHONPATH
```

### 3. **.ebextensions/01_packages.config**
```yaml
packages:
  yum:
    git: []
    postgresql-devel: []
    gcc: []
    python3-devel: []
```

### 4. **.ebextensions/02_django.config**
```yaml
container_commands:
  01_migrate:
    command: "source /var/app/venv/*/bin/activate && python manage.py migrate --noinput"
    leader_only: true
  02_collectstatic:
    command: "source /var/app/venv/*/bin/activate && python manage.py collectstatic --noinput"
  03_createsuperuser:
    command: "source /var/app/venv/*/bin/activate && echo 'from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username=\"admin\").exists() or User.objects.create_superuser(\"admin\", \"admin@example.com\", \"admin123\")' | python manage.py shell"
    leader_only: true
```

## 🚀 Passos para Deploy

### 1. **Instalar EB CLI**
```bash
pip install awsebcli
```

### 2. **Inicializar EB**
```bash
eb init
# Selecione sua região e credenciais AWS
```

### 3. **Criar Ambiente**
```bash
eb create seprom-production
# Escolha Python 3.11
```

### 4. **Configurar Variáveis de Ambiente**
```bash
eb setenv DEBUG=False
eb setenv SECRET_KEY=sua-chave-secreta
eb setenv SUPABASE_DATABASE=postgres
eb setenv SUPABASE_USER=postgres.vubnekyyfjcrswaufnla
eb setenv SUPABASE_PASSWORD=sua-senha
eb setenv SUPABASE_HOST=aws-0-sa-east-1.pooler.supabase.com
eb setenv SUPABASE_PORT=6543
```

### 5. **Fazer Deploy**
```bash
eb deploy
```

### 6. **Abrir Aplicação**
```bash
eb open
```

## 🔧 Configurações Importantes

### **Variáveis de Ambiente Necessárias:**
```
DEBUG=False
SECRET_KEY=sua-chave-secreta-muito-segura
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres.vubnekyyfjcrswaufnla
SUPABASE_PASSWORD=sua-senha-supabase
SUPABASE_HOST=aws-0-sa-east-1.pooler.supabase.com
SUPABASE_PORT=6543
```

### **Comandos Úteis:**
```bash
# Ver logs
eb logs

# Conectar via SSH
eb ssh

# Ver status
eb status

# Listar ambientes
eb list
```

## 🎯 Vantagens do Elastic Beanstalk

1. **✅ Suporte Completo a Django**
2. **✅ Auto-scaling automático**
3. **✅ Load balancing**
4. **✅ SSL/HTTPS automático**
5. **✅ Monitoramento integrado**
6. **✅ Rollback fácil**
7. **✅ Múltiplos ambientes (dev, staging, prod)**

## 📞 Suporte

Se houver problemas:
1. Verifique os logs: `eb logs`
2. Teste localmente primeiro
3. Verifique as variáveis de ambiente
4. Consulte a documentação do Elastic Beanstalk

## 🎉 Resultado Final

Após o deploy, você terá:
- ✅ Aplicação Django funcionando
- ✅ Banco de dados conectado
- ✅ Arquivos estáticos servidos
- ✅ Admin Django acessível
- ✅ Sistema completo operacional 