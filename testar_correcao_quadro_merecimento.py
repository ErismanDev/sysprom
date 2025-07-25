#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, Militar

print('=== TESTE DA CORREÇÃO DO QUADRO DE MERECIMENTO ===\n')

# Buscar o quadro de merecimento mais recente
quadro_merecimento = QuadroAcesso.objects.filter(tipo='MERECIMENTO').order_by('-data_promocao').first()

if not quadro_merecimento:
    print('❌ Nenhum quadro de merecimento encontrado!')
    exit()

print(f'Quadro de Merecimento ID: {quadro_merecimento.id}')
print(f'Data de promoção: {quadro_merecimento.data_promocao}')
print(f'Status: {quadro_merecimento.get_status_display()}\n')

# Regenerar o quadro para aplicar as correções
print('🔄 Regenerando o quadro de merecimento...')
sucesso, mensagem = quadro_merecimento.gerar_quadro_completo()
print(f'Resultado: {mensagem}\n')

# Listar os itens do quadro após a correção
itens = quadro_merecimento.itemquadroacesso_set.all().order_by('posicao')

print(f'📊 Total de itens no quadro após correção: {itens.count()}\n')

if itens.exists():
    print('--- ITENS DO QUADRO DE MERECIMENTO ---')
    for item in itens:
        print(f'Posição {item.posicao}: {item.militar.nome_completo}')
        print(f'  Posto: {item.militar.posto_graduacao} | Quadro: {item.militar.quadro}')
        print(f'  Pontuação: {item.pontuacao}')
        
        # Verificar se é subtenente (não deveria aparecer)
        if item.militar.posto_graduacao == 'ST':
            print(f'  ⚠️  ALERTA: Subtenente encontrado no quadro de merecimento!')
        
        # Verificar se é Tenente-Coronel Combatente (deveria aparecer)
        if item.militar.posto_graduacao == 'TC' and item.militar.quadro == 'COMB':
            print(f'  ✅ Tenente-Coronel Combatente encontrado (correto)')
        
        print()
else:
    print('❌ Nenhum item encontrado no quadro de merecimento')

# Verificar Tenentes-Coronéis Combatentes que deveriam estar no quadro
print('--- VERIFICAÇÃO DE TENENTES-CORONÉIS COMBATENTES ---')
tc_combatentes = Militar.objects.filter(
    posto_graduacao='TC',
    quadro='COMB',
    situacao='AT'
)

print(f'Total de Tenentes-Coronéis Combatentes ativos: {tc_combatentes.count()}')

for tc in tc_combatentes:
    print(f'\n- {tc.nome_completo}')
    
    # Verificar se tem ficha de conceito
    ficha = tc.fichaconceitooficiais_set.first() or tc.fichaconceitopracas_set.first()
    if ficha:
        print(f'  ✅ Tem ficha de conceito (Pontuação: {ficha.pontos})')
    else:
        print(f'  ❌ Não tem ficha de conceito')
    
    # Verificar se está no quadro
    item_quadro = quadro_merecimento.itemquadroacesso_set.filter(militar=tc).first()
    if item_quadro:
        print(f'  ✅ Está no quadro (Posição {item_quadro.posicao})')
    else:
        print(f'  ❌ Não está no quadro')
        
        # Verificar requisitos
        apto, motivo = quadro_merecimento.validar_requisitos_quadro_acesso(tc)
        if apto:
            print(f'  ⚠️  Está apto mas não foi incluído no quadro')
        else:
            print(f'  ❌ Não está apto: {motivo}')

print('\n=== FIM DO TESTE ===') 