# 🔧 Resolver Problema do Banco de Dados

## 📋 Status Atual

✅ **Aplicação funcionando** - O deploy está ativo em: https://sysprom.onrender.com
⚠️ **Problema de banco** - Erro de senha do Supabase
⚠️ **Arquivos estáticos** - Corrigidos no último deploy

## 🚨 Erro Identificado

```
django.db.utils.OperationalError: connection to server at "aws-0-sa-east-1.pooler.supabase.com" (52.67.1.88), port 6543 failed: error received from server in SCRAM exchange: Wrong password
```

## 🔧 Solução: Corrigir DATABASE_URL

### Passo 1: Acessar o Painel do Render
1. Vá para: https://dashboard.render.com
2. Clique no seu serviço `sepromcbmepi`
3. Vá para a aba **Environment**

### Passo 2: Verificar/Atualizar DATABASE_URL
1. Procure pela variável `DATABASE_URL`
2. **Verifique se a senha está correta**
3. **Formato esperado:**
   ```
   postgresql://usuario:senha@aws-0-sa-east-1.pooler.supabase.com:6543/nome_do_banco
   ```

### Passo 3: Obter Nova Senha do Supabase (se necessário)
1. Acesse: https://supabase.com/dashboard
2. Selecione seu projeto
3. Vá para **Settings** > **Database**
4. Copie a nova **Database Password**
5. Atualize a `DATABASE_URL` no Render

## 🧪 Testar Localmente

Execute o script de verificação:

```bash
python verificar_banco_render.py
```

## 📊 Verificar Status

Após corrigir a `DATABASE_URL`:

1. **Aguarde 2-3 minutos** para o Render processar
2. **Acesse:** https://sysprom.onrender.com
3. **Teste o login** com suas credenciais
4. **Verifique os logs** no painel do Render

## ✅ Resultado Esperado

- ✅ Login funcionando
- ✅ Páginas carregando corretamente
- ✅ Arquivos estáticos (CSS/JS) carregando
- ✅ Sem erros de banco nos logs

## 🆘 Se o Problema Persistir

1. **Verifique se o banco Supabase está ativo**
2. **Confirme se o IP do Render está liberado**
3. **Teste a conexão diretamente no Supabase**
4. **Verifique se há migrações pendentes**

---

**Última atualização:** 29/07/2025
**Status:** Aguardando correção da DATABASE_URL 