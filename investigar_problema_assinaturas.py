#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, AssinaturaQuadroAcesso
from django.contrib.auth.models import User

def investigar_problema_assinaturas():
    print("=== INVESTIGAÇÃO DETALHADA: PROBLEMA DAS ASSINATURAS ===\n")
    
    # Buscar o quadro específico mencionado pelo usuário (ID 142)
    try:
        quadro = QuadroAcesso.objects.get(pk=142)
        print(f"✅ Quadro encontrado: {quadro.get_titulo_completo()}")
        print(f"   ID: {quadro.id}")
        print(f"   Status: {quadro.get_status_display()}")
        print(f"   Tipo: {quadro.get_tipo_display()}")
        print(f"   Data de promoção: {quadro.data_promocao}")
        print(f"   Data de criação: {quadro.data_criacao}")
        print(f"   Data de atualização: {quadro.data_atualizacao}")
        
        # Verificar assinaturas
        assinaturas = quadro.assinaturas.all()
        print(f"\n📋 Assinaturas atuais: {assinaturas.count()}")
        
        for assinatura in assinaturas:
            print(f"   - {assinatura.assinado_por.get_full_name()} ({assinatura.get_tipo_assinatura_display()}) - {assinatura.data_assinatura}")
        
        # Verificar itens do quadro
        itens = quadro.itemquadroacesso_set.all()
        print(f"\n👥 Itens do quadro: {itens.count()}")
        
        # Verificar se há algum comportamento específico
        print(f"\n🔍 Verificando configurações:")
        print(f"   - is_manual: {quadro.is_manual}")
        print(f"   - ativo: {quadro.ativo}")
        print(f"   - motivo_nao_elaboracao: {quadro.motivo_nao_elaboracao}")
        
        # Testar regeneração
        print(f"\n🔄 TESTANDO REGENERAÇÃO...")
        
        # Salvar estado antes
        assinaturas_antes = list(quadro.assinaturas.all())
        itens_antes = list(quadro.itemquadroacesso_set.all())
        
        # Regenerar
        sucesso, mensagem = quadro.gerar_quadro_automatico()
        print(f"Resultado: {mensagem}")
        
        # Verificar estado depois
        quadro.refresh_from_db()
        assinaturas_depois = list(quadro.assinaturas.all())
        itens_depois = list(quadro.itemquadroacesso_set.all())
        
        print(f"\n📊 COMPARAÇÃO:")
        print(f"   Assinaturas: {len(assinaturas_antes)} → {len(assinaturas_depois)}")
        print(f"   Itens: {len(itens_antes)} → {len(itens_depois)}")
        
        if len(assinaturas_antes) != len(assinaturas_depois):
            print(f"❌ PROBLEMA DETECTADO: Assinaturas perdidas!")
            
            # Verificar quais assinaturas foram perdidas
            assinaturas_perdidas = set(assinaturas_antes) - set(assinaturas_depois)
            if assinaturas_perdidas:
                print(f"   Assinaturas perdidas:")
                for assinatura in assinaturas_perdidas:
                    print(f"     - {assinatura.assinado_por.get_full_name()} ({assinatura.get_tipo_assinatura_display()})")
        else:
            print(f"✅ Assinaturas mantidas corretamente")
        
        # Verificar se o quadro foi deletado e recriado
        print(f"\n🔍 Verificando se o quadro foi recriado:")
        print(f"   ID antes: {quadro.id}")
        print(f"   Data de criação antes: {quadro.data_criacao}")
        print(f"   Data de atualização antes: {quadro.data_atualizacao}")
        
        # Verificar se há múltiplos quadros com o mesmo tipo e data
        quadros_similares = QuadroAcesso.objects.filter(
            tipo=quadro.tipo,
            data_promocao=quadro.data_promocao
        ).order_by('data_criacao')
        
        print(f"\n📋 Quadros similares encontrados: {quadros_similares.count()}")
        for q in quadros_similares:
            print(f"   - ID: {q.id}, Status: {q.get_status_display()}, Criado: {q.data_criacao}")
        
    except QuadroAcesso.DoesNotExist:
        print(f"❌ Quadro com ID 142 não encontrado!")
        
        # Verificar se há outros quadros
        quadros = QuadroAcesso.objects.all().order_by('-data_criacao')[:5]
        print(f"\n📋 Últimos quadros criados:")
        for q in quadros:
            print(f"   - ID: {q.id}, {q.get_titulo_completo()}, Status: {q.get_status_display()}")
    
    # Verificar se há algum problema com o modelo AssinaturaQuadroAcesso
    print(f"\n🔧 Verificando modelo AssinaturaQuadroAcesso:")
    total_assinaturas = AssinaturaQuadroAcesso.objects.count()
    print(f"   Total de assinaturas no sistema: {total_assinaturas}")
    
    if total_assinaturas > 0:
        ultimas_assinaturas = AssinaturaQuadroAcesso.objects.all().order_by('-data_assinatura')[:5]
        print(f"   Últimas assinaturas:")
        for assinatura in ultimas_assinaturas:
            print(f"     - {assinatura.quadro_acesso.id}: {assinatura.assinado_por.get_full_name()} ({assinatura.get_tipo_assinatura_display()}) - {assinatura.data_assinatura}")

if __name__ == "__main__":
    investigar_problema_assinaturas() 