#!/usr/bin/env python
"""
Script para corrigir as permissões nas views de quadros de fixação de vagas
"""
import re

def corrigir_views():
    # Ler o arquivo views.py
    with open('militares/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrão para encontrar a verificação de permissões problemática
    old_pattern = r"""    # Verificar se o usuário é membro de alguma comissão e tem permissão para ver este quadro
    membro_comissao = MembroComissao\.objects\.filter\(
        usuario=request\.user,
        ativo=True,
        comissao__status='ATIVA'
    \)\.first\(\)
    
    if membro_comissao:
        if membro_comissao\.comissao\.tipo == 'CPO' and quadro\.tipo != 'OFICIAIS':
            messages\.error\(request, 'Você não tem permissão para visualizar este quadro\.'\)
            return redirect\('militares:quadro_fixacao_vagas_list'\)
        elif membro_comissao\.comissao\.tipo == 'CPP' and quadro\.tipo != 'PRACAS':
            messages\.error\(request, 'Você não tem permissão para visualizar este quadro\.'\)
            return redirect\('militares:quadro_fixacao_vagas_list'\)"""
    
    # Nova verificação que permite membros de ambas as comissões
    new_pattern = """    # Verificar se o usuário é membro de alguma comissão e tem permissão para ver este quadro
    membros_comissao = MembroComissao.objects.filter(
        usuario=request.user,
        ativo=True,
        comissao__status='ATIVA'
    )
    
    if membros_comissao.exists():
        # Verificar se é membro de ambas as comissões
        tem_cpo = membros_comissao.filter(comissao__tipo='CPO').exists()
        tem_cpp = membros_comissao.filter(comissao__tipo='CPP').exists()
        
        # Se é membro de ambas, pode ver todos os quadros
        if tem_cpo and tem_cpp:
            pass  # Pode ver todos os quadros
        elif tem_cpo and quadro.tipo != 'OFICIAIS':
            messages.error(request, 'Você não tem permissão para visualizar este quadro.')
            return redirect('militares:quadro_fixacao_vagas_list')
        elif tem_cpp and quadro.tipo != 'PRACAS':
            messages.error(request, 'Você não tem permissão para visualizar este quadro.')
            return redirect('militares:quadro_fixacao_vagas_list')"""
    
    # Substituir todas as ocorrências
    new_content = re.sub(old_pattern, new_pattern, content, flags=re.MULTILINE | re.DOTALL)
    
    # Escrever o arquivo corrigido
    with open('militares/views.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Views corrigidas com sucesso!")
    print("Agora membros de ambas as comissões (CPO e CPP) podem acessar todos os quadros.")

if __name__ == "__main__":
    corrigir_views() 