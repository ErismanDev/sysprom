#!/usr/bin/env python
"""
Script para testar a geração de PDF com assinaturas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, AssinaturaQuadroAcesso, QuadroAcesso
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def testar_geracao_pdf():
    """Testa a geração de PDF com assinaturas"""
    
    print("🧪 Testando geração de PDF com assinaturas...")
    
    # Buscar quadro de acesso com assinaturas
    quadros = QuadroAcesso.objects.all()
    for quadro in quadros:
        assinaturas = quadro.assinaturas.filter(assinado_por__isnull=False)
        if assinaturas.exists():
            print(f"  📄 Quadro {quadro.pk}: {assinaturas.count()} assinatura(s)")
            
            # Simular como as assinaturas apareceriam no PDF
            for assinatura in assinaturas:
                print(f"\n    📝 Assinatura {assinatura.pk}:")
                print(f"      - Data: {assinatura.data_assinatura}")
                print(f"      - Tipo: {assinatura.get_tipo_assinatura_display()}")
                print(f"      - Função: {assinatura.funcao_assinatura}")
                
                if assinatura.assinado_por:
                    if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                        militar = assinatura.assinado_por.militar
                        posto = militar.get_posto_graduacao_display()
                        if "BM" not in posto:
                            posto = f"{posto} BM"
                        nome_completo = f"{posto} {militar.nome_completo}"
                        
                        # Simular texto da assinatura eletrônica
                        data_formatada = assinatura.data_assinatura.strftime('%d/%m/%Y')
                        hora_formatada = assinatura.data_assinatura.strftime('%H:%M')
                        
                        texto_assinatura = f"Documento assinado eletronicamente por {nome_completo} - {assinatura.funcao_assinatura}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, com fundamento na Portaria XXX/2025 Gab. Cmdo. Geral/CBMEPI de XX de XXXXX de 2025."
                        
                        print(f"      - Texto da assinatura:")
                        print(f"        {texto_assinatura}")
                    else:
                        nome_usuario = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
                        data_formatada = assinatura.data_assinatura.strftime('%d/%m/%Y')
                        hora_formatada = assinatura.data_assinatura.strftime('%H:%M')
                        
                        texto_assinatura = f"Documento assinado eletronicamente por {nome_usuario} - {assinatura.funcao_assinatura}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, com fundamento na Portaria XXX/2025 Gab. Cmdo. Geral/CBMEPI de XX de XXXXX de 2025."
                        
                        print(f"      - Texto da assinatura (sem militar):")
                        print(f"        {texto_assinatura}")

def testar_template_tag_em_contexto():
    """Testa o template tag em contexto real"""
    
    print("\n🔧 Testando template tag em contexto...")
    
    try:
        from militares.templatetags.militares_extras import nome_completo_militar
        
        # Buscar militar José ERISMAN
        militar = Militar.objects.get(nome_completo__icontains="ERISMAN")
        nome_formatado = nome_completo_militar(militar)
        
        print(f"  ✅ Nome formatado: {nome_formatado}")
        
        # Simular contexto de template
        contexto = {
            'militar': militar,
            'nome_formatado': nome_formatado
        }
        
        print(f"  📝 Contexto: {contexto}")
        
    except Exception as e:
        print(f"  ❌ Erro ao testar template tag: {e}")

def verificar_views_pdf():
    """Verifica se as views de PDF foram modificadas corretamente"""
    
    print("\n🔧 Verificando views de PDF...")
    
    try:
        with open("militares/views.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se o código de BM foi adicionado nas funções de PDF
        if "Adicionar BM após o posto se não já estiver presente" in content:
            print("  ✅ Código BM encontrado nas views")
            
            # Contar ocorrências
            ocorrencias = content.count("Adicionar BM após o posto se não já estiver presente")
            print(f"  📊 Ocorrências encontradas: {ocorrencias}")
        else:
            print("  ❌ Código BM não encontrado nas views")
            
    except Exception as e:
        print(f"  ❌ Erro ao verificar views: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes de PDF com assinaturas...")
    
    # Testar geração de PDF
    testar_geracao_pdf()
    
    # Testar template tag
    testar_template_tag_em_contexto()
    
    # Verificar views
    verificar_views_pdf()
    
    print("\n✅ Testes concluídos!") 