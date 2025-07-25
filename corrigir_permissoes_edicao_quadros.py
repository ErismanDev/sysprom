#!/usr/bin/env python
"""
Script para corrigir permissões de edição dos quadros de fixação de vagas.
Membros das comissões devem apenas visualizar, não editar.
"""

import re

def corrigir_permissoes_quadros():
    """Corrige as permissões nos templates dos quadros de fixação de vagas"""
    
    arquivos_para_corrigir = [
        'militares/templates/militares/quadro_fixacao_vagas/list.html',
        'militares/templates/militares/quadro_fixacao_vagas/detail.html'
    ]
    
    for arquivo in arquivos_para_corrigir:
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se já tem verificação de permissão
            if 'user.is_staff' in content:
                print(f"✅ {arquivo} - Já tem verificação de permissão (user.is_staff)")
                continue
            
            # Corrigir list.html
            if 'list.html' in arquivo:
                # Padrão para encontrar botões de edição/exclusão
                pattern = r'(\s*)(<a href="{% url \'militares:quadro_fixacao_vagas_update\' quadro\.pk %}"[^>]*>.*?</a>)(\s*)(<a href="{% url \'militares:quadro_fixacao_vagas_delete\' quadro\.pk %}"[^>]*>.*?</a>)'
                
                if re.search(pattern, content, re.DOTALL):
                    # Adicionar verificação de permissão
                    new_content = re.sub(
                        pattern,
                        r'\1{% if user.is_staff %}\2\3\4{% endif %}',
                        content,
                        flags=re.DOTALL
                    )
                    
                    # Também corrigir botão de assinatura
                    pattern_assinatura = r'(\s*)(<a href="{% url \'militares:quadro_fixacao_vagas_visualizar_html\' quadro\.pk %}"[^>]*title="Assinar eletronicamente"[^>]*>.*?</a>)'
                    new_content = re.sub(
                        pattern_assinatura,
                        r'\1{% if user.is_staff %}\2{% endif %}',
                        new_content,
                        flags=re.DOTALL
                    )
                    
                    # Corrigir botão "Criar Primeiro Quadro"
                    pattern_criar = r'(\s*)(<a href="{% url \'militares:quadro_fixacao_vagas_create\' %}"[^>]*>.*?</a>)'
                    new_content = re.sub(
                        pattern_criar,
                        r'\1{% if user.is_staff %}\2{% endif %}',
                        new_content,
                        flags=re.DOTALL
                    )
                    
                    with open(arquivo, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"✅ {arquivo} - Permissões corrigidas")
                else:
                    print(f"⚠️  {arquivo} - Padrão não encontrado")
            
            # Corrigir detail.html
            elif 'detail.html' in arquivo:
                # Padrão para encontrar botões de edição
                pattern = r'(\s*)(<a href="{% url \'militares:quadro_fixacao_vagas_update\' quadro\.pk %}"[^>]*>.*?</a>)'
                
                if re.search(pattern, content, re.DOTALL):
                    # Adicionar verificação de permissão
                    new_content = re.sub(
                        pattern,
                        r'\1{% if user.is_staff %}\2{% endif %}',
                        content,
                        flags=re.DOTALL
                    )
                    
                    with open(arquivo, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"✅ {arquivo} - Permissões corrigidas")
                else:
                    print(f"⚠️  {arquivo} - Padrão não encontrado")
                    
        except Exception as e:
            print(f"❌ Erro ao processar {arquivo}: {e}")

def verificar_permissoes_views():
    """Verifica se as views têm verificação de permissão adequada"""
    
    print("\n🔍 Verificando permissões nas views...")
    
    # Verificar se as views de edição têm verificação de permissão
    views_para_verificar = [
        'quadro_fixacao_vagas_update',
        'quadro_fixacao_vagas_delete',
        'quadro_fixacao_vagas_create'
    ]
    
    try:
        with open('militares/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        for view in views_para_verificar:
            # Procurar pela definição da view
            pattern = rf'def {view}\(request, pk\):'
            if re.search(pattern, content):
                print(f"✅ View {view} encontrada")
                
                # Verificar se tem verificação de permissão
                if 'user.is_staff' in content or 'request.user.is_staff' in content:
                    print(f"   ✅ Já tem verificação de permissão")
                else:
                    print(f"   ⚠️  NÃO tem verificação de permissão")
            else:
                print(f"❌ View {view} não encontrada")
                
    except Exception as e:
        print(f"❌ Erro ao verificar views: {e}")

def main():
    print("🔧 Corrigindo permissões dos quadros de fixação de vagas...")
    print("=" * 60)
    
    # Corrigir templates
    corrigir_permissoes_quadros()
    
    # Verificar views
    verificar_permissoes_views()
    
    print("\n" + "=" * 60)
    print("💡 RESUMO:")
    print("   - Membros das comissões: APENAS visualização")
    print("   - Staff/Admin: Visualização + Edição")
    print("   - Botões de edição/exclusão: Apenas para staff")
    print("   - Botões de visualização: Para todos os membros")

if __name__ == "__main__":
    main() 