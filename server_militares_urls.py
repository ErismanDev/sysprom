from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import redirect
from . import views
from . import views_simples
from . import views_pracas
from . import views_publicacoes
from . import views_unificadas
from . import views_quadros_html
from . import views_ajax
from . import views_ajax_boletim
from . import views_assinaturas_escalas
from . import views_atas_melhoradas
from . import views_atas_padrao
from . import views_ajax_atas
from . import views_configuracao_planejadas
from . import views_planejadas
from . import views_configuracoes
from .views import reordenar_numeracoes_view
from .views_sessao_pdf import sessao_gerar_pdf_completo, upload_arquivos_sessao, testar_pdf
from .usuario_views import redirect_usuario_ficha, welcome_usuario, mark_welcome_shown
from django.db.models import Q
from .models import Militar
from django.shortcuts import redirect
from . import views_medalhas
from . import views_lotacao
from . import views_afastamento
from . import views_ferias
from . import views_licencas_especiais
from . import views_averbacao
from . import views_viaturas
from . import views_abastecimentos
from . import views_manutencoes
from . import views_trocas_oleo
from . import views_rodagens
from . import views_licenciamentos
from . import views_equipamentos_operacionais
from . import views_secao_promocoes
from . import views_elogios_punicoes
from . import views_assinaturas_notas, views_modelos_notas, views_anexos_notas, views_assinaturas_boletim, views_boletim_pdf, views_boletins_reservados, views_assinaturas_boletim_especial
from . import views_material_belico
from . import views_cautela_arma, views_municao, views_cautela_municao
from . import views_tombamento, views_almoxarifado, views_requisicao_almoxarifado, views_processos
from . import views_chat
from . import views_ensino
from . import views_dashboard_ensino
from . import views_login_ensino
from . import views_usuarios_ensino
from . import views_assinaturas_qts

app_name = 'militares'

def militar_autocomplete(request):
    """View para autocomplete de militares com hierarquia"""
    q = request.GET.get('q', '').strip()
    # Permitir busca vazia ou com menos de 2 caracteres para mostrar lista inicial
    if not q:
        q = ''  # Buscar todos se não houver termo
    
    # Buscar militares ativos (por nome, nome de guerra, matrícula, CPF ou posto)
    militares = Militar.objects.filter(
        classificacao='ATIVO'
    )
    
    # Se houver termo de busca, aplicar filtros
    if q:
        militares = militares.filter(
            Q(nome_completo__icontains=q) |
            Q(nome_guerra__icontains=q) |
            Q(matricula__icontains=q) |
            Q(cpf__icontains=q) |
            Q(posto_graduacao__icontains=q)
        )
    
    # Ordenar por hierarquia (posto) e depois por antiguidade
    ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
    
    from django.db.models import Case, When, Value, IntegerField
    hierarquia_ordem = Case(
        *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
        default=Value(len(ordem_hierarquica)),
        output_field=IntegerField()
    )
    
    militares = militares.annotate(
        ordem_hierarquia=hierarquia_ordem
    ).order_by(
        'ordem_hierarquia',
        'data_promocao_atual',
        'numeracao_antiguidade',
        'nome_completo'
    )[:50]  # Aumentar limite para mostrar mais resultados na lista inicial
    
    results = []
    for militar in militares:
        # Formatar texto com posto e nome
        text_display = f"{militar.get_posto_graduacao_display()} {militar.nome_completo}"
        if militar.nome_guerra:
            text_display += f" ({militar.nome_guerra})"
        if militar.cpf:
            text_display += f" - CPF: {militar.cpf}"
        
        results.append({
            'id': militar.id,
            'text': text_display,
        })
    
    return JsonResponse({'results': results}, content_type='application/json')

def lotacao_autocomplete(request):
    """View para autocomplete de estrutura organizacional baseado no nível de acesso"""
    from .models import Lotacao, Orgao, GrandeComando, Unidade, SubUnidade
    from .permissoes_militares import obter_nivel_acesso_usuario, obter_sessao_ativa_usuario
    from django.db.models import Q
    
    q = request.GET.get('q', '').strip()
    
    if len(q) < 2:
        return JsonResponse({'results': []})
    
    # Obter nível de acesso do usuário
    nivel_acesso = obter_nivel_acesso_usuario(request.user)
    sessao = obter_sessao_ativa_usuario(request.user)
    
    results = []
    
    if nivel_acesso == 'TOTAL':
        # Acesso total - pode buscar em todas as estruturas
        # Buscar por Órgãos
        orgaos = Orgao.objects.filter(
            nome__icontains=q,
            ativo=True
        )[:5]
        
        for orgao in orgaos:
            total_lotacoes = Lotacao.objects.filter(
                orgao=orgao,
                ativo=True
            ).count()
            
            results.append({
                'id': f"orgao_{orgao.id}",
                'nome': orgao.nome,
                'nome_hierarquico': f" {orgao.nome} ({total_lotacoes} lotações)",
                'tipo': 'orgao',
                'orgao_id': orgao.id,
                'grande_comando_id': None,
                'unidade_id': None,
                'sub_unidade_id': None
            })
        
        # Buscar por Grandes Comandos
        grandes_comandos = GrandeComando.objects.filter(
            nome__icontains=q,
            ativo=True
        )[:5]
        
        for gc in grandes_comandos:
            total_lotacoes = Lotacao.objects.filter(
                grande_comando=gc,
                ativo=True
            ).count()
            
            results.append({
                'id': f"gc_{gc.id}",
                'nome': gc.nome,
                'nome_hierarquico': f" {gc.nome} ({total_lotacoes} lotações)",
                'tipo': 'grande_comando',
                'orgao_id': gc.orgao.id if gc.orgao else None,
                'grande_comando_id': gc.id,
                'unidade_id': None,
                'sub_unidade_id': None
            })
        
        # Buscar por Unidades
        unidades = Unidade.objects.filter(
            nome__icontains=q,
            ativo=True
        )[:5]
        
        for unidade in unidades:
            total_lotacoes = Lotacao.objects.filter(
                unidade=unidade,
                ativo=True
            ).count()
            
            results.append({
                'id': f"unidade_{unidade.id}",
                'nome': unidade.nome,
                'nome_hierarquico': f" {unidade.nome} ({total_lotacoes} lotações)",
                'tipo': 'unidade',
                'orgao_id': unidade.grande_comando.orgao.id if unidade.grande_comando and unidade.grande_comando.orgao else None,
                'grande_comando_id': unidade.grande_comando.id if unidade.grande_comando else None,
                'unidade_id': unidade.id,
                'sub_unidade_id': None
            })
        
        # Buscar por Sub-Unidades
        sub_unidades = SubUnidade.objects.filter(
            nome__icontains=q,
            ativo=True
        )[:5]
        
        for sub_unidade in sub_unidades:
            total_lotacoes = Lotacao.objects.filter(
                sub_unidade=sub_unidade,
                ativo=True
            ).count()
            
            results.append({
                'id': f"sub_unidade_{sub_unidade.id}",
                'nome': sub_unidade.nome,
                'nome_hierarquico': f" {sub_unidade.nome} ({total_lotacoes} lotações)",
                'tipo': 'sub_unidade',
                'orgao_id': sub_unidade.unidade.grande_comando.orgao.id if sub_unidade.unidade and sub_unidade.unidade.grande_comando and sub_unidade.unidade.grande_comando.orgao else None,
                'grande_comando_id': sub_unidade.unidade.grande_comando.id if sub_unidade.unidade and sub_unidade.unidade.grande_comando else None,
                'unidade_id': sub_unidade.unidade.id if sub_unidade.unidade else None,
                'sub_unidade_id': sub_unidade.id
            })
    
    elif nivel_acesso == 'ORGAO' and sessao and sessao.funcao_militar_usuario and sessao.funcao_militar_usuario.orgao:
        # Acesso ao órgão - mostrar órgão e suas estruturas
        orgao = sessao.funcao_militar_usuario.orgao
        
        # Adicionar o próprio órgão
        if q.lower() in orgao.nome.lower():
            total_lotacoes = Lotacao.objects.filter(
                orgao=orgao,
                ativo=True
            ).count()
            
            results.append({
                'id': f"orgao_{orgao.id}",
                'nome': orgao.nome,
                'nome_hierarquico': f" {orgao.nome} ({total_lotacoes} lotações)",
                'tipo': 'orgao',
                'orgao_id': orgao.id,
                'grande_comando_id': None,
                'unidade_id': None,
                'sub_unidade_id': None
            })
        
        # Buscar grandes comandos do órgão
        grandes_comandos = GrandeComando.objects.filter(
            orgao=orgao,
            nome__icontains=q,
            ativo=True
        )[:5]
        
        for gc in grandes_comandos:
            total_lotacoes = Lotacao.objects.filter(
                grande_comando=gc,
                ativo=True
            ).count()
            
            results.append({
                'id': f"gc_{gc.id}",
                'nome': gc.nome,
                'nome_hierarquico': f" {gc.nome} ({total_lotacoes} lotações)",
                'tipo': 'grande_comando',
                'orgao_id': orgao.id,
                'grande_comando_id': gc.id,
                'unidade_id': None,
                'sub_unidade_id': None
            })
    
    elif nivel_acesso == 'GRANDE_COMANDO' and sessao and sessao.funcao_militar_usuario and sessao.funcao_militar_usuario.grande_comando:
        # Acesso ao grande comando - mostrar grande comando e suas estruturas
        gc = sessao.funcao_militar_usuario.grande_comando
        
        # Adicionar o próprio grande comando
        if q.lower() in gc.nome.lower():
            total_lotacoes = Lotacao.objects.filter(
                grande_comando=gc,
                ativo=True
            ).count()
            
            results.append({
                'id': f"gc_{gc.id}",
                'nome': gc.nome,
                'nome_hierarquico': f" {gc.nome} ({total_lotacoes} lotações)",
                'tipo': 'grande_comando',
                'orgao_id': gc.orgao.id if gc.orgao else None,
                'grande_comando_id': gc.id,
                'unidade_id': None,
                'sub_unidade_id': None
            })
        
        # Buscar unidades do grande comando
        unidades = Unidade.objects.filter(
            grande_comando=gc,
            nome__icontains=q,
            ativo=True
        )[:5]
        
        for unidade in unidades:
            total_lotacoes = Lotacao.objects.filter(
                unidade=unidade,
                ativo=True
            ).count()
            
            results.append({
                'id': f"unidade_{unidade.id}",
                'nome': unidade.nome,
                'nome_hierarquico': f" {unidade.nome} ({total_lotacoes} lotações)",
                'tipo': 'unidade',
                'orgao_id': gc.orgao.id if gc.orgao else None,
                'grande_comando_id': gc.id,
                'unidade_id': unidade.id,
                'sub_unidade_id': None
            })
    
    elif nivel_acesso == 'UNIDADE' and sessao and sessao.funcao_militar_usuario and sessao.funcao_militar_usuario.unidade:
        # Acesso à unidade - mostrar unidade e suas sub-unidades
        unidade = sessao.funcao_militar_usuario.unidade
        
        # Adicionar a própria unidade
        if q.lower() in unidade.nome.lower():
            total_lotacoes = Lotacao.objects.filter(
                unidade=unidade,
                ativo=True
            ).count()
            
            results.append({
                'id': f"unidade_{unidade.id}",
                'nome': unidade.nome,
                'nome_hierarquico': f" {unidade.nome} ({total_lotacoes} lotações)",
                'tipo': 'unidade',
                'orgao_id': unidade.grande_comando.orgao.id if unidade.grande_comando and unidade.grande_comando.orgao else None,
                'grande_comando_id': unidade.grande_comando.id if unidade.grande_comando else None,
                'unidade_id': unidade.id,
                'sub_unidade_id': None
            })
        
        # Buscar sub-unidades da unidade
        sub_unidades = SubUnidade.objects.filter(
            unidade=unidade,
            nome__icontains=q,
            ativo=True
        )[:5]
        
        for sub_unidade in sub_unidades:
            total_lotacoes = Lotacao.objects.filter(
                sub_unidade=sub_unidade,
                ativo=True
            ).count()
            
            results.append({
                'id': f"sub_unidade_{sub_unidade.id}",
                'nome': sub_unidade.nome,
                'nome_hierarquico': f" {sub_unidade.nome} ({total_lotacoes} lotações)",
                'tipo': 'sub_unidade',
                'orgao_id': unidade.grande_comando.orgao.id if unidade.grande_comando and unidade.grande_comando.orgao else None,
                'grande_comando_id': unidade.grande_comando.id if unidade.grande_comando else None,
                'unidade_id': unidade.id,
                'sub_unidade_id': sub_unidade.id
            })
    
    elif nivel_acesso == 'SUBUNIDADE' and sessao and sessao.funcao_militar_usuario and sessao.funcao_militar_usuario.sub_unidade:
        # Acesso apenas à sub-unidade
        sub_unidade = sessao.funcao_militar_usuario.sub_unidade
        
        if q.lower() in sub_unidade.nome.lower():
            total_lotacoes = Lotacao.objects.filter(
                sub_unidade=sub_unidade,
                ativo=True
            ).count()
            
            results.append({
                'id': f"sub_unidade_{sub_unidade.id}",
                'nome': sub_unidade.nome,
                'nome_hierarquico': f" {sub_unidade.nome} ({total_lotacoes} lotações)",
                'tipo': 'sub_unidade',
                'orgao_id': sub_unidade.unidade.grande_comando.orgao.id if sub_unidade.unidade and sub_unidade.unidade.grande_comando and sub_unidade.unidade.grande_comando.orgao else None,
                'grande_comando_id': sub_unidade.unidade.grande_comando.id if sub_unidade.unidade and sub_unidade.unidade.grande_comando else None,
                'unidade_id': sub_unidade.unidade.id if sub_unidade.unidade else None,
                'sub_unidade_id': sub_unidade.id
            })
    
    # Ordenar resultados por tipo (órgão primeiro, depois hierarquia)
    tipo_ordem = {'orgao': 1, 'grande_comando': 2, 'unidade': 3, 'sub_unidade': 4}
    results.sort(key=lambda x: (tipo_ordem.get(x['tipo'], 5), x['nome']))
    
    return JsonResponse({'results': results[:10]})

def redirect_voto_detail(request, pk):
    return redirect('militares:voto_visualizar_assinar', pk=pk)

