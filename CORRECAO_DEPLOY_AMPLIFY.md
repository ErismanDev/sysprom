# 🔧 Correção do Deploy AWS Amplify

## Problema Identificado

O deploy estava falhando devido a uma migração que ainda referenciava o módulo `ckeditor_uploader` antigo, que foi substituído por `django-ckeditor-5`.

## ✅ Correções Aplicadas

### 1. Migração Corrigida
- **Arquivo**: `militares/migrations/0035_alter_atasessao_conteudo_modeloata.py`
- **Problema**: Importava `ckeditor_uploader.fields`
- **Solução**: Alterado para `from django_ckeditor_5.fields import CKEditor5Field`

### 2. Configuração do Amplify Melhorada
- **Arquivo**: `amplify.yml`
- **Melhorias**:
  - Adicionada verificação de variáveis de ambiente
  - Configurado `DJANGO_SETTINGS_MODULE`
  - Melhor tratamento de erros

### 3. Configuração de Produção Robusta
- **Arquivo**: `sepromcbmepi/settings_aws_production.py`
- **Melhorias**:
  - Fallback seguro para `SECRET_KEY`
  - Configurações de SSL otimizadas

## 🚀 Próximos Passos

### 1. Configure as Variáveis de Ambiente no AWS Amplify

No console do AWS Amplify, vá em **App settings** > **Environment variables** e configure:

```
DEBUG=False
SECRET_KEY=sua-chave-secreta-muito-segura
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres.vubnekyyfjcrswaufnla
SUPABASE_PASSWORD=sua-senha-supabase
SUPABASE_HOST=aws-0-sa-east-1.pooler.supabase.com
SUPABASE_PORT=6543
SECURE_SSL_REDIRECT=True
```

### 2. Teste Localmente

```bash
# Execute o script de teste
python testar_deploy_local.py

# Ou teste manualmente
python manage.py collectstatic --noinput --settings=sepromcbmepi.settings_aws_production
python manage.py migrate --noinput --settings=sepromcbmepi.settings_aws_production
```

### 3. Faça o Deploy

```bash
# Commit das correções
git add .
git commit -m "Corrigir migração CKEditor para deploy Amplify"
git push origin main
```

## 🔍 Monitoramento

### Logs Importantes
- **Build logs**: Verifique se não há mais erros de `ckeditor_uploader`
- **Runtime logs**: Monitore a aplicação após o deploy

### Verificações Pós-Deploy
1. ✅ Aplicação carrega sem erros
2. ✅ Migrações aplicadas com sucesso
3. ✅ Arquivos estáticos servidos corretamente
4. ✅ Conexão com Supabase funcionando

## 🛠️ Scripts Úteis

### Correção Automática de Migrações
```bash
python corrigir_migracoes_ckeditor.py
```

### Teste de Configuração
```bash
python testar_deploy_local.py
```

## 📋 Checklist de Deploy

- [ ] Variáveis de ambiente configuradas no Amplify
- [ ] Migrações corrigidas e testadas
- [ ] Dependências atualizadas no `requirements.txt`
- [ ] Configuração de produção testada localmente
- [ ] Commit e push das correções
- [ ] Deploy monitorado no console Amplify
- [ ] Aplicação testada em produção

## 🆘 Solução de Problemas

### Erro: "No module named 'ckeditor_uploader'"
**Solução**: Execute `python corrigir_migracoes_ckeditor.py`

### Erro: "SECRET_KEY not configured"
**Solução**: Configure a variável `SECRET_KEY` no Amplify

### Erro: "Database connection failed"
**Solução**: Verifique as credenciais do Supabase no Amplify

### Erro: "Static files not found"
**Solução**: Verifique se o `collectstatic` foi executado corretamente

## 📞 Suporte

Se os problemas persistirem:
1. Verifique os logs completos no console Amplify
2. Execute os scripts de diagnóstico
3. Teste a configuração localmente
4. Consulte a documentação do AWS Amplify 