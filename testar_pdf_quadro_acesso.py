#!/usr/bin/env python
"""
Script para testar a geração de PDF do quadro de acesso com as melhorias implementadas:
- Data em português
- Assinaturas eletrônicas no final
- QR code no rodapé da última página
"""

import os
import sys
import django
from datetime import date, datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import QuadroAcesso, AssinaturaQuadroAcesso
from militares.views import quadro_acesso_pdf
from django.test import RequestFactory

def testar_geracao_pdf():
    """Testa a geração de PDF com as melhorias implementadas"""
    
    print("🧪 Testando geração de PDF do quadro de acesso...")
    
    # Buscar um quadro de acesso existente
    try:
        quadro = QuadroAcesso.objects.first()
        if not quadro:
            print("❌ Nenhum quadro de acesso encontrado no banco de dados.")
            return False
        
        print(f"✅ Quadro encontrado: {quadro}")
        print(f"   - Tipo: {quadro.get_tipo_display()}")
        print(f"   - Data de promoção: {quadro.data_promocao}")
        print(f"   - Status: {quadro.get_status_display()}")
        
        # Verificar assinaturas existentes
        assinaturas = quadro.assinaturas.all()
        print(f"   - Assinaturas: {assinaturas.count()}")
        
        for assinatura in assinaturas:
            print(f"     * {assinatura.get_tipo_assinatura_display()}: {assinatura.assinado_por.get_full_name()}")
        
        # Criar uma assinatura de teste se não existir
        if not assinaturas.exists():
            print("📝 Criando assinatura de teste...")
            user = User.objects.first()
            if user:
                assinatura_teste = AssinaturaQuadroAcesso.objects.create(
                    quadro_acesso=quadro,
                    assinado_por=user,
                    tipo_assinatura='APROVACAO',
                    observacoes='Assinatura de teste para verificação do PDF'
                )
                print(f"✅ Assinatura de teste criada: {assinatura_teste}")
        
        # Testar geração do PDF
        print("\n🔄 Testando geração do PDF...")
        
        # Criar request factory para simular requisição
        factory = RequestFactory()
        request = factory.get(f'/militares/quadros-acesso/{quadro.pk}/pdf/')
        
        # Simular usuário logado
        user = User.objects.first()
        if user:
            request.user = user
        
        # Chamar a função de geração de PDF
        try:
            response = quadro_acesso_pdf(request, quadro.pk)
            
            if response.status_code == 200:
                print("✅ PDF gerado com sucesso!")
                print(f"   - Content-Type: {response.get('Content-Type')}")
                print(f"   - Content-Disposition: {response.get('Content-Disposition')}")
                
                # Verificar se o conteúdo é um PDF válido
                content = response.content
                if content.startswith(b'%PDF'):
                    print("✅ Conteúdo é um PDF válido!")
                    print(f"   - Tamanho: {len(content)} bytes")
                    
                    # Salvar PDF para inspeção
                    filename = f"teste_quadro_acesso_{quadro.pk}.pdf"
                    with open(filename, 'wb') as f:
                        f.write(content)
                    print(f"📄 PDF salvo como: {filename}")
                    
                    return True
                else:
                    print("❌ Conteúdo não é um PDF válido!")
                    print(f"   - Primeiros bytes: {content[:50]}")
                    return False
            else:
                print(f"❌ Erro na geração do PDF: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verificar_melhorias_implementadas():
    """Verifica se as melhorias foram implementadas corretamente"""
    
    print("\n🔍 Verificando melhorias implementadas...")
    
    # Verificar se a função foi modificada
    try:
        from militares.views import quadro_acesso_pdf
        import inspect
        
        source = inspect.getsource(quadro_acesso_pdf)
        
        melhorias = {
            'Data em português': 'meses_pt' in source,
            'Assinaturas eletrônicas': 'assinaturas = quadro.assinaturas.all()' in source,
            'QR code no rodapé': 'rodape_table = Table' in source,
            'PageBreak para assinaturas': 'PageBreak()' in source,
            'Locale configurado': 'locale.setlocale' in source
        }
        
        print("📋 Status das melhorias:")
        for melhoria, implementada in melhorias.items():
            status = "✅" if implementada else "❌"
            print(f"   {status} {melhoria}")
        
        todas_implementadas = all(melhorias.values())
        if todas_implementadas:
            print("\n🎉 Todas as melhorias foram implementadas com sucesso!")
        else:
            print("\n⚠️  Algumas melhorias ainda precisam ser implementadas.")
        
        return todas_implementadas
        
    except Exception as e:
        print(f"❌ Erro ao verificar melhorias: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes do PDF do quadro de acesso...")
    print("=" * 60)
    
    # Verificar melhorias implementadas
    melhorias_ok = verificar_melhorias_implementadas()
    
    if melhorias_ok:
        # Testar geração do PDF
        pdf_ok = testar_geracao_pdf()
        
        if pdf_ok:
            print("\n🎉 Todos os testes passaram com sucesso!")
            print("✅ O PDF do quadro de acesso está funcionando corretamente com todas as melhorias.")
        else:
            print("\n❌ Falha na geração do PDF.")
    else:
        print("\n❌ Melhorias não implementadas corretamente.")
    
    print("\n" + "=" * 60)
    print("🏁 Testes concluídos.") 