urlpatterns = [
    # Páginas principais
    path('', views.home, name='home'),
    path('dashboard/', views.militar_dashboard, name='militar_dashboard'),
    path('estatisticas/', views.estatisticas, name='estatisticas'),
    
    # Almanaques - seguindo o padrão dos quadros de fixação de vagas
    path('almanaques/', views.almanaque_list, name='almanaque_list'),
    path('almanaques/novo/', views.almanaque_create, name='almanaque_create'),
    path('almanaques/<int:pk>/', views.almanaque_detail, name='almanaque_detail'),

    path('almanaques/<int:pk>/visualizar-html/', views.almanaque_visualizar_html, name='almanaque_visualizar_html'),
    path('almanaques/<int:pk>/pdf/', views.almanaque_gerar_pdf, name='almanaque_gerar_pdf'),
    path('almanaques/<int:pk>/assinar/', views.almanaque_assinatura_create, name='almanaque_assinatura_create'),
    path('almanaques/<int:pk>/retirar-assinatura/<int:assinatura_pk>/', views.almanaque_assinatura_delete, name='almanaque_assinatura_delete'),
    path('almanaques/<int:pk>/excluir/', views.almanaque_delete, name='almanaque_delete'),
    path('almanaques/<int:pk>/editar/', views.almanaque_edit, name='almanaque_edit'),
    path('almanaque/preview/', views.almanaque_preview, name='almanaque_preview'),
    path('almanaque/gerar-pdf-preview/', views.almanaque_gerar_pdf_preview, name='almanaque_gerar_pdf_preview'),
    path('usuario/welcome/', welcome_usuario, name='welcome_usuario'),
    path('usuario/ficha/', redirect_usuario_ficha, name='redirect_usuario_ficha'),
    path('usuario/mark-welcome-shown/', mark_welcome_shown, name='mark_welcome_shown'),
    
    # Chat em Tempo Real
    path('chat/', views_chat.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views_chat.chat_detail, name='chat_detail'),
    path('chat/iniciar/<int:usuario_id>/', views_chat.chat_iniciar, name='chat_iniciar'),
    path('chat/<int:chat_id>/enviar/', views_chat.chat_enviar_mensagem, name='chat_enviar_mensagem'),
    path('chat/<int:chat_id>/enviar-audio/', views_chat.chat_enviar_audio, name='chat_enviar_audio'),
    path('chat/<int:chat_id>/excluir/', views_chat.chat_delete, name='chat_delete'),
    path('chat/<int:chat_id>/mensagem/<int:mensagem_id>/deletar/', views_chat.chat_deletar_mensagem, name='chat_deletar_mensagem'),
    path('api/chat/<int:chat_id>/mensagens/', views_chat.chat_api_mensagens, name='chat_api_mensagens'),
    path('api/chat/<int:chat_id>/status-leitura/', views_chat.chat_api_status_leitura, name='chat_api_status_leitura'),
    path('api/chat/<int:chat_id>/chamada/iniciar/', views_chat.chat_chamada_iniciar, name='chat_chamada_iniciar'),
    path('api/chat/<int:chat_id>/chamada/aceitar/', views_chat.chat_chamada_aceitar, name='chat_chamada_aceitar'),
    path('api/chat/<int:chat_id>/chamada/pendente/', views_chat.chat_chamada_pendente, name='chat_chamada_pendente'),
    path('api/chat/chamada/pendente/todas/', views_chat.chat_chamada_pendente_todas, name='chat_chamada_pendente_todas'),
    path('api/chat/<int:chat_id>/chamada/<int:chamada_id>/status/', views_chat.chat_chamada_status, name='chat_chamada_status'),
    path('api/chat/<int:chat_id>/chamada/<int:chamada_id>/finalizar/', views_chat.chat_chamada_finalizar, name='chat_chamada_finalizar'),
    path('api/chat/<int:chat_id>/chamada/<int:chamada_id>/rejeitar/', views_chat.chat_chamada_rejeitar, name='chat_chamada_rejeitar'),
    path('api/chat/<int:chat_id>/chamada/<int:chamada_id>/cancelar/', views_chat.chat_chamada_cancelar, name='chat_chamada_cancelar'),
    path('api/chat/chats/', views_chat.chat_api_chats, name='chat_api_chats'),
    path('api/chat/status-online/<int:usuario_id>/', views_chat.chat_api_status_online, name='chat_api_status_online'),
    path('api/chat/usuarios/', views_chat.chat_api_usuarios, name='chat_api_usuarios'),
    
    # Militares
    path('militares/', views_simples.militar_list_simples, name='militar_list'),
    path('militares-nvrr/', views_simples.nvrr_list, name='nvrr_list'),
    path('militares-original/', views.militar_list, name='militar_list_original'),
    path('militares/sincronizar-situacoes/', views_simples.sincronizar_situacoes_militares, name='sincronizar_situacoes_militares'),
    
    # Redirecionamento para compatibilidade (militar singular -> militares plural)
    path('militar/<int:pk>/', lambda request, pk: redirect('militares:militar_detail', pk=pk)),
    path('militares/exportar-excel/', views.exportar_militares_excel, name='exportar_excel'),

    path('militares/novo/', views.militar_create, name='militar_create'),
    path('militares/<int:pk>/', views.militar_detail, name='militar_detail'),
    path('militares/<int:pk>/promocoes-pdf/', views.militar_promocoes_pdf, name='militar_promocoes_pdf'),
    path('militares/<int:militar_id>/tempo-servico/certidao/pdf/', views.tempo_servico_certidao_pdf, name='tempo_servico_certidao_pdf'),
    path('militares/<int:pk>/editar/', views.militar_update, name='militar_edit'),
    path('militares/<int:pk>/excluir/', views.militar_delete, name='militar_delete'),
    path('minha-ficha/', views.militar_detail_pessoal, name='militar_detail_pessoal'),

    
    # Militares Inativos
    path('militares-inativos/', views.militar_inativo_list, name='militar_inativo_list'),
    path('militares-inativos/<int:pk>/', views.militar_inativo_detail, name='militar_inativo_detail'),
    path('militares/<int:pk>/transferir-inativo/', views.militar_transferir_inativo, name='militar_transferir_inativo'),
    path('militares-inativos/<int:pk>/reativar/', views.militar_reativar, name='militar_reativar'),
    
    # Fichas de Conceito
    path('fichas-conceito/', views.ficha_conceito_list, name='ficha_conceito_list'),
    path('fichas-conceito/gerar-todos/', views.gerar_fichas_conceito_todos, name='gerar_fichas_conceito_todos'),
    path('fichas-conceito/limpar-pontos/', views.limpar_pontos_fichas_conceito, name='limpar_pontos_fichas_conceito'),
    path('fichas-conceito/nova/', views.ficha_conceito_create, name='ficha_conceito_create'),
    path('militares/<int:militar_pk>/ficha-conceito/', views.ficha_conceito_form, name='ficha_conceito_form'),
    path('ficha-conceito/<int:pk>/editar/', views.ficha_conceito_edit, name='ficha_conceito_edit'),
    path('ficha-conceito/<int:pk>/', views.ficha_conceito_detail, name='ficha_conceito_detail'),
    path('ficha-conceito/<int:pk>/conferir/', views.conferir_ficha, name='conferir_ficha'),
    path('ficha-conceito/<int:pk>/excluir/', views.ficha_conceito_delete, name='ficha_conceito_delete'),
    
    # Documentos
    path('ficha-conceito/<int:ficha_pk>/documento/', views.documento_upload, name='documento_upload'),
    path('documento/<int:pk>/conferir/', views.conferir_documento, name='conferir_documento'),
    path('documento/<int:pk>/excluir/', views.documento_delete, name='documento_delete'),
    path('quadros-acesso/<int:pk>/assinar-documentos/', views.assinar_documentos_quadro, name='assinar_documentos_quadro'),
    path('documento/<int:pk>/assinar/', views.assinar_documento, name='assinar_documento'),
    path('quadros-acesso/<int:pk>/assinar/', views.assinar_quadro_acesso, name='assinar_quadro_acesso'),
    path('quadros-acesso/<int:pk>/retirar-assinatura/<int:assinatura_pk>/', views.retirar_assinatura_quadro_acesso, name='retirar_assinatura_quadro_acesso'),
    
    # Quadros de Acesso
    path('quadros-acesso/', views.quadro_acesso_list, name='quadro_acesso_list'),
    path('quadros-acesso/<int:pk>/', views.quadro_acesso_detail, name='quadro_acesso_detail'),
    path('quadros-acesso/<int:pk>/editar/', views.quadro_acesso_edit, name='quadro_acesso_edit'),
    path('quadros-acesso/<int:pk>/pdf/', views.quadro_acesso_pdf, name='quadro_acesso_pdf'),
    path('quadros-acesso/<int:pk>/imprimir/', views.quadro_acesso_print, name='quadro_acesso_print'),
    path('quadros-acesso/<int:pk>/adicionar-oficial/', views.adicionar_oficial_quadro_oficiais, name='adicionar_oficial_quadro_oficiais'),
    path('quadros-acesso/<int:pk>/remover-militar/<int:militar_id>/', views.remover_militar_quadro_oficiais, name='remover_militar_quadro_oficiais'),
    path('gerar-quadro-acesso/', views.gerar_quadro_acesso, name='gerar_quadro_acesso'),
    path('regerar-quadro-acesso/<int:pk>/', views.regerar_quadro_acesso, name='regerar_quadro_acesso'),
    path('delete-quadro-acesso/<int:pk>/', views.delete_quadro_acesso, name='delete_quadro_acesso'),
    path('homologar-quadro-acesso/<int:pk>/', views.homologar_quadro_acesso, name='homologar_quadro_acesso'),
    path('deshomologar-quadro-acesso/<int:pk>/', views.deshomologar_quadro_acesso, name='deshomologar_quadro_acesso'),
    path('elaborar-quadro-acesso/<int:pk>/', views.elaborar_quadro_acesso, name='elaborar_quadro_acesso'),
    path('marcar-nao-elaborado/<int:pk>/', views.marcar_nao_elaborado, name='marcar_nao_elaborado'),
    path('quadro-acesso/<int:pk>/relatorio-requisitos/', views.relatorio_requisitos_quadro, name='relatorio_requisitos_quadro'),
    
    # Quadros de Acesso Unificados
    path('quadros-acesso-unificado/', views_unificadas.quadro_acesso_unificado_list, name='quadro_acesso_unificado_list'),
    path('quadros-acesso-unificado/gerar/', views_unificadas.gerar_quadro_acesso_unificado, name='gerar_quadro_acesso_unificado'),
    
    # Promoções
    path('promocoes/', views.promocao_list, name='promocao_list'),
    path('promocoes/nova/', views.promocao_create, name='promocao_create'),
    path('promocoes/historica/', views.promocao_historica_create, name='promocao_historica_create'),
    path('promocoes/<int:pk>/', views.promocao_detail, name='promocao_detail'),
    path('promocoes/<int:pk>/editar/', views.promocao_update, name='promocao_update'),
    path('promocoes/<int:pk>/excluir/', views.promocao_delete, name='promocao_delete'),
    
    # Vagas

    path('vagas/nova/', views.vaga_create, name='vaga_create'),
    
    # Busca AJAX
    path('busca-militares/', views.militar_search_ajax, name='militar_search_ajax'),
    path('buscar-oficiais-elegiveis/', views.buscar_oficiais_elegiveis, name='buscar_oficiais_elegiveis'),
    path('buscar-usuarios/', views.buscar_usuarios_ajax, name='buscar_usuarios_ajax'),
    path('proxima-numeracao/', views.proxima_numeracao_disponivel, name='proxima_numeracao_disponivel'),
    path('reordenar-numeracoes/', views.reordenar_numeracoes_view, name='reordenar_numeracoes'),
    path('aplicar-promocao/', views.aplicar_promocao_view, name='aplicar_promocao'),
    path('promocao-subtenente/', views.promocao_subtenente_view, name='promocao_subtenente'),
    path('buscar-funcao-militar/', views.buscar_funcao_militar, name='buscar_funcao_militar'),
    path('buscar-funcoes-usuario/', views.buscar_funcoes_usuario, name='buscar_funcoes_usuario'),
    path('selecionar-funcao/', views.selecionar_funcao, name='selecionar_funcao'),
    path('trocar-funcao-ajax/', views.trocar_funcao_ajax, name='trocar_funcao_ajax'),
    path('sincronizar-funcoes/', views.sincronizar_funcoes_todos_militares, name='sincronizar_funcoes'),
    
    # Autenticação
    path('register/', views.register, name='register'),
    
    # Interstícios
    path('intersticios/', views.intersticio_list, name='intersticio_list'),
    path('intersticios/gerenciar/', views.intersticio_manage, name='intersticio_manage'),
    path('intersticios/criar/', views.intersticio_create, name='intersticio_create'),
    path('intersticios/<int:pk>/excluir/', views.intersticio_delete, name='intersticio_delete'),
    
    # Órgãos
    path('orgaos/', views.orgao_list, name='orgao_list'),
    path('orgaos/criar/', views.orgao_create, name='orgao_create'),
    path('orgaos/<int:pk>/', views.orgao_detail, name='orgao_detail'),
    path('orgaos/<int:pk>/editar/', views.orgao_update, name='orgao_update'),
    path('orgaos/<int:pk>/excluir/', views.orgao_delete, name='orgao_delete'),
    
    # Organograma
    path('organograma/', views.organograma_view, name='organograma'),
    
    # Grandes Comandos
    path('grandes-comandos/', views.grande_comando_list, name='grande_comando_list'),
    path('grandes-comandos/criar/', views.grande_comando_create, name='grande_comando_create'),
    path('grandes-comandos/<int:pk>/', views.grande_comando_detail, name='grande_comando_detail'),
    path('grandes-comandos/<int:pk>/editar/', views.grande_comando_update, name='grande_comando_update'),
    path('grandes-comandos/<int:pk>/excluir/', views.grande_comando_delete, name='grande_comando_delete'),
    
    # Unidades
    path('unidades/', views.unidade_list, name='unidade_list'),
    path('unidades/criar/', views.unidade_create, name='unidade_create'),
    path('unidades/<int:pk>/', views.unidade_detail, name='unidade_detail'),
    path('unidades/<int:pk>/editar/', views.unidade_update, name='unidade_update'),
    path('unidades/<int:pk>/excluir/', views.unidade_delete, name='unidade_delete'),
    
    # Sub-Unidades
    path('sub-unidades/', views.sub_unidade_list, name='sub_unidade_list'),
    path('sub-unidades/criar/', views.sub_unidade_create, name='sub_unidade_create'),
    path('sub-unidades/<int:pk>/', views.sub_unidade_detail, name='sub_unidade_detail'),
    path('sub-unidades/<int:pk>/editar/', views.sub_unidade_update, name='sub_unidade_update'),
    path('sub-unidades/<int:pk>/excluir/', views.sub_unidade_delete, name='sub_unidade_delete'),
    
    # Previsão de Vagas

    path('previsao-vagas/gerenciar/', views.previsao_vaga_manage, name='previsao_vaga_manage'),
    path('previsao-vagas/criar/', views.previsao_vaga_create, name='previsao_vaga_create'),
    path('previsao-vagas/<int:pk>/excluir/', views.previsao_vaga_delete, name='previsao_vaga_delete'),
    path('previsao-vagas/<int:pk>/excluir-ajax/', views.previsao_vaga_delete_ajax, name='previsao_vaga_delete_ajax'),
    
    # Cursos Inerentes
    path('militares/<int:militar_pk>/marcar-cursos-inerentes/', views.marcar_cursos_inerentes, name='marcar_cursos_inerentes'),
    
    # Test Template
    path('test-template/', views.test_template, name='test_template'),
    
    # Teste Modal Bootstrap
    path('teste-modal/', views.teste_modal, name='teste_modal'),
    path('teste-ficha-conceito-modal/', views.teste_ficha_conceito_modal, name='teste_ficha_conceito_modal'),
    path('teste-modal-debug/', views.teste_modal_debug, name='teste_modal_debug'),
    path('teste-modal-simples/', views.teste_modal_simples, name='teste_modal_simples'),
    
    # Relatório de Aptos à Promoção
    path('relatorio-aptos-promocao/', views.relatorio_aptos_promocao, name='relatorio_aptos_promocao'),

    # Medalhas - Concessões Individuais
    path('medalhas/', views_medalhas.concessoes_list, name='concessoes_list'),
    path('medalhas/<int:pk>/cancelar/', views_medalhas.cancelar_concessao, name='cancelar_concessao'),
    path('medalhas/<int:pk>/deletar/', views_medalhas.deletar_concessao, name='deletar_concessao'),
    path('medalhas/<int:pk>/editar/', views_medalhas.editar_concessao, name='editar_concessao'),
    path('medalhas/<int:pk>/confirmar-outorga/', views_medalhas.confirmar_outorga, name='confirmar_outorga'),
    path('medalhas/<int:pk>/reverter-proposta/', views_medalhas.reverter_proposta, name='reverter_proposta'),
    path('medalhas/confirmar-outorga-em-lote/', views_medalhas.confirmar_outorga_em_lote, name='confirmar_outorga_em_lote'),
    path('medalhas/elegiveis/tempo-servico/', views_medalhas.elegiveis_tempo_servico, name='elegiveis_tempo_servico'),
    path('medalhas/conceder/militar/', views_medalhas.conceder_medalha_militar, name='conceder_medalha_militar'),
    path('medalhas/conceder/externo/', views_medalhas.conceder_medalha_externo, name='conceder_medalha_externo'),
    path('medalhas/configurar-pdf/', views_medalhas.configurar_pdf_medalhas, name='configurar_pdf_medalhas'),
    path('medalhas/pdf/', views_medalhas.concessoes_pdf, name='concessoes_pdf'),
    path('medalhas/<int:pk>/assinar/', views_medalhas.assinar_concessao_medalha, name='assinar_concessao_medalha'),
    path('medalhas/<int:pk>/retirar-assinatura/<int:assinatura_pk>/', views_medalhas.retirar_assinatura_concessao_medalha, name='retirar_assinatura_concessao_medalha'),
    
    # Medalhas - Propostas (Reorganizado)
    path('medalhas/propostas/', views_medalhas.lista_propostas, name='lista_propostas'),
    path('medalhas/propostas/salvar/', views_medalhas.salvar_proposta, name='salvar_proposta'),
    path('medalhas/propostas/teste/', views_medalhas.lista_propostas_teste, name='lista_propostas_teste'),
    path('medalhas/propostas/<int:pk>/', views_medalhas.visualizar_proposta, name='visualizar_proposta'),
    path('medalhas/propostas/<int:pk>/pdf/', views_medalhas.proposta_pdf, name='proposta_pdf'),
    path('medalhas/propostas/<int:pk>/assinar/', views_medalhas.assinar_proposta_medalha, name='assinar_proposta_medalha'),
    path('medalhas/propostas/<int:pk>/retirar-assinatura/<int:assinatura_pk>/', views_medalhas.retirar_assinatura_proposta_medalha, name='retirar_assinatura_proposta_medalha'),
    path('medalhas/propostas/<int:pk>/excluir/', views_medalhas.excluir_proposta_medalha, name='excluir_proposta_medalha'),
    path('medalhas/propostas/teste/<int:pk>/', views_medalhas.visualizar_proposta_teste, name='visualizar_proposta_teste'),
    
    # API para Medalhas
    path('api/buscar-militares/', views_medalhas.buscar_militares_api, name='buscar_militares_api'),
    
    # Test Quadro Simple
    path('test-quadro-simple/', views.test_quadro_simple, name='test_quadro_simple'),
    


    # Comissão de Promoções de Oficiais
    path('comissao/', views.comissao_list, name='comissao_list'),
    path('comissao/nova/', views.comissao_create, name='comissao_create'),
    path('comissao/<int:pk>/', views.comissao_detail, name='comissao_detail'),
    path('comissao/<int:pk>/editar/', views.comissao_update, name='comissao_update'),
    path('comissao/<int:pk>/excluir/', views.comissao_delete, name='comissao_delete'),
    path('comissao/<int:pk>/pdf/', views.comissao_pdf, name='comissao_pdf'),
    path('comissao/<int:pk>/encerrar/', views.comissao_encerrar, name='comissao_encerrar'),

    
    # Membros da Comissão
    path('comissao/<int:comissao_pk>/membros/', views.membro_comissao_list, name='membro_comissao_list'),
    path('comissao/<int:comissao_pk>/membros/sincronizar/', views.sincronizar_membros_comissao, name='sincronizar_membros_comissao'),
    path('comissao/<int:comissao_pk>/membros/adicionar/', views.membro_comissao_add, name='membro_comissao_add'),
    path('comissao/<int:comissao_pk>/membros/<int:pk>/editar/', views.membro_comissao_update, name='membro_comissao_update'),
    path('comissao/<int:comissao_pk>/membros/<int:pk>/excluir/', views.membro_comissao_delete, name='membro_comissao_delete'),
    path('comissao/membros/autocomplete/', views.membro_comissao_autocomplete, name='membro_comissao_autocomplete'),
    
    # Sessões da Comissão
    path('comissao/sessoes/', views.sessao_comissao_list, name='sessao_comissao_list'),
    path('comissao/sessoes/nova/', views.sessao_comissao_create, name='sessao_comissao_create'),
    path('comissao/sessoes/<int:pk>/', views.sessao_comissao_detail, name='sessao_comissao_detail'),
    path('comissao/sessoes/<int:pk>/editar/', views.sessao_comissao_update, name='sessao_comissao_update'),
    path('comissao/sessoes/<int:pk>/excluir/', views.sessao_comissao_delete, name='sessao_comissao_delete'),
    path('comissao/sessoes/<int:sessao_pk>/presenca/', views.presenca_sessao_update, name='presenca_sessao_update'),
    path('comissao/sessoes/<int:pk>/encerrar/', views.sessao_encerrar, name='sessao_encerrar'),
    path('comissao/sessoes/<int:pk>/ata/', views.sessao_gerar_ata, name='sessao_gerar_ata'),
    path('comissao/sessoes/<int:pk>/pdf-completo/', sessao_gerar_pdf_completo, name='sessao_gerar_pdf_completo'),
    path('comissao/sessoes/<int:pk>/upload-arquivos/', upload_arquivos_sessao, name='upload_arquivos_sessao'),
    path('testar-pdf/', testar_pdf, name='testar_pdf'),
    path('comissao/sessoes/<int:pk>/editar-ata/', views.sessao_editar_ata, name='sessao_editar_ata'),
    path('comissao/sessoes/<int:pk>/editar-ata-popup/', views.sessao_editar_ata_popup, name='sessao_editar_ata_popup'),

    path('comissao/sessoes/<int:pk>/ata-conteudo/', views.ata_conteudo_ajax, name='ata_conteudo_ajax'),
    path('comissao/sessoes/<int:pk>/ata-para-assinatura/', views.ata_para_assinatura, name='ata_para_assinatura'),
    path('comissao/sessoes/<int:pk>/ata-assinaturas/', views.ata_assinaturas, name='ata_assinaturas'),

    path('comissao/sessoes/<int:pk>/membros-ajax/', views_ajax_atas.membros_comissao_ajax, name='membros_comissao_ajax'),
    path('comissao/sessoes/<int:pk>/assinaturas-ajax/', views_ajax_atas.assinaturas_existentes_ajax, name='assinaturas_existentes_ajax'),
    path('comissao/sessoes/assinar-ata-ajax/', views_ajax_atas.assinar_ata_ajax, name='assinar_ata_ajax'),
    path('comissao/sessoes/<int:pk>/deletar-ata-ajax/', views_ajax_atas.deletar_ata_ajax, name='deletar_ata_ajax'),

    path('comissao/sessoes/<int:pk>/ata-gerar-pdf/', views.ata_gerar_pdf, name='ata_gerar_pdf'),
    path('comissao/sessoes/<int:pk>/ata-finalizar/', views.ata_finalizar, name='ata_finalizar'),
    path('comissao/sessoes/<int:pk>/assinar-ata-html/', views.assinar_ata_html, name='assinar_ata_html'),
    path('comissao/sessoes/<int:pk>/assinar-ata-sessao/', views.assinar_ata_html, name='assinar_ata_sessao'),
    path('comissao/sessoes/<int:pk>/retirar-assinatura-ata/<int:assinatura_pk>/', views.retirar_assinatura_ata, name='retirar_assinatura_ata'),
    
    # Deliberações da Comissão
    path('comissao/deliberacoes/nova/', views.deliberacao_comissao_create, name='deliberacao_comissao_create'),
    path('comissao/deliberacoes/<int:pk>/editar/', views.deliberacao_comissao_update, name='deliberacao_comissao_update'),
    path('comissao/deliberacoes/<int:pk>/resultado/', views.deliberacao_resultado_update, name='deliberacao_resultado_update'),
    path('comissao/deliberacoes/<int:deliberacao_pk>/votos/', views.voto_deliberacao_create, name='voto_deliberacao_create'),
    path('comissao/deliberacoes/<int:deliberacao_pk>/votos/editor/', views.voto_deliberacao_editor_popup, name='voto_deliberacao_editor_popup'),
    path('comissao/deliberacoes/votos/<int:voto_pk>/excluir/', views.voto_deliberacao_delete, name='voto_deliberacao_delete'),
    path('comissao/deliberacoes/resultado/<int:sessao_pk>/', views.deliberacao_comissao_resultado, name='deliberacao_comissao_resultado'),
    
    # Gerenciamento de Votos do Usuário
    path('meus-votos/', views.meus_votos_list, name='meus_votos_list'),
    path('meus-votos/<int:pk>/', redirect_voto_detail, name='meu_voto_detail'),
    path('meus-votos/<int:pk>/editar/', views.meu_voto_update, name='meu_voto_update'),
    path('meus-votos/<int:pk>/excluir/', views.meu_voto_delete, name='meu_voto_delete'),
    path('meus-votos/<int:pk>/pdf/', views.voto_deliberacao_pdf, name='voto_deliberacao_pdf'),
    path('meus-votos/<int:pk>/visualizar/', views.voto_visualizar_assinar, name='voto_visualizar_assinar'),
    path('meus-votos/<int:pk>/assinar/', views.assinar_voto, name='assinar_voto'),
    
    # Documentos da Sessão
    path('comissao/documentos/upload/', views.documento_sessao_create, name='documento_sessao_create'),
    path('comissao/documentos/<int:pk>/editar/', views.documento_sessao_update, name='documento_sessao_update'),
    path('comissao/documentos/<int:pk>/excluir/', views.documento_sessao_delete, name='documento_sessao_delete'),
    path('comissao/documentos/<int:pk>/visualizar/', views.documento_sessao_view, name='documento_sessao_view'),
    path('comissao/documentos/<int:pk>/download/', views.documento_sessao_download, name='documento_sessao_download'),
    
    # Modelos de Ata
    path('modelos-ata/', views.modelo_ata_list, name='modelo_ata_list'),
    path('modelos-ata/novo/', views.modelo_ata_create, name='modelo_ata_create'),
    path('modelos-ata/<int:pk>/', views.modelo_ata_detail, name='modelo_ata_detail'),
    path('modelos-ata/<int:pk>/editar/', views.modelo_ata_update, name='modelo_ata_update'),
    path('modelos-ata/<int:pk>/excluir/', views.modelo_ata_delete, name='modelo_ata_delete'),
    path('comissao/sessoes/<int:sessao_pk>/aplicar-modelo/', views.modelo_ata_aplicar, name='modelo_ata_aplicar'),
    path('comissao/sessoes/<int:sessao_pk>/salvar-como-modelo/', views.modelo_ata_salvar_atual, name='modelo_ata_salvar_atual'),
    
    # Notificações
    path('notificacoes/', views.notificacoes_list, name='notificacoes_list'),
    path('notificacoes/<int:pk>/marcar-lida/', views.notificacao_marcar_lida, name='notificacao_marcar_lida'),
    path('notificacoes/marcar-todas-lidas/', views.notificacao_marcar_todas_lidas, name='notificacao_marcar_todas_lidas'),
    path('notificacoes/<int:pk>/excluir/', views.notificacao_delete, name='notificacao_delete'),
    path('api/notificacoes/nao-lidas/', views.notificacoes_api_nao_lidas, name='notificacoes_api_nao_lidas'),
    
    # Cargos da Comissão
    path('comissao/cargos/', views.cargo_comissao_list, name='cargo_comissao_list'),
    path('comissao/cargos/novo/', views.cargo_comissao_create, name='cargo_comissao_create'),
    path('comissao/cargos/<int:pk>/editar/', views.cargo_comissao_update, name='cargo_comissao_update'),
    path('comissao/cargos/<int:pk>/excluir/', views.cargo_comissao_delete, name='cargo_comissao_delete'),

    # Quadros de Fixação de Vagas
    path('quadros-fixacao-vagas/', views.quadro_fixacao_vagas_list, name='quadro_fixacao_vagas_list'),
    path('quadros-fixacao-vagas/novo/', views.quadro_fixacao_vagas_create, name='quadro_fixacao_vagas_create'),
    path('quadros-fixacao-vagas/<int:pk>/', views.quadro_fixacao_vagas_detail, name='quadro_fixacao_vagas_detail'),
    path('quadros-fixacao-vagas/<int:pk>/visualizar/', views.quadro_fixacao_vagas_pdf_view, name='quadro_fixacao_vagas_pdf_view'),
    path('quadros-fixacao-vagas/<int:pk>/visualizar-html/', views.quadro_fixacao_vagas_visualizar_html, name='quadro_fixacao_vagas_visualizar_html'),
    path('quadros-fixacao-vagas/<int:pk>/pdf/', views.quadro_fixacao_vagas_pdf, name='quadro_fixacao_vagas_pdf'),
    path('quadros-fixacao-vagas/<int:pk>/assinar/', views.assinar_quadro_fixacao_vagas, name='assinar_quadro_fixacao_vagas'),
    path('quadros-fixacao-vagas/<int:pk>/retirar-assinatura/<int:assinatura_pk>/', views.retirar_assinatura_quadro_fixacao_vagas, name='retirar_assinatura_quadro_fixacao_vagas'),
    path('quadros-fixacao-vagas/<int:pk>/excluir/', views.quadro_fixacao_vagas_delete, name='quadro_fixacao_vagas_delete'),
    path('quadros-fixacao-vagas/<int:pk>/editar/', views.quadro_fixacao_vagas_update, name='quadro_fixacao_vagas_update'),

    # Quadros de Fixação de Vagas para Oficiais
    path('quadros-fixacao-vagas-oficiais/novo/', views.quadro_fixacao_vagas_oficiais_create, name='quadro_fixacao_vagas_oficiais_create'),
    path('quadros-fixacao-vagas-oficiais/<int:pk>/', views.quadro_fixacao_vagas_oficiais_detail, name='quadro_fixacao_vagas_oficiais_detail'),
    path('quadros-fixacao-vagas-oficiais/<int:pk>/editar/', views.quadro_fixacao_vagas_oficiais_update, name='quadro_fixacao_vagas_oficiais_update'),
    path('quadros-fixacao-vagas-oficiais/<int:pk>/excluir/', views.quadro_fixacao_vagas_oficiais_delete, name='quadro_fixacao_vagas_oficiais_delete'),
    
    # Praças - Fichas de Conceito
    path('pracas/fichas-conceito/', views_pracas.ficha_conceito_pracas_list, name='ficha_conceito_pracas_list'),
    path('pracas/militares/<int:militar_pk>/ficha-conceito/', views_pracas.ficha_conceito_pracas_form, name='ficha_conceito_pracas_form'),
    path('pracas/fichas-conceito/gerar-todos/', views_pracas.gerar_fichas_conceito_pracas_todos, name='gerar_fichas_conceito_pracas_todos'),
    path('pracas/fichas-conceito/limpar-pontos/', views_pracas.limpar_pontos_fichas_conceito_pracas, name='limpar_pontos_fichas_conceito_pracas'),
    
    # Títulos de Publicações
    path('titulos-publicacao/', views_pracas.titulos_publicacao_list, name='titulos_publicacao_list'),
    path('titulos-publicacao/novo/', views_pracas.titulo_publicacao_create, name='titulo_publicacao_create'),
    path('titulos-publicacao/<int:pk>/editar/', views_pracas.titulo_publicacao_edit, name='titulo_publicacao_edit'),
    path('titulos-publicacao/<int:pk>/excluir/', views_pracas.titulo_publicacao_delete, name='titulo_publicacao_delete'),
    path('titulos-publicacao/reordenar/', views_pracas.titulos_publicacao_reordenar, name='titulos_publicacao_reordenar'),
    
    # Publicações - URLs Gerais (removidas - usar listas específicas)
    
    # Publicações - URLs Específicas por Tipo
    # Notas
    path('notas/', views_publicacoes.notas_list, name='notas_list'),
    path('notas/novo/', views_publicacoes.notas_create, name='notas_create'),
    path('notas/<int:pk>/', views_publicacoes.nota_detail, name='nota_detail'),
    path('notas/<int:pk>/visualizar/', views_publicacoes.nota_visualizar, name='nota_visualizar'),
    path('notas/<int:pk>/modal-content/', views_publicacoes.nota_modal_content, name='nota_modal_content'),
    path('notas/<int:pk>/editar/', views_publicacoes.nota_edit, name='nota_edit'),
    path('notas/<int:pk>/publicar-boletim/', views_publicacoes.nota_publicar_boletim, name='nota_publicar_boletim'),
    path('notas/<int:pk>/excluir/', views_publicacoes.nota_delete, name='nota_delete'),
    path('notas/reordenar/', views_publicacoes.reordenar_notas, name='reordenar_notas'),
    path('notas/corrigir-formatos/', views_publicacoes.corrigir_formatos_notas, name='corrigir_formatos_notas'),
    
    # Assinaturas de Notas
    path('notas/<int:pk>/dados-assinatura/', views_assinaturas_notas.dados_assinatura_nota, name='dados_assinatura_nota'),
    path('notas/<int:pk>/assinar-revisao/', views_assinaturas_notas.assinar_nota_revisao, name='assinar_nota_revisao'),
    path('notas/<int:pk>/assinar-aprovacao/', views_assinaturas_notas.assinar_nota_aprovacao, name='assinar_nota_aprovacao'),
    path('notas/<int:pk>/assinar-edicao/', views_assinaturas_notas.assinar_nota_edicao, name='assinar_nota_edicao'),
    path('notas/<int:pk>/devolver/', views_publicacoes.devolver_nota, name='devolver_nota'),
    path('notas-reservadas/<int:pk>/devolver/', views_boletins_reservados.devolver_nota_reservada, name='devolver_nota_reservada'),
    path('notas/<int:pk>/arquivar/', views_publicacoes.arquivar_nota, name='arquivar_nota'),
    path('notas/<int:pk>/transferir/', views_assinaturas_notas.transferir_nota, name='transferir_nota'),
    path('notas/<int:pk>/editar-modal/', views_assinaturas_notas.editar_nota_modal, name='editar_nota_modal'),
    path('notas/<int:pk>/dados-devolucao/', views_assinaturas_notas.dados_devolucao_nota, name='dados_devolucao_nota'),
    path('notas/<int:pk>/retirar-assinatura/<int:assinatura_pk>/', views_assinaturas_notas.retirar_assinatura_nota, name='retirar_assinatura_nota'),
    path('notas/<int:pk>/gerar-pdf/', views_assinaturas_notas.nota_gerar_pdf, name='nota_gerar_pdf'),
    
    # Modelos de Notas
    path('modelos-notas/', views_modelos_notas.modelos_notas_list, name='modelos_notas_list'),
    path('modelos-notas/novo/', views_modelos_notas.modelo_nota_create, name='modelo_nota_create'),
    path('modelos-notas/<int:pk>/', views_modelos_notas.modelo_nota_detail, name='modelo_nota_detail'),
    path('modelos-notas/<int:pk>/editar/', views_modelos_notas.modelo_nota_edit, name='modelo_nota_edit'),
    path('modelos-notas/<int:pk>/excluir/', views_modelos_notas.modelo_nota_delete, name='modelo_nota_delete'),
    path('ajax/modelos-notas/', views_modelos_notas.ajax_modelos_notas, name='ajax_modelos_notas'),
    path('ajax/modelos-notas/<int:pk>/', views_modelos_notas.ajax_modelo_nota_detail, name='ajax_modelo_nota_detail'),
    
    # Boletins Ostensivos
    path('boletins-ostensivos/', views_publicacoes.boletins_ostensivos_list, name='boletins_ostensivos_list'),
    path('boletins-ostensivos/novo/', views_publicacoes.boletins_ostensivos_create, name='boletins_ostensivos_create'),
    path('boletins-ostensivos/<int:pk>/', views_publicacoes.boletim_ostensivo_detail, name='boletim_ostensivo_detail'),
    path('boletins-ostensivos/<int:boletim_pk>/adicionar-nota/<int:nota_pk>/', views_publicacoes.adicionar_nota_boletim, name='adicionar_nota_boletim'),
    path('boletins-ostensivos/<int:boletim_pk>/remover-nota/<int:nota_pk>/', views_publicacoes.remover_nota_boletim, name='remover_nota_boletim'),
    path('boletins-ostensivos/<int:pk>/disponibilizar/', views_publicacoes.disponibilizar_boletim, name='disponibilizar_boletim'),
    path('boletins-ostensivos/<int:pk>/retornar/', views_publicacoes.retornar_boletim_ostensivo, name='retornar_boletim_ostensivo'),
    path('boletins-ostensivos/<int:pk>/deletar/', views_publicacoes.deletar_boletim_ostensivo, name='deletar_boletim_ostensivo'),
    path('boletins-ostensivos/<int:pk>/visualizar/', views_publicacoes.boletim_ostensivo_visualizar, name='boletim_ostensivo_visualizar'),
    path('boletins-ostensivos/<int:pk>/dados-assinatura/', views_assinaturas_boletim.dados_assinatura_boletim, name='dados_assinatura_boletim'),
    path('boletins-ostensivos/<int:pk>/pdf/', views_boletim_pdf.boletim_gerar_pdf, name='boletim_gerar_pdf'),
    
    # Assinaturas de Boletim
    path('boletins-ostensivos/<int:pk>/assinaturas/', views_assinaturas_boletim.assinaturas_boletim, name='assinaturas_boletim'),
    path('boletins-ostensivos/<int:pk>/assinar/', views_assinaturas_boletim.assinar_boletim, name='assinar_boletim'),
    path('boletins-ostensivos/<int:pk>/retirar-assinatura/<int:assinatura_pk>/', views_assinaturas_boletim.retirar_assinatura_boletim, name='retirar_assinatura_boletim'),
    
    # AJAX para boletins
    path('ajax/verificar-boletim-hoje/', views_publicacoes.ajax_verificar_boletim_hoje, name='ajax_verificar_boletim_hoje'),
    path('ajax/proximo-numero-boletim/', views_publicacoes.ajax_proximo_numero_boletim, name='ajax_proximo_numero_boletim'),
    path('ajax/notas-disponiveis-boletim/', views_publicacoes.ajax_notas_disponiveis_boletim, name='ajax_notas_disponiveis_boletim'),
    path('ajax/notas-incluidas-boletim/', views_publicacoes.ajax_notas_incluidas_boletim, name='ajax_notas_incluidas_boletim'),
    path('ajax/assinaturas-boletim/', views_publicacoes.ajax_assinaturas_boletim, name='ajax_assinaturas_boletim'),
    path('ajax/boletins-disponiveis/', views_publicacoes.ajax_boletins_disponiveis, name='ajax_boletins_disponiveis'),
    
    # Boletins Reservados
    path('boletins-reservados/', views_boletins_reservados.boletins_reservados_list, name='boletins_reservados_list'),
    path('boletins-reservados/novo/', views_boletins_reservados.boletins_reservados_create, name='boletins_reservados_create'),
    path('boletins-reservados/<int:pk>/', views_boletins_reservados.boletim_reservado_detail, name='boletim_reservado_detail'),
    path('boletins-reservados/<int:boletim_pk>/adicionar-nota/<int:nota_pk>/', views_boletins_reservados.adicionar_nota_boletim_reservado, name='adicionar_nota_boletim_reservado'),
    path('boletins-reservados/<int:boletim_pk>/remover-nota/<int:nota_pk>/', views_boletins_reservados.remover_nota_boletim_reservado, name='remover_nota_boletim_reservado'),
    path('boletins-reservados/<int:pk>/disponibilizar/', views_boletins_reservados.disponibilizar_boletim_reservado, name='disponibilizar_boletim_reservado'),
    path('boletins-reservados/<int:pk>/retornar/', views_boletins_reservados.retornar_boletim_reservado, name='retornar_boletim_reservado'),
    path('boletins-reservados/<int:pk>/deletar/', views_boletins_reservados.deletar_boletim_reservado, name='deletar_boletim_reservado'),
    path('boletins-reservados/<int:pk>/visualizar/', views_boletins_reservados.boletim_reservado_visualizar, name='boletim_reservado_visualizar'),
    
    # Assinaturas de Boletins Reservados
    path('boletins-reservados/<int:pk>/dados-assinatura/', views_boletins_reservados.dados_assinatura_boletim_reservado, name='dados_assinatura_boletim_reservado'),
    path('boletins-reservados/<int:pk>/assinaturas/', views_boletins_reservados.assinaturas_boletim_reservado, name='assinaturas_boletim_reservado'),
    path('boletins-reservados/<int:pk>/assinar/', views_boletins_reservados.assinar_boletim_reservado, name='assinar_boletim_reservado'),
    path('boletins-reservados/<int:pk>/retirar-assinatura/<int:assinatura_pk>/', views_boletins_reservados.retirar_assinatura_boletim_reservado, name='retirar_assinatura_boletim_reservado'),
    path('boletins-reservados/<int:pk>/pdf/', views_boletim_pdf.boletim_reservado_gerar_pdf, name='boletim_reservado_gerar_pdf'),
    
    # AJAX para boletins reservados
    path('ajax/verificar-boletim-reservado-hoje/', views_boletins_reservados.ajax_verificar_boletim_reservado_hoje, name='ajax_verificar_boletim_reservado_hoje'),
    path('ajax/proximo-numero-boletim-reservado/', views_boletins_reservados.ajax_proximo_numero_boletim_reservado, name='ajax_proximo_numero_boletim_reservado'),
    path('ajax/notas-disponiveis-boletim-reservado/<int:boletim_pk>/', views_boletins_reservados.ajax_notas_disponiveis_boletim_reservado, name='ajax_notas_disponiveis_boletim_reservado'),
    path('ajax/notas-incluidas-boletim-reservado/<int:boletim_pk>/', views_boletins_reservados.ajax_notas_incluidas_boletim_reservado, name='ajax_notas_incluidas_boletim_reservado'),
    path('ajax/boletins-reservados-disponiveis/', views_boletins_reservados.ajax_boletins_reservados_disponiveis, name='ajax_boletins_reservados_disponiveis'),
    
    # AJAX para boletins especiais
    path('ajax/notas-incluidas-boletim-especial/<int:boletim_pk>/', views_publicacoes.ajax_notas_incluidas_boletim_especial, name='ajax_notas_incluidas_boletim_especial'),
    
    # Notas Reservadas
    
    # AJAX para notas reservadas
    
    # URLs para assinaturas de notas reservadas
    
    # Boletins Especiais
    path('boletins-especiais/', views_publicacoes.boletins_especiais_list, name='boletins_especiais_list'),
    path('boletins-especiais/<int:pk>/disponibilizar/', views_publicacoes.disponibilizar_boletim_especial, name='disponibilizar_boletim_especial'),
    path('boletins-especiais/<int:pk>/retornar/', views_publicacoes.retornar_boletim_especial, name='retornar_boletim_especial'),
    path('boletins-especiais/<int:pk>/deletar/', views_publicacoes.deletar_boletim_especial, name='deletar_boletim_especial'),
    path('boletins-especiais/novo/', views_publicacoes.boletins_especiais_create, name='boletins_especiais_create'),
    path('boletins-especiais/<int:pk>/', views_publicacoes.boletim_especial_detail, name='boletim_especial_detail'),
    path('boletins-especiais/<int:pk>/visualizar/', views_publicacoes.boletim_especial_visualizar, name='boletim_especial_visualizar'),
    path('boletins-especiais/<int:boletim_pk>/adicionar-nota/<int:nota_pk>/', views_publicacoes.adicionar_nota_boletim_especial, name='adicionar_nota_boletim_especial'),
    path('boletins-especiais/<int:boletim_pk>/remover-nota/<int:nota_pk>/', views_publicacoes.remover_nota_boletim_especial, name='remover_nota_boletim_especial'),
    path('boletins-especiais/<int:pk>/pdf/', views_boletim_pdf.boletim_especial_gerar_pdf, name='boletim_especial_gerar_pdf'),
    
    # Assinaturas de Boletins Especiais
    path('boletins-especiais/<int:pk>/dados-assinatura/', views_assinaturas_boletim_especial.dados_assinatura_boletim_especial, name='dados_assinatura_boletim_especial'),
    path('boletins-especiais/<int:pk>/assinaturas/', views_assinaturas_boletim_especial.assinaturas_boletim_especial, name='assinaturas_boletim_especial'),
    path('boletins-especiais/<int:pk>/assinar/', views_assinaturas_boletim_especial.assinar_boletim_especial, name='assinar_boletim_especial'),
    path('boletins-especiais/<int:pk>/retirar-assinatura/<int:assinatura_pk>/', views_assinaturas_boletim_especial.retirar_assinatura_boletim_especial, name='retirar_assinatura_boletim_especial'),
    
    # Avisos
    path('avisos/', views_publicacoes.avisos_list, name='avisos_list'),
    path('avisos/novo/', views_publicacoes.avisos_create, name='avisos_create'),
    
    # Ordens de Serviço
    path('ordens-servico/', views_publicacoes.ordens_servico_list, name='ordens_servico_list'),
    path('ordens-servico/novo/', views_publicacoes.ordens_servico_create, name='ordens_servico_create'),
    path('publicacoes/<int:pk>/', views_publicacoes.publicacao_detail, name='publicacao_detail'),
    path('publicacoes/<int:pk>/editar/', views_publicacoes.publicacao_edit, name='publicacao_edit'),
    path('publicacoes/<int:pk>/publicar/', views_publicacoes.publicacao_publish, name='publicacao_publish'),
    path('publicacoes/<int:pk>/excluir/', views_publicacoes.publicacao_delete, name='publicacao_delete'),
    path('ajax/organograma-publicacoes/', views_publicacoes.ajax_organograma_publicacoes, name='ajax_organograma_publicacoes'),
    path('ajax/titulos-publicacao/', views_publicacoes.ajax_titulos_publicacao, name='ajax_titulos_publicacao'),
    path('ajax/titulo-publicacao/<int:pk>/', views_publicacoes.ajax_titulo_publicacao_detail, name='ajax_titulo_publicacao_detail'),
    path('ajax/nota-detail/<int:pk>/', views_publicacoes.ajax_nota_detail, name='ajax_nota_detail'),
    path('notas/<int:pk>/editar-ajax/', views_publicacoes.nota_edit_ajax, name='nota_edit_ajax'),
    path('publicacoes/<int:pk>/visualizar/', views_publicacoes.publicacao_visualizar_ajax, name='publicacao_visualizar_ajax'),
    
    # URLs para anexos de notas
    path('notas/<int:nota_id>/anexos/upload/', views_anexos_notas.upload_anexo_nota, name='upload_anexo_nota'),
    path('notas/<int:nota_id>/anexos/', views_anexos_notas.listar_anexos_nota, name='listar_anexos_nota'),
    path('anexos/<int:anexo_id>/excluir/', views_anexos_notas.excluir_anexo_nota, name='excluir_anexo_nota'),
    path('anexos/<int:anexo_id>/download/', views_anexos_notas.download_anexo_nota, name='download_anexo_nota'),
    path('anexos/<int:anexo_id>/atualizar-descricao/', views_anexos_notas.atualizar_descricao_anexo, name='atualizar_descricao_anexo'),
    
    # Status do Efetivo - Vagas
    path('status-efetivo-vagas/', views.status_efetivo_vagas, name='status_efetivo_vagas'),
    path('reordenar-antiguidade-apos-inativacao/', views.reordenar_antiguidade_apos_inativacao, name='reordenar_antiguidade_apos_inativacao'),
    path('pracas/fichas-conceito/<int:pk>/', views_pracas.ficha_conceito_pracas_detail, name='ficha_conceito_pracas_detail'),
    path('pracas/fichas-conceito/<int:pk>/excluir/', views_pracas.ficha_conceito_pracas_delete, name='ficha_conceito_pracas_delete'),
    
    # Praças - Quadros de Acesso
    path('pracas/quadros-acesso/<int:pk>/', views_pracas.quadro_acesso_pracas_detail, name='quadro_acesso_pracas_detail'),
    path('pracas/quadros-acesso/<int:pk>/editar/', views_pracas.quadro_acesso_pracas_edit, name='quadro_acesso_pracas_edit'),
    path('pracas/quadros-acesso/<int:pk>/pdf/', views_pracas.quadro_acesso_pracas_pdf, name='quadro_acesso_pracas_pdf'),
    path('pracas/quadros-acesso/<int:pk>/assinar/', views_pracas.assinar_quadro_acesso_pracas, name='assinar_quadro_acesso_pracas'),
    path('pracas/quadros-acesso/<int:pk>/retirar-assinatura/<int:assinatura_pk>/', views.retirar_assinatura_quadro_acesso, name='retirar_assinatura_quadro_acesso_pracas'),
    path('pracas/gerar-quadro-acesso/', views_pracas.gerar_quadro_acesso_pracas, name='gerar_quadro_acesso_pracas'),
    path('pracas/quadros-acesso/<int:pk>/regerar/', views_pracas.regerar_quadro_acesso_pracas, name='regerar_quadro_acesso_pracas'),
    path('pracas/quadros-acesso/<int:pk>/excluir/', views_pracas.delete_quadro_acesso_pracas, name='delete_quadro_acesso_pracas'),
    path('pracas/quadros-acesso/<int:pk>/confirmar-exclusao/', views_pracas.delete_quadro_acesso_pracas, name='quadro_acesso_pracas_confirm_delete'),
    path('pracas/quadros-acesso/<int:pk>/homologar/', views_pracas.homologar_quadro_acesso_pracas, name='homologar_quadro_acesso_pracas'),
    path('pracas/quadros-acesso/<int:pk>/deshomologar/', views_pracas.deshomologar_quadro_acesso_pracas, name='deshomologar_quadro_acesso_pracas'),
    path('pracas/quadros-acesso/<int:pk>/elaborar/', views_pracas.elaborar_quadro_acesso_pracas, name='elaborar_quadro_acesso_pracas'),
    path('pracas/quadros-acesso/<int:pk>/nao-elaborado/', views_pracas.marcar_nao_elaborado_pracas, name='marcar_nao_elaborado_pracas'),
    path('pracas/quadro-acesso/<int:pk>/relatorio-requisitos/', views_pracas.relatorio_requisitos_quadro_pracas, name='relatorio_requisitos_quadro_pracas'),
    path('pracas/quadros-acesso/<int:pk>/print/', views_pracas.quadro_acesso_pracas_print, name='quadro_acesso_pracas_print'),
    
    # Praças - Quadros de Fixação de Vagas (removido - redundante com /quadros-fixacao-vagas/)
    
    # Regras de requisitos para praças
    path('pracas/regras-requisitos/', views_pracas.regras_requisitos_pracas, name='regras_requisitos_pracas'),
    
    # Praças - Quadros Manuais
    path('pracas/criar-quadro-manual/', views_pracas.criar_quadro_manual_pracas, name='criar_quadro_manual_pracas'),
    path('pracas/quadros-acesso/<int:pk>/montar/', views_pracas.montar_quadro_acesso_pracas, name='montar_quadro_acesso_pracas'),
    path('pracas/buscar-pracas-elegiveis/', views_pracas.buscar_pracas_elegiveis, name='buscar_pracas_elegiveis'),
    path('pracas/quadros-manuais/', views_pracas.quadros_manuais_pracas_list, name='quadros_manuais_pracas_list'),
    path('pracas/quadros-acesso/<int:pk>/adicionar-militar/', views_pracas.adicionar_militar_quadro_pracas, name='adicionar_militar_quadro_pracas'),
    path('pracas/quadros-acesso/<int:pk>/remover-militar/<int:militar_id>/', views_pracas.remover_militar_quadro_pracas, name='remover_militar_quadro_pracas'),
    path('pracas/quadros-acesso/<int:pk>/buscar-pracas-disponiveis/', views_pracas.buscar_pracas_disponiveis_modal, name='buscar_pracas_disponiveis_modal'),
    path('quadros-acesso/<int:pk>/visualizar-html/', views_quadros_html.visualizar_quadro_html, name='visualizar_quadro_html'),
    path('quadros-acesso/<int:pk>/assinar-html/', views_quadros_html.assinar_quadro_html, name='assinar_quadro_html'),

    # Verificação de Autenticidade
    path('verificar-autenticidade/', views.verificar_autenticidade, name='verificar_autenticidade'),

    path('militares/info/', views_ajax.militar_info_ajax, name='militar_info_ajax'),
    path('militares/info-completa/', views_ajax.militar_info_completa_ajax, name='militar_info_completa_ajax'),
    path('militar/<int:militar_id>/data-ingresso/', views_ajax.militar_data_ingresso_ajax, name='militar_data_ingresso_ajax'),
    path('militares/update-voluntario-status/', views_ajax.update_voluntario_status, name='update_voluntario_status'),
] 
urlpatterns += [
    path('militar-autocomplete/', militar_autocomplete, name='militar-autocomplete'),
    path('lotacao-autocomplete/', lotacao_autocomplete, name='lotacao-autocomplete'),
] 
urlpatterns += [
    path('militares/reordenar/', reordenar_numeracoes_view, name='militares_reordenar'),
] 
urlpatterns += [
    path('usuarios/custom/', views.usuarios_custom_list, name='usuarios_custom_list'),
    path('usuarios/replicar-funcoes/', views.replicar_funcoes_ativas, name='replicar_funcoes_ativas'),
    path('usuarios/novo/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:pk>/', views.usuario_detail, name='usuario_detail'),
    path('usuarios/<int:pk>/editar/', views.usuario_update, name='usuario_update'),
    path('usuarios/<int:pk>/excluir/', views.usuario_delete, name='usuario_delete'),
    path('usuarios/<int:pk>/funcoes/', views.usuario_funcoes_list, name='usuario_funcoes_list'),
    path('usuarios/<int:pk>/funcoes/adicionar/', views.usuario_funcao_add, name='usuario_funcao_add'),
    path('usuarios/<int:pk>/funcoes/<int:funcao_id>/editar/', views.usuario_funcao_edit, name='usuario_funcao_edit'),
    path('usuarios/<int:pk>/funcoes/<int:funcao_id>/excluir/', views.usuario_funcao_delete, name='usuario_funcao_delete'),
    
    # Alterar senha
    path('alterar-senha/', views.alterar_senha, name='alterar_senha'),
    path('usuarios/<int:pk>/alterar-senha/', views.alterar_senha_usuario, name='alterar_senha_usuario'),
    
    # Gerenciamento de Permissões

    
    # Calendários de Promoções
    path('calendarios-promocoes/', views.calendario_promocao_list, name='calendario_promocao_list'),
    path('calendarios-promocoes/novo/', views.calendario_promocao_create, name='calendario_promocao_create'),
    path('calendarios-promocoes/<int:pk>/', views.calendario_promocao_detail, name='calendario_promocao_detail'),
    path('calendarios-promocoes/<int:pk>/editar/', views.calendario_promocao_update, name='calendario_promocao_update'),
    path('calendarios-promocoes/<int:pk>/excluir/', views.calendario_promocao_delete, name='calendario_promocao_delete'),
    path('calendarios-promocoes/<int:pk>/aprovar/', views.calendario_promocao_aprovar, name='calendario_promocao_aprovar'),
                    path('calendarios-promocoes/<int:pk>/homologar/', views.calendario_promocao_homologar, name='calendario_promocao_homologar'),
                path('calendarios-promocoes/<int:calendario_pk>/item/novo/', views.item_calendario_create, name='item_calendario_create'),
                path('calendarios-promocoes/<int:pk>/visualizar-assinatura/', views.calendario_promocao_visualizar_assinatura, name='calendario_promocao_visualizar_assinatura'),
                path('calendarios-promocoes/<int:pk>/assinar/', views.calendario_promocao_assinar, name='calendario_promocao_assinar'),
                path('calendarios-promocoes/<int:pk>/retirar-assinatura/<int:assinatura_pk>/', views.retirar_assinatura_calendario, name='retirar_assinatura_calendario'),
                path('calendarios-promocoes/<int:pk>/gerar-pdf/', views.calendario_promocao_gerar_pdf, name='calendario_promocao_gerar_pdf'),
    path('calendarios-promocoes/item/<int:pk>/editar/', views.item_calendario_update, name='item_calendario_update'),
    path('calendarios-promocoes/item/<int:pk>/excluir/', views.item_calendario_delete, name='item_calendario_delete'),
    path('calendarios-promocoes/visualizar/', views.calendario_promocao_visualizar, name='calendario_promocao_visualizar'),
    
    # URLs para gerenciamento de usuários admin
    path('usuarios/admin/', views.gerenciar_usuarios_admin, name='gerenciar_usuarios_admin'),
    path('usuarios/admin/criar/', views.criar_usuario_admin_web, name='criar_usuario_admin'),
    path('usuarios/admin/listar/', views.listar_usuarios_admin_web, name='listar_usuarios_admin'),
    path('usuarios/admin/remover/<int:user_id>/', views.remover_usuario_admin_web, name='remover_usuario_admin'),
]
urlpatterns += [
    
    # URLs para Funções Militares
    path('funcoes/', views.funcoes_militares_list, name='funcoes_militares_list'),
    path('funcoes-simples/', views.funcoes_militares_list, name='funcoes_simples'),
    path('funcoes/novo/', views.funcoes_militares_create, name='funcoes_militares_create'),
    path('funcoes/<int:funcao_id>/', views.funcoes_militares_detail, name='funcoes_militares_detail'),
    path('funcoes/<int:funcao_id>/editar/', views.funcoes_militares_update, name='funcoes_militares_update'),
    path('funcoes/<int:funcao_id>/excluir/', views.funcoes_militares_delete, name='funcoes_militares_delete'),
    path('funcoes/<int:funcao_id>/gerenciar-permissoes/', views.gerenciar_permissoes_unificado, name='gerenciar_permissoes_unificado'),
    path('funcoes/<int:funcao_id>/teste-permissoes/', views.teste_permissoes_simples, name='teste_permissoes_simples'),
    path('funcoes/<int:funcao_id>/debug-permissoes/', views.debug_permissoes, name='debug_permissoes'),
    path('teste-template/', views.teste_template, name='teste_template'),
    path('funcoes/<int:funcao_id>/configurar-permissoes-automaticas/', views.configurar_permissoes_automaticas, name='configurar_permissoes_automaticas'),
    path('funcoes/sincronizar/', views.funcoes_militares_sincronizar, name='funcoes_militares_sincronizar'),
    path('funcoes/tempo-atual/', views.funcoes_militares_tempo_atual, name='funcoes_militares_tempo_atual'),
    path('funcoes/media-tempo/', views.funcoes_militares_media_tempo, name='funcoes_militares_media_tempo'),
]

