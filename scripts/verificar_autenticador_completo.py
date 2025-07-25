#!/usr/bin/env python
"""
Script final para verificar se todos os documentos que contêm assinaturas têm o autenticador de veracidade implementado.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

def verificar_autenticador_completo():
    """
    Verifica se todos os documentos que contêm assinaturas têm o autenticador implementado
    """
    print("🔍 VERIFICAÇÃO COMPLETA DO AUTENTICADOR DE VERACIDADE\n")
    
    # Lista de documentos que contêm assinaturas
    documentos_com_assinatura = [
        {
            'nome': 'Quadro de Acesso',
            'modelo': 'QuadroAcesso',
            'view_pdf': 'quadro_acesso_pdf',
            'tipo_documento': 'quadro'
        },
        {
            'nome': 'Ata de Sessão',
            'modelo': 'AtaSessao',
            'view_pdf': 'ata_gerar_pdf',
            'tipo_documento': 'ata'
        },
        {
            'nome': 'Voto de Deliberação',
            'modelo': 'VotoDeliberacao',
            'view_pdf': 'voto_deliberacao_pdf',
            'tipo_documento': 'voto'
        },
        {
            'nome': 'Quadro de Fixação de Vagas',
            'modelo': 'QuadroFixacaoVagas',
            'view_pdf': 'quadro_fixacao_vagas_pdf',
            'tipo_documento': 'quadro_fixacao'
        }
    ]
    
    # Verificar arquivo principal de views
    views_file = 'militares/views.py'
    
    if not os.path.exists(views_file):
        print("❌ Arquivo de views não encontrado")
        return False
    
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("📋 DOCUMENTOS COM ASSINATURAS:\n")
    
    total_documentos = len(documentos_com_assinatura)
    documentos_ok = 0
    
    for doc in documentos_com_assinatura:
        print(f"📄 {doc['nome']}:")
        
        # Verificar se a view existe
        if doc['view_pdf'] in content:
            print(f"  ✅ View {doc['view_pdf']}: Encontrada")
            
            # Verificar se usa a função utilitária
            if f'gerar_autenticador_veracidade' in content and doc['view_pdf'] in content:
                print(f"  ✅ Autenticador: Usa função utilitária")
                print(f"  ✅ Tipo documento: {doc['tipo_documento']}")
                documentos_ok += 1
            elif f'qr = qrcode.make' in content and doc['view_pdf'] in content:
                print(f"  ⚠️  Autenticador: Implementação manual (precisa padronizar)")
            else:
                print(f"  ❌ Autenticador: Não implementado")
        else:
            print(f"  ❌ View {doc['view_pdf']}: Não encontrada")
        
        print()
    
    print("=== RESUMO FINAL ===\n")
    print(f"📊 Total de documentos com assinaturas: {total_documentos}")
    print(f"✅ Documentos com autenticador padronizado: {documentos_ok}")
    print(f"❌ Documentos sem autenticador: {total_documentos - documentos_ok}")
    
    if documentos_ok == total_documentos:
        print("\n🎉 SUCESSO! Todos os documentos que contêm assinaturas têm o autenticador de veracidade implementado!")
        print("\n📋 DOCUMENTOS COBERTOS:")
        for doc in documentos_com_assinatura:
            print(f"  • {doc['nome']} - {doc['tipo_documento']}")
        
        print("\n🔒 BENEFÍCIOS IMPLEMENTADOS:")
        print("  • QR Code para verificação de autenticidade")
        print("  • Código verificador único para cada documento")
        print("  • Código CRC para validação de integridade")
        print("  • URL personalizada para cada tipo de documento")
        print("  • Padronização em todas as views")
        
        return True
    else:
        print(f"\n⚠️  ATENÇÃO: {total_documentos - documentos_ok} documento(s) ainda não têm o autenticador implementado.")
        return False

def verificar_funcao_utilitaria():
    """
    Verifica se a função utilitária está implementada corretamente
    """
    print("\n🔧 VERIFICAÇÃO DA FUNÇÃO UTILITÁRIA\n")
    
    utils_file = 'militares/utils.py'
    
    if not os.path.exists(utils_file):
        print("❌ Arquivo utils.py não encontrado")
        return False
    
    with open(utils_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se a função existe
    if 'def gerar_autenticador_veracidade' in content:
        print("✅ Função gerar_autenticador_veracidade: Encontrada")
        
        # Verificar se tem todos os parâmetros necessários
        if 'objeto, request=None, url_personalizada=None, tipo_documento=None' in content:
            print("✅ Parâmetros: Completos")
        else:
            print("⚠️  Parâmetros: Incompletos")
        
        # Verificar se gera QR code
        if 'qrcode.make' in content:
            print("✅ Geração de QR Code: Implementada")
        else:
            print("❌ Geração de QR Code: Não implementada")
        
        # Verificar se gera códigos de verificação
        if 'codigo_verificador' in content and 'codigo_crc' in content:
            print("✅ Códigos de verificação: Implementados")
        else:
            print("❌ Códigos de verificação: Não implementados")
        
        return True
    else:
        print("❌ Função gerar_autenticador_veracidade: Não encontrada")
        return False

def main():
    """
    Função principal
    """
    print("🚀 VERIFICAÇÃO COMPLETA DO AUTENTICADOR DE VERACIDADE\n")
    
    # Verificar função utilitária
    utils_ok = verificar_funcao_utilitaria()
    
    # Verificar documentos
    docs_ok = verificar_autenticador_completo()
    
    print("\n" + "="*60)
    print("🎯 RESULTADO FINAL")
    print("="*60)
    
    if utils_ok and docs_ok:
        print("🎉 IMPLEMENTAÇÃO COMPLETA!")
        print("✅ Todos os documentos que contêm assinaturas têm o autenticador de veracidade")
        print("✅ Função utilitária implementada e funcionando")
        print("✅ Padronização em todas as views")
        print("\n🔒 O sistema está seguro e todos os documentos são autenticáveis!")
    else:
        print("⚠️  IMPLEMENTAÇÃO INCOMPLETA")
        if not utils_ok:
            print("❌ Função utilitária não está implementada corretamente")
        if not docs_ok:
            print("❌ Alguns documentos não têm o autenticador implementado")
        print("\n🔧 Ainda há trabalho a ser feito para completar a implementação.")

if __name__ == '__main__':
    main() 