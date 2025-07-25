#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, Militar, FichaConceito

print('=== INVESTIGAÇÃO DETALHADA DO TENENTE-CORONEL ===\n')

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
print(f'Data de promoção atual: {tc.data_promocao_atual}')
print(f'Data de ingresso: {tc.data_ingresso}\n')

# Verificar ficha de conceito detalhadamente
fichas = tc.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all()))
print(f'Total de fichas de conceito: {fichas.count()}')

if fichas.exists():
    for i, ficha in enumerate(fichas, 1):
        print(f'\n--- FICHA DE CONCEITO {i} ---')
        print(f'ID: {ficha.id}')
        print(f'Data de registro: {ficha.data_registro}')
        print(f'Pontuação total: {ficha.pontos}')
        print(f'Observações: {ficha.observacoes}')
        
        # Detalhes da pontuação
        print(f'\n  Detalhes da pontuação:')
        print(f'    Tempo no posto: {ficha.tempo_posto}')
        print(f'    Cursos especialização: {ficha.cursos_especializacao}')
        print(f'    CSBM: {ficha.cursos_csbm}')
        print(f'    CFSD: {ficha.cursos_cfsd}')
        print(f'    CHC: {ficha.cursos_chc}')
        print(f'    CHSGT: {ficha.cursos_chsgt}')
        print(f'    CAS: {ficha.cursos_cas}')
        print(f'    CHO: {ficha.cursos_cho}')
        print(f'    CFO: {ficha.cursos_cfo}')
        print(f'    CAO: {ficha.cursos_cao}')
        print(f'    CSBM Instrutor: {ficha.cursos_instrutor_csbm}')
        print(f'    Superior civil: {ficha.cursos_civis_superior}')
        print(f'    Especialização civil: {ficha.cursos_civis_especializacao}')
        print(f'    Mestrado: {ficha.cursos_civis_mestrado}')
        print(f'    Doutorado: {ficha.cursos_civis_doutorado}')
        print(f'    Medalha Federal: {ficha.medalha_federal}')
        print(f'    Medalha Estadual: {ficha.medalha_estadual}')
        print(f'    Medalha CBMEPI: {ficha.medalha_cbmepi}')
        print(f'    Elogio Individual: {ficha.elogio_individual}')
        print(f'    Elogio Coletivo: {ficha.elogio_coletivo}')
        print(f'    Repreensão: {ficha.punicao_repreensao}')
        print(f'    Detenção: {ficha.punicao_detencao}')
        print(f'    Prisão: {ficha.punicao_prisao}')
        print(f'    Falta aproveitamento: {ficha.falta_aproveitamento}')
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

# Verificar se está no quadro
item_quadro = quadro_merecimento.itemquadroacesso_set.filter(militar=tc).first()
if item_quadro:
    print(f'✅ Está no quadro - Posição {item_quadro.posicao}, Pontuação: {item_quadro.pontuacao}')
else:
    print(f'❌ Não está no quadro')
    
    # Testar a validação manualmente
    print(f'\n--- TESTE DE VALIDAÇÃO MANUAL ---')
    
    # 1. Verificar se tem ficha de conceito (filtro do método)
    tem_ficha = tc.fichaconceitooficiais_set.exists() or tc.fichaconceitopracas_set.exists()
    print(f'1. Tem ficha de conceito: {"Sim" if tem_ficha else "Não"}')
    
    # 2. Verificar requisitos completos
    apto, motivo = quadro_merecimento.validar_requisitos_quadro_acesso(tc)
    print(f'2. Apto para promoção: {"Sim" if apto else "Não"}')
    if not apto:
        print(f'   Motivo: {motivo}')
    
    # 3. Verificar tipo de transição
    proximo_posto = quadro_merecimento._obter_proximo_posto('TC')
    tipo_transicao = quadro_merecimento.determinar_tipo_quadro_por_transicao('TC', proximo_posto)
    print(f'3. Próximo posto: {proximo_posto}')
    print(f'4. Tipo de transição: {tipo_transicao}')
    
    # 4. Simular o filtro do método gerar_quadro_completo
    print(f'\n--- SIMULAÇÃO DO FILTRO DO MÉTODO ---')
    
    # Buscar militares candidatos como o método faz
    militares_candidatos = Militar.objects.filter(
        quadro='COMB',
        posto_graduacao='TC',
        situacao='AT'
    )
    print(f'Militares candidatos encontrados: {militares_candidatos.count()}')
    
    # Aplicar filtro de ficha de conceito
    if tipo_transicao == 'MERECIMENTO':
        militares_com_ficha = militares_candidatos.filter(Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False))
        print(f'Militares com ficha de conceito: {militares_com_ficha.count()}')
        
        for militar in militares_com_ficha:
            print(f'  - {militar.nome_completo}')
            ficha = militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
            print(f'    Ficha ID: {ficha.id if ficha else "N/A"}')
            print(f'    Pontuação: {ficha.pontos if ficha else "N/A"}')
    
    # 5. Testar validação de requisitos para cada candidato
    print(f'\n--- VALIDAÇÃO DE REQUISITOS ---')
    for militar in militares_candidatos:
        print(f'\nMilitar: {militar.nome_completo}')
        apto, motivo = quadro_merecimento.validar_requisitos_quadro_acesso(militar)
        print(f'  Apto: {"Sim" if apto else "Não"}')
        if not apto:
            print(f'  Motivo: {motivo}')

print('\n=== FIM DA INVESTIGAÇÃO ===') 