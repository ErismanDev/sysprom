# Sistema de Permissões Simplificado

## Visão Geral

O sistema de permissões foi simplificado para ser baseado **apenas nas funções** do usuário, eliminando a complexidade dos grupos e permissões granulares. Agora o controle de acesso é feito de forma mais direta e intuitiva.

## Arquivo Principal

O sistema está implementado no arquivo `militares/permissoes_simples.py`

## Funções de Verificação

### Funções Básicas

```python
from militares.permissoes_simples import *

# Verificar permissões específicas
pode_editar_militares(user)           # Diretor, Chefe, Administrador
pode_editar_fichas_conceito(user)     # Diretor, Chefe, Administrador
pode_gerenciar_quadros_vagas(user)    # Diretor, Chefe, Administrador
pode_gerenciar_comissoes(user)        # Diretor, Chefe, Administrador
pode_gerenciar_usuarios(user)         # Apenas Administrador
pode_assinar_documentos(user)         # Diretor, Chefe, Administrador, Presidentes
pode_visualizar_tudo(user)            # Diretor, Chefe, Administrador
eh_membro_comissao(user)              # Qualquer membro de comissão
```

### Função Genérica

```python
# Verificar se tem alguma função específica
tem_funcao_especial(user, 'Diretor de Gestão de Pessoas,Chefe da Seção de Promoções')
```

## Decorators de Permissão

### Decorators Específicos

```python
from militares.permissoes_simples import *

@requer_edicao_militares
def militar_update(request, pk):
    # Apenas Diretor, Chefe e Administrador podem acessar
    pass

@requer_edicao_fichas_conceito
def ficha_conceito_edit(request, pk):
    # Apenas Diretor, Chefe e Administrador podem acessar
    pass

@requer_gerenciamento_quadros_vagas
def quadro_vagas_create(request):
    # Apenas Diretor, Chefe e Administrador podem acessar
    pass

@requer_gerenciamento_comissoes
def comissao_create(request):
    # Apenas Diretor, Chefe e Administrador podem acessar
    pass

@requer_gerenciamento_usuarios
def usuario_create(request):
    # Apenas Administrador pode acessar
    pass

@requer_assinatura_documentos
def assinar_documento(request, pk):
    # Diretor, Chefe, Administrador e Presidentes podem acessar
    pass
```

### Decorator Genérico

```python
@requer_funcao_especial('Diretor de Gestão de Pessoas,Chefe da Seção de Promoções')
def view_especial(request):
    # Apenas usuários com as funções especificadas podem acessar
    pass
```

### Decorator para Comissões

```python
@apenas_visualizacao_comissao
def militar_list(request):
    # Membros de comissão podem apenas visualizar
    # Diretores, Chefes e Administradores podem editar
    pass
```

## Uso nos Templates

### Context Processor

O context processor `permissoes_simples_processor` disponibiliza as funções nos templates:

```html
{% if pode_editar_militares %}
    <a href="{% url 'militares:militar_edit' militar.pk %}">Editar</a>
{% endif %}

{% if pode_gerenciar_quadros_vagas %}
    <a href="{% url 'militares:quadro_vagas_create' %}">Novo Quadro</a>
{% endif %}

{% if tem_funcao_especial('Diretor de Gestão de Pessoas,Chefe da Seção de Promoções') %}
    <a href="{% url 'militares:admin_area' %}">Área Administrativa</a>
{% endif %}
```

### Template Tag

```html
{% load militares_extras %}

{% if user|tem_funcao_especifica:'Diretor de Gestão de Pessoas,Chefe da Seção de Promoções' %}
    <button>Editar</button>
{% endif %}
```

## Funções Auxiliares

```python
# Obter todas as funções do usuário
funcoes = obter_funcoes_usuario(user)

# Obter funções especiais (Diretor, Chefe, Administrador)
funcoes_especiais = obter_funcoes_especiais_usuario(user)

# Obter funções de comissão
funcoes_comissao = obter_funcoes_comissao_usuario(user)
```

## Hierarquia de Permissões

### 1. Administrador do Sistema
- **Acesso Total**: Pode fazer tudo no sistema
- **Função**: Administrador do Sistema

### 2. Diretor de Gestão de Pessoas
- **Acesso**: Editar militares, fichas, quadros, comissões, assinar documentos
- **Função**: Diretor de Gestão de Pessoas

### 3. Chefe da Seção de Promoções
- **Acesso**: Editar militares, fichas, quadros, comissões, assinar documentos
- **Função**: Chefe da Seção de Promoções

### 4. Presidentes de Comissão
- **Acesso**: Visualizar tudo, assinar documentos
- **Função**: Presidente da CPO, Presidente da CPP

### 5. Membros de Comissão
- **Acesso**: Apenas visualização
- **Função**: CPO, CPP, Membro da CPO, Membro da CPP, etc.

### 6. Usuários Comuns
- **Acesso**: Apenas visualização básica
- **Função**: Usuário

## Migração do Sistema Anterior

### O que Mudou

1. **Eliminação de Grupos**: Não dependemos mais dos grupos do Django
2. **Simplificação**: Permissões baseadas apenas nas funções
3. **Centralização**: Todas as verificações em um único arquivo
4. **Clareza**: Funções com nomes mais descritivos

### Como Migrar

1. **Substituir imports**:
   ```python
   # Antes
   from militares.decorators import can_edit_militar
   
   # Depois
   from militares.permissoes_simples import pode_editar_militares
   ```

2. **Substituir decorators**:
   ```python
   # Antes
   @militar_edit_permission
   
   # Depois
   @requer_edicao_militares
   ```

3. **Substituir verificações**:
   ```python
   # Antes
   if can_edit_militar(request.user):
   
   # Depois
   if pode_editar_militares(request.user):
   ```

## Vantagens do Novo Sistema

1. **Simplicidade**: Menos complexidade, mais fácil de entender
2. **Manutenibilidade**: Código mais limpo e organizado
3. **Performance**: Menos consultas ao banco de dados
4. **Flexibilidade**: Fácil adicionar novas funções e permissões
5. **Clareza**: Nomes de funções mais descritivos

## Exemplo de Uso Completo

```python
from militares.permissoes_simples import *

@login_required
@requer_edicao_militares
def militar_update(request, pk):
    """Atualiza um militar existente"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES, instance=militar)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} atualizado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
    else:
        form = MilitarForm(instance=militar)
    
    context = {
        'form': form,
        'militar': militar,
    }
    
    return render(request, 'militares/militar_form.html', context)
```

## Configuração

O context processor já está configurado no `settings.py`:

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... outros processors
                'militares.permissoes_simples.permissoes_simples_processor',
            ],
        },
    },
]
``` 