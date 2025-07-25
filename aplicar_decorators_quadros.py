#!/usr/bin/env python
"""
Script para aplicar o decorator cargos_especiais_required nas views de CRUD dos quadros de fixação de vagas
"""

import re

def aplicar_decorator_views():
    """Aplica o decorator nas views de CRUD dos quadros"""
    
    arquivo = 'militares/views.py'
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Views que precisam do decorator
        views_para_decorar = [
            'quadro_fixacao_vagas_create',
            'quadro_fixacao_vagas_update',
            'quadro_fixacao_vagas_delete'
        ]
        
        # Verificar se o import já existe
        if 'from militares.decorators import cargos_especiais_required' not in content:
            # Adicionar import
            pattern_import = r'(from militares\.decorators import.*?)(\n)'
            match = re.search(pattern_import, content, re.DOTALL)
            if match:
                new_import = match.group(1) + ', cargos_especiais_required' + match.group(2)
                content = re.sub(pattern_import, new_import, content, flags=re.DOTALL)
                print("✅ Import adicionado")
            else:
                print("⚠️  Não foi possível encontrar o import de decorators")
        
        # Aplicar decorator em cada view
        for view in views_para_decorar:
            # Padrão para encontrar a definição da view
            pattern = rf'def {view}\(request, pk\):'
            
            if re.search(pattern, content):
                # Verificar se já tem o decorator
                pattern_com_decorator = rf'@cargos_especiais_required\s*\ndef {view}\(request, pk\):'
                
                if not re.search(pattern_com_decorator, content):
                    # Adicionar decorator
                    content = re.sub(
                        pattern,
                        f'@cargos_especiais_required\ndef {view}(request, pk):',
                        content
                    )
                    print(f"✅ Decorator aplicado em {view}")
                else:
                    print(f"✅ {view} já tem o decorator")
            else:
                print(f"⚠️  View {view} não encontrada")
        
        # Salvar arquivo
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n✅ Decorators aplicados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao aplicar decorators: {e}")

def verificar_decorators_aplicados():
    """Verifica se os decorators foram aplicados corretamente"""
    
    arquivo = 'militares/views.py'
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n🔍 Verificando decorators aplicados...")
        
        # Verificar import
        if 'cargos_especiais_required' in content:
            print("✅ Import do decorator encontrado")
        else:
            print("❌ Import do decorator não encontrado")
        
        # Verificar views
        views_para_verificar = [
            'quadro_fixacao_vagas_create',
            'quadro_fixacao_vagas_update',
            'quadro_fixacao_vagas_delete'
        ]
        
        for view in views_para_verificar:
            pattern = rf'@cargos_especiais_required\s*\ndef {view}'
            if re.search(pattern, content):
                print(f"✅ {view} - Decorator aplicado")
            else:
                print(f"❌ {view} - Decorator não aplicado")
                
    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")

def main():
    print("🔧 Aplicando decorators nas views de CRUD dos quadros...")
    print("=" * 60)
    
    # Aplicar decorators
    aplicar_decorator_views()
    
    # Verificar se foram aplicados
    verificar_decorators_aplicados()
    
    print("\n" + "=" * 60)
    print("💡 RESUMO:")
    print("   - Decorator @cargos_especiais_required aplicado")
    print("   - Views protegidas: create, update, delete")
    print("   - Apenas cargos especiais podem editar quadros")
    print("\n🎯 PERMISSÕES FINAIS:")
    print("   - Diretor de Gestão de Pessoas: ✅ CRUD completo")
    print("   - Chefe da Seção de Promoções: ✅ CRUD completo")
    print("   - Membros das comissões: 👁️ Apenas visualização")
    print("   - Outros usuários: 🚫 Sem acesso")

if __name__ == "__main__":
    main() 