# 🚀 GUIA DE MIGRAÇÃO SUPABASE - 3 ETAPAS

## 📋 VISÃO GERAL

Este guia orienta a migração completa dos dados do banco local para o Supabase, dividida em 3 etapas controladas para evitar sobrecarga e travamentos.

## 🎯 OBJETIVOS

- ✅ Migrar todos os dados de forma segura
- ✅ Evitar sobrecarga do banco Supabase
- ✅ Manter integridade dos dados
- ✅ Associar usuários aos militares corretamente
- ✅ Gerar logs detalhados do processo

## 📁 ARQUIVOS NECESSÁRIOS

1. **`migracao_supabase_3_etapas.py`** - Script principal de migração
2. **`configurar_migracao.py`** - Configurador de ambiente
3. **`GUIA_MIGRACAO_3_ETAPAS.md`** - Este guia
4. **`.env`** - Arquivo de configurações (será criado)

## 🔧 PRÉ-REQUISITOS

### 1. Dependências Python
```bash
pip install psycopg2-binary python-dotenv
```

### 2. Acesso aos Bancos
- ✅ Acesso ao painel do Supabase
- ✅ Credenciais do banco local
- ✅ Conexão de rede estável

### 3. Backup
- ✅ Backup do banco local realizado
- ✅ Backup do Supabase (se houver dados)

## 🚀 PROCESSO DE MIGRAÇÃO

### PASSO 1: Configuração

1. **Execute o configurador:**
   ```bash
   python configurar_migracao.py
   ```

2. **Preencha as informações solicitadas:**
   - Host do Supabase
   - Senha do Supabase
   - Configurações do banco local
   - Outras configurações opcionais

3. **Verifique se o arquivo `.env` foi criado:**
   ```bash
   cat .env
   ```

### PASSO 2: Execução da Migração

1. **Execute o script principal:**
   ```bash
   python migracao_supabase_3_etapas.py
   ```

2. **Confirme a execução quando solicitado**

3. **Aguarde a conclusão das 3 etapas**

## 📊 DETALHES DAS ETAPAS

### ETAPA 1: Usuários e Dados Básicos
- **Objetivo**: Migrar todos os usuários do sistema
- **Dados**: Tabela `auth_user`
- **Lotes**: 50 usuários por vez
- **Pausa**: 2 segundos entre lotes
- **Tempo estimado**: 5-10 minutos

### ETAPA 2: Militares e Associações
- **Objetivo**: Migrar militares e associar aos usuários
- **Dados**: Tabela `militares_militar` + associações
- **Lotes**: 30 militares por vez
- **Pausa**: 3 segundos entre lotes
- **Tempo estimado**: 10-15 minutos

### ETAPA 3: Dados Complementares
- **Objetivo**: Migrar todas as outras tabelas
- **Dados**: Comissões, quadros, documentos, etc.
- **Lotes**: 20 registros por vez
- **Pausa**: 2 segundos entre lotes
- **Tempo estimado**: 15-20 minutos

## 📋 TABELAS MIGRADAS

### Etapa 1
- `auth_user` - Usuários do sistema

### Etapa 2
- `militares_militar` - Militares
- Associações usuário-militar

### Etapa 3
- `militares_cargo` - Cargos
- `militares_funcao` - Funções
- `militares_comissaopromocao` - Comissões
- `militares_membrocomissao` - Membros de comissão
- `militares_quadroacesso` - Quadros de acesso
- `militares_documentosessao` - Documentos de sessão
- `militares_ataassinatura` - Assinaturas de ata
- `militares_votodeliberacao` - Votos de deliberação
- `militares_documentocomissao` - Documentos de comissão
- `militares_almanaque` - Almanaques
- `militares_almanaqueassinatura` - Assinaturas de almanaque
- `militares_calendariopromocao` - Calendários de promoção
- `militares_notificacao` - Notificações

## 📊 MONITORAMENTO

### Logs Gerados
- **Arquivo**: `migracao_log_YYYYMMDD_HHMMSS.txt`
- **Conteúdo**: Todas as operações realizadas
- **Formato**: Timestamp + mensagem

### Verificações Automáticas
- Contagem de registros por tabela
- Verificação de associações
- Status de sequências de ID
- Tratamento de erros

## ⚠️ PONTOS DE ATENÇÃO

### Antes da Migração
- ✅ Faça backup completo do banco local
- ✅ Faça backup do Supabase (se houver dados)
- ✅ Verifique conexão de rede
- ✅ Confirme credenciais corretas

### Durante a Migração
- ⏸️ Não interrompa o processo
- 📊 Monitore o arquivo de log
- 🔍 Verifique se não há erros
- ⏱️ Aguarde cada etapa completar

### Após a Migração
- ✅ Verifique os totais de registros
- ✅ Teste login com diferentes usuários
- ✅ Confirme associações usuário-militar
- ✅ Teste funcionalidades principais

## 🔍 SOLUÇÃO DE PROBLEMAS

### Erro de Conexão
```
❌ Erro ao conectar ao banco Supabase
```
**Solução:**
1. Verifique as credenciais no arquivo `.env`
2. Confirme se o host está correto
3. Teste a conexão manualmente

### Erro de Permissão
```
❌ Erro de permissão na tabela
```
**Solução:**
1. Verifique se o usuário tem permissões adequadas
2. Confirme se as migrações Django foram aplicadas
3. Verifique se as tabelas existem

### Erro de Constraint
```
❌ Erro de foreign key
```
**Solução:**
1. Verifique se os dados relacionados existem
2. Confirme se as sequências estão corretas
3. Verifique se não há dados duplicados

### Migração Interrompida
**Solução:**
1. Verifique o arquivo de log
2. Identifique onde parou
3. Execute novamente (o script é idempotente)

## 📞 SUPORTE

### Informações Úteis
- **Arquivo de log**: Contém detalhes de todas as operações
- **Configurações**: Arquivo `.env` com todas as credenciais
- **Backup**: Sempre mantenha backups antes da migração

### Em Caso de Problemas
1. Verifique o arquivo de log
2. Confirme as configurações no `.env`
3. Teste as conexões manualmente
4. Verifique se as dependências estão instaladas

## ✅ CHECKLIST FINAL

- [ ] Dependências instaladas
- [ ] Configurações definidas no `.env`
- [ ] Backup do banco local realizado
- [ ] Backup do Supabase realizado
- [ ] Migração executada com sucesso
- [ ] Logs verificados
- [ ] Funcionalidades testadas
- [ ] Usuários associados corretamente

## 🎉 CONCLUSÃO

Após seguir este guia, todos os dados estarão migrados para o Supabase de forma segura e controlada. O sistema estará pronto para uso em produção.

---

**Versão**: 1.0  
**Data**: 29/07/2025  
**Autor**: Sistema de Promoções CBMEPI 