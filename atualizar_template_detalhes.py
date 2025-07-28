#!/usr/bin/env python
"""
Script para atualizar o template de detalhes com os novos módulos
"""

def atualizar_template_detalhes():
    """Atualiza o template de detalhes com os novos módulos"""
    
    print("🔧 ATUALIZANDO TEMPLATE DE DETALHES")
    print("=" * 60)
    
    # Ler o arquivo template
    with open('militares/templates/militares/cargos/cargo_funcao_detail.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Novos módulos para adicionar
    novos_modulos = [
        ('ALMANAQUES', 'fas fa-book'),
        ('CALENDARIOS', 'fas fa-calendar-alt'),
        ('NOTIFICACOES', 'fas fa-bell'),
        ('MODELOS_ATA', 'fas fa-file-contract'),
        ('CARGOS_COMISSAO', 'fas fa-user-tie'),
        ('QUADROS_FIXACAO', 'fas fa-thumbtack'),
        ('ASSINATURAS', 'fas fa-signature'),
        ('ESTATISTICAS', 'fas fa-chart-line'),
        ('EXPORTACAO', 'fas fa-download'),
        ('IMPORTACAO', 'fas fa-upload'),
        ('BACKUP', 'fas fa-database'),
        ('AUDITORIA', 'fas fa-clipboard-list'),
        ('DASHBOARD', 'fas fa-tachometer-alt'),
        ('BUSCA', 'fas fa-search'),
        ('AJAX', 'fas fa-sync-alt'),
        ('API', 'fas fa-code'),
        ('SESSAO', 'fas fa-clock'),
        ('FUNCAO', 'fas fa-user-tag'),
        ('PERFIL', 'fas fa-id-card'),
        ('SISTEMA', 'fas fa-server')
    ]
    
    # Encontrar onde adicionar os novos módulos (após CONFIGURACOES)
    config_end = content.find("{% elif modulo == 'CONFIGURACOES' %}")
    if config_end != -1:
        # Encontrar o final do bloco CONFIGURACOES
        config_end = content.find("{% else %}", config_end)
        
        if config_end != -1:
            # Criar HTML para os novos módulos
            novos_modulos_html = '\n'
            for modulo, icon in novos_modulos:
                novos_modulos_html += f"                                            {{% elif modulo == '{modulo}' %}}\n"
                novos_modulos_html += f"                                                <i class=\"{icon} modulo-icon\"></i>\n"
            
            # Inserir os novos módulos
            content = content[:config_end] + novos_modulos_html + content[config_end:]
            
            print("✅ Novos módulos adicionados ao template de detalhes")
        else:
            print("❌ Local para inserção não encontrado")
            return
    else:
        print("❌ Bloco CONFIGURACOES não encontrado")
        return
    
    # Salvar o arquivo atualizado
    with open('militares/templates/militares/cargos/cargo_funcao_detail.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Template de detalhes atualizado com sucesso!")
    print("=" * 60)
    print("📋 Módulos adicionados:")
    for modulo, icon in novos_modulos:
        print(f"   - {modulo} ({icon})")
    
    print(f"\n🎯 Total de novos módulos: {len(novos_modulos)}")
    print("🎮 Agora acesse /militares/cargos/1/ para ver todos os módulos!")

if __name__ == "__main__":
    atualizar_template_detalhes() 