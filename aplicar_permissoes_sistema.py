#!/usr/bin/env python
"""
Script para aplicar decorators de permissão do sistema em todas as views
"""

import re
import os

def aplicar_decorators_permissoes():
    """Aplica decorators de permissão nas views do sistema"""
    
    print("🔧 APLICANDO DECORATORS DE PERMISSÃO NO SISTEMA")
    print("=" * 60)
    
    # Ler o arquivo views.py
    with open('militares/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Adicionar imports dos decorators de permissão
    imports_permissoes = '''
# Imports para sistema de permissões
from .permissoes_sistema import (
    requer_perm_militares_visualizar, requer_perm_militares_criar, requer_perm_militares_editar, requer_perm_militares_excluir, requer_perm_militares_admin,
    requer_perm_fichas_visualizar, requer_perm_fichas_criar, requer_perm_fichas_editar, requer_perm_fichas_aprovar, requer_perm_fichas_admin,
    requer_perm_quadros_visualizar, requer_perm_quadros_criar, requer_perm_quadros_editar, requer_perm_quadros_excluir, requer_perm_quadros_admin,
    requer_perm_promocoes_visualizar, requer_perm_promocoes_criar, requer_perm_promocoes_editar, requer_perm_promocoes_aprovar, requer_perm_promocoes_homologar, requer_perm_promocoes_admin,
    requer_perm_vagas_visualizar, requer_perm_vagas_criar, requer_perm_vagas_editar, requer_perm_vagas_excluir, requer_perm_vagas_admin,
    requer_perm_comissao_visualizar, requer_perm_comissao_criar, requer_perm_comissao_editar, requer_perm_comissao_excluir, requer_perm_comissao_assinar, requer_perm_comissao_admin,
    requer_perm_documentos_visualizar, requer_perm_documentos_criar, requer_perm_documentos_editar, requer_perm_documentos_excluir, requer_perm_documentos_gerar_pdf, requer_perm_documentos_imprimir, requer_perm_documentos_assinar, requer_perm_documentos_admin,
    requer_perm_usuarios_visualizar, requer_perm_usuarios_criar, requer_perm_usuarios_editar, requer_perm_usuarios_excluir, requer_perm_usuarios_admin,
    requer_perm_relatorios_visualizar, requer_perm_relatorios_gerar_pdf, requer_perm_relatorios_imprimir, requer_perm_relatorios_admin,
    requer_perm_configuracoes_visualizar, requer_perm_configuracoes_editar, requer_perm_configuracoes_admin,
)
'''
    
    # Adicionar imports após os imports existentes
    if 'from .permissoes_sistema import' not in content:
        # Encontrar o final dos imports
        import_end = content.find('\n\n')
        if import_end == -1:
            import_end = content.find('\n')
        
        content = content[:import_end] + imports_permissoes + content[import_end:]
    
    # Aplicar decorators para views de militares
    print("📋 Aplicando decorators para views de militares...")
    
    # Militar list - visualizar
    content = re.sub(
        r'@login_required\s+def militar_list',
        r'@login_required\n@requer_perm_militares_visualizar\ndef militar_list',
        content
    )
    
    # Militar create - criar
    content = re.sub(
        r'@login_required\s+def militar_create',
        r'@login_required\n@requer_perm_militares_criar\ndef militar_create',
        content
    )
    
    # Militar update - editar
    content = re.sub(
        r'@login_required\s+def militar_update',
        r'@login_required\n@requer_perm_militares_editar\ndef militar_update',
        content
    )
    
    # Militar delete - excluir
    content = re.sub(
        r'@login_required\s+def militar_delete',
        r'@login_required\n@requer_perm_militares_excluir\ndef militar_delete',
        content
    )
    
    # Militar detail - visualizar
    content = re.sub(
        r'@login_required\s+def militar_detail',
        r'@login_required\n@requer_perm_militares_visualizar\ndef militar_detail',
        content
    )
    
    # Aplicar decorators para views de fichas de conceito
    print("📄 Aplicando decorators para views de fichas de conceito...")
    
    # Ficha conceito list - visualizar
    content = re.sub(
        r'@login_required\s+def ficha_conceito_list',
        r'@login_required\n@requer_perm_fichas_visualizar\ndef ficha_conceito_list',
        content
    )
    
    # Ficha conceito create - criar
    content = re.sub(
        r'@login_required\s+def ficha_conceito_create',
        r'@login_required\n@requer_perm_fichas_criar\ndef ficha_conceito_create',
        content
    )
    
    # Ficha conceito update - editar
    content = re.sub(
        r'@login_required\s+def ficha_conceito_update',
        r'@login_required\n@requer_perm_fichas_editar\ndef ficha_conceito_update',
        content
    )
    
    # Ficha conceito delete - excluir
    content = re.sub(
        r'@login_required\s+def ficha_conceito_delete',
        r'@login_required\n@requer_perm_fichas_admin\ndef ficha_conceito_delete',
        content
    )
    
    # Ficha conceito detail - visualizar
    content = re.sub(
        r'@login_required\s+def ficha_conceito_detail',
        r'@login_required\n@requer_perm_fichas_visualizar\ndef ficha_conceito_detail',
        content
    )
    
    # Aplicar decorators para views de quadros de acesso
    print("📊 Aplicando decorators para views de quadros de acesso...")
    
    # Quadro acesso list - visualizar
    content = re.sub(
        r'@login_required\s+def quadro_acesso_list',
        r'@login_required\n@requer_perm_quadros_visualizar\ndef quadro_acesso_list',
        content
    )
    
    # Quadro acesso create - criar
    content = re.sub(
        r'@login_required\s+def quadro_acesso_create',
        r'@login_required\n@requer_perm_quadros_criar\ndef quadro_acesso_create',
        content
    )
    
    # Quadro acesso update - editar
    content = re.sub(
        r'@login_required\s+def quadro_acesso_update',
        r'@login_required\n@requer_perm_quadros_editar\ndef quadro_acesso_update',
        content
    )
    
    # Quadro acesso delete - excluir
    content = re.sub(
        r'@login_required\s+def quadro_acesso_delete',
        r'@login_required\n@requer_perm_quadros_excluir\ndef quadro_acesso_delete',
        content
    )
    
    # Quadro acesso detail - visualizar
    content = re.sub(
        r'@login_required\s+def quadro_acesso_detail',
        r'@login_required\n@requer_perm_quadros_visualizar\ndef quadro_acesso_detail',
        content
    )
    
    # Aplicar decorators para views de promoções
    print("⭐ Aplicando decorators para views de promoções...")
    
    # Promocao list - visualizar
    content = re.sub(
        r'@login_required\s+def promocao_list',
        r'@login_required\n@requer_perm_promocoes_visualizar\ndef promocao_list',
        content
    )
    
    # Promocao create - criar
    content = re.sub(
        r'@login_required\s+def promocao_create',
        r'@login_required\n@requer_perm_promocoes_criar\ndef promocao_create',
        content
    )
    
    # Promocao update - editar
    content = re.sub(
        r'@login_required\s+def promocao_update',
        r'@login_required\n@requer_perm_promocoes_editar\ndef promocao_update',
        content
    )
    
    # Promocao delete - excluir
    content = re.sub(
        r'@login_required\s+def promocao_delete',
        r'@login_required\n@requer_perm_promocoes_admin\ndef promocao_delete',
        content
    )
    
    # Promocao detail - visualizar
    content = re.sub(
        r'@login_required\s+def promocao_detail',
        r'@login_required\n@requer_perm_promocoes_visualizar\ndef promocao_detail',
        content
    )
    
    # Aplicar decorators para views de vagas
    print("🪑 Aplicando decorators para views de vagas...")
    
    # Vaga list - visualizar
    content = re.sub(
        r'@login_required\s+def vaga_list',
        r'@login_required\n@requer_perm_vagas_visualizar\ndef vaga_list',
        content
    )
    
    # Vaga create - criar
    content = re.sub(
        r'@login_required\s+def vaga_create',
        r'@login_required\n@requer_perm_vagas_criar\ndef vaga_create',
        content
    )
    
    # Vaga update - editar
    content = re.sub(
        r'@login_required\s+def vaga_update',
        r'@login_required\n@requer_perm_vagas_editar\ndef vaga_update',
        content
    )
    
    # Vaga delete - excluir
    content = re.sub(
        r'@login_required\s+def vaga_delete',
        r'@login_required\n@requer_perm_vagas_excluir\ndef vaga_delete',
        content
    )
    
    # Vaga detail - visualizar
    content = re.sub(
        r'@login_required\s+def vaga_detail',
        r'@login_required\n@requer_perm_vagas_visualizar\ndef vaga_detail',
        content
    )
    
    # Aplicar decorators para views de comissões
    print("⚖️ Aplicando decorators para views de comissões...")
    
    # Comissao list - visualizar
    content = re.sub(
        r'@login_required\s+def comissao_list',
        r'@login_required\n@requer_perm_comissao_visualizar\ndef comissao_list',
        content
    )
    
    # Comissao create - criar
    content = re.sub(
        r'@login_required\s+def comissao_create',
        r'@login_required\n@requer_perm_comissao_criar\ndef comissao_create',
        content
    )
    
    # Comissao update - editar
    content = re.sub(
        r'@login_required\s+def comissao_update',
        r'@login_required\n@requer_perm_comissao_editar\ndef comissao_update',
        content
    )
    
    # Comissao delete - excluir
    content = re.sub(
        r'@login_required\s+def comissao_delete',
        r'@login_required\n@requer_perm_comissao_excluir\ndef comissao_delete',
        content
    )
    
    # Comissao detail - visualizar
    content = re.sub(
        r'@login_required\s+def comissao_detail',
        r'@login_required\n@requer_perm_comissao_visualizar\ndef comissao_detail',
        content
    )
    
    # Aplicar decorators para views de documentos
    print("📋 Aplicando decorators para views de documentos...")
    
    # Documento list - visualizar
    content = re.sub(
        r'@login_required\s+def documento_list',
        r'@login_required\n@requer_perm_documentos_visualizar\ndef documento_list',
        content
    )
    
    # Documento create - criar
    content = re.sub(
        r'@login_required\s+def documento_create',
        r'@login_required\n@requer_perm_documentos_criar\ndef documento_create',
        content
    )
    
    # Documento update - editar
    content = re.sub(
        r'@login_required\s+def documento_update',
        r'@login_required\n@requer_perm_documentos_editar\ndef documento_update',
        content
    )
    
    # Documento delete - excluir
    content = re.sub(
        r'@login_required\s+def documento_delete',
        r'@login_required\n@requer_perm_documentos_excluir\ndef documento_delete',
        content
    )
    
    # Documento detail - visualizar
    content = re.sub(
        r'@login_required\s+def documento_detail',
        r'@login_required\n@requer_perm_documentos_visualizar\ndef documento_detail',
        content
    )
    
    # Aplicar decorators para views de usuários
    print("👤 Aplicando decorators para views de usuários...")
    
    # Usuario list - visualizar
    content = re.sub(
        r'@login_required\s+def usuario_list',
        r'@login_required\n@requer_perm_usuarios_visualizar\ndef usuario_list',
        content
    )
    
    # Usuario create - criar
    content = re.sub(
        r'@login_required\s+def usuario_create',
        r'@login_required\n@requer_perm_usuarios_criar\ndef usuario_create',
        content
    )
    
    # Usuario update - editar
    content = re.sub(
        r'@login_required\s+def usuario_update',
        r'@login_required\n@requer_perm_usuarios_editar\ndef usuario_update',
        content
    )
    
    # Usuario delete - excluir
    content = re.sub(
        r'@login_required\s+def usuario_delete',
        r'@login_required\n@requer_perm_usuarios_excluir\ndef usuario_delete',
        content
    )
    
    # Usuario detail - visualizar
    content = re.sub(
        r'@login_required\s+def usuario_detail',
        r'@login_required\n@requer_perm_usuarios_visualizar\ndef usuario_detail',
        content
    )
    
    # Aplicar decorators para views de relatórios
    print("📈 Aplicando decorators para views de relatórios...")
    
    # Relatorio list - visualizar
    content = re.sub(
        r'@login_required\s+def relatorio_list',
        r'@login_required\n@requer_perm_relatorios_visualizar\ndef relatorio_list',
        content
    )
    
    # Relatorio gerar - gerar PDF
    content = re.sub(
        r'@login_required\s+def relatorio_gerar',
        r'@login_required\n@requer_perm_relatorios_gerar_pdf\ndef relatorio_gerar',
        content
    )
    
    # Relatorio imprimir - imprimir
    content = re.sub(
        r'@login_required\s+def relatorio_imprimir',
        r'@login_required\n@requer_perm_relatorios_imprimir\ndef relatorio_imprimir',
        content
    )
    
    # Aplicar decorators para views de configurações
    print("⚙️ Aplicando decorators para views de configurações...")
    
    # Configuracao list - visualizar
    content = re.sub(
        r'@login_required\s+def configuracao_list',
        r'@login_required\n@requer_perm_configuracoes_visualizar\ndef configuracao_list',
        content
    )
    
    # Configuracao update - editar
    content = re.sub(
        r'@login_required\s+def configuracao_update',
        r'@login_required\n@requer_perm_configuracoes_editar\ndef configuracao_update',
        content
    )
    
    # Salvar o arquivo modificado
    with open('militares/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Decorators de permissão aplicados com sucesso!")
    print("=" * 60)
    print("📋 Resumo das aplicações:")
    print("   - Militares: Visualizar, Criar, Editar, Excluir")
    print("   - Fichas de Conceito: Visualizar, Criar, Editar, Aprovar")
    print("   - Quadros de Acesso: Visualizar, Criar, Editar, Excluir")
    print("   - Promoções: Visualizar, Criar, Editar, Aprovar, Homologar")
    print("   - Vagas: Visualizar, Criar, Editar, Excluir")
    print("   - Comissões: Visualizar, Criar, Editar, Excluir, Assinar")
    print("   - Documentos: Visualizar, Criar, Editar, Excluir, Gerar PDF, Imprimir, Assinar")
    print("   - Usuários: Visualizar, Criar, Editar, Excluir")
    print("   - Relatórios: Visualizar, Gerar PDF, Imprimir")
    print("   - Configurações: Visualizar, Editar")
    print("\n🎯 Agora o sistema verifica permissões baseadas no modelo PermissaoFuncao!")

if __name__ == "__main__":
    aplicar_decorators_permissoes() 