# Reordenação Automática Após Inativação de Militares

## Visão Geral

Esta funcionalidade implementa a reordenação automática das numerações de antiguidade quando um militar é inativado, garantindo que a hierarquia seja mantida corretamente e que as vagas sejam atualizadas automaticamente.

## Funcionalidades Implementadas

### 1. Reordenação Automática
- **Quando**: Um militar é inativado (situação alterada para IN, TR, AP, EX)
- **O que acontece**: 
  - As numerações de antiguidade dos militares ativos do mesmo posto/quadro são reordenadas
  - Militares "sobem" uma posição para preencher o gap deixado pelo inativado
  - A numeração é baseada na data da promoção atual (mais antiga = menor número)

### 2. Atualização Automática de Vagas
- **Quando**: Um militar é inativado
- **O que acontece**:
  - A vaga correspondente ao posto/quadro do militar inativado é atualizada
  - O efetivo atual da vaga é diminuído em 1
  - Se não existir vaga, uma nova é criada automaticamente

### 3. Tratamento Especial para Subtenentes
- **Subtenentes com CHO**: Reordenados separadamente
- **Subtenentes sem CHO**: Reordenados separadamente
- **Lógica**: Cada grupo mantém sua própria numeração sequencial

## Como Funciona

### Processo Automático
1. **Detecção de Inativação**: O método `save()` do modelo `Militar` detecta quando a situação muda de 'AT' para uma situação inativa
2. **Reordenação**: Chama o método `reordenar_apos_inativacao()` que:
   - Busca militares ativos do mesmo posto/quadro
   - Reordena as numerações sequencialmente (1º, 2º, 3º, etc.)
   - Atualiza o banco de dados em lote para eficiência
3. **Atualização de Vaga**: Chama o método `_atualizar_vaga_apos_inativacao()` que:
   - Busca a vaga correspondente
   - Diminui o efetivo atual em 1
   - Cria nova vaga se não existir

### Exemplo Prático
```
ANTES da inativação:
- Militar A: 1º (Capitão - COMB)
- Militar B: 2º (Capitão - COMB) ← Será inativado
- Militar C: 3º (Capitão - COMB)
- Militar D: 4º (Capitão - COMB)

DEPOIS da inativação:
- Militar A: 1º (Capitão - COMB)
- Militar C: 2º (Capitão - COMB) ← "Subiu" uma posição
- Militar D: 3º (Capitão - COMB) ← "Subiu" uma posição
- Militar B: Inativo (não aparece mais na lista)
```

## Métodos Implementados

### Militar.reordenar_apos_inativacao()
```python
def reordenar_apos_inativacao(self):
    """
    Reordena as numerações de antiguidade após a inativação de um militar
    """
```

### Militar._atualizar_vaga_apos_inativacao()
```python
def _atualizar_vaga_apos_inativacao(self):
    """
    Atualiza a vaga correspondente quando um militar é inativado
    """
```

### Militar.reordenar_todos_apos_inativacao()
```python
@classmethod
def reordenar_todos_apos_inativacao(cls, posto_graduacao=None, quadro=None):
    """
    Reordena automaticamente todas as numerações de antiguidade após inativações
    """
```

## Interface de Usuário

### 1. Reordenação Manual
- **Acesso**: Status do Efetivo → "Reordenar Antiguidade"
- **Funcionalidade**: Permite reordenar manualmente por posto/quadro específico
- **URL**: `/militares/reordenar-antiguidade-apos-inativacao/`

### 2. Comando de Gerenciamento
```bash
# Reordenar todos os militares
python manage.py reordenar_apos_inativacao

# Reordenar por posto específico
python manage.py reordenar_apos_inativacao --posto CP

# Reordenar por quadro específico
python manage.py reordenar_apos_inativacao --quadro COMB

# Modo de teste (não salva alterações)
python manage.py reordenar_apos_inativacao --dry-run

# Mostrar detalhes
python manage.py reordenar_apos_inativacao --verbose
```

## Casos de Uso

### 1. Inativação Individual
- Militar é inativado através da interface
- Reordenação acontece automaticamente
- Vaga é atualizada automaticamente

### 2. Inativação em Lote
- Múltiplos militares são inativados
- Usar comando de gerenciamento para reordenar todos
- Verificar resultados após execução

### 3. Correção de Inconsistências
- Quando há numerações incorretas
- Usar reordenação manual por posto/quadro
- Verificar resultados antes de prosseguir

## Precauções

### 1. Backup
- Sempre fazer backup antes de executar reordenações em lote
- Testar em ambiente de desenvolvimento primeiro

### 2. Horário de Execução
- Executar em horário de baixo movimento
- Avisar usuários sobre manutenção

### 3. Verificação
- Sempre verificar os resultados após execução
- Confirmar que as numerações estão corretas

## Logs e Monitoramento

### Logs de Erro
- Erros na atualização de vagas são logados
- Não interrompem o processo de reordenação
- Verificar logs em caso de problemas

### Monitoramento
- Verificar periodicamente a consistência das numerações
- Usar relatórios para identificar inconsistências

## Troubleshooting

### Problema: Numerações não foram reordenadas
**Solução**: 
1. Verificar se o militar foi realmente inativado
2. Executar reordenação manual
3. Verificar logs de erro

### Problema: Vaga não foi atualizada
**Solução**:
1. Verificar se existe vaga para o posto/quadro
2. Verificar logs de erro
3. Atualizar vaga manualmente se necessário

### Problema: Inconsistências após reordenação
**Solução**:
1. Executar reordenação completa
2. Verificar dados de entrada
3. Corrigir manualmente se necessário

## Testes

### Script de Teste
```bash
python testar_reordenacao_inativacao.py
```

### Testes Manuais
1. Inativar um militar através da interface
2. Verificar se a reordenação aconteceu
3. Verificar se a vaga foi atualizada
4. Reativar o militar para não afetar os dados

## Configurações

### Mapeamento de Postos
```python
mapeamento_postos = {
    'CB': 'CB',    # Coronel
    'TC': 'TC',    # Tenente-Coronel
    'MJ': 'MJ',    # Major
    'CP': 'CP',    # Capitão
    '1T': '1T',    # 1º Tenente
    '2T': '2T',    # 2º Tenente
    'ST': 'ST',    # Subtenente
    '1S': '1S',    # 1º Sargento
    '2S': '2S',    # 2º Sargento
    '3S': '3S',    # 3º Sargento
    'CAB': 'CAB',  # Cabo
    'SD': 'SD',    # Soldado
}
```

### Situações de Inativação
- `'IN'`: Inativo
- `'TR'`: Transferido
- `'AP'`: Aposentado
- `'EX'`: Exonerado

## Conclusão

Esta funcionalidade garante que a hierarquia militar seja mantida corretamente após inativações, automatizando um processo que antes era manual e propenso a erros. A integração com o sistema de vagas também garante que o controle de efetivo seja sempre atualizado. 