# URLs para Logs do Sistema
urlpatterns += [
    path('logs/', views.logs_sistema_list, name='logs_sistema_list'),
    path('logs/<int:pk>/', views.logs_sistema_detail, name='logs_sistema_detail'),
    path('logs/<int:pk>/marcar-processado/', views.logs_sistema_marcar_processado, name='logs_sistema_marcar_processado'),
    path('logs/<int:pk>/marcar-notificado/', views.logs_sistema_marcar_notificado, name='logs_sistema_marcar_notificado'),
    path('logs/limpar-antigos/', views.logs_sistema_limpar_antigos, name='logs_sistema_limpar_antigos'),
    path('logs/estatisticas/', views.logs_sistema_estatisticas, name='logs_sistema_estatisticas'),
    path('logs/exportar/', views.logs_sistema_exportar, name='logs_sistema_exportar'),
    
    # URLs para Escalas de Serviço
    path('escalas/', views.escalas_list, name='escalas_list'),
    path('escalas/gerar/', views.gerar_escalas_mes, name='gerar_escalas_mes'),
    path('api/organizacoes-disponiveis/', views.api_organizacoes_disponiveis, name='api_organizacoes_disponiveis'),
    path('escalas/configuracao/', views.escalas_configuracao, name='escalas_configuracao'),
    path('escalas/abonar/', views.escalas_configuracao, name='escalas_abonar'),
    path('escalas/abono-pdf/', views.escalas_abono_pdf, name='escalas_abono_pdf'),
    path('escalas/banco-horas/', views.escalas_banco_horas, name='escalas_banco_horas'),
    path('escalas/banco-horas/editar/<int:pk>/', views.banco_horas_editar, name='banco_horas_editar'),
    path('escalas/banco-horas/excluir/<int:pk>/', views.banco_horas_excluir, name='banco_horas_excluir'),
    path('escalas/banco-horas/relatorio-pdf/', views.banco_horas_relatorio_pdf, name='banco_horas_relatorio_pdf'),
    path('escalas/banco-horas/relatorio-pdf-militar/', views.banco_horas_relatorio_pdf_militar, name='banco_horas_relatorio_pdf_militar'),
    path('escalas/banco-horas/sincronizar/', views.banco_horas_sincronizar, name='banco_horas_sincronizar'),
    path('escalas/banco-horas/api/detalhes-militar/', views.api_banco_horas_detalhes_militar, name='api_banco_horas_detalhes_militar'),
    path('escalas/operacoes/', views.escalas_operacoes, name='escalas_operacoes'),
    path('escalas/controle/', views.escalas_controle, name='escalas_controle'),
    path('escalas/<int:pk>/', views.escala_detail, name='escala_detail'),
    path('escalas/<int:pk>/pdf/', views.escala_pdf, name='escala_pdf'),
    path('api/verificar-disponibilidade-militar/', views.api_verificar_disponibilidade_militar, name='api_verificar_disponibilidade_militar'),
    path('api/verificar-conflitos-planejadas/', views.api_verificar_conflitos_planejadas, name='api_verificar_conflitos_planejadas'),
    
    # APIs para modal de gerenciar militares
    path('escalas/<int:pk>/api/militares-disponiveis/', views.api_militares_disponiveis, name='api_militares_disponiveis'),
    path('escalas/<int:pk>/api/militares-escalados/', views.api_militares_escalados, name='api_militares_escalados'),
    path('escalas/<int:pk>/api/adicionar-militar/', views.api_adicionar_militar, name='api_adicionar_militar'),
    path('escalas/<int:pk>/api/adicionar-coletivo/', views.api_adicionar_coletivo, name='api_adicionar_coletivo'),
    path('escalas/<int:pk>/api/remover-militar/', views.api_remover_militar, name='api_remover_militar'),
    path('alteracoes/<int:alteracao_id>/visualizar-documento/', views.visualizar_documento_alteracao, name='visualizar_documento_alteracao'),
    path('api/secoes-disponiveis/', views.api_secoes_disponiveis, name='api_secoes_disponiveis'),
    path('api/equipes-disponiveis/', views.api_equipes_disponiveis, name='api_equipes_disponiveis'),
    path('api/funcoes-operacionais-disponiveis/', views.api_funcoes_operacionais_disponiveis, name='api_funcoes_operacionais_disponiveis'),
    path('api/viaturas-disponiveis/', views.api_viaturas_disponiveis, name='api_viaturas_disponiveis'),
    path('escalas/<int:pk>/api/revisar/', views.api_revisar_escala, name='api_revisar_escala'),
    path('escalas/<int:pk>/api/aprovar/', views.api_aprovar_escala, name='api_aprovar_escala'),
    path('escalas/<int:pk>/api/registrar-alteracao/', views.api_registrar_alteracao_escala, name='api_registrar_alteracao_escala'),
    path('escalas/<int:pk>/sincronizar-abonar/', views.sincronizar_escala_abonar, name='sincronizar_escala_abonar'),
    
    # URLs para assinaturas de escalas
    path('escalas/<int:pk>/assinar/', views_assinaturas_escalas.assinar_escala, name='assinar_escala'),
    path('escalas/<int:pk>/verificar-assinaturas/', views_assinaturas_escalas.verificar_assinaturas_escala, name='verificar_assinaturas_escala'),
    path('escalas/<int:pk>/api/dados-assinatura/', views_assinaturas_escalas.dados_assinatura_escala, name='dados_assinatura_escala'),
]

