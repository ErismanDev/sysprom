# Documentação - Geração de Quadro de Acesso

## Visão Geral

A funcionalidade de **Geração de Quadro de Acesso** permite criar automaticamente quadros de acesso para promoções de militares conforme a Lei 5.461/2005, alterada pela Lei 7.772/2022.

## Acesso à Funcionalidade

**URL:** `/militares/gerar-quadro-acesso/`

## Como Usar

### 1. Acessar a Página
- Navegue até `/militares/gerar-quadro-acesso/`
- Faça login no sistema (se necessário)

### 2. Preencher os Campos Obrigatórios

#### Tipo de Quadro
- **Antiguidade:** Ordenação por data de promoção atual (mais antigo primeiro)
- **Merecimento:** Ordenação por pontuação da ficha de conceito (maior pontuação primeiro)

#### Quadro
- **Combatente:** Quadro de oficiais combatentes
- **Saúde:** Quadro de oficiais da área de saúde
- **Engenheiro:** Quadro de oficiais engenheiros
- **Complementar:** Quadro de oficiais complementares

#### Posto Atual
- Selecione o posto atual dos militares que serão promovidos
- O sistema mostrará automaticamente o próximo posto

#### Data da Promoção
- Informe a data prevista para a promoção
- Não pode ser anterior à data atual

### 3. Gerar o Quadro
- Clique em "Gerar Quadro"
- O sistema processará automaticamente e criará o quadro

## Validações Automáticas

O sistema valida automaticamente os seguintes requisitos para cada militar:

### 1. Ficha de Conceito
- Militar deve possuir ficha de conceito cadastrada

### 2. Interstício Mínimo
- Militar deve ter completado o interstício mínimo até a data da promoção
- Configurado por posto e quadro no sistema

### 3. Inspeção de Saúde
- Militar deve estar apto em inspeção de saúde
- Data de validade deve estar em dia

### 4. Cursos Inerentes
- Militar deve possuir os cursos necessários para o posto subsequente

### 5. Numeração de Antiguidade
- Cada militar possui uma numeração de antiguidade dentro do seu posto e quadro
- **Informada manualmente** pelos usuários do sistema
- Militar mais antigo no posto deve ter numeração menor
- Importante para desempates e identificação da posição hierárquica

#### Cursos por Quadro:

**Combatente:**
- 2º Tenente → 1º Tenente: CFO
- 1º Tenente → Capitão: CFO
- Capitão → Major: CFO + CAO
- Major → Tenente-Coronel: CFO + CAO
- Tenente-Coronel → Coronel: CFO + CAO + CSBM

**Saúde:**
- Mesmos requisitos do quadro combatente

**Engenheiro:**
- Aspirante → 2º Tenente: CADOF
- Demais postos: Mesmos requisitos do quadro combatente

**Complementar:**
- Subtenente → 2º Tenente: CHO
- 2º Tenente → 1º Tenente: CHO
- 1º Tenente → Capitão: CHO
- Capitão → Major: CHO + Curso Superior
- Major → Tenente-Coronel: CHO + Curso Superior + Pós-Graduação
- Tenente-Coronel → Coronel: CHO + Curso Superior + Pós-Graduação + CSBM

## Critérios de Ordenação

### Quadro por Antiguidade
- Ordenação por data de promoção atual (mais antiga primeiro)
- Não considera pontuação da ficha de conceito
- Usado para promoções automáticas

### Quadro por Merecimento
- Ordenação por pontuação da ficha de conceito (maior pontuação primeiro)
- Em caso de empate, considera antiguidade
- Usado para promoções por mérito

## Numeração de Antiguidade

### Como Funciona
Cada militar possui uma numeração de antiguidade específica dentro do seu posto e quadro. Esta numeração deve ser **informada manualmente** pelos usuários do sistema.

