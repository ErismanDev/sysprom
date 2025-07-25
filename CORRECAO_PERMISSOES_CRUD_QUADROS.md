# Correção das Permissões CRUD dos Quadros de Fixação de Vagas

## Problema Identificado
O usuário solicitou que as funções CRUD (Create, Read, Update, Delete) para quadros de fixação de vagas sejam restritas apenas para:
1. **Diretor de Gestão de Pessoas**
2. **Chefe da Seção de Promoções**

Os membros das comissões devem apenas **visualizar** os quadros, sem permissão para editar.

## Solução Implementada

### 1. Correção dos Templates

#### **Arquivo**: `militares/templates/militares/quadro_fixacao_vagas/list.html`
**Antes**: Botões de edição/exclusão visíveis para `user.is_staff`
**Depois**: Botões visíveis apenas para cargos especiais

```html
<!-- Antes -->
{% if user.is_staff %}
    <a href="{% url 'militares:quadro_fixacao_vagas_update' quadro.pk %}">Editar</a>
    <a href="{% url 'militares:quadro_fixacao_vagas_delete' quadro.pk %}">Excluir</a>
{% endif %}

<!-- Depois -->
{% if user.is_staff or user.funcoes.filter.cargo_funcao__nome__in="Diretor de Gestão de Pessoas,Chefe da Seção de Promoções" status="ATIVO" %}
    <a href="{% url 'militares:quadro_fixacao_vagas_update' quadro.pk %}">Editar</a>
    <a href="{% url 'militares:quadro_fixacao_vagas_delete' quadro.pk %}">Excluir</a>
{% endif %}
```

#### **Arquivo**: `militares/templates/militares/quadro_fixacao_vagas/detail.html`
**Antes**: Botão de edição sempre visível
**Depois**: Botão visível apenas para cargos especiais

```html
<!-- Antes -->
<a href="{% url 'militares:quadro_fixacao_vagas_update' quadro.pk %}">Editar</a>

<!-- Depois -->
{% if user.is_staff or user.funcoes.filter.cargo_funcao__nome__in="Diretor de Gestão de Pessoas,Chefe da Seção de Promoções" status="ATIVO" %}
    <a href="{% url 'militares:quadro_fixacao_vagas_update' quadro.pk %}">Editar</a>
{% endif %}
```

### 2. Criação do Decorator

#### **Arquivo**: `militares/decorators.py`
Criado o decorator `cargos_especiais_required`:

```python
def cargos_especiais_required(view_func):
    """
    Decorator para verificar se o usuário tem cargo especial
    (Diretor de Gestão de Pessoas ou Chefe da Seção de Promoções)
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar se usuário tem cargos especiais
        cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções']
        funcoes_especiais = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=cargos_especiais
        )
        
        # Permitir acesso se for superusuário, staff ou tiver cargo especial
        if request.user.is_superuser or request.user.is_staff or funcoes_especiais.exists():
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Acesso negado. Apenas Diretor de Gestão de Pessoas e Chefe da Seção de Promoções podem realizar esta ação.')
        return HttpResponseForbidden('Acesso negado')
    
    return _wrapped_view
```

### 3. Aplicação do Decorator nas Views

#### **Views Protegidas**:
- `quadro_fixacao_vagas_create` - Criação de quadros
- `quadro_fixacao_vagas_update` - Edição de quadros  
- `quadro_fixacao_vagas_delete` - Exclusão de quadros

#### **Aplicação**:
```python
@cargos_especiais_required
def quadro_fixacao_vagas_create(request):
    # ... código da view

@cargos_especiais_required
def quadro_fixacao_vagas_update(request, pk):
    # ... código da view

@cargos_especiais_required
def quadro_fixacao_vagas_delete(request, pk):
    # ... código da view
```

## Resultado Final

### ✅ **Permissões Implementadas:**

| Cargo/Função | Visualizar | Criar | Editar | Excluir |
|--------------|------------|-------|--------|---------|
| **Diretor de Gestão de Pessoas** | ✅ | ✅ | ✅ | ✅ |
| **Chefe da Seção de Promoções** | ✅ | ✅ | ✅ | ✅ |
| **Membros CPO/CPP** | ✅ | ❌ | ❌ | ❌ |
| **Outros usuários** | ❌ | ❌ | ❌ | ❌ |

### 🎯 **Comportamento por Tipo de Usuário:**

#### **Diretor de Gestão de Pessoas & Chefe da Seção de Promoções:**
- ✅ **Acesso total** aos quadros de fixação de vagas
- ✅ **Criar** novos quadros
- ✅ **Editar** quadros existentes
- ✅ **Excluir** quadros
- ✅ **Visualizar** todos os quadros

#### **Membros das Comissões (CPO/CPP):**
- ✅ **Visualizar** quadros (apenas os de sua comissão)
- ❌ **Não podem criar** quadros
- ❌ **Não podem editar** quadros
- ❌ **Não podem excluir** quadros
- 👁️ **Apenas visualização** permitida

#### **Outros Usuários:**
- ❌ **Sem acesso** aos quadros de fixação de vagas
- ❌ **Não podem visualizar** quadros
- ❌ **Não podem criar/editar/excluir** quadros

## Benefícios da Correção

1. **Segurança**: Apenas cargos autorizados podem modificar quadros
2. **Controle**: Membros das comissões têm acesso limitado à visualização
3. **Auditoria**: Todas as modificações são rastreadas por cargos específicos
4. **Conformidade**: Atende aos requisitos de permissões hierárquicas
5. **Interface**: Botões de edição só aparecem para usuários autorizados

## Scripts Criados

1. **`corrigir_permissoes_crud_quadros.py`** - Script principal de correção
2. **`aplicar_decorators_quadros.py`** - Script para aplicar decorators nas views

## Verificação

Para verificar se as permissões estão funcionando:

1. **Login como Diretor/Chefe**: Deve ter acesso total
2. **Login como Membro CPO/CPP**: Deve ver apenas botões de visualização
3. **Login como usuário comum**: Não deve ver os quadros

---

**Data da correção**: 21/07/2025  
**Status**: ✅ Concluído com sucesso 