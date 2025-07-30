# 🚀 MIGRAÇÃO COMPLETA PARA SUPABASE - SISTEMA CBMEPI

## 📋 VISÃO GERAL

Este projeto contém todos os scripts necessários para migrar o sistema de promoções do CBMEPI do banco local para o Supabase de forma segura e controlada, dividindo o processo em 3 etapas para evitar sobrecarga.

## 🎯 OBJETIVOS

- ✅ Migrar todos os dados de forma segura
- ✅ Evitar sobrecarga do banco Supabase
- ✅ Manter integridade dos dados
- ✅ Associar usuários aos militares corretamente
- ✅ Gerar logs detalhados do processo
- ✅ Permitir verificação pós-migração

## 📁 ARQUIVOS DO PROJETO

### Scripts Principais
- **`executar_migracao_completa.py`** - Script principal que orquestra todo o processo
- **`migracao_supabase_3_etapas.py`** - Script de migração dividida em 3 etapas
- **`configurar_migracao.py`** - Configurador de ambiente e credenciais
- **`backup_pre_migracao.py`** - Script de backup antes da migração
- **`verificar_migracao.py`** - Verificador pós-migração

### Documentação
- **`README_MIGRACAO_SUPABASE.md`** - Este arquivo
- **`GUIA_MIGRACAO_3_ETAPAS.md`** - Guia detalhado das 3 etapas
- **`MIGRACAO_SUPABASE_README.md`** - Documentação original

### Arquivos de Dados
- **`migracao_supabase_20250729_130359.sql`** - Script SQL de migração
- **`associacao_usuarios_20250729_130444.sql`** - Script de associação de usuários

## 🔧 PRÉ-REQUISITOS

### 1. Dependências Python
```bash
pip install psycopg2-binary python-dotenv
```

### 2. Acesso aos Bancos
- ✅ Acesso ao painel do Supabase
- ✅ Credenciais do banco local PostgreSQL
- ✅ Conexão de rede estável

### 3. Permissões
- ✅ Permissões de escrita no Supabase
- ✅ Permissões de leitura no banco local
- ✅ Permissões para executar pg_dump

## 🚀 EXECUÇÃO RÁPIDA

### Opção 1: Execução Automatizada (Recomendada)
```bash
python executar_migracao_completa.py
```

Este comando irá:
1. ✅ Verificar dependências
2. ✅ Configurar ambiente
3. ✅ Fazer backup dos dados
4. ✅ Executar migração em 3 etapas
5. ✅ Verificar resultados

### Opção 2: Execução Manual
```bash
# 1. Configurar ambiente
python configurar_migracao.py

# 2. Fazer backup
python backup_pre_migracao.py

# 3. Executar migração
python migracao_supabase_3_etapas.py

# 4. Verificar resultados
python verificar_migracao.py
```

## 📊 DETALHES DAS 3 ETAPAS

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

## 📊 MONITORAMENTO E LOGS

### Arquivos de Log Gerados
- **`execucao_completa_YYYYMMDD_HHMMSS.log`** - Log da execução completa
- **`migracao_log_YYYYMMDD_HHMMSS.txt`** - Log da migração
- **`relatorio_verificacao_YYYYMMDD_HHMMSS.txt`** - Relatório de verificação

### Backup Gerados
- **`backups_pre_migracao_YYYYMMDD_HHMMSS/`** - Diretório com backups
  - `backup_local_YYYYMMDD_HHMMSS.dump` - Backup do banco local
  - `backup_supabase_YYYYMMDD_HHMMSS.dump` - Backup do Supabase
  - `dados_backup_YYYYMMDD_HHMMSS.json` - Dados em JSON
  - `relatorio_backup_YYYYMMDD_HHMMSS.txt` - Relatório de backup

## ⚠️ PONTOS DE ATENÇÃO

### Antes da Migração
- ✅ Faça backup completo do banco local
- ✅ Faça backup do Supabase (se houver dados)
- ✅ Verifique conexão de rede
- ✅ Confirme credenciais corretas
- ✅ Teste em ambiente de desenvolvimento

### Durante a Migração
- ⏸️ Não interrompa o processo
- 📊 Monitore os arquivos de log
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

### Timeout na Execução
**Solução:**
1. Verifique a conexão de rede
2. Aumente o timeout se necessário
3. Execute em horários de menor tráfego

## 📞 SUPORTE

### Informações Úteis
- **Arquivos de log**: Contêm detalhes de todas as operações
- **Configurações**: Arquivo `.env` com todas as credenciais
- **Backup**: Sempre mantenha backups antes da migração

### Em Caso de Problemas
1. Verifique os arquivos de log
2. Confirme as configurações no `.env`
3. Teste as conexões manualmente
4. Verifique se as dependências estão instaladas
5. Consulte a documentação detalhada

## ✅ CHECKLIST FINAL

- [ ] Dependências instaladas (`psycopg2-binary`)
- [ ] Configurações definidas no `.env`
- [ ] Backup do banco local realizado
- [ ] Backup do Supabase realizado
- [ ] Migração executada com sucesso
- [ ] Logs verificados
- [ ] Funcionalidades testadas
- [ ] Usuários associados corretamente
- [ ] Sistema funcionando em produção

## 🎉 CONCLUSÃO

Após seguir este guia, todos os dados estarão migrados para o Supabase de forma segura e controlada. O sistema estará pronto para uso em produção com todas as funcionalidades preservadas.

### Próximos Passos
1. Configure o ambiente de produção para usar o Supabase
2. Atualize as configurações do Django
3. Teste todas as funcionalidades
4. Monitore o sistema nos primeiros dias

---

**Versão**: 1.0  
**Data**: 29/07/2025  
**Autor**: Sistema de Promoções CBMEPI  
**Status**: Pronto para produção 