# URL para debug das funções do usuário
urlpatterns += [
    path('debug-funcoes/', views.debug_funcoes_usuario, name='debug_funcoes_usuario'),
    
    # URLs para Qualificações
    path('qualificacoes/<int:militar_id>/', views.qualificacoes_militar, name='qualificacoes_militar'),
    path('qualificacoes/<int:militar_id>/adicionar/', views.adicionar_qualificacao, name='adicionar_qualificacao'),
    path('qualificacoes/visualizar/<int:qualificacao_id>/', views.visualizar_qualificacao, name='visualizar_qualificacao'),
    path('qualificacoes/documento/<int:qualificacao_id>/', views.visualizar_documento_qualificacao, name='visualizar_documento_qualificacao'),
    path('qualificacoes/editar/<int:qualificacao_id>/', views.editar_qualificacao, name='editar_qualificacao'),
    path('qualificacoes/excluir/<int:qualificacao_id>/', views.excluir_qualificacao, name='excluir_qualificacao'),
    path('qualificacoes/verificar/<int:qualificacao_id>/', views.verificar_qualificacao, name='verificar_qualificacao'),
    
    # URLs para Lotações
    path('lotacoes/', views_lotacao.LotacaoListView.as_view(), name='lotacao_list'),
    path('lotacoes/criar/', views_lotacao.LotacaoCreateView.as_view(), name='lotacao_create'),
    path('lotacoes/<int:pk>/', views_lotacao.LotacaoDetailView.as_view(), name='lotacao_detail'),
    path('lotacoes/<int:pk>/editar/', views_lotacao.LotacaoUpdateView.as_view(), name='lotacao_update'),
    path('lotacoes/<int:pk>/excluir/', views_lotacao.LotacaoDeleteView.as_view(), name='lotacao_delete'),
    path('lotacoes/militar/<int:militar_id>/', views_lotacao.lotacao_militar_list, name='lotacao_militar_list'),
    path('lotacoes/estatisticas/', views_lotacao.lotacao_estatisticas, name='lotacao_estatisticas'),
    
    # URLs AJAX para Lotações
    path('lotacoes/ajax/criar/', views_lotacao.lotacao_create_ajax, name='lotacao_create_ajax'),
    path('lotacoes/ajax/<int:pk>/editar/', views_lotacao.lotacao_update_ajax, name='lotacao_update_ajax'),
    path('lotacoes/ajax/<int:pk>/excluir/', views_lotacao.lotacao_delete_ajax, name='lotacao_delete_ajax'),
    path('lotacoes/ajax/militar/<int:militar_id>/', views_lotacao.lotacao_militar_ajax, name='lotacao_militar_ajax'),
    
    # URLs para Afastamentos
    path('afastamentos/', views_afastamento.AfastamentoListView.as_view(), name='afastamento_list'),
    path('afastamentos/criar/', views_afastamento.AfastamentoCreateView.as_view(), name='afastamento_create'),
    path('afastamentos/<int:pk>/', views_afastamento.AfastamentoDetailView.as_view(), name='afastamento_detail'),
    path('afastamentos/<int:pk>/editar/', views_afastamento.AfastamentoUpdateView.as_view(), name='afastamento_update'),
    path('afastamentos/<int:pk>/excluir/', views_afastamento.AfastamentoDeleteView.as_view(), name='afastamento_delete'),
    path('afastamentos/<int:pk>/documento/upload/', views_afastamento.documento_afastamento_upload, name='documento_afastamento_upload'),
    path('documentos-afastamento/<int:documento_id>/excluir/', views_afastamento.documento_afastamento_delete, name='documento_afastamento_delete'),
    path('afastamentos/militar/<int:militar_id>/certidao/pdf/', views_afastamento.afastamento_certidao_pdf, name='afastamento_certidao_pdf'),
    
    # URLs para Averbações
    path('averbacoes/', views_averbacao.AverbacaoListView.as_view(), name='averbacao_list'),
    path('averbacoes/criar/', views_averbacao.AverbacaoCreateView.as_view(), name='averbacao_create'),
    path('averbacoes/<int:pk>/', views_averbacao.AverbacaoDetailView.as_view(), name='averbacao_detail'),
    path('averbacoes/<int:pk>/editar/', views_averbacao.AverbacaoUpdateView.as_view(), name='averbacao_update'),
    path('averbacoes/<int:pk>/excluir/', views_averbacao.AverbacaoDeleteView.as_view(), name='averbacao_delete'),
    
    # URLs para Licenças Especiais
    path('licencas-especiais/', views_licencas_especiais.LicencaEspecialListView.as_view(), name='licenca_especial_list'),
    path('licencas-especiais/criar/', views_licencas_especiais.LicencaEspecialCreateView.as_view(), name='licenca_especial_create'),
    path('licencas-especiais/<int:pk>/', views_licencas_especiais.LicencaEspecialDetailView.as_view(), name='licenca_especial_detail'),
    path('licencas-especiais/<int:pk>/editar/', views_licencas_especiais.LicencaEspecialUpdateView.as_view(), name='licenca_especial_update'),
    path('licencas-especiais/<int:pk>/excluir/', views_licencas_especiais.LicencaEspecialDeleteView.as_view(), name='licenca_especial_delete'),
    
    # Planos de Licenças Especiais
    path('planos-licencas-especiais/', views_licencas_especiais.PlanoLicencaEspecialListView.as_view(), name='plano_licenca_especial_list'),
    path('planos-licencas-especiais/pdf/', views_licencas_especiais.plano_licenca_especial_list_pdf, name='plano_licenca_especial_list_pdf'),
    path('planos-licencas-especiais/criar/', views_licencas_especiais.PlanoLicencaEspecialCreateView.as_view(), name='plano_licenca_especial_create'),
    path('planos-licencas-especiais/<int:pk>/', views_licencas_especiais.PlanoLicencaEspecialDetailView.as_view(), name='plano_licenca_especial_detail'),
    path('planos-licencas-especiais/<int:pk>/editar/', views_licencas_especiais.PlanoLicencaEspecialUpdateView.as_view(), name='plano_licenca_especial_update'),
    path('planos-licencas-especiais/<int:pk>/excluir/', views_licencas_especiais.PlanoLicencaEspecialDeleteView.as_view(), name='plano_licenca_especial_delete'),
    path('planos-licencas-especiais/<int:pk>/aprovar/', views_licencas_especiais.aprovar_plano_licenca_especial, name='plano_licenca_especial_aprovar'),
    path('planos-licencas-especiais/<int:plano_id>/adicionar-licenca/', views_licencas_especiais.LicencaEspecialCreateParaPlanoView.as_view(), name='licenca_especial_create_para_plano'),
    path('licencas-especiais/<int:pk>/homologar/', views_licencas_especiais.licenca_especial_homologar, name='licenca_especial_homologar'),
    path('licencas-especiais/<int:pk>/desomologar/', views_licencas_especiais.licenca_especial_desomologar, name='licenca_especial_desomologar'),
    path('licencas-especiais/<int:pk>/reprogramar/', views_licencas_especiais.licenca_especial_reprogramar, name='licenca_especial_reprogramar'),
    
    # URLs para Férias - Planos
    path('ferias/', views_ferias.PlanoFeriasListView.as_view(), name='ferias_list'),
    path('ferias/pdf/', views_ferias.ferias_list_pdf, name='ferias_list_pdf'),
    path('ferias/plano/criar/', views_ferias.PlanoFeriasCreateView.as_view(), name='plano_ferias_create'),
    path('ferias/plano/<int:pk>/', views_ferias.PlanoFeriasDetailView.as_view(), name='plano_ferias_detail'),
    path('ferias/plano/<int:pk>/editar/', views_ferias.PlanoFeriasUpdateView.as_view(), name='plano_ferias_update'),
    path('ferias/plano/<int:pk>/excluir/', views_ferias.PlanoFeriasDeleteView.as_view(), name='plano_ferias_delete'),
    
    # URLs para Férias Individuais
    path('ferias/individual/criar/', views_ferias.FeriasCreateView.as_view(), name='ferias_create'),
    path('ferias/militar/<int:militar_id>/criar/', views_ferias.FeriasCreateView.as_view(), name='ferias_create_militar'),
    path('ferias/plano/<int:plano_id>/militar/<int:militar_id>/criar/', views_ferias.FeriasCreateParaPlanoView.as_view(), name='ferias_create_para_plano'),
    path('ferias/<int:pk>/', views_ferias.FeriasDetailView.as_view(), name='ferias_detail'),
    path('ferias/<int:pk>/editar/', views_ferias.FeriasUpdateView.as_view(), name='ferias_update'),
    path('ferias/<int:pk>/excluir/', views_ferias.FeriasDeleteView.as_view(), name='ferias_delete'),
    path('ferias/<int:pk>/documento/upload/', views_ferias.documento_ferias_upload, name='documento_ferias_upload'),
    path('documentos-ferias/<int:documento_id>/excluir/', views_ferias.documento_ferias_delete, name='documento_ferias_delete'),
    path('ferias/<int:pk>/homologar/', views_ferias.ferias_homologar, name='ferias_homologar'),
    path('ferias/<int:pk>/desomologar/', views_ferias.ferias_desomologar, name='ferias_desomologar'),
    path('planos-ferias/<int:plano_id>/homologar-massa/', views_ferias.ferias_homologar_em_massa, name='ferias_homologar_em_massa'),
    path('ferias/<int:pk>/reprogramar/', views_ferias.ferias_reprogramar, name='ferias_reprogramar'),
    path('ferias/plano/<int:pk>/aprovar/', views_ferias.plano_ferias_aprovar, name='plano_ferias_aprovar'),
    path('ferias/militar/<int:militar_id>/certidao/pdf/', views_ferias.ferias_certidao_pdf, name='ferias_certidao_pdf'),
    path('licencas-especiais/militar/<int:militar_id>/certidao/pdf/', views_licencas_especiais.licenca_especial_certidao_pdf, name='licenca_especial_certidao_pdf'),
    
    # URLs para Viaturas
    path('viaturas/', views_viaturas.ViaturaListView.as_view(), name='viatura_list'),
    path('viaturas/criar/', views_viaturas.ViaturaCreateView.as_view(), name='viatura_create'),
    path('viaturas/<int:pk>/', views_viaturas.ViaturaDetailView.as_view(), name='viatura_detail'),
    path('viaturas/<int:pk>/transferir/', views_viaturas.ViaturaTransferenciaView.as_view(), name='viatura_transferencia'),
    path('viaturas/<int:pk>/editar/', views_viaturas.ViaturaUpdateView.as_view(), name='viatura_update'),
    path('viaturas/<int:pk>/excluir/', views_viaturas.ViaturaDeleteView.as_view(), name='viatura_delete'),
    path('viaturas/<int:pk>/qrcode/', views_viaturas.viatura_qrcode, name='viatura_qrcode'),
    path('ajax/viaturas-autocomplete/', views_viaturas.viatura_autocomplete, name='viatura_autocomplete'),
    
    # URLs para Controle de Combustível (Abastecimentos)
    path('abastecimentos/', views_abastecimentos.AbastecimentoListView.as_view(), name='abastecimento_list'),
    path('abastecimentos/criar/', views_abastecimentos.AbastecimentoCreateView.as_view(), name='abastecimento_create'),
    path('abastecimentos/<int:pk>/', views_abastecimentos.AbastecimentoDetailView.as_view(), name='abastecimento_detail'),
    path('abastecimentos/<int:pk>/editar/', views_abastecimentos.AbastecimentoUpdateView.as_view(), name='abastecimento_update'),
    path('abastecimentos/<int:pk>/excluir/', views_abastecimentos.AbastecimentoDeleteView.as_view(), name='abastecimento_delete'),
    path('viaturas/<int:viatura_id>/abastecimentos/', views_abastecimentos.abastecimento_por_viatura, name='abastecimento_por_viatura'),
    
    # URLs para Abastecimento via QR Code (Mobile)
    path('abastecimento-qr/', views_abastecimentos.abastecimento_qr, name='abastecimento_qr_busca'),
    path('abastecimento-qr/<int:viatura_id>/', views_abastecimentos.abastecimento_qr, name='abastecimento_qr'),
    path('frota-mobile/<int:viatura_id>/', views_abastecimentos.abastecimento_create_mobile, name='frota_create_mobile'),
    path('abastecimento-qr/sucesso/<int:abastecimento_id>/', views_abastecimentos.abastecimento_qr_success, name='abastecimento_qr_success'),
    path('abastecimentos/<int:abastecimento_id>/pdf/', views_abastecimentos.abastecimento_pdf, name='abastecimento_pdf'),
    path('viaturas/<int:viatura_id>/abastecimentos/historico-pdf/', views_abastecimentos.historico_abastecimento_pdf, name='historico_abastecimento_pdf'),
    
    # URLs para Controle de Manutenção
    path('manutencoes/', views_manutencoes.ManutencaoListView.as_view(), name='manutencao_list'),
    path('manutencoes/criar/', views_manutencoes.ManutencaoCreateView.as_view(), name='manutencao_create'),
    path('manutencoes/<int:pk>/', views_manutencoes.ManutencaoDetailView.as_view(), name='manutencao_detail'),
    path('manutencoes/<int:pk>/editar/', views_manutencoes.ManutencaoUpdateView.as_view(), name='manutencao_update'),
    path('manutencoes/<int:pk>/excluir/', views_manutencoes.ManutencaoDeleteView.as_view(), name='manutencao_delete'),
    path('manutencoes/<int:manutencao_id>/pdf/', views_manutencoes.manutencao_pdf, name='manutencao_pdf'),
    path('viaturas/<int:viatura_id>/manutencoes/', views_manutencoes.manutencao_por_viatura, name='manutencao_por_viatura'),
    path('viaturas/<int:viatura_id>/manutencoes/historico-pdf/', views_manutencoes.historico_manutencao_pdf, name='historico_manutencao_pdf'),
    
    # URLs para Controle de Troca de Óleo
    path('trocas-oleo/', views_trocas_oleo.TrocaOleoListView.as_view(), name='troca_oleo_list'),
    path('trocas-oleo/criar/', views_trocas_oleo.TrocaOleoCreateView.as_view(), name='troca_oleo_create'),
    path('trocas-oleo/<int:pk>/', views_trocas_oleo.TrocaOleoDetailView.as_view(), name='troca_oleo_detail'),
    path('trocas-oleo/<int:pk>/editar/', views_trocas_oleo.TrocaOleoUpdateView.as_view(), name='troca_oleo_update'),
    path('trocas-oleo/<int:pk>/excluir/', views_trocas_oleo.TrocaOleoDeleteView.as_view(), name='troca_oleo_delete'),
    path('trocas-oleo/<int:troca_oleo_id>/pdf/', views_trocas_oleo.troca_oleo_pdf, name='troca_oleo_pdf'),
    path('viaturas/<int:viatura_id>/trocas-oleo/', views_trocas_oleo.troca_oleo_por_viatura, name='troca_oleo_por_viatura'),
    
    # URLs para Controle de Rodagem
    path('rodagens/', views_rodagens.RodagemListView.as_view(), name='rodagem_list'),
    path('rodagens/criar/', views_rodagens.RodagemCreateView.as_view(), name='rodagem_create'),
    path('rodagens/<int:pk>/', views_rodagens.RodagemDetailView.as_view(), name='rodagem_detail'),
    path('rodagens/<int:pk>/editar/', views_rodagens.RodagemUpdateView.as_view(), name='rodagem_update'),
    path('rodagens/<int:pk>/excluir/', views_rodagens.RodagemDeleteView.as_view(), name='rodagem_delete'),
    path('rodagens/<int:pk>/encerrar/', views_rodagens.rodagem_encerrar, name='rodagem_encerrar'),
    path('viaturas/<int:viatura_id>/rodagens/', views_rodagens.rodagem_por_viatura, name='rodagem_por_viatura'),
    path('viaturas/<int:viatura_id>/rodagens/historico-pdf/', views_rodagens.historico_rodagem_pdf, name='historico_rodagem_pdf'),
    path('painel-guarda/', views_rodagens.painel_guarda, name='painel_guarda'),
    path('painel-guarda/registrar-saida/<int:viatura_id>/', views_rodagens.painel_registrar_saida, name='painel_registrar_saida'),
    path('painel-guarda/registrar-retorno/<int:rodagem_id>/', views_rodagens.painel_registrar_retorno, name='painel_registrar_retorno'),
    
    # URLs para Material Bélico - Armas da Instituição
    path('armas/', views_material_belico.ArmaListView.as_view(), name='arma_list'),
    path('armas/pdf/', views_material_belico.armas_pdf, name='armas_pdf'),
    path('armas/criar/', views_material_belico.ArmaCreateView.as_view(), name='arma_create'),
    path('configuracao-arma/<int:pk>/dados/', views_material_belico.configuracao_arma_dados, name='configuracao_arma_dados'),
    path('configuracao-arma/buscar/', views_material_belico.configuracao_arma_buscar, name='configuracao_arma_buscar'),
    path('militar/<int:pk>/lotacao-atual/', views_material_belico.militar_lotacao_atual, name='militar_lotacao_atual'),
    path('armas/<int:pk>/', views_material_belico.ArmaDetailView.as_view(), name='arma_detail'),
    path('armas/<int:pk>/ficha-pdf/', views_material_belico.arma_ficha_pdf, name='arma_ficha_pdf'),
    path('armas/<int:pk>/qrcode/', views_material_belico.arma_qrcode, name='arma_qrcode'),
    path('armas/<int:pk>/editar/', views_material_belico.ArmaUpdateView.as_view(), name='arma_update'),
    path('armas/<int:pk>/excluir/', views_material_belico.ArmaDeleteView.as_view(), name='arma_delete'),
    path('armas/<int:pk>/movimentar/', views_material_belico.MovimentacaoArmaCreateView.as_view(), name='arma_movimentar'),
    path('armas/<int:pk>/transferir/', views_material_belico.ArmaTransferenciaView.as_view(), name='arma_transferencia'),
    
    # URLs para Cautela de Armas
    path('cautelas-armas/', views_cautela_arma.CautelaArmaListView.as_view(), name='cautela_arma_list'),
    path('cautelas-armas/criar/', views_cautela_arma.CautelaArmaCreateView.as_view(), name='cautela_arma_create'),
    path('cautelas-armas/<int:pk>/', views_cautela_arma.CautelaArmaDetailView.as_view(), name='cautela_arma_detail'),
    path('cautelas-armas/<int:pk>/pdf/', views_cautela_arma.cautela_arma_pdf, name='cautela_arma_pdf'),
    path('cautelas-armas/<int:pk>/devolver/', views_cautela_arma.devolver_cautela_arma, name='cautela_arma_devolver'),
    path('cautelas-armas/<int:pk>/assinar/', views_cautela_arma.assinar_cautela_arma, name='cautela_arma_assinar'),
    path('cautelas-armas/<int:pk>/deletar/', views_cautela_arma.deletar_cautela_arma, name='cautela_arma_deletar'),
    path('armas/<int:pk>/dados-organizacao/', views_cautela_arma.arma_dados_organizacao, name='arma_dados_organizacao'),
    
    # URLs para Cautela Coletiva de Armas
    # path('cautelas-armas-coletivas/', views_cautela_arma.CautelaArmaColetivaListView.as_view(), name='cautela_arma_coletiva_list'),  # Removido - agora integrado em cautelas-armas/
    path('cautelas-armas-coletivas/criar/', views_cautela_arma.CautelaArmaColetivaCreateView.as_view(), name='cautela_arma_coletiva_create'),
    path('cautelas-armas-coletivas/<int:pk>/', views_cautela_arma.CautelaArmaColetivaDetailView.as_view(), name='cautela_arma_coletiva_detail'),
    path('cautelas-armas-coletivas/<int:pk>/pdf/', views_cautela_arma.cautela_arma_coletiva_pdf, name='cautela_arma_coletiva_pdf'),
    path('cautelas-armas-coletivas/<int:pk>/adicionar-arma/', views_cautela_arma.adicionar_arma_cautela_coletiva, name='cautela_arma_coletiva_adicionar_arma'),
    path('cautelas-armas-coletivas/<int:pk>/remover-arma/<int:item_id>/', views_cautela_arma.remover_arma_cautela_coletiva, name='cautela_arma_coletiva_remover_arma'),
    path('cautelas-armas-coletivas/<int:pk>/finalizar/', views_cautela_arma.finalizar_cautela_coletiva, name='cautela_arma_coletiva_finalizar'),
    path('cautelas-armas-coletivas/<int:pk>/assinar/', views_cautela_arma.assinar_cautela_arma_coletiva, name='cautela_arma_coletiva_assinar'),
    
    # URLs para Controle de Munição
    path('municoes/', views_municao.MunicaoListView.as_view(), name='municao_list'),
    path('municoes/criar/', views_municao.MunicaoCreateView.as_view(), name='municao_create'),
    path('municoes/<int:pk>/', views_municao.MunicaoDetailView.as_view(), name='municao_detail'),
    path('municoes/<int:pk>/dados/', views_municao.municao_dados_ajax, name='municao_dados_ajax'),
    path('municoes/estoque-ajax/', views_municao.municao_estoque_ajax, name='municao_estoque_ajax'),
    
    # URLs para Entrada de Munição
    path('municoes/entradas/', views_municao.EntradaMunicaoListView.as_view(), name='entrada_municao_list'),
    path('municoes/entradas/criar/', views_municao.EntradaMunicaoCreateView.as_view(), name='entrada_municao_create'),
    
    # URLs para Saída de Munição
    path('municoes/saidas/', views_municao.SaidaMunicaoListView.as_view(), name='saida_municao_list'),
    path('municoes/saidas/criar/', views_municao.SaidaMunicaoCreateView.as_view(), name='saida_municao_create'),
    
    # URLs para Devolução de Munição
    path('municoes/devolucoes/', views_municao.DevolucaoMunicaoListView.as_view(), name='devolucao_municao_list'),
    path('municoes/devolucoes/criar/', views_municao.DevolucaoMunicaoCreateView.as_view(), name='devolucao_municao_create'),
    
    # URLs para Cautela de Munição
    path('cautelas-municoes/', views_cautela_municao.CautelaMunicaoListView.as_view(), name='cautela_municao_list'),
    path('cautelas-municoes/criar/', views_cautela_municao.CautelaMunicaoCreateView.as_view(), name='cautela_municao_create'),
    path('cautelas-municoes/<int:pk>/', views_cautela_municao.CautelaMunicaoDetailView.as_view(), name='cautela_municao_detail'),
    path('cautelas-municoes/<int:pk>/devolver/', views_cautela_municao.devolver_cautela_municao, name='cautela_municao_devolver'),
    path('cautelas-municoes/<int:pk>/deletar/', views_cautela_municao.deletar_cautela_municao, name='cautela_municao_deletar'),
    path('cautelas-armas-coletivas/<int:pk>/deletar/', views_cautela_arma.deletar_cautela_arma_coletiva, name='cautela_arma_coletiva_deletar'),
    
    # URLs para Material Bélico - Armas Particulares
    path('armas-particulares/', views_material_belico.ArmaParticularListView.as_view(), name='arma_particular_list'),
    path('armas-particulares/criar/', views_material_belico.ArmaParticularCreateView.as_view(), name='arma_particular_create'),
    path('armas-particulares/<int:pk>/', views_material_belico.ArmaParticularDetailView.as_view(), name='arma_particular_detail'),
    path('armas-particulares/<int:pk>/editar/', views_material_belico.ArmaParticularUpdateView.as_view(), name='arma_particular_update'),
    path('armas-particulares/<int:pk>/excluir/', views_material_belico.ArmaParticularDeleteView.as_view(), name='arma_particular_delete'),
    
    # URLs para Movimentações de Armas
    path('movimentacoes-armas/', views_material_belico.MovimentacaoArmaListView.as_view(), name='movimentacao_arma_list'),
    path('movimentacoes-armas/criar/', views_material_belico.MovimentacaoArmaCreateView.as_view(), name='movimentacao_arma_create'),
    path('movimentacoes-armas/<int:pk>/', views_material_belico.MovimentacaoArmaDetailView.as_view(), name='movimentacao_arma_detail'),
    path('movimentacoes-armas/<int:pk>/editar/', views_material_belico.MovimentacaoArmaUpdateView.as_view(), name='movimentacao_arma_update'),
    path('movimentacoes-armas/<int:pk>/excluir/', views_material_belico.MovimentacaoArmaDeleteView.as_view(), name='movimentacao_arma_delete'),
    path('movimentacoes-armas/<int:pk>/assinar-entregando/', views_material_belico.assinar_movimentacao_entregando, name='assinar_movimentacao_entregando'),
    path('movimentacoes-armas/<int:pk>/assinar-recebendo/', views_material_belico.assinar_movimentacao_recebendo, name='assinar_movimentacao_recebendo'),
    
    # URL para página de configurações (cartucheira)
    path('configuracoes/', views_configuracoes.configuracoes_cartucheira, name='configuracoes_cartucheira'),
    
    # URLs para Configurações de Armas
    path('configuracoes-armas/', views_material_belico.ConfiguracaoArmaListView.as_view(), name='configuracao_arma_list'),
    path('configuracoes-armas/criar/', views_material_belico.ConfiguracaoArmaCreateView.as_view(), name='configuracao_arma_create'),
    path('configuracoes-armas/<int:pk>/', views_material_belico.ConfiguracaoArmaDetailView.as_view(), name='configuracao_arma_detail'),
    path('configuracoes-armas/<int:pk>/editar/', views_material_belico.ConfiguracaoArmaUpdateView.as_view(), name='configuracao_arma_update'),
    path('configuracoes-armas/<int:pk>/excluir/', views_material_belico.ConfiguracaoArmaDeleteView.as_view(), name='configuracao_arma_delete'),
    
    # URLs para Configurações de Munições
    path('configuracoes-municoes/', views_material_belico.ConfiguracaoMunicaoListView.as_view(), name='configuracao_municao_list'),
    path('configuracoes-municoes/criar/', views_material_belico.ConfiguracaoMunicaoCreateView.as_view(), name='configuracao_municao_create'),
    path('configuracoes-municoes/<int:pk>/', views_material_belico.ConfiguracaoMunicaoDetailView.as_view(), name='configuracao_municao_detail'),
    path('configuracoes-municoes/<int:pk>/editar/', views_material_belico.ConfiguracaoMunicaoUpdateView.as_view(), name='configuracao_municao_update'),
    path('configuracoes-municoes/<int:pk>/excluir/', views_material_belico.ConfiguracaoMunicaoDeleteView.as_view(), name='configuracao_municao_delete'),
    
    path('painel-guarda-login/', views_rodagens.painel_guarda_login, name='painel_guarda_login'),
    path('painel-guarda-ajax/', views_rodagens.painel_guarda_ajax, name='painel_guarda_ajax'),
    path('painel-guarda-enderecos-ajax/', views_rodagens.painel_guarda_enderecos_ajax, name='painel_guarda_enderecos_ajax'),
    path('painel-guarda-unidades-ajax/', views_rodagens.painel_guarda_unidades_ajax, name='painel_guarda_unidades_ajax'),
    path('viaturas/<int:viatura_id>/ultimo-km/', views_rodagens.viatura_ultimo_km, name='viatura_ultimo_km'),
    
    # URLs para Controle de Licenciamento
    path('licenciamentos/', views_licenciamentos.LicenciamentoListView.as_view(), name='licenciamento_list'),
    path('licenciamentos/criar/', views_licenciamentos.LicenciamentoCreateView.as_view(), name='licenciamento_create'),
    path('licenciamentos/<int:pk>/', views_licenciamentos.LicenciamentoDetailView.as_view(), name='licenciamento_detail'),
    path('licenciamentos/<int:pk>/editar/', views_licenciamentos.LicenciamentoUpdateView.as_view(), name='licenciamento_update'),
    path('licenciamentos/<int:pk>/excluir/', views_licenciamentos.LicenciamentoDeleteView.as_view(), name='licenciamento_delete'),
    path('viaturas/<int:viatura_id>/licenciamentos/', views_licenciamentos.licenciamento_por_viatura, name='licenciamento_por_viatura'),
    
    # URLs para Equipamentos Operacionais
    path('equipamentos-operacionais/', views_equipamentos_operacionais.equipamento_operacional_list, name='equipamento_operacional_list'),
    path('equipamentos-operacionais/criar/', views_equipamentos_operacionais.equipamento_operacional_create, name='equipamento_operacional_create'),
    path('equipamentos-operacionais/<int:pk>/', views_equipamentos_operacionais.equipamento_operacional_detail, name='equipamento_operacional_detail'),
    path('equipamentos-operacionais/<int:pk>/editar/', views_equipamentos_operacionais.equipamento_operacional_update, name='equipamento_operacional_update'),
    path('equipamentos-operacionais/<int:pk>/excluir/', views_equipamentos_operacionais.equipamento_operacional_delete, name='equipamento_operacional_delete'),
    path('equipamentos-operacionais/<int:equipamento_id>/tempos-uso/', views_equipamentos_operacionais.tempo_uso_por_equipamento, name='tempo_uso_por_equipamento'),
    path('equipamentos-operacionais/<int:equipamento_id>/tempos-uso/criar/', views_equipamentos_operacionais.tempo_uso_create, name='tempo_uso_create'),
    path('tempos-uso/<int:pk>/editar/', views_equipamentos_operacionais.tempo_uso_update, name='tempo_uso_update'),
    path('tempos-uso/<int:pk>/excluir/', views_equipamentos_operacionais.tempo_uso_delete, name='tempo_uso_delete'),
    
    # URLs para Controle de Combustível de Equipamentos
    path('equipamentos-abastecimentos/', views_equipamentos_operacionais.equipamento_abastecimento_list, name='equipamento_abastecimento_list'),
    path('equipamentos-abastecimentos/criar/', views_equipamentos_operacionais.equipamento_abastecimento_create, name='equipamento_abastecimento_create'),
    path('equipamentos-abastecimentos/<int:pk>/', views_equipamentos_operacionais.equipamento_abastecimento_detail, name='equipamento_abastecimento_detail'),
    path('equipamentos-abastecimentos/<int:pk>/editar/', views_equipamentos_operacionais.equipamento_abastecimento_update, name='equipamento_abastecimento_update'),
    path('equipamentos-abastecimentos/<int:pk>/excluir/', views_equipamentos_operacionais.equipamento_abastecimento_delete, name='equipamento_abastecimento_delete'),
    path('equipamentos-operacionais/<int:equipamento_id>/abastecimentos/', views_equipamentos_operacionais.equipamento_abastecimento_por_equipamento, name='equipamento_abastecimento_por_equipamento'),
    
    # URLs para Manutenções de Equipamentos
    path('equipamentos-manutencoes/', views_equipamentos_operacionais.equipamento_manutencao_list, name='equipamento_manutencao_list'),
    path('equipamentos-manutencoes/criar/', views_equipamentos_operacionais.equipamento_manutencao_create, name='equipamento_manutencao_create'),
    path('equipamentos-manutencoes/<int:pk>/', views_equipamentos_operacionais.equipamento_manutencao_detail, name='equipamento_manutencao_detail'),
    path('equipamentos-manutencoes/<int:pk>/editar/', views_equipamentos_operacionais.equipamento_manutencao_update, name='equipamento_manutencao_update'),
    path('equipamentos-manutencoes/<int:pk>/excluir/', views_equipamentos_operacionais.equipamento_manutencao_delete, name='equipamento_manutencao_delete'),
    
    # URLs para Trocas de Óleo de Equipamentos
    path('equipamentos-trocas-oleo/', views_equipamentos_operacionais.equipamento_troca_oleo_list, name='equipamento_troca_oleo_list'),
    path('equipamentos-trocas-oleo/criar/', views_equipamentos_operacionais.equipamento_troca_oleo_create, name='equipamento_troca_oleo_create'),
    path('equipamentos-trocas-oleo/<int:pk>/', views_equipamentos_operacionais.equipamento_troca_oleo_detail, name='equipamento_troca_oleo_detail'),
    path('equipamentos-trocas-oleo/<int:pk>/editar/', views_equipamentos_operacionais.equipamento_troca_oleo_update, name='equipamento_troca_oleo_update'),
    path('equipamentos-trocas-oleo/<int:pk>/excluir/', views_equipamentos_operacionais.equipamento_troca_oleo_delete, name='equipamento_troca_oleo_delete'),
    path('ajax/equipamentos-operacionais/<int:equipamento_id>/ultimas-horas/', views_equipamentos_operacionais.equipamento_ultimas_horas, name='equipamento_ultimas_horas'),
    
    # URLs AJAX para Militares
    path('ajax/militares-disponiveis/', views.militares_disponiveis_ajax, name='militares_disponiveis_ajax'),
    path('ajax/militares-indexados/<int:pk>/', views.buscar_militares_indexados_ajax, name='buscar_militares_indexados_ajax'),
    path('ajax/publicacoes-militar/<int:pk>/', views.buscar_publicacoes_militar_ajax, name='buscar_publicacoes_militar_ajax'),
    path('ajax/salvar-indexacao/<int:pk>/', views.salvar_indexacao_militares_ajax, name='salvar_indexacao_militares_ajax'),
    path('ajax/buscar-militares-lotacao/', views_lotacao.ajax_buscar_militares, name='ajax_buscar_militares_lotacao'),
    
    # URLs AJAX para Organograma
    path('ajax/grandes-comandos/', views.ajax_grandes_comandos, name='ajax_grandes_comandos'),
    path('ajax/unidades/', views.ajax_unidades, name='ajax_unidades'),
    path('ajax/sub-unidades/', views.ajax_sub_unidades, name='ajax_sub_unidades'),
    
    path('ajax/organograma-completo/', views.ajax_organograma_completo, name='ajax_organograma_completo'),
    path('ajax/organograma-completo-sem-filtro/', views.ajax_organograma_completo_sem_filtro, name='ajax_organograma_completo_sem_filtro'),
    path('ajax/ajudante-geral/', views.ajudante_geral_ajax, name='ajudante_geral_ajax'),
    path('ajax/buscar-nota-por-numero/<str:numero>/', views.buscar_nota_por_numero_ajax, name='buscar_nota_por_numero_ajax'),
    path('ajax/devolver-nota-origem/<int:pk>/', views_ajax_boletim.devolver_nota_origem_ajax, name='devolver_nota_origem_ajax'),
    path('ajax/transferir-nota-boletim/<int:pk>/', views_ajax_boletim.transferir_nota_boletim_ajax, name='transferir_nota_boletim_ajax'),
    
    # URLs para Funções dos Militares
    path('militares/<int:militar_id>/funcoes/', views.militar_funcao_list, name='militar_funcao_list'),                                                         
    path('militares/<int:militar_id>/funcoes/adicionar/', views.militar_funcao_create, name='militar_funcao_create'),                                           
    path('militares/<int:militar_id>/funcoes/<int:funcao_id>/editar/', views.militar_funcao_update, name='militar_funcao_update'),                              
    path('militares/<int:militar_id>/funcoes/<int:funcao_id>/excluir/', views.militar_funcao_delete, name='militar_funcao_delete'),                             
    
    # URLs para Elogios
    path('elogios/', views_elogios_punicoes.ElogioListView.as_view(), name='elogio_list'),
    path('elogios/criar/', views_elogios_punicoes.ElogioCreateView.as_view(), name='elogio_create'),
    path('elogios/<int:pk>/', views_elogios_punicoes.ElogioDetailView.as_view(), name='elogio_detail'),
    path('elogios/<int:pk>/editar/', views_elogios_punicoes.ElogioUpdateView.as_view(), name='elogio_update'),
    path('elogios/<int:pk>/excluir/', views_elogios_punicoes.ElogioDeleteView.as_view(), name='elogio_delete'),
    # Redirecionamentos para URLs antigas (compatibilidade)
    path('elogios/oficiais/', views_elogios_punicoes.elogios_oficiais_list_redirect, name='elogios_oficiais_list'),
    path('elogios/pracas/', views_elogios_punicoes.elogios_pracas_list_redirect, name='elogios_pracas_list'),
    
    # URLs para Punições
    path('punicoes/', views_elogios_punicoes.PunicaoListView.as_view(), name='punicao_list'),
    path('punicoes/criar/', views_elogios_punicoes.PunicaoCreateView.as_view(), name='punicao_create'),
    path('punicoes/<int:pk>/', views_elogios_punicoes.PunicaoDetailView.as_view(), name='punicao_detail'),
    path('punicoes/<int:pk>/editar/', views_elogios_punicoes.PunicaoUpdateView.as_view(), name='punicao_update'),
    path('punicoes/<int:pk>/excluir/', views_elogios_punicoes.PunicaoDeleteView.as_view(), name='punicao_delete'),
    # Redirecionamentos para URLs antigas (compatibilidade)
    path('punicoes/oficiais/', views_elogios_punicoes.punicoes_oficiais_list_redirect, name='punicoes_oficiais_list'),
    path('punicoes/pracas/', views_elogios_punicoes.punicoes_pracas_list_redirect, name='punicoes_pracas_list'),
    
    # URLs para Sistema de Login e Sessão
    path('selecionar-funcao-lotacao/', views.selecionar_funcao_lotacao, name='selecionar_funcao_lotacao'),
    path('trocar-funcao-lotacao/', views.trocar_funcao_lotacao, name='trocar_funcao_lotacao'),
    
    # URLs AJAX para carregamento hierárquico
    path('ajax/grandes-comandos/', views.ajax_grandes_comandos, name='ajax_grandes_comandos'),
    
    # URLs para Comissão - Fichas de Conceito
    path('comissao-fichas-oficiais/', views.comissao_fichas_oficiais, name='comissao_fichas_oficiais'),
    path('comissao-fichas-pracas/', views.comissao_fichas_pracas, name='comissao_fichas_pracas'),
    
    # URLs para transferência de militares
    path('militar/<int:militar_id>/transferir/', views.transferir_militar_ajax, name='transferir_militar_ajax'),
    path('ajax/estruturas-organizacionais/', views.obter_estruturas_organizacionais, name='obter_estruturas_organizacionais'),
    path('ajax/unidades/', views.ajax_unidades, name='ajax_unidades'),
    path('ajax/sub-unidades/', views.ajax_sub_unidades, name='ajax_sub_unidades'),
    
    # URLs para Seção de Promoções
    path('secao-promocoes/', views_secao_promocoes.secao_promocoes_list, name='secao_promocoes_list'),
    path('secao-promocoes/dashboard/', views_secao_promocoes.secao_promocoes_dashboard, name='secao_promocoes_dashboard'),
    path('secao-promocoes/nova/', views_secao_promocoes.secao_promocoes_create, name='secao_promocoes_create'),
    path('secao-promocoes/<int:pk>/', views_secao_promocoes.secao_promocoes_detail, name='secao_promocoes_detail'),
    path('secao-promocoes/<int:pk>/editar/', views_secao_promocoes.secao_promocoes_edit, name='secao_promocoes_edit'),
    path('secao-promocoes/<int:pk>/excluir/', views_secao_promocoes.secao_promocoes_delete, name='secao_promocoes_delete'),
    path('secao-promocoes/<int:pk>/ativar/', views_secao_promocoes.secao_promocoes_ativar, name='secao_promocoes_ativar'),
    path('secao-promocoes/<int:pk>/desativar/', views_secao_promocoes.secao_promocoes_desativar, name='secao_promocoes_desativar'),
    
    # URLs para Configuração de Planejadas
    path('configuracao-planejadas/', views_configuracao_planejadas.configuracao_planejadas_list, name='configuracao_planejadas_list'),
    path('configuracao-planejadas/nova/', views_configuracao_planejadas.configuracao_planejadas_create, name='configuracao_planejadas_create'),
    path('configuracao-planejadas/<int:pk>/', views_configuracao_planejadas.configuracao_planejadas_detail, name='configuracao_planejadas_detail'),
    path('configuracao-planejadas/<int:pk>/editar/', views_configuracao_planejadas.configuracao_planejadas_edit, name='configuracao_planejadas_edit'),
    path('configuracao-planejadas/<int:pk>/ativar/', views_configuracao_planejadas.configuracao_planejadas_activate, name='configuracao_planejadas_activate'),
    path('configuracao-planejadas/<int:pk>/excluir/', views_configuracao_planejadas.configuracao_planejadas_delete, name='configuracao_planejadas_delete'),
    path('configuracao-planejadas/ajax/', views_configuracao_planejadas.configuracao_planejadas_ajax, name='configuracao_planejadas_ajax'),
    
    # URLs para Planejadas (Orçamento e Distribuição)
    path('planejadas/', views_planejadas.orcamento_planejadas_list, name='orcamento_planejadas_list'),
    path('planejadas/nova/', views_planejadas.orcamento_planejadas_create, name='orcamento_planejadas_create'),
    path('planejadas/<int:pk>/', views_planejadas.orcamento_planejadas_detail, name='orcamento_planejadas_detail'),
    path('planejadas/<int:pk>/editar/', views_planejadas.orcamento_planejadas_edit, name='orcamento_planejadas_edit'),
    path('planejadas/<int:pk>/excluir/', views_planejadas.orcamento_planejadas_delete, name='orcamento_planejadas_delete'),
    
    
    
    
    
    # URLs para distribuição de orçamento
    path('planejadas/<int:orcamento_id>/distribuir/', views_planejadas.distribuir_orcamento_organizacoes, name='distribuir_orcamento_organizacoes'),
    path('planejadas/organizacao/<str:tipo>/<int:org_id>/', views_planejadas.visualizar_planejadas_organizacao, name='visualizar_planejadas_organizacao'),
    
    # URLs para operações planejadas
    path('operacoes-planejadas/', views_planejadas.planejadas_list, name='planejadas_list'),
    path('operacoes-planejadas/nova/', views_planejadas.planejada_create, name='planejada_create'),
    path('operacoes-planejadas/<int:planejada_id>/', views_planejadas.planejada_detail, name='planejada_detail'),
    path('operacoes-planejadas/<int:planejada_id>/editar/', views_planejadas.planejada_edit, name='planejada_edit'),
    path('operacoes-planejadas/<int:planejada_id>/excluir/', views_planejadas.planejada_delete, name='planejada_delete'),
    
    # APIs para seleção de militares em operações planejadas
    path('operacoes-planejadas/<int:planejada_id>/api/militares-disponiveis/', views_planejadas.api_militares_disponiveis_planejada, name='api_militares_disponiveis_planejada'),
    path('operacoes-planejadas/<int:planejada_id>/api/militares-escalados/', views_planejadas.api_militares_escalados_planejada, name='api_militares_escalados_planejada'),
    path('operacoes-planejadas/<int:planejada_id>/api/adicionar-militar/', views_planejadas.api_adicionar_militar_planejada, name='api_adicionar_militar_planejada'),
    path('operacoes-planejadas/<int:planejada_id>/api/remover-militar/', views_planejadas.api_remover_militar_planejada, name='api_remover_militar_planejada'),
    path('operacoes-planejadas/<int:planejada_id>/api/verificar-folga/<int:militar_id>/', views_planejadas.api_verificar_folga_militar, name='api_verificar_folga_militar'),
    path('operacoes-planejadas/<int:planejada_id>/api/status-tempo/', views_planejadas.api_status_tempo, name='api_status_tempo'),
    path('operacoes-planejadas/<int:planejada_id>/assinaturas/', views_planejadas.api_assinaturas_planejada, name='api_assinaturas_planejada'),
    path('operacoes-planejadas/<int:planejada_id>/pdf/', views_planejadas.planejada_gerar_pdf, name='planejada_gerar_pdf'),
    
    # API genérica para militares (usada na criação)
    path('api/militares-disponiveis/', views_planejadas.api_militares_disponiveis_geral, name='api_militares_disponiveis_geral'),
    path('api/militares-disponiveis-planejada/', views_planejadas.api_militares_disponiveis_planejada_criacao, name='api_militares_disponiveis_planejada_criacao'),
    
    # API para buscar nota por número
    path('api/buscar-nota-por-numero/<str:numero_nota>/', views_planejadas.api_buscar_nota_por_numero, name='api_buscar_nota_por_numero'),
    # API para buscar nota por ID
    path('api/buscar-nota-por-id/<int:nota_id>/', views_planejadas.api_buscar_nota_por_id, name='api_buscar_nota_por_id'),
    # API para assinatura de planejada
    path('api/assinatura-planejada/<int:planejada_id>/<str:tipo>/', views_planejadas.api_assinatura_planejada, name='api_assinatura_planejada'),
    # API para funções do usuário
    path('api/funcoes-usuario/', views_planejadas.api_funcoes_usuario, name='api_funcoes_usuario'),
    
    # API para saldo de OM
    path('api/saldo-om/<str:tipo>/<int:id>/', views_planejadas.api_saldo_om, name='api_saldo_om'),
    # API para valor utilizado
    path('api/valor-utilizado/<str:tipo>/<int:id>/', views_planejadas.api_valor_utilizado, name='api_valor_utilizado'),
    
    # API para militares da planejada
    path('planejadas/<int:planejada_id>/militares/', views_planejadas.planejada_militares, name='planejada_militares'),
    
    # Relatório Mensal de Liquidação
    path('operacoes-planejadas/relatorio-mensal/', views_planejadas.relatorio_mensal_liquidacao, name='relatorio_mensal_liquidacao'),
    
    # Relatório Individual de Militar
    path('operacoes-planejadas/relatorio-individual/', views_planejadas.relatorio_individual_militar, name='relatorio_individual_militar'),
    path('operacoes-planejadas/relatorio-individual/pdf/', views_planejadas.relatorio_individual_militar_pdf, name='relatorio_individual_militar_pdf'),
    
    # ============================================================================
    # TOMBAMENTO DE BENS MÓVEIS
    # ============================================================================
    path('bens-moveis/', views_tombamento.BemMovelListView.as_view(), name='bem_movel_list'),
    path('bens-moveis/criar/', views_tombamento.bem_movel_create, name='bem_movel_create'),
    path('bens-moveis/<int:pk>/', views_tombamento.bem_movel_detail, name='bem_movel_detail'),
    path('bens-moveis/<int:pk>/editar/', views_tombamento.bem_movel_update, name='bem_movel_update'),
    path('bens-moveis/<int:pk>/excluir/', views_tombamento.bem_movel_delete, name='bem_movel_delete'),
    
    path('tombamentos/', views_tombamento.TombamentoBemMovelListView.as_view(), name='tombamento_list'),
    path('tombamentos/criar/', views_tombamento.tombamento_create, name='tombamento_create'),
    path('tombamentos/<int:pk>/editar/', views_tombamento.tombamento_update, name='tombamento_update'),
    path('tombamentos/<int:pk>/excluir/', views_tombamento.tombamento_delete, name='tombamento_delete'),
    
    # ============================================================================
    # ALMOXARIFADO
    # ============================================================================
    path('almoxarifado/produtos/', views_almoxarifado.ProdutoAlmoxarifadoListView.as_view(), name='produto_almoxarifado_list'),
    path('almoxarifado/produtos/json/', views_almoxarifado.produto_almoxarifado_list_json, name='produto_almoxarifado_list_json'),
    path('almoxarifado/produtos/criar/', views_almoxarifado.produto_almoxarifado_create, name='produto_almoxarifado_create'),
    path('almoxarifado/produtos/<int:pk>/', views_almoxarifado.produto_almoxarifado_detail, name='produto_almoxarifado_detail'),
    path('almoxarifado/produtos/<int:pk>/om/', views_almoxarifado.produto_almoxarifado_om, name='produto_almoxarifado_om'),
    path('almoxarifado/produtos/<int:pk>/pdf/', views_almoxarifado.produto_almoxarifado_pdf, name='produto_almoxarifado_pdf'),
    path('ajax/produto-almoxarifado-info/<int:pk>/', views_almoxarifado.produto_almoxarifado_info, name='produto_almoxarifado_info'),
    path('almoxarifado/produtos/<int:pk>/editar/', views_almoxarifado.produto_almoxarifado_update, name='produto_almoxarifado_update'),
    path('almoxarifado/produtos/<int:pk>/localizacao/', views_almoxarifado.produto_almoxarifado_update_localizacao, name='produto_almoxarifado_update_localizacao'),
    path('almoxarifado/produtos/<int:pk>/duplicar/', views_almoxarifado.produto_almoxarifado_duplicate, name='produto_almoxarifado_duplicate'),
    path('almoxarifado/produtos/<int:pk>/excluir/', views_almoxarifado.produto_almoxarifado_delete, name='produto_almoxarifado_delete'),
    path('almoxarifado/produtos/<int:pk>/codigo-barras/', views_almoxarifado.produto_almoxarifado_barcode, name='produto_almoxarifado_barcode'),
    path('almoxarifado/produtos/<int:pk>/qrcode/', views_almoxarifado.produto_almoxarifado_qrcode, name='produto_almoxarifado_qrcode'),
    path('almoxarifado/subcategorias/', views_almoxarifado.subcategorias_ajax, name='subcategorias_ajax'),
    path('almoxarifado/subcategorias/get/', views_almoxarifado.get_subcategorias, name='get_subcategorias'),
    path('almoxarifado/subcategorias/criar/', views_almoxarifado.criar_subcategoria, name='criar_subcategoria'),
    
    # Categorias
    path('almoxarifado/categorias/', views_almoxarifado.CategoriaListView.as_view(), name='categoria_list'),
    path('almoxarifado/categorias/criar/', views_almoxarifado.categoria_create, name='categoria_create'),
    path('almoxarifado/categorias/<int:pk>/editar/', views_almoxarifado.categoria_update, name='categoria_update'),
    path('almoxarifado/categorias/<int:pk>/excluir/', views_almoxarifado.categoria_delete, name='categoria_delete'),
    
    # Subcategorias
    path('almoxarifado/subcategorias/list/', views_almoxarifado.SubcategoriaListView.as_view(), name='subcategoria_list'),
    path('almoxarifado/subcategorias/list/criar/', views_almoxarifado.subcategoria_create, name='subcategoria_create'),
    path('almoxarifado/subcategorias/list/<int:pk>/editar/', views_almoxarifado.subcategoria_update, name='subcategoria_update'),
    path('almoxarifado/subcategorias/list/<int:pk>/excluir/', views_almoxarifado.subcategoria_delete, name='subcategoria_delete'),
    path('almoxarifado/buscar-item/', views_almoxarifado.buscar_item_por_codigo_barras, name='buscar_item_por_codigo_barras'),
    
    path('almoxarifado/entradas/', views_almoxarifado.EntradaAlmoxarifadoListView.as_view(), name='entrada_almoxarifado_list'),
    path('almoxarifado/entradas/criar/', views_almoxarifado.entrada_almoxarifado_create, name='entrada_almoxarifado_create'),
    path('almoxarifado/entradas/<int:pk>/', views_almoxarifado.entrada_almoxarifado_detail, name='entrada_almoxarifado_detail'),
    path('almoxarifado/entradas/<int:pk>/editar/', views_almoxarifado.entrada_almoxarifado_update, name='entrada_almoxarifado_update'),
    path('almoxarifado/entradas/<int:pk>/excluir/', views_almoxarifado.entrada_almoxarifado_delete, name='entrada_almoxarifado_delete'),
    path('almoxarifado/entradas/<int:pk>/pdf/', views_almoxarifado.entrada_almoxarifado_pdf, name='entrada_almoxarifado_pdf'),
    
    path('almoxarifado/saidas/', views_almoxarifado.SaidaAlmoxarifadoListView.as_view(), name='saida_almoxarifado_list'),
    path('almoxarifado/saidas/criar/', views_almoxarifado.saida_almoxarifado_create, name='saida_almoxarifado_create'),
    path('almoxarifado/saidas/<int:pk>/', views_almoxarifado.saida_almoxarifado_detail, name='saida_almoxarifado_detail'),
    path('almoxarifado/saidas/<int:pk>/editar/', views_almoxarifado.saida_almoxarifado_update, name='saida_almoxarifado_update'),
    path('almoxarifado/saidas/<int:pk>/excluir/', views_almoxarifado.saida_almoxarifado_delete, name='saida_almoxarifado_delete'),
    path('almoxarifado/saidas/<int:pk>/assinar/', views_almoxarifado.assinar_saida_almoxarifado, name='saida_almoxarifado_assinar'),
    path('almoxarifado/saidas/<int:pk>/pdf/', views_almoxarifado.saida_almoxarifado_pdf, name='saida_almoxarifado_pdf'),
    
    # Requisições
    path('almoxarifado/requisicoes/', views_requisicao_almoxarifado.RequisicaoAlmoxarifadoListView.as_view(), name='requisicao_almoxarifado_list'),
    path('almoxarifado/requisicoes/criar/', views_requisicao_almoxarifado.requisicao_almoxarifado_create, name='requisicao_almoxarifado_create'),
    path('almoxarifado/requisicoes/<int:pk>/editar/', views_requisicao_almoxarifado.requisicao_almoxarifado_update, name='requisicao_almoxarifado_update'),
    path('almoxarifado/requisicoes/<int:pk>/aprovar/', views_requisicao_almoxarifado.requisicao_almoxarifado_aprovar, name='requisicao_almoxarifado_aprovar'),
    path('almoxarifado/requisicoes/<int:pk>/negar/', views_requisicao_almoxarifado.requisicao_almoxarifado_negar, name='requisicao_almoxarifado_negar'),
    path('almoxarifado/requisicoes/<int:pk>/confirmar-recebimento/', views_requisicao_almoxarifado.requisicao_almoxarifado_confirmar_recebimento, name='requisicao_almoxarifado_confirmar_recebimento'),
    path('almoxarifado/requisicoes/<int:pk>/excluir/', views_requisicao_almoxarifado.requisicao_almoxarifado_excluir, name='requisicao_almoxarifado_excluir'),
    path('almoxarifado/requisicoes/<int:pk>/', views_requisicao_almoxarifado.requisicao_almoxarifado_detail, name='requisicao_almoxarifado_detail'),
    
    # ============================================================================
    # PROCESSOS ADMINISTRATIVOS
    # ============================================================================
    path('processos/', views_processos.ProcessoAdministrativoListView.as_view(), name='processo_administrativo_list'),
    path('processos/criar/', views_processos.processo_administrativo_create, name='processo_administrativo_create'),
    path('processos/proximo-numero/', views_processos.processo_administrativo_proximo_numero, name='processo_administrativo_proximo_numero'),
    path('processos/<int:pk>/', views_processos.processo_administrativo_detail, name='processo_administrativo_detail'),
    path('processos/<int:pk>/editar/', views_processos.processo_administrativo_update, name='processo_administrativo_update'),
    path('processos/<int:pk>/excluir/', views_processos.processo_administrativo_delete, name='processo_administrativo_delete'),
    path('processos/<int:pk>/pdf/', views_processos.processo_administrativo_pdf, name='processo_administrativo_pdf'),
    
    # ============================================================================
    # MÓDULO DE ENSINO
    # Organizado na sequência hierárquica: Curso → Turmas → Disciplinas → Instrutores → Monitores → Alunos → Aulas → Frequências → Notas
    # ============================================================================
    
    # Dashboard
    path('ensino/', views_ensino.dashboard_ensino, name='ensino_dashboard'),
    
    # Dashboards específicos por tipo de usuário
    path('ensino/dashboard/aluno/', views_dashboard_ensino.dashboard_aluno, name='ensino_dashboard_aluno'),
    path('ensino/dashboard/instrutor/', views_dashboard_ensino.dashboard_instrutor, name='ensino_dashboard_instrutor'),
    path('ensino/dashboard/supervisor/', views_dashboard_ensino.dashboard_supervisor, name='ensino_dashboard_supervisor'),
    path('ensino/dashboard/coordenador/', views_dashboard_ensino.dashboard_coordenador, name='ensino_dashboard_coordenador'),
    
    # Login unificado para o módulo de ensino
    path('ensino/login/', views_login_ensino.login_ensino, name='ensino_login'),
    path('ensino/alterar-senha/', views_login_ensino.alterar_senha_primeiro_login, name='ensino_alterar_senha_primeiro_login'),
    path('ensino/alterar-senha/minha/', views_login_ensino.alterar_senha_ensino, name='ensino_alterar_senha'),
    # Redirecionamentos para URLs antigas (compatibilidade)
    path('ensino/login/aluno/', lambda request: redirect('militares:ensino_login'), name='ensino_login_aluno'),
    path('ensino/login/instrutor/', lambda request: redirect('militares:ensino_login'), name='ensino_login_instrutor'),
    path('ensino/login/monitor/', lambda request: redirect('militares:ensino_login'), name='ensino_login_monitor'),
    
    # Controle de Usuários do Módulo de Ensino
    path('ensino/usuarios/', views_usuarios_ensino.usuarios_ensino_listar, name='ensino_usuarios_listar'),
    path('ensino/usuarios/<str:tipo>/<int:pk>/senha/', views_usuarios_ensino.usuario_ensino_definir_senha, name='ensino_usuario_definir_senha'),
    path('ensino/usuarios/<str:tipo>/<int:pk>/detalhes/', views_usuarios_ensino.usuario_ensino_detalhes, name='ensino_usuario_detalhes'),
    
    # 0. PESSOAS EXTERNAS (Auxiliar - usada por outros módulos)
    path('ensino/pessoas-externas/', views_ensino.listar_pessoas_externas, name='ensino_pessoas_externas_listar'),
    path('ensino/pessoas-externas/criar/', views_ensino.criar_pessoa_externa, name='ensino_pessoa_externa_criar'),
    path('ensino/pessoas-externas/<int:pk>/', views_ensino.detalhes_pessoa_externa, name='ensino_pessoa_externa_detalhes'),
    path('ensino/pessoas-externas/<int:pk>/editar/', views_ensino.editar_pessoa_externa, name='ensino_pessoa_externa_editar'),
    
    # 0. EDIÇÕES DE CURSO (Para cursos permanentes)
    path('ensino/edicoes/', views_ensino.listar_edicoes, name='ensino_edicoes_listar'),
    path('ensino/edicoes/criar/', views_ensino.criar_edicao, name='ensino_edicao_criar'),
    path('ensino/edicoes/<int:pk>/', views_ensino.detalhes_edicao, name='ensino_edicao_detalhes'),
    path('ensino/edicoes/<int:pk>/editar/', views_ensino.editar_edicao, name='ensino_edicao_editar'),
    path('ensino/edicoes/<int:pk>/deletar/', views_ensino.deletar_edicao, name='ensino_edicao_deletar'),
    path('ensino/edicoes/<int:pk>/resultado-final/', views_ensino.resultado_final_edicao, name='ensino_edicao_resultado_final'),
    path('ensino/edicoes/por-curso/<int:curso_id>/', views_ensino.edicoes_por_curso_json, name='ensino_edicoes_por_curso_json'),
    
    # 1. CURSOS (Nível Principal)
    path('ensino/cursos/', views_ensino.listar_cursos, name='ensino_cursos_listar'),
    path('ensino/cursos/criar/', views_ensino.criar_curso, name='ensino_curso_criar'),
    path('ensino/cursos/<int:pk>/', views_ensino.detalhes_curso, name='ensino_curso_detalhes'),
    path('ensino/cursos/<int:pk>/editar/', views_ensino.editar_curso, name='ensino_curso_editar'),
    path('ensino/cursos/<int:pk>/disciplinas/', views_ensino.disciplinas_curso_json, name='ensino_curso_disciplinas_json'),
    
    # 2. TURMAS (Dependem de Curso e podem ter Edição)
    path('ensino/turmas/', views_ensino.listar_turmas, name='ensino_turmas_listar'),
    path('ensino/turmas/criar/', views_ensino.criar_turma, name='ensino_turma_criar'),
    path('ensino/turmas/<int:pk>/', views_ensino.detalhes_turma, name='ensino_turma_detalhes'),
    path('ensino/turmas/<int:pk>/dashboard/', views_ensino.dashboard_turma, name='ensino_turma_dashboard'),
    path('ensino/turmas/<int:turma_id>/disciplinas/<int:disciplina_id>/caderneta-frequencia/', views_ensino.caderneta_frequencia_disciplina, name='ensino_caderneta_frequencia_disciplina'),
    path('ensino/turmas/<int:pk>/editar/', views_ensino.editar_turma, name='ensino_turma_editar'),
    path('ensino/turmas/<int:pk>/excluir/', views_ensino.excluir_turma, name='ensino_turma_excluir'),
    path('ensino/turmas/<int:turma_id>/disciplinas/<int:disciplina_id>/trocar-instrutor-monitor/', views_ensino.trocar_instrutor_monitor_disciplina, name='ensino_trocar_instrutor_monitor'),
    
    # 3. DISCIPLINAS (Relacionadas a Curso e Turma)
    path('ensino/disciplinas/', views_ensino.listar_disciplinas, name='ensino_disciplinas_listar'),
    path('ensino/disciplinas/criar/', views_ensino.criar_disciplina, name='ensino_disciplina_criar'),
    path('ensino/disciplinas/<int:pk>/', views_ensino.detalhes_disciplina, name='ensino_disciplina_detalhes'),
    path('ensino/disciplinas/<int:pk>/editar/', views_ensino.editar_disciplina, name='ensino_disciplina_editar'),
    path('ensino/disciplinas/<int:pk>/deletar/', views_ensino.deletar_disciplina, name='ensino_disciplina_deletar'),
    
    # 4. INSTRUTORES (Relacionados a Turma e Disciplina)
    path('ensino/instrutores/', views_ensino.listar_instrutores, name='ensino_instrutores_listar'),
    path('ensino/instrutores/criar/', views_ensino.criar_instrutor, name='ensino_instrutor_criar'),
    path('ensino/instrutores/<int:pk>/', views_ensino.detalhes_instrutor, name='ensino_instrutor_detalhes'),
    path('ensino/instrutores/<int:pk>/editar/', views_ensino.editar_instrutor, name='ensino_instrutor_editar'),
    path('ensino/instrutores/<int:pk>/excluir/', views_ensino.excluir_instrutor, name='ensino_instrutor_excluir'),
    path('ensino/instrutores/<int:pk>/ficha-pdf/', views_ensino.ficha_instrutor_pdf, name='ensino_instrutor_ficha_pdf'),
    
    # 5. MONITORES (Relacionados a Turma)
    path('ensino/monitores/', views_ensino.listar_monitores, name='ensino_monitores_listar'),
    path('ensino/monitores/criar/', views_ensino.criar_monitor, name='ensino_monitor_criar'),
    path('ensino/monitores/<int:pk>/', views_ensino.detalhes_monitor, name='ensino_monitor_detalhes'),
    path('ensino/monitores/<int:pk>/editar/', views_ensino.editar_monitor, name='ensino_monitor_editar'),
    path('ensino/monitores/<int:pk>/excluir/', views_ensino.excluir_monitor, name='ensino_monitor_excluir'),
    
    # 6. ALUNOS (Relacionados a Turma)
    path('ensino/alunos/', views_ensino.listar_alunos, name='ensino_alunos_listar'),
    path('ensino/alunos/criar/', views_ensino.criar_aluno, name='ensino_aluno_criar'),
    path('ensino/alunos/<int:pk>/', views_ensino.detalhes_aluno, name='ensino_aluno_detalhes'),
    path('ensino/alunos/<int:pk>/editar/', views_ensino.editar_aluno, name='ensino_aluno_editar'),
    path('ensino/alunos/<int:pk>/desligar/', views_ensino.desligar_aluno, name='ensino_aluno_desligar'),
    path('ensino/alunos/<int:pk>/reativar/', views_ensino.reativar_aluno, name='ensino_aluno_reativar'),
    path('ensino/alunos/<int:pk>/ficha-pdf/', views_ensino.ficha_aluno_pdf, name='ensino_aluno_ficha_pdf'),
    
    # 7. AULAS (Relacionadas a Turma e Disciplina)
    path('ensino/aulas/', views_ensino.listar_aulas, name='ensino_aulas_listar'),
    path('ensino/aulas/criar/', views_ensino.criar_aula, name='ensino_aula_criar'),
    path('ensino/aulas/<int:pk>/', views_ensino.detalhes_aula, name='ensino_aula_detalhes'),
    path('ensino/aulas/<int:pk>/editar/', views_ensino.editar_aula, name='ensino_aula_editar'),
    path('ensino/aulas/<int:pk>/deletar/', views_ensino.deletar_aula, name='ensino_aula_deletar'),
    path('ensino/aulas/<int:pk>/chamada/', views_ensino.registrar_chamada_aula, name='ensino_aula_registrar_chamada'),
    path('ensino/turmas/<int:turma_id>/dados/', views_ensino.obter_dados_turma, name='ensino_turma_dados'),
    path('ensino/turmas/<int:turma_id>/alunos/', views_ensino.obter_alunos_turma, name='ensino_turma_alunos'),
    path('ensino/disciplinas/<int:disciplina_id>/dados/', views_ensino.obter_dados_disciplina, name='ensino_disciplina_dados'),
    path('ensino/quadros-trabalho-semanal/<int:quadro_id>/ultimo-horario-dia/<str:dia_semana>/', views_ensino.obter_ultimo_horario_dia, name='ensino_quadro_ultimo_horario_dia'),
    
    # 9. AVALIAÇÕES E NOTAS (Relacionadas a Turma, Disciplina e Aluno)
    path('ensino/avaliacoes/', views_ensino.listar_avaliacoes, name='ensino_avaliacoes_listar'),
    path('ensino/avaliacoes/criar/', views_ensino.criar_avaliacao, name='ensino_avaliacao_criar'),
    path('ensino/avaliacoes/<int:pk>/', views_ensino.detalhes_avaliacao, name='ensino_avaliacao_detalhes'),
    path('ensino/avaliacoes/<int:pk>/editar/', views_ensino.editar_avaliacao, name='ensino_avaliacao_editar'),
    path('ensino/avaliacoes/<int:pk>/deletar/', views_ensino.deletar_avaliacao, name='ensino_avaliacao_deletar'),
    path('ensino/avaliacoes/<int:avaliacao_id>/lancar-notas/', views_ensino.lancar_notas, name='ensino_avaliacao_lancar_notas'),
    path('ensino/turmas/<int:turma_id>/disciplinas/<int:disciplina_id>/inserir-notas/', views_ensino.inserir_notas_disciplina, name='ensino_inserir_notas_disciplina'),
    path('ensino/avaliacoes/nota/<int:nota_id>/revisao/solicitar/', views_ensino.solicitar_revisao_prova, name='ensino_solicitar_revisao_prova'),
    path('ensino/avaliacoes/nota/<int:nota_id>/revisao/solicitar/form/', views_ensino.solicitar_revisao_prova_form, name='ensino_revisao_solicitar_form'),
    path('ensino/revisoes/<int:pedido_id>/despachar-instrutor/', views_ensino.ensino_despachar_revisao_para_instrutor, name='ensino_despachar_revisao_instrutor'),
    path('ensino/revisoes/<int:pedido_id>/instrutor-parecer/', views_ensino.instrutor_parecer_revisao, name='ensino_instrutor_parecer_revisao'),
    path('ensino/revisoes/<int:pedido_id>/aluno-recorrer-diretoria/', views_ensino.aluno_recorrer_diretoria, name='ensino_aluno_recorrer_diretoria'),
    path('ensino/revisoes/<int:pedido_id>/aluno-reenviar/', views_ensino.aluno_reenviar_recurso, name='ensino_aluno_reenviar_recurso'),
    path('ensino/revisoes/<int:pedido_id>/nomear-comissao/', views_ensino.ensino_nomear_comissao_revisao, name='ensino_nomear_comissao_revisao'),
    path('ensino/revisoes/<int:pedido_id>/comissao-parecer-final/', views_ensino.comissao_parecer_revisao, name='ensino_comissao_parecer_final'),
    path('ensino/revisoes/<int:pedido_id>/detalhes/', views_ensino.pedido_revisao_detalhes, name='ensino_pedido_revisao_detalhes'),
    
    # CERTIFICADOS (Relacionados a Aluno, Curso e Turma)
    path('ensino/certificados/', views_ensino.listar_certificados, name='ensino_certificados_listar'),
    
    # QUADRO DE TRABALHO SEMANAL
    path('ensino/quadros-trabalho-semanal/', views_ensino.listar_quadros_trabalho_semanal, name='ensino_quadros_trabalho_semanal_listar'),
    path('ensino/quadros-trabalho-semanal/criar/', views_ensino.criar_quadro_trabalho_semanal, name='ensino_quadro_trabalho_semanal_criar'),
    path('ensino/quadros-trabalho-semanal/<int:pk>/', views_ensino.visualizar_quadro_trabalho_semanal, name='ensino_quadro_trabalho_semanal_visualizar'),
    path('ensino/quadros-trabalho-semanal/<int:pk>/pdf/', views_ensino.quadro_trabalho_semanal_pdf, name='ensino_quadro_trabalho_semanal_pdf'),
    path('ensino/quadros-trabalho-semanal/<int:pk>/editar/', views_ensino.editar_quadro_trabalho_semanal, name='ensino_quadro_trabalho_semanal_editar'),
    path('ensino/quadros-trabalho-semanal/<int:pk>/deletar/', views_ensino.deletar_quadro_trabalho_semanal, name='ensino_quadro_trabalho_semanal_deletar'),
    path('ensino/turmas/<int:turma_id>/quadro-trabalho-semanal/', views_ensino.visualizar_quadro_trabalho_semanal_turma, name='ensino_quadro_trabalho_semanal_turma'),
    path('ensino/quadros-trabalho-semanal/<int:quadro_id>/adicionar-aula/', views_ensino.adicionar_aula_quadro_trabalho_semanal, name='ensino_quadro_trabalho_semanal_adicionar_aula'),
    # Assinaturas QTS
    path('ensino/quadros-trabalho-semanal/<int:pk>/dados-assinatura/', views_assinaturas_qts.dados_assinatura_qts, name='ensino_qts_dados_assinatura'),
    path('ensino/quadros-trabalho-semanal/<int:pk>/assinar-revisao/', views_assinaturas_qts.assinar_qts_revisao, name='ensino_qts_assinar_revisao'),
    path('ensino/quadros-trabalho-semanal/<int:pk>/assinar-aprovacao/', views_assinaturas_qts.assinar_qts_aprovacao, name='ensino_qts_assinar_aprovacao'),
    path('ensino/quadros-trabalho-semanal/<int:pk>/retirar-assinatura/<int:assinatura_pk>/', views_assinaturas_qts.retirar_assinatura_qts, name='ensino_qts_retirar_assinatura'),
    path('ensino/quadros-trabalho-semanal/aulas/<int:pk>/editar/', views_ensino.editar_aula_quadro_trabalho_semanal, name='ensino_aula_quadro_trabalho_semanal_editar'),
    path('ensino/quadros-trabalho-semanal/aulas/<int:pk>/deletar/', views_ensino.deletar_aula_quadro_trabalho_semanal, name='ensino_aula_quadro_trabalho_semanal_deletar'),
    
    # ============================================================================
    # MODELOS ITE 01/2024 - DEIP/CBMEPI
    # ============================================================================
    
    # PLANO GERAL DE ENSINO
    path('ensino/ite/planos-gerais/', views_ensino.listar_planos_gerais_ensino, name='ensino_planos_gerais_listar'),
    path('ensino/ite/planos-gerais/criar/', views_ensino.criar_plano_geral_ensino, name='ensino_planos_gerais_criar'),
    path('ensino/ite/planos-gerais/<int:pk>/', views_ensino.detalhes_plano_geral_ensino, name='ensino_planos_gerais_detalhes'),
    
    # PROJETO PEDAGÓGICO
    path('ensino/ite/projetos-pedagogicos/', views_ensino.listar_projetos_pedagogicos, name='ensino_projetos_pedagogicos_listar'),
    path('ensino/ite/projetos-pedagogicos/criar/', views_ensino.criar_projeto_pedagogico, name='ensino_projetos_pedagogicos_criar'),
    path('ensino/ite/projetos-pedagogicos/criar/<int:curso_id>/', views_ensino.criar_projeto_pedagogico, name='ensino_projetos_pedagogicos_criar_curso'),
    path('ensino/ite/projetos-pedagogicos/<int:pk>/', views_ensino.detalhes_projeto_pedagogico, name='ensino_projetos_pedagogicos_detalhes'),
    
    # PLANO DE CURSO/ESTÁGIO
    path('ensino/ite/planos-curso-estagio/', views_ensino.listar_planos_curso_estagio, name='ensino_planos_curso_estagio_listar'),
    path('ensino/ite/planos-curso-estagio/criar/', views_ensino.criar_plano_curso_estagio, name='ensino_planos_curso_estagio_criar'),
    path('ensino/ite/planos-curso-estagio/criar/<int:projeto_id>/', views_ensino.criar_plano_curso_estagio, name='ensino_planos_curso_estagio_criar_projeto'),
    path('ensino/ite/planos-curso-estagio/<int:pk>/', views_ensino.detalhes_plano_curso_estagio, name='ensino_planos_curso_estagio_detalhes'),
    
    # PROCESSO DE SELEÇÃO DE ALUNOS
    path('ensino/ite/processos-selecao/', views_ensino.listar_processos_selecao, name='ensino_processos_selecao_listar'),
    path('ensino/ite/processos-selecao/criar/', views_ensino.criar_processo_selecao, name='ensino_processos_selecao_criar'),
    path('ensino/ite/processos-selecao/criar/<int:curso_id>/', views_ensino.criar_processo_selecao, name='ensino_processos_selecao_criar_curso'),
    path('ensino/ite/processos-selecao/<int:pk>/', views_ensino.detalhes_processo_selecao, name='ensino_processos_selecao_detalhes'),
    
    # RELATÓRIO ANUAL DA DEIP
    path('ensino/ite/relatorios-anuais/', views_ensino.listar_relatorios_anuais_deip, name='ensino_relatorios_anuais_listar'),
    path('ensino/ite/relatorios-anuais/criar/', views_ensino.criar_relatorio_anual_deip, name='ensino_relatorios_anuais_criar'),
    path('ensino/ite/relatorios-anuais/<int:pk>/', views_ensino.detalhes_relatorio_anual_deip, name='ensino_relatorios_anuais_detalhes'),
    
    # TRABALHO DE CONCLUSÃO DE CURSO (TCC)
    path('ensino/ite/tccs/', views_ensino.listar_trabalhos_conclusao_curso, name='ensino_tccs_listar'),
    path('ensino/ite/tccs/criar/', views_ensino.criar_trabalho_conclusao_curso, name='ensino_tccs_criar'),
    path('ensino/ite/tccs/criar/<int:aluno_id>/', views_ensino.criar_trabalho_conclusao_curso, name='ensino_tccs_criar_aluno'),
    path('ensino/ite/tccs/<int:pk>/', views_ensino.detalhes_trabalho_conclusao_curso, name='ensino_tccs_detalhes'),
    path('ensino/ite/tccs/<int:pk>/editar/', views_ensino.editar_trabalho_conclusao_curso, name='ensino_tccs_editar'),
    
    # PLANO DE SEGURANÇA
    path('ensino/ite/planos-seguranca/', views_ensino.listar_planos_seguranca, name='ensino_planos_seguranca_listar'),
    path('ensino/ite/planos-seguranca/criar/', views_ensino.criar_plano_seguranca, name='ensino_planos_seguranca_criar'),
    path('ensino/ite/planos-seguranca/criar/curso/<int:curso_id>/', views_ensino.criar_plano_seguranca, name='ensino_planos_seguranca_criar_curso'),
    path('ensino/ite/planos-seguranca/criar/turma/<int:turma_id>/', views_ensino.criar_plano_seguranca, name='ensino_planos_seguranca_criar_turma'),
    path('ensino/ite/planos-seguranca/criar/disciplina/<int:disciplina_id>/', views_ensino.criar_plano_seguranca, name='ensino_planos_seguranca_criar_disciplina'),
    path('ensino/ite/planos-seguranca/criar/aula/<int:aula_id>/', views_ensino.criar_plano_seguranca, name='ensino_planos_seguranca_criar_aula'),
    path('ensino/ite/planos-seguranca/<int:pk>/', views_ensino.detalhes_plano_seguranca, name='ensino_planos_seguranca_detalhes'),
    path('ensino/ite/planos-seguranca/<int:pk>/editar/', views_ensino.editar_plano_seguranca, name='ensino_planos_seguranca_editar'),
    
    # CLASSIFICAÇÃO FINAL DO CURSO
    path('ensino/ite/classificacoes-finais/', views_ensino.listar_classificacoes_finais, name='ensino_classificacoes_finais_listar'),
    path('ensino/ite/classificacoes-finais/turma/<int:turma_id>/', views_ensino.listar_classificacoes_finais, name='ensino_classificacoes_finais_turma'),
    path('ensino/ite/classificacoes-finais/turma/<int:turma_id>/calcular/', views_ensino.calcular_classificacao_final, name='ensino_classificacoes_finais_calcular'),
    path('ensino/ite/classificacoes-finais/<int:pk>/', views_ensino.detalhes_classificacao_final, name='ensino_classificacoes_finais_detalhes'),
    
    # PLANO DE PALESTRA
    path('ensino/ite/planos-palestra/', views_ensino.listar_planos_palestra, name='ensino_planos_palestra_listar'),
    path('ensino/ite/planos-palestra/criar/', views_ensino.criar_plano_palestra, name='ensino_planos_palestra_criar'),
    path('ensino/ite/planos-palestra/criar/curso/<int:curso_id>/', views_ensino.criar_plano_palestra, name='ensino_planos_palestra_criar_curso'),
    path('ensino/ite/planos-palestra/criar/turma/<int:turma_id>/', views_ensino.criar_plano_palestra, name='ensino_planos_palestra_criar_turma'),
    path('ensino/ite/planos-palestra/<int:pk>/', views_ensino.detalhes_plano_palestra, name='ensino_planos_palestra_detalhes'),
    
    # ATIVIDADE DE TREINAMENTO DE CAMPO (ATC)
    path('ensino/ite/atcs/', views_ensino.listar_atividades_treinamento_campo, name='ensino_atcs_listar'),
    path('ensino/ite/atcs/criar/', views_ensino.criar_atividade_treinamento_campo, name='ensino_atcs_criar'),
    path('ensino/ite/atcs/criar/curso/<int:curso_id>/', views_ensino.criar_atividade_treinamento_campo, name='ensino_atcs_criar_curso'),
    path('ensino/ite/atcs/criar/turma/<int:turma_id>/', views_ensino.criar_atividade_treinamento_campo, name='ensino_atcs_criar_turma'),
    path('ensino/ite/atcs/<int:pk>/', views_ensino.detalhes_atividade_treinamento_campo, name='ensino_atcs_detalhes'),
    
    # ATIVIDADE COMPLEMENTAR DE ENSINO (ACE)
    path('ensino/ite/aces/', views_ensino.listar_atividades_complementares, name='ensino_aces_listar'),
    path('ensino/ite/aces/criar/', views_ensino.criar_atividade_complementar, name='ensino_aces_criar'),
    path('ensino/ite/aces/criar/curso/<int:curso_id>/', views_ensino.criar_atividade_complementar, name='ensino_aces_criar_curso'),
    path('ensino/ite/aces/criar/turma/<int:turma_id>/', views_ensino.criar_atividade_complementar, name='ensino_aces_criar_turma'),
    path('ensino/ite/aces/<int:pk>/', views_ensino.detalhes_atividade_complementar, name='ensino_aces_detalhes'),
    
    # TESTE DE CONHECIMENTOS PROFISSIONAIS (TCP)
    path('ensino/ite/tcps/', views_ensino.listar_testes_conhecimentos_profissionais, name='ensino_tcps_listar'),
    path('ensino/ite/tcps/criar/', views_ensino.criar_teste_conhecimentos_profissionais, name='ensino_tcps_criar'),
    path('ensino/ite/tcps/<int:pk>/', views_ensino.detalhes_teste_conhecimentos_profissionais, name='ensino_tcps_detalhes'),
    
    # PLANO DE ESTÁGIO DE NIVELAMENTO PROFISSIONAL
    path('ensino/ite/planos-estagio-nivelamento/', views_ensino.listar_planos_estagio_nivelamento, name='ensino_planos_estagio_nivelamento_listar'),
    path('ensino/ite/planos-estagio-nivelamento/criar/', views_ensino.criar_plano_estagio_nivelamento, name='ensino_planos_estagio_nivelamento_criar'),
    path('ensino/ite/planos-estagio-nivelamento/<int:pk>/', views_ensino.detalhes_plano_estagio_nivelamento, name='ensino_planos_estagio_nivelamento_detalhes'),
    
]