### Inserção Manual
1. **Campo editável**: No cadastro do militar, campo "Numeração de Antiguidade (Manual)"
2. **Validação automática**: Sistema verifica duplicações no mesmo posto/quadro
3. **Formato**: Número inteiro positivo (ex: 1, 2, 3...)
4. **Obrigatoriedade**: Militares ativos devem ter numeração informada
5. **Interface**: Campo disponível nos templates de criação e edição
6. **Visualização**: Exibida na lista de militares e página de detalhes

### Exemplo
- **2º Tenente/Combatente**: 5 militares
  - 1º - Militar A (numeração: 1)
  - 2º - Militar B (numeração: 2)
  - 3º - Militar C (numeração: 3)
  - 4º - Militar D (numeração: 4)
  - 5º - Militar E (numeração: 5)

### Importância
- **Desempates**: Usada para resolver empates em quadros por merecimento
- **Hierarquia**: Identifica a posição hierárquica dentro de cada posto
- **Transparência**: Torna clara a ordem de antiguidade
- **Conformidade**: Atende aos requisitos legais de antiguidade

### Validações
- **Duplicação**: Não permite mesma numeração no mesmo posto/quadro
- **Formato**: Apenas números inteiros positivos
- **Obrigatoriedade**: Militares ativos devem ter numeração
- **Verificação**: Comando para validar numerações existentes

### Templates Atualizados
- **Formulário de Militar**: Campo de numeração na seção "Informações Básicas" (antes da matrícula)
- **Lista de Militares**: Coluna "Antiguidade" na tabela
- **Detalhes do Militar**: Exibição da numeração na página de detalhes
- **Validação JavaScript**: Validação em tempo real no formulário
- **Campo Estado Civil**: Removido do sistema conforme solicitação

## Status do Quadro

### Elaborado
- Quadro foi gerado com sucesso
- Militares aptos foram incluídos e ordenados

### Não Elaborado
- Não há militares aptos para o quadro
- Motivo detalhado é registrado

### Em Elaboração
- Quadro está sendo processado

### Homologado
- Quadro foi homologado oficialmente

## Funcionalidades Adicionais

### Visualizar Quadro
- Após a geração, clique em "Visualizar" para ver o quadro completo
- Mostra posição, militar e pontuação de cada item

### Regenerar Quadro
- Permite regenerar um quadro existente
- Útil quando há mudanças nos dados dos militares

### Homologar Quadro
- Marca o quadro como homologado oficialmente
- Registra a data de homologação

### Excluir Quadro
- Remove o quadro e todos os seus itens
- Ação irreversível

## Relatórios

### Relatório de Requisitos
- Mostra detalhes dos requisitos de cada militar
- Útil para identificar motivos de inaptidão

### Relatório de Aptos à Promoção
- Lista militares aptos para promoção
- Filtros por tipo de quadro e data

## Observações Importantes

1. **Unicidade:** Não é possível criar dois quadros com os mesmos parâmetros (tipo, quadro, posto, data)

2. **Validação em Tempo Real:** O sistema valida os requisitos no momento da geração

3. **Histórico:** Quadros recentes são exibidos na página para consulta

4. **Auditoria:** Todas as ações são registradas com data e usuário

5. **Flexibilidade:** O sistema permite regenerar quadros quando necessário

## Comandos de Gerenciamento

### Validar Numeração de Antiguidade
Para verificar a numeração de antiguidade dos militares:

```bash
# Verificar numeração de todos os militares
python manage.py atualizar_numeracao_antiguidade

# Verificar duplicações na numeração
python manage.py atualizar_numeracao_antiguidade --check
```

### Uso do Comando
- **Sem --check**: Mostra a numeração de todos os militares por grupo
- **Com --check**: Verifica se há duplicações na numeração
- **Saída**: Mostra resumo por grupo (posto/quadro) e alerta sobre duplicações

## Suporte

Para dúvidas ou problemas:
- Consulte a documentação do sistema
- Entre em contato com o administrador
- Verifique os logs do sistema para detalhes técnicos 