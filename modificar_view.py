#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def modificar_view():
    """Modifica a view modelo_ata_list para suportar JSON"""
    
    with open('militares/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar a linha do return render
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'return render(request, \'militares/modelo_ata/list.html\', context)' in line:
            print(f"Encontrada linha {i+1}: {line}")
            
            # Adicionar código JSON antes do return
            json_code = '''    # Verificar se é uma requisição para JSON
    if request.GET.get('format') == 'json' or request.GET.get('ajax') == '1':
        modelos_data = []
        for modelo in modelos:
            modelos_data.append({
                'id': modelo.pk,
                'nome': modelo.nome,
                'descricao': modelo.descricao,
                'tipo_comissao': modelo.tipo_comissao,
                'tipo_comissao_display': modelo.get_tipo_comissao_display(),
                'tipo_sessao': modelo.tipo_sessao,
                'tipo_sessao_display': modelo.get_tipo_sessao_display(),
                'ativo': modelo.ativo,
                'padrao': modelo.padrao,
                'criado_por': modelo.criado_por.get_full_name() if modelo.criado_por else modelo.criado_por.username,
                'data_criacao': modelo.data_criacao.strftime('%d/%m/%Y %H:%M') if modelo.data_criacao else '',
            })
        
        return JsonResponse({
            'success': True,
            'modelos': modelos_data
        })
    
'''
            
            # Inserir o código JSON antes do return
            lines.insert(i, json_code)
            break
    
    # Salvar o arquivo modificado
    with open('militares/views.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("View modificada com sucesso!")

if __name__ == "__main__":
    modificar_view() 