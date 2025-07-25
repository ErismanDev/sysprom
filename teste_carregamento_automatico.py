#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso
from datetime import date

def testar_carregamento_automatico():
    """Testa o carregamento automático de militares aptos"""
    print("=== TESTE DE CARREGAMENTO AUTOMÁTICO ===")
    
    # Buscar um quadro manual de praças
    quadros_manuais = QuadroAcesso.objects.filter(
        is_manual=True,
        tipo='MANUAL'
    ).order_by('-data_criacao')
    
    if not quadros_manuais.exists():
        print("❌ Nenhum quadro manual encontrado!")
        return
    
    quadro = quadros_manuais.first()
    print(f"📋 Testando quadro: {quadro.data_promocao} (ID: {quadro.pk})")
    print(f"   Status: {quadro.get_status_display()}")
    print(f"   Critério: {quadro.criterio_ordenacao_manual}")
    print(f"   Militares atuais: {quadro.itemquadroacesso_set.count()}")
    
    # Limpar quadro para teste
    print("\n🧹 Limpando quadro para teste...")
    quadro.itemquadroacesso_set.all().delete()
    
    # Buscar praças ativos
    pracas_ativos = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    )
    
    print(f"\n📊 Estatísticas:")
    print(f"   Total de praças ativos: {pracas_ativos.count()}")
    
    # Contar por posto
    for posto in ['ST', '1S', '2S', '3S', 'CAB', 'SD']:
        count = pracas_ativos.filter(posto_graduacao=posto).count()
        print(f"   {posto}: {count}")
    
    # Testar adição manual
    print(f"\n🔧 Testando adição manual...")
    militares_aptos = []
    
    for i, praca in enumerate(pracas_ativos[:5], 1):  # Testar apenas os primeiros 5
        try:
            # Verificar se já está no quadro
            if not quadro.itemquadroacesso_set.filter(militar=praca).exists():
                # Para merecimento, verificar se tem ficha de conceito
                if quadro.criterio_ordenacao_manual == 'MERECIMENTO':
                    ficha = praca.fichaconceitooficiais_set.first() or praca.fichaconceitopracas_set.first()
                    if ficha:
                        militares_aptos.append((praca, ficha.pontos))
                        print(f"✅ {praca.nome_completo} - {ficha.pontos} pontos")
                    else:
                        print(f"❌ {praca.nome_completo} - Sem ficha de conceito")
                else:  # ANTIGUIDADE
                    militares_aptos.append((praca, 0))
                    print(f"✅ {praca.nome_completo} - Para antiguidade")
            else:
                print(f"⚠️ {praca.nome_completo} - Já está no quadro")
                
        except Exception as e:
            print(f"❌ Erro ao processar {praca.nome_completo}: {str(e)}")
    
    print(f"\n📝 Total de militares para adicionar: {len(militares_aptos)}")
    
    # Adicionar militares ao quadro
    adicionados = 0
    for i, (militar, pontuacao) in enumerate(militares_aptos, 1):
        try:
            print(f"➕ Adicionando {militar.nome_completo}...")
            quadro.adicionar_militar_manual(militar, i, pontuacao)
            adicionados += 1
            print(f"✅ Adicionado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao adicionar {militar.nome_completo}: {str(e)}")
    
    print(f"\n📊 Resultado final:")
    print(f"   Militares adicionados: {adicionados}")
    print(f"   Total no quadro: {quadro.itemquadroacesso_set.count()}")
    
    # Verificar itens no quadro
    itens = quadro.itemquadroacesso_set.all().order_by('posicao')
    print(f"\n📋 Itens no quadro:")
    for item in itens:
        print(f"   {item.posicao}. {item.militar.nome_completo} - {item.pontuacao} pontos")
    
    # Verificar se há duplicatas
    militar_ids = list(itens.values_list('militar_id', flat=True))
    if len(militar_ids) != len(set(militar_ids)):
        print(f"\n⚠️ ATENÇÃO: Há militares duplicados no quadro!")
        from collections import Counter
        duplicatas = [k for k, v in Counter(militar_ids).items() if v > 1]
        print(f"   IDs duplicados: {duplicatas}")
    else:
        print(f"\n✅ Nenhuma duplicata encontrada")

if __name__ == '__main__':
    testar_carregamento_automatico() 