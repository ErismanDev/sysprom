#!/usr/bin/env python
"""
Script para atualizar o template de permissões com os novos módulos
"""

import re

def atualizar_template_permissoes():
    """Atualiza o template com os novos módulos de permissões"""
    
    print("🔧 ATUALIZANDO TEMPLATE DE PERMISSÕES")
    print("=" * 60)
    
    # Ler o arquivo template
    with open('militares/templates/militares/cargos/cargo_funcao_form.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Novos módulos para adicionar
    novos_modulos = [
        {
            'nome': 'almanaques',
            'label': 'Almanaques',
            'icon': 'fas fa-book',
            'campo': 'permissoes_almanaques'
        },
        {
            'nome': 'calendarios',
            'label': 'Calendários',
            'icon': 'fas fa-calendar-alt',
            'campo': 'permissoes_calendarios'
        },
        {
            'nome': 'notificacoes',
            'label': 'Notificações',
            'icon': 'fas fa-bell',
            'campo': 'permissoes_notificacoes'
        },
        {
            'nome': 'modelos_ata',
            'label': 'Modelos de Ata',
            'icon': 'fas fa-file-contract',
            'campo': 'permissoes_modelos_ata'
        },
        {
            'nome': 'cargos_comissao',
            'label': 'Cargos da Comissão',
            'icon': 'fas fa-user-tie',
            'campo': 'permissoes_cargos_comissao'
        },
        {
            'nome': 'quadros_fixacao',
            'label': 'Quadros de Fixação',
            'icon': 'fas fa-thumbtack',
            'campo': 'permissoes_quadros_fixacao'
        },
        {
            'nome': 'assinaturas',
            'label': 'Assinaturas',
            'icon': 'fas fa-signature',
            'campo': 'permissoes_assinaturas'
        },
        {
            'nome': 'estatisticas',
            'label': 'Estatísticas',
            'icon': 'fas fa-chart-line',
            'campo': 'permissoes_estatisticas'
        },
        {
            'nome': 'exportacao',
            'label': 'Exportação',
            'icon': 'fas fa-download',
            'campo': 'permissoes_exportacao'
        },
        {
            'nome': 'importacao',
            'label': 'Importação',
            'icon': 'fas fa-upload',
            'campo': 'permissoes_importacao'
        },
        {
            'nome': 'backup',
            'label': 'Backup',
            'icon': 'fas fa-database',
            'campo': 'permissoes_backup'
        },
        {
            'nome': 'auditoria',
            'label': 'Auditoria',
            'icon': 'fas fa-clipboard-list',
            'campo': 'permissoes_auditoria'
        },
        {
            'nome': 'dashboard',
            'label': 'Dashboard',
            'icon': 'fas fa-tachometer-alt',
            'campo': 'permissoes_dashboard'
        },
        {
            'nome': 'busca',
            'label': 'Busca',
            'icon': 'fas fa-search',
            'campo': 'permissoes_busca'
        },
        {
            'nome': 'ajax',
            'label': 'AJAX',
            'icon': 'fas fa-sync-alt',
            'campo': 'permissoes_ajax'
        },
        {
            'nome': 'api',
            'label': 'API',
            'icon': 'fas fa-code',
            'campo': 'permissoes_api'
        },
        {
            'nome': 'sessao',
            'label': 'Sessão',
            'icon': 'fas fa-clock',
            'campo': 'permissoes_sessao'
        },
        {
            'nome': 'funcao',
            'label': 'Função',
            'icon': 'fas fa-user-tag',
            'campo': 'permissoes_funcao'
        },
        {
            'nome': 'perfil',
            'label': 'Perfil',
            'icon': 'fas fa-id-card',
            'campo': 'permissoes_perfil'
        },
        {
            'nome': 'sistema',
            'label': 'Sistema',
            'icon': 'fas fa-server',
            'campo': 'permissoes_sistema'
        }
    ]
    
    # Encontrar onde adicionar os novos módulos (após a coluna 3)
    coluna3_end = content.find('                            </div>\n                        </div>')
    
    if coluna3_end != -1:
        # Criar HTML para os novos módulos
        novos_modulos_html = '\n\n                        <!-- Novos Módulos -->\n                        <div class="row">\n'
        
        # Dividir em 3 colunas
        colunas = [[], [], []]
        for i, modulo in enumerate(novos_modulos):
            colunas[i % 3].append(modulo)
        
        for col_idx, coluna in enumerate(colunas):
            novos_modulos_html += f'                            <!-- Coluna {col_idx + 4} -->\n                            <div class="col-md-4">\n'
            
            for modulo in coluna:
                novos_modulos_html += f'''                                <!-- {modulo['label']} -->
                                <div class="card mb-3 permissao-modulo" data-modulo="{modulo['nome']}">
                                    <div class="card-header bg-light d-flex justify-content-between align-items-center">
                                        <h6 class="mb-0">
                                            <i class="{modulo['icon']}"></i> {{ form.{modulo['campo']}.label }}
                                        </h6>
                                        <div class="btn-group btn-group-sm">
                                            <button type="button" class="btn btn-outline-success btn-sm marcar-todos" data-modulo="{modulo['nome']}">
                                                <i class="fas fa-check-double"></i> Marcar
                                            </button>
                                            <button type="button" class="btn btn-outline-danger btn-sm desmarcar-todos" data-modulo="{modulo['nome']}">
                                                <i class="fas fa-times"></i> Desmarcar
                                            </button>
                                        </div>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            {{% for choice in form.{modulo['campo']} %}}
                                            <div class="col-md-6 mb-2">
                                                <div class="form-check">
                                                    {{ choice.tag }}
                                                    <label class="form-check-label" for="{{ choice.id_for_label }}">
                                                        {{ choice.choice_label }}
                                                    </label>
                                                </div>
                                            </div>
                                            {{% endfor %}}
                                        </div>
                                    </div>
                                </div>

'''
            
            novos_modulos_html += '                            </div>\n'
        
        novos_modulos_html += '                        </div>\n'
        
        # Inserir os novos módulos
        content = content[:coluna3_end] + novos_modulos_html + content[coluna3_end:]
        
        print("✅ Novos módulos adicionados ao template")
    else:
        print("❌ Local para inserção não encontrado")
        return
    
    # Salvar o arquivo atualizado
    with open('militares/templates/militares/cargos/cargo_funcao_form.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Template atualizado com sucesso!")
    print("=" * 60)
    print("📋 Módulos adicionados:")
    for modulo in novos_modulos:
        print(f"   - {modulo['label']} ({modulo['nome']})")
    
    print(f"\n🎯 Total de novos módulos: {len(novos_modulos)}")
    print("🎮 Agora acesse /militares/cargos/ para ver todos os módulos!")

if __name__ == "__main__":
    atualizar_template_permissoes() 