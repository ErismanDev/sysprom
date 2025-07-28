#!/usr/bin/env python
"""
Script para testar se o formulário está salvando permissões corretamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, PermissaoFuncao
from militares.forms import CargoFuncaoForm

def testar_formulario_permissoes():
    """Testa se o formulário está salvando permissões corretamente"""
    
    print("🧪 TESTANDO FORMULÁRIO DE PERMISSÕES")
    print("=" * 60)
    
    # Buscar um cargo para testar
    cargo = CargoFuncao.objects.filter(nome__icontains='teste').first()
    if not cargo:
        print("❌ Cargo de teste não encontrado")
        return
    
    print(f"✅ Cargo encontrado: {cargo.nome} (ID: {cargo.id})")
    
    # Contar permissões antes
    permissoes_antes = PermissaoFuncao.objects.filter(cargo_funcao=cargo).count()
    print(f"📊 Permissões antes: {permissoes_antes}")
    
    # Criar dados de teste com todas as permissões marcadas
    dados_teste = {
        'nome': cargo.nome,
        'descricao': cargo.descricao,
        'ativo': cargo.ativo,
        'ordem': cargo.ordem,
        # Marcar todas as permissões
        'permissoes_militares': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'ADMINISTRAR'],
        'permissoes_fichas_conceito': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'ADMINISTRAR'],
        'permissoes_quadros_acesso': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'ADMINISTRAR'],
        'permissoes_promocoes': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'APROVAR', 'HOMOLOGAR', 'ADMINISTRAR'],
        'permissoes_vagas': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'ADMINISTRAR'],
        'permissoes_comissao': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_documentos': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_usuarios': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'ADMINISTRAR'],
        'permissoes_relatorios': ['VISUALIZAR', 'GERAR_PDF', 'IMPRIMIR', 'ADMINISTRAR'],
        'permissoes_configuracoes': ['VISUALIZAR', 'EDITAR', 'ADMINISTRAR'],
        # Novos módulos
        'permissoes_almanaques': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_calendarios': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_notificacoes': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_modelos_ata': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_cargos_comissao': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_quadros_fixacao': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_assinaturas': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_estatisticas': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_exportacao': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_importacao': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_backup': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_auditoria': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_dashboard': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_busca': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_ajax': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_api': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_sessao': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_funcao': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_perfil': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
        'permissoes_sistema': ['VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'],
    }
    
    # Criar formulário
    form = CargoFuncaoForm(dados_teste, instance=cargo)
    
    print("🔍 Validando formulário...")
    if form.is_valid():
        print("✅ Formulário válido!")
        
        # Salvar
        print("💾 Salvando...")
        cargo_salvo = form.save()
        print("✅ Cargo salvo!")
        
        # Verificar permissões após salvar
        permissoes_depois = PermissaoFuncao.objects.filter(cargo_funcao=cargo).count()
        print(f"📊 Permissões depois: {permissoes_depois}")
        
        # Verificar módulos com permissões
        permissoes_por_modulo = {}
        for permissao in PermissaoFuncao.objects.filter(cargo_funcao=cargo, ativo=True):
            if permissao.modulo not in permissoes_por_modulo:
                permissoes_por_modulo[permissao.modulo] = []
            permissoes_por_modulo[permissao.modulo].append(permissao.acesso)
        
        print(f"\n📋 Módulos com permissões: {len(permissoes_por_modulo)}")
        for modulo in sorted(permissoes_por_modulo.keys()):
            print(f"   - {modulo}: {len(permissoes_por_modulo[modulo])} permissões")
        
        # Verificar se os novos módulos foram salvos
        novos_modulos = [
            'ALMANAQUES', 'CALENDARIOS', 'NOTIFICACOES', 'MODELOS_ATA',
            'CARGOS_COMISSAO', 'QUADROS_FIXACAO', 'ASSINATURAS', 'ESTATISTICAS',
            'EXPORTACAO', 'IMPORTACAO', 'BACKUP', 'AUDITORIA', 'DASHBOARD',
            'BUSCA', 'AJAX', 'API', 'SESSAO', 'FUNCAO', 'PERFIL', 'SISTEMA'
        ]
        
        print("\n🔍 Verificando novos módulos:")
        for modulo in novos_modulos:
            if modulo in permissoes_por_modulo:
                print(f"   ✅ {modulo}: {len(permissoes_por_modulo[modulo])} permissões")
            else:
                print(f"   ❌ {modulo}: Nenhuma permissão")
        
        print(f"\n🎯 Agora teste acessando:")
        print(f"   http://127.0.0.1:8000/militares/cargos/{cargo.id}/")
        
    else:
        print("❌ Formulário inválido!")
        print("Erros:", form.errors)

if __name__ == "__main__":
    testar_formulario_permissoes() 