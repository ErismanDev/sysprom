#!/usr/bin/env python
ipt para verificar e adicionar Major ao quadro de acesso366
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE, romcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, Militar, ItemQuadroAcesso

def verificar_major_quadro():
   Verifica se há Majores no quadro366iona se necessário
    
    # Buscar o quadro 366ry:
        quadro = QuadroAcesso.objects.get(id=366)
        print(f"✅ Quadro encontrado: {quadro})
        print(f"   Tipo: {quadro.get_tipo_display()})
        print(f"   Status: {quadro.get_status_display()})
        print(f"   Data:[object Object]quadro.data_promocao})
    except QuadroAcesso.DoesNotExist:
        print("❌ Quadro 366não encontrado!")
        return
    
    # Buscar Majores combatentes ativos
    majores = Militar.objects.filter(
        posto_graduacao='MJ',
        quadro='COMB',
        situacao='AT'
    )
    
    print(f"\n📋 Majores combatentes encontrados: {majores.count()}")
    for major in majores:
        print(f"   - {major.nome_completo} ({major.matricula})")
    
    # Verificar quais Majores já estão no quadro
    majores_no_quadro = quadro.itemquadroacesso_set.filter(
        militar__posto_graduacao='MJ,
        militar__quadro=COMB'
    )
    
    print(f"\n📊 Majores no quadro366: {majores_no_quadro.count()})   for item in majores_no_quadro:
        print(f"   - {item.militar.nome_completo} (posição {item.posicao})")
    
    # Adicionar Majores que não estão no quadro
    majores_para_adicionar = majores.exclude(
        id__in=majores_no_quadro.values_list(militar_id', flat=True)
    )
    
    print(f"\n➕ Majores para adicionar: {majores_para_adicionar.count()})   
    if majores_para_adicionar.exists():
        print("\n🔧 Adicionando Majores ao quadro...")
        
        for major in majores_para_adicionar:
            try:
                # Verificar se o Major está apto
                apto, motivo = quadro.validar_requisitos_quadro_acesso(major)
                
                if apto:
                    # Adicionar ao quadro
                    quadro.adicionar_militar_manual(major)
                    print(f"   ✅ {major.nome_completo} adicionado com sucesso)              else:
                    print(f"   ❌ {major.nome_completo} não está apto: {motivo}")
                    
            except Exception as e:
                print(f"   ❌ Erro ao adicionar {major.nome_completo}: {str(e)}")
    else:
        print("✅ Todos os Majores já estão no quadro")
    
    # Verificar se a transição MJ → TC aparece no PDF
    print(f"\n🔍 Verificando transições do quadro...")
    
    # Buscar transições do quadro COMB
    from militares.views import transicoes_por_quadro
    
    if quadro.tipo == 'ANTIGUIDADE':
        transicoes = transicoes_por_quadro.get('COMB',])
        print(f"   Transições encontradas: {len(transicoes)}")
        
        for transicao in transicoes:
            print(f   -{transicao[numero']}: {transicao['titulo']}")
            
            # Verificar se há militares para esta transição
            aptos = quadro.itemquadroacesso_set.filter(
                militar__posto_graduacao=transicao['origem'],
                militar__quadro=COMB'
            )
            
            if aptos.exists():
                print(f"     ✅ {aptos.count()} militares aptos)               for apto in aptos:
                    print(f"       - {apto.militar.nome_completo}")
            else:
                print(f"     ❌ Nenhum militar apto")
    
    print(f"\n✅ Verificação concluída!)if __name__ == '__main__:   verificar_major_quadro() 