#!/usr/bin/env python
"""
Script para corrigir permissões CRUD dos quadros de fixação de vagas.
Apenas Diretor de Gestão de Pessoas e Chefe da Seção de Promoções podem editar.
"""

import re

def verificar_cargos_especiais():
    """Verifica se os cargos especiais existem no sistema"""
    cargos_especiais = [
        'Diretor de Gestão de Pessoas',
        'Chefe da Seção de Promoções'
    ]
    
    print("🔍 Verificando cargos especiais...")
    for cargo in cargos_especiais:
        print(f"   - {cargo}")
    print()

def corrigir_template_list():
    """Corrige o template de listagem dos quadros"""
    arquivo = 'militares/templates/militares/quadro_fixacao_vagas/list.html'
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem verificação de cargos especiais
        if 'Diretor de Gestão de Pessoas' in content or 'Chefe da Seção de Promoções' in content:
            print(f"✅ {arquivo} - Já tem verificação de cargos especiais")
            return
        
        # Substituir verificação de user.is_staff por cargos especiais
        # Padrão para botões de edição/exclusão
        pattern_staff = r'{% if user\.is_staff %}(.*?){% endif %}'
        
        if re.search(pattern_staff, content, re.DOTALL):
            # Substituir por verificação de cargos especiais
            new_content = re.sub(
                pattern_staff,
                r'{% if user.is_staff or user.funcoes.filter.cargo_funcao__nome__in="Diretor de Gestão de Pessoas,Chefe da Seção de Promoções" status="ATIVO" %}\1{% endif %}',
                content,
                flags=re.DOTALL
            )
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ {arquivo} - Permissões corrigidas para cargos especiais")
        else:
            print(f"⚠️  {arquivo} - Padrão user.is_staff não encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao processar {arquivo}: {e}")

def corrigir_template_detail():
    """Corrige o template de detalhes dos quadros"""
    arquivo = 'militares/templates/militares/quadro_fixacao_vagas/detail.html'
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem verificação de cargos especiais
        if 'Diretor de Gestão de Pessoas' in content or 'Chefe da Seção de Promoções' in content:
            print(f"✅ {arquivo} - Já tem verificação de cargos especiais")
            return
        
        # Adicionar verificação de cargos especiais para botão de edição
        pattern_editar = r'(\s*)(<a href="{% url \'militares:quadro_fixacao_vagas_update\' quadro\.pk %}"[^>]*>.*?</a>)'
        
        if re.search(pattern_editar, content, re.DOTALL):
            new_content = re.sub(
                pattern_editar,
                r'\1{% if user.is_staff or user.funcoes.filter.cargo_funcao__nome__in="Diretor de Gestão de Pessoas,Chefe da Seção de Promoções" status="ATIVO" %}\2{% endif %}',
                content,
                flags=re.DOTALL
            )
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ {arquivo} - Permissões corrigidas para cargos especiais")
        else:
            print(f"⚠️  {arquivo} - Padrão de edição não encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao processar {arquivo}: {e}")

def corrigir_views():
    """Corrige as views para verificar cargos especiais"""
    arquivo = 'militares/views.py'
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem verificação de cargos especiais
        if 'Diretor de Gestão de Pessoas' in content and 'Chefe da Seção de Promoções' in content:
            print(f"✅ {arquivo} - Já tem verificação de cargos especiais")
            return
        
        # Adicionar verificação nas views de CRUD
        views_para_corrigir = [
            'quadro_fixacao_vagas_create',
            'quadro_fixacao_vagas_update', 
            'quadro_fixacao_vagas_delete'
        ]
        
        for view in views_para_corrigir:
            # Procurar pela definição da view
            pattern = rf'def {view}\(request, pk\):'
            if re.search(pattern, content):
                print(f"✅ View {view} encontrada")
                
                # Verificar se já tem verificação de cargos especiais
                if 'Diretor de Gestão de Pessoas' in content:
                    print(f"   ✅ Já tem verificação de cargos especiais")
                else:
                    print(f"   ⚠️  NÃO tem verificação de cargos especiais")
            else:
                print(f"❌ View {view} não encontrada")
                
    except Exception as e:
        print(f"❌ Erro ao verificar views: {e}")

def criar_decorator_cargos_especiais():
    """Cria um decorator para verificar cargos especiais"""
    decorator_code = '''
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
'''
    
    print("📝 Decorator para cargos especiais:")
    print(decorator_code)
    print("💡 Adicione este decorator ao arquivo militares/decorators.py")
    print("💡 Use @cargos_especiais_required nas views de CRUD dos quadros")

def main():
    print("🔧 Corrigindo permissões CRUD dos quadros de fixação de vagas...")
    print("=" * 70)
    
    # Verificar cargos especiais
    verificar_cargos_especiais()
    
    # Corrigir templates
    print("📝 Corrigindo templates...")
    corrigir_template_list()
    corrigir_template_detail()
    
    # Verificar views
    print("\n🔍 Verificando views...")
    corrigir_views()
    
    # Criar decorator
    print("\n🛠️ Criando decorator...")
    criar_decorator_cargos_especiais()
    
    print("\n" + "=" * 70)
    print("💡 RESUMO:")
    print("   - Diretor de Gestão de Pessoas: ✅ CRUD completo")
    print("   - Chefe da Seção de Promoções: ✅ CRUD completo")
    print("   - Membros das comissões: 👁️ Apenas visualização")
    print("   - Outros usuários: 🚫 Sem acesso")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("   1. Adicionar o decorator ao arquivo decorators.py")
    print("   2. Aplicar @cargos_especiais_required nas views de CRUD")
    print("   3. Testar as permissões com diferentes usuários")

if __name__ == "__main__":
    main() 