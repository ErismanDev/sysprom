# Guia de Gerenciamento de Permissões

## 📋 Visão Geral

O sistema de permissões permite controlar o que cada usuário pode fazer no sistema baseado em sua função/cargo. A interface web facilita o gerenciamento dessas permissões de forma intuitiva.

## 🚀 Como Acessar

1. **URL Principal**: `http://127.0.0.1:8000/militares/permissoes/`
2. **Menu Lateral**: Clique em "Permissões" no menu lateral
3. **Requisitos**: Usuário deve ter permissão de visualização de usuários

## 🎯 Funcionalidades Principais

### 1. Dashboard de Permissões
- **Estatísticas**: Visualize total de cargos, perfis e permissões
- **Lista de Cargos**: Veja todos os cargos/funções ativos
- **Lista de Perfis**: Veja todos os perfis de acesso disponíveis
- **Ações Rápidas**: Links diretos para funcionalidades principais

### 2. Gerenciar Permissões por Cargo
- **Visualizar**: Veja todas as permissões de um cargo específico
- **Editar**: Modifique permissões individualmente
- **Aplicar Perfil**: Use um perfil predefinido para aplicar múltiplas permissões

### 3. Gerenciar Perfis de Acesso
- **Criar**: Crie novos perfis de acesso
- **Editar**: Modifique perfis existentes
- **Visualizar**: Veja detalhes de cada perfil

## 📝 Como Usar

### Passo 1: Acessar a Interface
```
http://127.0.0.1:8000/militares/permissoes/
```

### Passo 2: Visualizar Cargos
1. Na seção "Cargos/Funções", clique no ícone de olho (👁️) ao lado do cargo
2. Veja todas as permissões configuradas para aquele cargo
3. As permissões são agrupadas por módulo (Militares, Documentos, etc.)

### Passo 3: Editar Permissões
1. Clique no ícone de editar (✏️) ao lado do cargo
2. Marque/desmarque as permissões desejadas:
   - **Módulos**: Militares, Fichas de Conceito, Quadros de Acesso, etc.
   - **Acessos**: Visualizar, Criar, Editar, Excluir, Aprovar, etc.
3. Clique em "Salvar Permissões"

### Passo 4: Aplicar Perfil
1. Na tela de edição, role até "Aplicar Perfil de Acesso"
2. Selecione um perfil da lista
3. Clique em "Aplicar Perfil"
4. Confirme a ação

### Passo 5: Criar Novo Perfil
1. Clique em "Novo Perfil" na seção de perfis
2. Preencha nome e descrição
3. Marque as permissões desejadas
4. Clique em "Salvar"

## 🔧 Módulos Disponíveis

| Módulo | Descrição |
|--------|-----------|
| MILITARES | Gestão de Militares |
| FICHAS_CONCEITO | Fichas de Conceito |
| QUADROS_ACESSO | Quadros de Acesso |
| PROMOCOES | Promoções |
| VAGAS | Gestão de Vagas |
| COMISSAO | Comissão de Promoções |
| DOCUMENTOS | Documentos |
| USUARIOS | Gestão de Usuários |
| RELATORIOS | Relatórios |
| CONFIGURACOES | Configurações do Sistema |

## 🔑 Tipos de Acesso

| Acesso | Descrição |
|--------|-----------|
| VISUALIZAR | Pode ver informações |
| CRIAR | Pode criar novos registros |
| EDITAR | Pode modificar registros existentes |
| EXCLUIR | Pode remover registros |
| APROVAR | Pode aprovar processos |
| HOMOLOGAR | Pode homologar documentos |
| GERAR_PDF | Pode gerar PDFs |
| IMPRIMIR | Pode imprimir documentos |
| ASSINAR | Pode assinar documentos |
| ADMINISTRAR | Acesso administrativo completo |

## 👥 Perfis Predefinidos

### 1. Administrador
- **Descrição**: Acesso total ao sistema
- **Permissões**: Todas as permissões em todos os módulos
- **Usado para**: Administradores do sistema

### 2. Gestor
- **Descrição**: Acesso de gestão sem administração
- **Permissões**: Criar, editar, visualizar na maioria dos módulos
- **Usado para**: Chefes de seção, diretores

### 3. Operador
- **Descrição**: Acesso operacional básico
- **Permissões**: Visualizar e criar em módulos específicos
- **Usado para**: Digitadores, operadores

### 4. Membro de Comissão
- **Descrição**: Acesso específico para comissões
- **Permissões**: Visualizar e participar de comissões
- **Usado para**: Membros de comissões de promoções

### 5. Consulta
- **Descrição**: Acesso apenas de visualização
- **Permissões**: Apenas visualizar
- **Usado para**: Consultas gerais

## 🎯 Casos de Uso Comuns

### 1. Novo Usuário
1. Criar usuário no sistema
2. Atribuir função/cargo ao usuário
3. Verificar se o cargo tem permissões configuradas
4. Se não tiver, aplicar um perfil adequado

### 2. Mudança de Função
1. Acessar gerenciamento de usuários
2. Alterar função do usuário
3. Verificar se a nova função tem permissões adequadas

### 3. Ajuste de Permissões
1. Identificar o cargo que precisa de ajuste
2. Acessar edição de permissões
3. Marcar/desmarcar permissões específicas
4. Salvar alterações

### 4. Criação de Perfil Personalizado
1. Identificar necessidade de novo perfil
2. Criar perfil com nome e descrição
3. Marcar permissões específicas
4. Aplicar perfil aos cargos adequados

## 🔍 Troubleshooting

### Problema: Usuário não consegue acessar funcionalidade
**Solução**:
1. Verificar se o usuário tem função atribuída
2. Verificar se a função tem permissão para o módulo
3. Verificar se a permissão está ativa

### Problema: Permissões não aparecem
**Solução**:
1. Verificar se o cargo está ativo
2. Verificar se as permissões estão marcadas como ativas
3. Limpar cache do navegador

### Problema: Erro ao salvar permissões
**Solução**:
1. Verificar se tem permissão de administração
2. Verificar se o formulário está completo
3. Tentar novamente

## 📊 Relatórios e Estatísticas

### Estatísticas Disponíveis
- Total de cargos ativos
- Total de perfis de acesso
- Total de permissões ativas
- Usuários por cargo
- Permissões por módulo

### Como Acessar
1. Dashboard principal: `http://127.0.0.1:8000/militares/permissoes/`
2. Detalhes do cargo: Clique no cargo específico
3. Detalhes do perfil: Clique no perfil específico

## 🔗 Links Úteis

- **Gerenciar Permissões**: `/militares/permissoes/`
- **Gerenciar Usuários**: `/militares/usuarios/custom/`
- **Admin Django**: `/admin/`
- **Dashboard**: `/militares/`

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique este guia
2. Consulte a documentação do sistema
3. Entre em contato com o administrador do sistema

---

**Última atualização**: Janeiro 2025
**Versão**: 1.0 