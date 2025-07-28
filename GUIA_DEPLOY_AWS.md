# 🚀 Guia de Deploy na AWS - SEPROM CBMEPI

## ✅ Sistema Pronto para AWS

O sistema está **100% configurado** para deploy na AWS com Supabase!

## 📋 Configurações Implementadas

### 1. ✅ Configurações de Produção
- **Arquivo**: `sepromcbmepi/settings_aws_production.py`
- **Segurança**: Configurada para produção
- **SSL/HTTPS**: Habilitado
- **Logging**: Configurado para AWS

### 2. ✅ Supabase Integrado
- **Banco de dados**: PostgreSQL no Supabase
- **Conexão**: SSL habilitado
- **Hosts**: Configurados para AWS

### 3. ✅ Arquivos de Deploy
- **buildspec.yml**: Para AWS CodeBuild
- **amplify.yml**: Para AWS Amplify
- **Procfile**: Para Elastic Beanstalk

## 🎯 Opções de Deploy na AWS

### Opção 1: AWS Amplify (Recomendado)
```bash
# 1. Conectar repositório no AWS Amplify
# 2. Configurar variáveis de ambiente
# 3. Deploy automático
```

### Opção 2: AWS Elastic Beanstalk
```bash
# 1. Criar aplicação no Elastic Beanstalk
# 2. Fazer upload do código
# 3. Configurar variáveis de ambiente
```

### Opção 3: AWS CodeBuild + CodePipeline
```bash
# 1. Configurar pipeline no CodePipeline
# 2. Usar buildspec.yml
# 3. Deploy automático
```

## 🔧 Variáveis de Ambiente Necessárias

Configure estas variáveis no seu serviço AWS:

```env
# Supabase
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres.vubnekyyfjcrswaufnla
SUPABASE_PASSWORD=2YXGdmXESoZAoPkO
SUPABASE_HOST=aws-0-sa-east-1.pooler.supabase.com
SUPABASE_PORT=6543

# Segurança
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False
SECURE_SSL_REDIRECT=True

# Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,.amplifyapp.com,.amazonaws.com,.elasticbeanstalk.com
```

## 📁 Arquivos de Configuração

### ✅ Arquivos Criados/Atualizados:
1. `sepromcbmepi/settings_aws_production.py` - Configurações de produção
2. `buildspec.yml` - Para AWS CodeBuild
3. `amplify.yml` - Para AWS Amplify
4. `Procfile` - Para Elastic Beanstalk
5. `aws_config.env` - Exemplo de variáveis

### ✅ Dependências Incluídas:
- `python-dotenv==1.0.0`
- `gunicorn==21.2.0`
- `whitenoise==6.6.0`
- `psycopg2-binary==2.9.10`

## 🚀 Passos para Deploy

### 1. Preparar Código
```bash
# Verificar se tudo está commitado
git add .
git commit -m "Configurações AWS prontas"
git push
```

### 2. AWS Amplify (Mais Fácil)
1. Acesse AWS Amplify Console
2. Conecte seu repositório
3. Configure variáveis de ambiente
4. Deploy automático

### 3. Verificar Deploy
- ✅ Sistema funcionando
- ✅ Banco Supabase conectado
- ✅ SSL/HTTPS ativo
- ✅ Arquivos estáticos servidos

## 🔍 Verificações Pós-Deploy

1. **Acesso ao sistema**: https://seu-dominio.amplifyapp.com
2. **Admin**: https://seu-dominio.amplifyapp.com/admin
3. **Logs**: Verificar CloudWatch
4. **Banco**: Testar conexão Supabase

## ⚠️ Importante

- **Sempre use HTTPS** em produção
- **Configure SECRET_KEY** única
- **Monitore logs** no CloudWatch
- **Backup automático** no Supabase

## 🎉 Status Final

**O SEPROM CBMEPI está 100% pronto para deploy na AWS!**

- ✅ Configurações de produção
- ✅ Supabase integrado
- ✅ Arquivos de deploy
- ✅ Segurança configurada
- ✅ SSL/HTTPS pronto

**Próximo passo**: Escolher serviço AWS e fazer deploy! 🚀 