from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from militares.models import QuadroAcesso
from militares.utils import criptografar_cpf_lgpd
from django.contrib.auth.models import User

def quadros_em_geracao(request):
    quadros = QuadroAcesso.objects.filter(status='ELABORADO')  # ajuste o status conforme seu sistema
    return render(request, 'militares/quadros_em_geracao.html', {'quadros': quadros})

@login_required
def visualizar_quadro_html(request, pk):
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    # Buscar funções ativas do usuário
    from militares.models import UsuarioFuncao
    funcoes_usuario = UsuarioFuncao.objects.filter(
        usuario=request.user,
        status='ATIVO'
    ).select_related('cargo_funcao').order_by('cargo_funcao__nome')
    
    # Função atual selecionada (da sessão ou primeira disponível)
    funcao_atual = request.session.get('funcao_atual_nome', )
    if not funcao_atual and funcoes_usuario.exists():
        funcao_atual = funcoes_usuario.first().cargo_funcao.nome

    militares = quadro.itemquadroacesso_set.select_related('militar').all().order_by('posicao')

    meses_pt = [
        '', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
        'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
    ]
    data_formatada = f"{quadro.data_promocao.day} de {meses_pt[quadro.data_promocao.month]} de {quadro.data_promocao.year}"

    # Verificar se é quadro de oficiais ou praças
    if quadro.categoria == 'OFICIAIS':
        # Lógica para quadros de oficiais
        if quadro.tipo == 'ANTIGUIDADE':
            tipo_quadro = 'por Antiguidade'
            sigla_quadro = 'QAA'
            texto_intro = (
                f"Fica organizado o Quadro de Acesso {tipo_quadro} ({sigla_quadro}) "
                f"que visa às promoções do dia {data_formatada}, com fulcro nos artigos 12, 13, c/c § 3º do Art. 20, da Lei nº 5.461, de 30 de junho de 2005, "
                "alterada pela Lei Nº 7.772, de 04 de abril de 2022."
            )
        else:  # MERECIMENTO
            tipo_quadro = 'por Merecimento'
            sigla_quadro = 'QAM'
            texto_intro = (
                f"Fica organizado o Quadro de Acesso {tipo_quadro} ({sigla_quadro}) "
                f"que visa às promoções do dia {data_formatada}, tudo com fulcro no parágrafo único do art. 6º c/c o § 2° do art. 20 da Lei n° 5.462, de 30 de junho de 2005 "
                "c/c o art. 10 da Lei 7.772 de 04 de abril de 2022."
            )

        # Quadros de oficiais
        quadros_info = [
            {
                'numero': 1,
                'nome': 'QUADRO DE OFICIAIS BOMBEIROS MILITARES COMBATENTES (QOBM/Comb.)',
                'codigo': 'COMB'
            },
            {
                'numero': 2,
                'nome': 'QUADRO DE OFICIAIS BOMBEIROS MILITARES DE SAÚDE (QOBM/S)',
                'codigo': 'SAUDE'
            },
            {
                'numero': 3,
                'nome': 'QUADRO DE OFICIAIS BOMBEIROS MILITARES ENGENHEIROS (QOBM/E)',
                'codigo': 'ENG'
            },
            {
                'numero': 4,
                'nome': 'QUADRO DE OFICIAIS BOMBEIROS MILITARES COMPLEMENTARES (QOBM/C)',
                'codigo': 'COMP'
            }
        ]

        # Transições para oficiais (por merecimento)
        if quadro.tipo == 'MERECIMENTO':
            transicoes_por_quadro = {
                'COMB': [
                    {
                        'numero': 'I',
                        'titulo': 'TENENTE-CORONEL para o posto de CORONEL',
                        'origem': 'TC',
                        'destino': 'CB',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'II',
                        'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                        'origem': 'MJ',
                        'destino': 'TC',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'III',
                        'titulo': 'CAPITÃO para o posto de MAJOR',
                        'origem': 'CP',
                        'destino': 'MJ',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    }
                ],
                'SAUDE': [
                    {
                        'numero': 'I',
                        'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                        'origem': 'MJ',
                        'destino': 'TC',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'II',
                        'titulo': 'CAPITÃO para o posto de MAJOR',
                        'origem': 'CP',
                        'destino': 'MJ',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    }
                ],
                'ENG': [
                    {
                        'numero': 'I',
                        'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                        'origem': 'MJ',
                        'destino': 'TC',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'II',
                        'titulo': 'CAPITÃO para o posto de MAJOR',
                        'origem': 'CP',
                        'destino': 'MJ',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    }
                ],
                'COMP': [
                    {
                        'numero': 'I',
                        'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                        'origem': 'MJ',
                        'destino': 'TC',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'II',
                        'titulo': 'CAPITÃO para o posto de MAJOR',
                        'origem': 'CP',
                        'destino': 'MJ',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    }
                ]
            }
        else:  # ANTIGUIDADE
            transicoes_por_quadro = {
                'COMB': [
                    {
                        'numero': 'I',
                        'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                        'origem': 'MJ',
                        'destino': 'TC',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'II',
                        'titulo': 'CAPITÃO para o posto de MAJOR',
                        'origem': 'CP',
                        'destino': 'MJ',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'III',
                        'titulo': '1º TENENTE para o posto de CAPITÃO',
                        'origem': '1T',
                        'destino': 'CP',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'IV',
                        'titulo': '2º TENENTE para o posto de 1º TENENTE',
                        'origem': '2T',
                        'destino': '1T',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'V',
                        'titulo': 'ASPIRANTE A OFICIAL para o posto de 2º TENENTE',
                        'origem': 'AS',
                        'destino': '2T',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    }
                ],
                'SAUDE': [
                    {
                        'numero': 'I',
                        'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                        'origem': 'MJ',
                        'destino': 'TC',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'II',
                        'titulo': 'CAPITÃO para o posto de MAJOR',
                        'origem': 'CP',
                        'destino': 'MJ',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'III',
                        'titulo': '1º TENENTE para o posto de CAPITÃO',
                        'origem': '1T',
                        'destino': 'CP',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'IV',
                        'titulo': '2º TENENTE para o posto de 1º TENENTE',
                        'origem': '2T',
                        'destino': '1T',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'V',
                        'titulo': 'ALUNO DE ADAPTAÇÃO para o posto de 2º TENENTE',
                        'origem': 'AA',
                        'destino': '2T',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    }
                ],
                'ENG': [
                    {
                        'numero': 'I',
                        'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                        'origem': 'MJ',
                        'destino': 'TC',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'II',
                        'titulo': 'CAPITÃO para o posto de MAJOR',
                        'origem': 'CP',
                        'destino': 'MJ',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'III',
                        'titulo': '1º TENENTE para o posto de CAPITÃO',
                        'origem': '1T',
                        'destino': 'CP',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'IV',
                        'titulo': '2º TENENTE para o posto de 1º TENENTE',
                        'origem': '2T',
                        'destino': '1T',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'V',
                        'titulo': 'ALUNO DE ADAPTAÇÃO para o posto de 2º TENENTE',
                        'origem': 'AA',
                        'destino': '2T',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    }
                ],
                'COMP': [
                    {
                        'numero': 'I',
                        'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                        'origem': 'MJ',
                        'destino': 'TC',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'II',
                        'titulo': 'CAPITÃO para o posto de MAJOR',
                        'origem': 'CP',
                        'destino': 'MJ',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'III',
                        'titulo': '1º TENENTE para o posto de CAPITÃO',
                        'origem': '1T',
                        'destino': 'CP',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'IV',
                        'titulo': '2º TENENTE para o posto de 1º TENENTE',
                        'origem': '2T',
                        'destino': '1T',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    },
                    {
                        'numero': 'V',
                        'titulo': 'SUBTENENTE para o posto de 2º TENENTE',
                        'origem': 'ST',
                        'destino': '2T',
                        'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    }
                ]
            }

        # Para oficiais, agrupar por quadro (COMB, SAUDE, ENG, COMP) - replicar estrutura do PDF
        quadros_completos = []
        for quadro_info in quadros_info:
            codigo_quadro = quadro_info['codigo']
            if codigo_quadro in transicoes_por_quadro:
                quadro_completo = {
                    'numero': quadro_info['numero'],
                    'nome': quadro_info['nome'],
                    'codigo': codigo_quadro,
                    'transicoes': []
                }
                
                for transicao in transicoes_por_quadro[codigo_quadro]:
                    # Buscar militares para esta transição específica
                    if codigo_quadro == 'COMP' and transicao['origem'] == 'ST' and transicao['destino'] == '2T':
                        # Para transição ST->2T do COMP, incluir subtenentes do quadro PRACAS
                        militares_transicao = militares.filter(
                            militar__posto_graduacao=transicao['origem'], 
                            militar__quadro='PRACAS'
                        ).order_by('posicao')
                    else:
                        # Para outras transições, usar filtro normal
                        militares_transicao = militares.filter(
                            militar__posto_graduacao=transicao['origem'], 
                            militar__quadro=codigo_quadro
                        ).order_by('posicao')

                    # Mensagem padrão jurídica para Major -> Tenente-Coronel (Combatente)
                    if not militares_transicao.exists() and transicao['origem'] == 'MJ' and transicao['destino'] == 'TC' and codigo_quadro == 'COMB':
                        texto_sem_aptos = 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                    else:
                        texto_sem_aptos = transicao['texto']

                    transicao_completa = {
                        'numero': transicao['numero'],
                        'titulo': transicao['titulo'],
                        'origem': transicao['origem'],
                        'destino': transicao['destino'],
                        'texto': texto_sem_aptos,
                        'militares': [
                            {
                                'ordem': idx + 1,
                                'cpf': criptografar_cpf_lgpd(item.militar.cpf),
                                'graduacao': item.militar.get_posto_graduacao_display(),
                                'nome': item.militar.nome_completo,
                                'pontuacao': item.pontuacao,
                            }
                            for idx, item in enumerate(militares_transicao, 0)
                        ]
                    }
                    quadro_completo['transicoes'].append(transicao_completa)
                

                
                quadros_completos.append(quadro_completo)
        
        # Manter compatibilidade com template atual
        transicoes = []
        for quadro_completo in quadros_completos:
            for transicao in quadro_completo['transicoes']:
                transicoes.append(transicao)

    else:
        # Lógica para quadros de praças (mantida como estava)
        if quadro.tipo == 'ANTIGUIDADE':
            tipo_quadro = 'por Antiguidade'
            sigla_quadro = 'QAA'
            texto_intro = (
                f"Fica organizado o Quadro de Acesso {tipo_quadro} ({sigla_quadro}) "
                f"que visa às promoções do dia {data_formatada}, com fulcro nos artigos 12, 13, c/c § 3º do Art. 20, da Lei nº 5.461, de 30 de junho de 2005, "
                "alterada pela Lei Nº 7.772, de 04 de abril de 2022."
            )
            transicoes = [
                {
                    'numero': 'I',
                    'titulo': '1º SARGENTO para a graduação de SUBTENENTE',
                    'origem': '1S',
                    'destino': 'ST',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para a graduação de Subtenente em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': '2º SARGENTO para a graduação de 1º SARGENTO',
                    'origem': '2S',
                    'destino': '1S',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para a graduação de 1º Sargento em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '3º SARGENTO para a graduação de 2º SARGENTO',
                    'origem': '3S',
                    'destino': '2S',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para a graduação de 2º Sargento em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': 'CABO para a graduação de 3º SARGENTO',
                    'origem': 'CAB',
                    'destino': '3S',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para a graduação de 3º Sargento em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'SOLDADO para a graduação de CABO',
                    'origem': 'SD',
                    'destino': 'CAB',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para a graduação de Cabo em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ]
        else:
            tipo_quadro = 'por Merecimento'
            sigla_quadro = 'QAM'
            texto_intro = (
                f"Fica organizado o Quadro de Acesso {tipo_quadro} ({sigla_quadro}) "
                f"que visa às promoções do dia {data_formatada}, tudo com fulcro no parágrafo único do art. 6º c/c o § 2° do art. 20 da Lei n° 5.462, de 30 de junho de 2005 "
                "c/c o art. 10 da Lei 7.772 de 04 de abril de 2022."
            )
            transicoes = [
                {
                    'numero': 'I',
                    'titulo': '1º SARGENTO para a graduação de SUBTENENTE',
                    'origem': '1S',
                    'destino': 'ST',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para a graduação de Subtenente em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': '2º SARGENTO para a graduação de 1º SARGENTO',
                    'origem': '2S',
                    'destino': '1S',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para a graduação de 1º Sargento em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ]

        # Para praças, agrupar por transição
        for transicao in transicoes:
            transicao['militares'] = [
                {
                    'ordem': idx + 1,
                    'cpf': criptografar_cpf_lgpd(item.militar.cpf),
                    'graduacao': item.militar.get_posto_graduacao_display(),
                    'nome': item.militar.nome_completo,
                    'pontuacao': item.pontuacao,
                }
                for idx, item in enumerate(
                    militares.filter(militar__posto_graduacao=transicao['origem']), 0
                )
            ]

    context = {
        'quadro': quadro,
        'texto_intro': texto_intro,
        'transicoes': transicoes,
        'assinaturas': quadro.assinaturas.all().order_by('-data_assinatura'),
        'funcoes_usuario': funcoes_usuario,
        'funcao_atual': funcao_atual,
    }
    
    # Adicionar quadros_completos para oficiais
    if quadro.categoria == 'OFICIAIS':
        context['quadros_completos'] = quadros_completos
    
    return render(request, 'militares/quadro_acesso_visualizar.html', context)

def assinar_quadro_html(request, pk):
    """Assinar quadro de acesso via modal"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    if request.method == 'POST':
        senha = request.POST.get('senha')
        tipo_assinatura = request.POST.get('tipo_assinatura', 'APROVACAO')
        observacoes = request.POST.get('observacoes', '')
        funcao_assinatura = request.POST.get('funcao_assinatura', '')
        
        # Verificar senha do usuário
        if not request.user.check_password(senha):
            messages.error(request, 'Senha incorreta. Tente novamente.')
            return redirect('militares:visualizar_quadro_html', pk=quadro.pk)
        
        # Verificar se já existe uma assinatura deste usuário para este tipo
        from militares.models import AssinaturaQuadroAcesso
        assinatura_existente = AssinaturaQuadroAcesso.objects.filter(
            quadro_acesso=quadro,
            assinado_por=request.user,
            tipo_assinatura=tipo_assinatura
        ).first()
        
        if assinatura_existente:
            messages.error(request, f'Você já assinou este quadro como "{assinatura_existente.get_tipo_assinatura_display()}".')
            return redirect('militares:visualizar_quadro_html', pk=quadro.pk)
        
        # Usar a função selecionada pelo usuário ou função padrão
        if not funcao_assinatura:
            funcao_assinatura = request.session.get('funcao_atual_nome', 'Usuário do Sistema')
        
        # Criar a assinatura
        try:
            assinatura = AssinaturaQuadroAcesso.objects.create(
                quadro_acesso=quadro,
                assinado_por=request.user,
                observacoes=observacoes,
                tipo_assinatura=tipo_assinatura,
                funcao_assinatura=funcao_assinatura
            )
            messages.success(request, f'Quadro de acesso assinado com sucesso como "{assinatura.get_tipo_assinatura_display()}"!')
        except Exception as e:
            messages.error(request, f'Erro ao assinar quadro: {str(e)}')
        
        return redirect('militares:visualizar_quadro_html', pk=quadro.pk)
    
    return redirect('militares:visualizar_quadro_html', pk=quadro.pk) 