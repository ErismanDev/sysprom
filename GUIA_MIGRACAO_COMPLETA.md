# 🚀 Guia Completo de Migração para Supabase

## 📋 Objetivo
Migrar todos os dados do banco local PostgreSQL para o Supabase, incluindo usuários, militares, comissões, quadros e todos os dados relacionados.

## 🔧 Pré-requisitos

### 1. ✅ Banco Local Funcionando
- PostgreSQL local configurado
- Dados existentes no banco local
- Django funcionando localmente

### 2. ✅ Supabase Configurado
- Projeto Supabase criado
- Credenciais de acesso
- DATABASE_URL configurada no Render

### 3. ✅ Render Configurado
- Aplicação deployada no Render
- Variáveis de ambiente configuradas
- Build funcionando

## 🚀 Processo de Migração

### Passo 1: Verificar Configuração Atual

Execute o script de verificação:

```bash
python verificar_configuracao_render.py
```

**Resultado esperado:**
- ✅ Variáveis de ambiente configuradas
- ✅ Conexão com Supabase estabelecida
- ⚠️ Nenhum dado encontrado no banco (normal, pois ainda não migramos)

### Passo 2: Executar Migração Completa

Execute o script de migração:

```bash
python migrar_dados_completos_supabase.py
```

**O que o script fará:**
1. 🔍 Verificar dados no banco local
2. 💾 Fazer backup completo dos dados
3. 🌐 Configurar ambiente Supabase
4. 🧪 Testar conexão com Supabase
5. 🗄️ Aplicar migrações no Supabase
6. 📤 Carregar dados no Supabase
7. 🔍 Verificar se a migração foi bem-sucedida
8. 👤 Criar superusuário (se necessário)
9. 🧹 Limpar arquivos temporários

### Passo 3: Verificar Migração

Após a migração, execute novamente:

```bash
python verificar_configuracao_render.py
```

**Resultado esperado:**
- ✅ Dados encontrados no banco
- ✅ Usuários, militares, comissões presentes

## 📊 Dados que Serão Migrados

### 👥 Usuários e Autenticação
- Todos os usuários do sistema
- Grupos e permissões
- Perfis de acesso

### 🎖️ Militares
- Dados pessoais completos
- Informações militares
- Fichas de conceito (oficiais e praças)
- Documentos anexados
- Histórico de promoções

### 🏛️ Comissões
- Comissões de promoção
- Membros das comissões
- Sessões realizadas
- Deliberações e votos
- Atas de sessão

### 📋 Quadros e Vagas
- Quadros de acesso
- Itens dos quadros
- Vagas disponíveis
- Previsões de vagas
- Quadros de fixação

### 📚 Cursos e Condecorações
- Cursos cadastrados
- Medalhas e condecorações
- Interstícios

### 📄 Documentação
- Modelos de ata
- Notificações
- Calendários de promoção
- Almanaques

## 🔧 Configurações Especiais

### Arquivos de Mídia
Os arquivos de mídia (fotos, documentos) precisam ser migrados separadamente:

1. **Fazer backup dos arquivos:**
   ```bash
   # Copiar pasta media
   cp -r media/ media_backup/
   ```

2. **Fazer upload para o Supabase Storage (se necessário):**
   - Acesse o painel do Supabase
   - Vá para Storage
   - Faça upload dos arquivos

### Configurações de Segurança
- Senhas de usuários são preservadas
- Chaves de criptografia mantidas
- Permissões e grupos preservados

## ⚠️ Problemas Comuns e Soluções

### Erro: "Conexão com Supabase falhou"
**Causa:** DATABASE_URL incorreta ou Supabase inacessível

**Solução:**
1. Verificar DATABASE_URL no painel do Render
2. Confirmar credenciais do Supabase
3. Verificar conectividade de rede

### Erro: "Nenhum dado encontrado no banco local"
**Causa:** Banco local vazio ou configuração incorreta

**Solução:**
1. Verificar se o banco local tem dados
2. Confirmar configuração do settings.py
3. Testar conexão local

### Erro: "Migrações falharam"
**Causa:** Conflitos de migração ou estrutura de banco diferente

**Solução:**
1. Verificar se todas as migrações estão aplicadas localmente
2. Executar `python manage.py makemigrations` se necessário
3. Verificar compatibilidade de versões

### Erro: "Dados não carregados"
**Causa:** Problemas no formato do backup ou conflitos de chaves

**Solução:**
1. Verificar se o backup foi criado corretamente
2. Verificar logs de erro detalhados
3. Tentar carregar dados em lotes menores

## 📋 Verificação Pós-Migração

### 1. Testar Aplicação no Render
- Acesse: https://sysprom.onrender.com
- Faça login com credenciais existentes
- Verifique se todos os dados estão presentes

### 2. Verificar Funcionalidades Principais
- ✅ Lista de militares
- ✅ Comissões de promoção
- ✅ Quadros de acesso
- ✅ Geração de documentos
- ✅ Sistema de permissões

### 3. Verificar Dados Específicos
- Contagem de registros
- Relacionamentos entre tabelas
- Arquivos anexados
- Histórico de atividades

## 🔄 Rollback (Se Necessário)

Se algo der errado, você pode:

1. **Restaurar banco local:**
   ```bash
   python manage.py loaddata backup_completo_YYYYMMDD_HHMMSS.json
   ```

2. **Limpar Supabase:**
   ```bash
   python manage.py flush --settings=sepromcbmepi.settings_render
   ```

3. **Recomeçar migração:**
   ```bash
   python migrar_dados_completos_supabase.py
   ```

## 📞 Suporte

Se encontrar problemas:

1. **Verificar logs detalhados** do script de migração
2. **Consultar logs do Render** no painel
3. **Verificar logs do Supabase** no dashboard
4. **Testar conexões** individualmente

## 🎯 Resultado Final

Após a migração bem-sucedida:

- ✅ Todos os dados migrados para o Supabase
- ✅ Aplicação funcionando no Render
- ✅ Usuários podem fazer login
- ✅ Todas as funcionalidades operacionais
- ✅ Sistema pronto para produção

---

**Última atualização:** 29/07/2025
**Status:** Pronto para execução 