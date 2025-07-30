# 🚀 MIGRAÇÃO PARA SUPABASE - SISTEMA DE PROMOÇÕES CBMEPI

## 📋 RESUMO

Este documento contém as instruções completas para migrar os dados do banco local para o Supabase, resolvendo o problema de associação de usuários aos militares.

## 📁 ARQUIVOS GERADOS

1. **`migracao_supabase_20250729_130359.sql`** - Script principal de migração
2. **`associacao_usuarios_20250729_130444.sql`** - Script de associação de usuários
3. **`MIGRACAO_SUPABASE_README.md`** - Este arquivo de instruções

## 🔧 PRÉ-REQUISITOS

- Acesso ao painel do Supabase
- Banco de dados local funcionando
- Arquivos SQL gerados pelos scripts

## 📊 DADOS A SEREM MIGRADOS

- **Usuários**: 493 registros
- **Militares**: Todos os militares do sistema
- **Comissões**: Comissões de promoção
- **Quadros**: Quadros de acesso
- **Outros modelos**: Cargos, funções, etc.

## 🚀 PROCESSO DE MIGRAÇÃO

### Passo 1: Preparação

1. Verifique se os arquivos SQL foram gerados corretamente
2. Faça backup do banco Supabase atual (se houver dados)
3. Certifique-se de que as migrações Django estão aplicadas no Supabase

### Passo 2: Migração Principal

1. **Acesse o painel do Supabase**
   - Vá para https://supabase.com
   - Acesse seu projeto

2. **Abra o SQL Editor**
   - No menu lateral, clique em "SQL Editor"
   - Clique em "New query"

3. **Execute o script principal**
   - Abra o arquivo `migracao_supabase_20250729_130359.sql`
   - Cole todo o conteúdo no editor SQL
   - Clique em "Run" para executar

4. **Verifique a execução**
   - O script desabilita triggers temporariamente
   - Insere todos os usuários e militares
   - Reseta as sequências de ID
   - Reabilita os triggers

### Passo 3: Associação de Usuários

1. **Execute o script de associação**
   - Abra o arquivo `associacao_usuarios_20250729_130444.sql`
   - Cole todo o conteúdo no editor SQL
   - Clique em "Run" para executar

2. **Verifique as associações**
   - O script mostra quantas associações foram realizadas
   - Lista usuários que não puderam ser associados automaticamente

### Passo 4: Verificação Final

Execute as seguintes consultas para verificar se tudo foi migrado corretamente:

```sql
-- Verificar total de usuários
SELECT COUNT(*) as total_usuarios FROM auth_user;

-- Verificar total de militares
SELECT COUNT(*) as total_militares FROM militares_militar;

-- Verificar associações
SELECT COUNT(*) as militares_com_usuario FROM militares_militar WHERE user_id IS NOT NULL;
SELECT COUNT(*) as militares_sem_usuario FROM militares_militar WHERE user_id IS NULL;

-- Verificar comissões
SELECT COUNT(*) as total_comissoes FROM militares_comissaopromocao;

-- Verificar quadros
SELECT COUNT(*) as total_quadros FROM militares_quadroacesso;
```

## ⚠️ IMPORTANTE

### Antes da Migração
- **FAÇA BACKUP** do banco Supabase atual
- Teste em ambiente de desenvolvimento primeiro
- Verifique se as constraints e foreign keys estão corretas

### Durante a Migração
- Execute os scripts na ordem correta
- Aguarde a conclusão de cada script
- Verifique se não há erros na execução

### Após a Migração
- Teste o login com usuários diferentes
- Verifique se as funcionalidades principais funcionam
- Confirme se os usuários estão associados aos militares corretos

## 🔍 SOLUÇÃO DE PROBLEMAS

### Erro de Constraint
Se houver erro de foreign key:
```sql
-- Verificar constraints
SELECT * FROM information_schema.table_constraints WHERE table_name = 'militares_militar';
```

### Usuários Não Associados
Se muitos usuários não foram associados:
1. Verifique se os CPFs estão corretos
2. Confirme se os nomes estão iguais
3. Verifique se os emails estão corretos

### Dados Duplicados
Se houver dados duplicados:
```sql
-- Limpar dados duplicados (se necessário)
DELETE FROM auth_user WHERE id NOT IN (SELECT MIN(id) FROM auth_user GROUP BY username);
```

## 📞 SUPORTE

Se encontrar problemas durante a migração:

1. Verifique os logs do Supabase
2. Confirme se as credenciais estão corretas
3. Verifique se o banco local está acessível
4. Execute os scripts de verificação

## ✅ CHECKLIST FINAL

- [ ] Backup do Supabase realizado
- [ ] Script principal executado com sucesso
- [ ] Script de associação executado com sucesso
- [ ] Verificações de dados realizadas
- [ ] Login testado com diferentes usuários
- [ ] Funcionalidades principais testadas
- [ ] Usuários associados aos militares corretos

## 🎉 CONCLUSÃO

Após seguir todos os passos, o sistema estará migrado para o Supabase com todos os usuários corretamente associados aos militares. O sistema estará pronto para uso em produção.

---

**Gerado em**: 29/07/2025 13:04:44  
**Versão**: 1.0  
**Status**: Pronto para migração 