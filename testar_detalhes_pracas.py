#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso
from militares.views_pracas import quadro_acesso_pracas_detail
from django.test import RequestFactory
from django.contrib.auth.models import User

def testar_detalhes_pracas():
    print("=== TESTANDO VIEW DE DETALHES DE PRACAS ===\n")
    
    # 1. Verificar quadros com praças
    print("1. QUADROS COM PRACAS:")
    print("-" * 50)
    
    postos_pracas = ['SD', 'CAB', '3S', '2S', '1S', 'ST']
    quadros_com_pracas = []
    
    for quadro in QuadroAcesso.objects.all():
        itens_pracas = quadro.itemquadroacesso_set.filter(
            militar__posto_graduacao__in=postos_pracas
        )
        if itens_pracas.exists():
            quadros_com_pracas.append(quadro)
            print(f"  ✅ {quadro.get_tipo_display()} (ID: {quadro.id}) - {itens_pracas.count()} praças")
        else:
            print(f"  ❌ {quadro.get_tipo_display()} (ID: {quadro.id}) - 0 praças")
    
    if not quadros_com_pracas:
        print("❌ Nenhum quadro com praças encontrado!")
        return
    
    # 2. Testar a view de detalhes
    print(f"\n2. TESTANDO VIEW DE DETALHES:")
    print("-" * 50)
    
    # Criar um usuário de teste
    user, created = User.objects.get_or_create(
        username='teste_detalhes',
        defaults={'email': 'teste@teste.com'}
    )
    
    # Criar uma requisição de teste
    factory = RequestFactory()
    
    for quadro in quadros_com_pracas:
        print(f"\nTestando quadro {quadro.id} ({quadro.get_tipo_display()}):")
        
        request = factory.get(f'/militares/pracas/quadros-acesso/{quadro.id}/')
        request.user = user
        
        try:
            response = quadro_acesso_pracas_detail(request, pk=quadro.id)
            print(f"  Status da resposta: {response.status_code}")
            
            # Verificar o contexto
            if hasattr(response, 'context_data'):
                context = response.context_data
                print(f"  Contexto disponível: {list(context.keys())}")
                
                # Verificar estrutura_quadros
                if 'estrutura_quadros' in context:
                    estrutura = context['estrutura_quadros']
                    print(f"  Estrutura de quadros: {list(estrutura.keys())}")
                    
                    for quadro_nome, dados in estrutura.items():
                        print(f"    Quadro: {dados['nome']}")
                        print(f"    Transições: {len(dados['transicoes'])}")
                        
                        for i, transicao in enumerate(dados['transicoes']):
                            print(f"      Transição {i+1}: {transicao['origem_nome']} → {transicao['destino_nome']}")
                            print(f"        Militares: {len(transicao['militares'])}")
                            
                            for item in transicao['militares']:
                                print(f"          - {item.militar.nome_completo} ({item.militar.posto_graduacao}) - Pos: {item.posicao}")
                else:
                    print("  ❌ estrutura_quadros não encontrada no contexto")
                
                # Verificar militares inaptos
                if 'militares_inaptos' in context:
                    inaptos = context['militares_inaptos']
                    print(f"  Militares inaptos: {len(inaptos)}")
                    for inapto in inaptos:
                        print(f"    - {inapto['militar'].nome_completo}: {inapto['motivo']}")
                else:
                    print("  Militares inaptos: 0")
                    
            else:
                print("  Resposta não tem context_data")
                
        except Exception as e:
            print(f"  ❌ Erro na view: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 3. Verificar dados manualmente
    print(f"\n3. VERIFICAÇÃO MANUAL DOS DADOS:")
    print("-" * 50)
    
    for quadro in quadros_com_pracas:
        print(f"\nQuadro {quadro.id} ({quadro.get_tipo_display()}):")
        
        # Verificar todos os itens
        todos_itens = quadro.itemquadroacesso_set.all().select_related('militar')
        print(f"  Total de itens: {todos_itens.count()}")
        
        # Separar por tipo
        itens_pracas = []
        itens_oficiais = []
        
        for item in todos_itens:
            if item.militar.posto_graduacao in postos_pracas:
                itens_pracas.append(item)
            else:
                itens_oficiais.append(item)
        
        print(f"  Itens de praças: {len(itens_pracas)}")
        print(f"  Itens de oficiais: {len(itens_oficiais)}")
        
        if itens_pracas:
            print("  Praças no quadro:")
            for item in itens_pracas:
                print(f"    - {item.militar.nome_completo} ({item.militar.posto_graduacao}) - Pos: {item.posicao}")
        
        if itens_oficiais:
            print("  Oficiais no quadro:")
            for item in itens_oficiais:
                print(f"    - {item.militar.nome_completo} ({item.militar.posto_graduacao}) - Pos: {item.posicao}")
    
    # 4. Resumo final
    print(f"\n4. RESUMO FINAL:")
    print("-" * 50)
    print("Para corrigir o problema:")
    print("1. O template deve mostrar apenas as praças organizadas por transições")
    print("2. A view deve filtrar apenas militares com postos de praças")
    print("3. As transições devem ser específicas para praças")
    print("\nPróximos passos:")
    print("1. Verificar se a view está filtrando corretamente")
    print("2. Verificar se o template está usando os dados corretos")
    print("3. Testar a página no navegador")

if __name__ == "__main__":
    testar_detalhes_pracas() 