#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, Militar

print('=== INVESTIGAÇÃO DE TENENTES-CORONÉIS ===\n')

# Buscar todos os Tenentes-Coronéis ativos
tenentes_coroneis = Militar.objects.filter(
    posto_graduacao='TC',
    situacao='AT'
).order_by('quadro', 'nome_completo')

print(f'Total de Tenentes-Coronéis ativos: {tenentes_coroneis.count()}\n')

if not tenentes_coroneis.exists():
    print('❌ Nenhum Tenente-Coronel ativo encontrado!')
    exit()

# Buscar o quadro de merecimento
quadro_merecimento = QuadroAcesso.objects.filter(tipo='MERECIMENTO').order_by('-data_promocao').first()

if not quadro_merecimento:
    print('❌ Nenhum quadro de merecimento encontrado!')
    exit()

print(f'Quadro de Merecimento: ID {quadro_merecimento.id} | Data: {quadro_merecimento.data_promocao}\n')

# Analisar cada Tenente-Coronel
for i, tc in enumerate(tenentes_coroneis, 1):
    print(f'--- TENENTE-CORONEL {i} ---')
    print(f'Nome: {tc.nome_completo}')
    print(f'Quadro: {tc.get_quadro_display()} ({tc.quadro})')
    print(f'Data de promoção atual: {tc.data_promocao_atual}')
    print(f'Data de ingresso: {tc.data_ingresso}')
    
    # Verificar ficha de conceito
    ficha = tc.fichaconceitooficiais_set.first() or tc.fichaconceitopracas_set.first()
    if ficha:
        print(f'✅ Tem ficha de conceito - Pontuação: {ficha.pontos}')
    else:
        print(f'❌ Não tem ficha de conceito')
    
    # Verificar se está no quadro de merecimento
    item_quadro = quadro_merecimento.itemquadroacesso_set.filter(militar=tc).first()
    if item_quadro:
        print(f'✅ Está no quadro de merecimento - Posição {item_quadro.posicao}')
    else:
        print(f'❌ Não está no quadro de merecimento')
        
        # Verificar requisitos detalhadamente
        print(f'  Verificando requisitos...')
        
        # 1. Verificar interstício
        tempo_posto = tc.tempo_posto_atual()
        intersticio_min = tc.intersticio_minimo()
        print(f'    Tempo no posto: {tempo_posto} anos')
        print(f'    Interstício mínimo: {intersticio_min} meses ({intersticio_min/12:.1f} anos)')
        print(f'    Apto interstício: {"Sim" if tc.apto_intersticio() else "Não"}')
        
        # 2. Verificar inspeção de saúde
        print(f'    Apto inspeção de saúde: {"Sim" if tc.apto_inspecao_saude else "Não"}')
        if tc.data_inspecao_saude:
            print(f'    Data inspeção: {tc.data_inspecao_saude}')
        if tc.data_validade_inspecao_saude:
            print(f'    Validade inspeção: {tc.data_validade_inspecao_saude}')
        
        # 3. Verificar cursos inerentes
        cursos_inerentes = tc.cursos_inerentes_quadro()
        print(f'    Cursos inerentes: {cursos_inerentes}')
        
        # 4. Verificar validação completa
        apto, motivo = quadro_merecimento.validar_requisitos_quadro_acesso(tc)
        print(f'    Resultado validação: {"Apto" if apto else "Inapto"}')
        if not apto:
            print(f'    Motivo: {motivo}')
        
        # 5. Verificar tipo de transição
        proximo_posto = quadro_merecimento._obter_proximo_posto('TC')
        tipo_transicao = quadro_merecimento.determinar_tipo_quadro_por_transicao('TC', proximo_posto)
        print(f'    Próximo posto: {proximo_posto}')
        print(f'    Tipo de transição: {tipo_transicao}')
        
        # 6. Verificar se deveria estar no quadro de merecimento
        if tipo_transicao == 'MERECIMENTO':
            print(f'    ✅ Transição é por merecimento - deveria estar no quadro')
        elif tipo_transicao == 'AMBOS':
            print(f'    ⚠️  Transição permite ambos - pode estar no quadro de merecimento')
        else:
            print(f'    ❌ Transição não é por merecimento - não deveria estar no quadro')
    
    print()

# Verificar itens atuais do quadro de merecimento
print('--- ITENS ATUAIS DO QUADRO DE MERECIMENTO ---')
itens_quadro = quadro_merecimento.itemquadroacesso_set.all().order_by('posicao')
print(f'Total de itens: {itens_quadro.count()}')

for item in itens_quadro:
    print(f'  Posição {item.posicao}: {item.militar.nome_completo} ({item.militar.posto_graduacao} - {item.militar.quadro}) - Pontuação: {item.pontuacao}')

print('\n=== FIM DA INVESTIGAÇÃO ===') 