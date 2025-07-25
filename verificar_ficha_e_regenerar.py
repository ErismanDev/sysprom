#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, Militar, FichaConceito

print('=== VERIFICAÇÃO DE FICHA E REGENERAÇÃO ===\n')

# Buscar o Tenente-Coronel Combatente
tc = Militar.objects.filter(
    posto_graduacao='TC',
    quadro='COMB',
    situacao='AT'
).first()

if not tc:
    print('❌ Tenente-Coronel Combatente não encontrado!')
    exit()

print(f'Nome: {tc.nome_completo}')
print(f'Quadro: {tc.get_quadro_display()} ({tc.quadro})')

# Verificar ficha de conceito
fichas = list(tc.fichaconceitooficiais_set.all()) + list(tc.fichaconceitopracas_set.all())
print(f'\nTotal de fichas de conceito: {fichas.count()}')

if fichas.exists():
    for ficha in fichas:
        print(f'✅ Ficha encontrada - ID: {ficha.id}, Pontuação: {ficha.pontos}')
else:
    print('❌ Nenhuma ficha de conceito encontrada!')

# Buscar o quadro de merecimento
quadro_merecimento = QuadroAcesso.objects.filter(tipo='MERECIMENTO').order_by('-data_promocao').first()

if not quadro_merecimento:
    print('\n❌ Nenhum quadro de merecimento encontrado!')
    exit()

print(f'\n--- QUADRO DE MERECIMENTO ---')
print(f'ID: {quadro_merecimento.id}')
print(f'Data de promoção: {quadro_merecimento.data_promocao}')
print(f'Status: {quadro_merecimento.get_status_display()}')

# Verificar itens atuais
itens_atuais = quadro_merecimento.itemquadroacesso_set.all()
print(f'Itens atuais: {itens_atuais.count()}')

# Regenerar o quadro
print(f'\n🔄 Regenerando o quadro de merecimento...')
sucesso, mensagem = quadro_merecimento.gerar_quadro_completo()
print(f'Resultado: {mensagem}')

# Verificar itens após regeneração
itens_novos = quadro_merecimento.itemquadroacesso_set.all()
print(f'\nItens após regeneração: {itens_novos.count()}')

if itens_novos.exists():
    print('Itens no quadro:')
    for item in itens_novos.order_by('posicao'):
        print(f'  Posição {item.posicao}: {item.militar.nome_completo} ({item.militar.posto_graduacao} - {item.militar.quadro}) - Pontuação: {item.pontuacao}')
        
        # Verificar se é o Tenente-Coronel
        if item.militar == tc:
            print(f'    ✅ TENENTE-CORONEL ENCONTRADO NO QUADRO!')
else:
    print('❌ Nenhum item encontrado no quadro após regeneração')

# Verificar especificamente o Tenente-Coronel
item_tc = quadro_merecimento.itemquadroacesso_set.filter(militar=tc).first()
if item_tc:
    print(f'\n✅ Tenente-Coronel está no quadro - Posição {item_tc.posicao}, Pontuação: {item_tc.pontuacao}')
else:
    print(f'\n❌ Tenente-Coronel NÃO está no quadro')
    
    # Verificar requisitos novamente
    apto, motivo = quadro_merecimento.validar_requisitos_quadro_acesso(tc)
    print(f'  Apto: {"Sim" if apto else "Não"}')
    if not apto:
        print(f'  Motivo: {motivo}')

print('\n=== FIM ===') 