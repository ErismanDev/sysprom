from django.urls import path
from django.http import JsonResponse
from . import views
from . import views_simples
from . import views_pracas
from . import views_unificadas
from . import views_quadros_html
from . import views_ajax
from . import views_atas_melhoradas
from . import views_atas_padrao
from . import views_ajax_atas
from .views import reordenar_numeracoes_view
from .views_sessao_pdf import sessao_gerar_pdf_completo, upload_arquivos_sessao, testar_pdf
from .usuario_views import redirect_usuario_ficha, welcome_usuario, mark_welcome_shown
from django.db.models import Q
from .models import Militar
from django.shortcuts import redirect

app_name = 'militares'

def militar_autocomplete(request):
    """View para autocomplete de militares"""
    q = request.GET.get('q', '')
    if len(q) < 2:
        return JsonResponse({'results': []})
    
    militares = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T']  # Apenas oficiais
    ).filter(
        Q(nome_completo__icontains=q) |
        Q(nome_guerra__icontains=q) |
        Q(matricula__icontains=q)
    ).order_by('nome_completo')[:10]
    
    results = []
    for militar in militares:
        results.append({
            'id': militar.id,
            'text': f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula}",
        })
    
    return JsonResponse({'results': results})

def redirect_voto_detail(request, pk):
    return redirect('militares:voto_visualizar_assinar', pk=pk)

urlpatterns = [
    # Dashboard e páginas principais
    path('', views.militar_dashboard, name='militar_dashboard'),
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
    
    # Militares
    path('militares/', views_simples.militar_list_simples, name='militar_list'),
    path('militares-original/', views.militar_list, name='militar_list_original'),
    path('militares/exportar-excel/', views.exportar_militares_excel, name='exportar_excel'),

    path('militares/novo/', views.militar_create, name='militar_create'),
    path('militares/<int:pk>/', views.militar_detail, name='militar_detail'),
    path('militares/<int:pk>/editar/', views.militar_update, name='militar_edit'),
    path('militares/<int:pk>/excluir/', views.militar_delete, name='militar_delete'),

    
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
    
    # Autenticação
    path('register/', views.register, name='register'),
    
    # Interstícios
    path('intersticios/', views.intersticio_list, name='intersticio_list'),
    path('intersticios/gerenciar/', views.intersticio_manage, name='intersticio_manage'),
    path('intersticios/criar/', views.intersticio_create, name='intersticio_create'),
    path('intersticios/<int:pk>/excluir/', views.intersticio_delete, name='intersticio_delete'),
    
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
    path('comissao/<int:comissao_pk>/membros/adicionar/', views.membro_comissao_add, name='membro_comissao_add'),
    path('comissao/<int:comissao_pk>/membros/<int:pk>/editar/', views.membro_comissao_update, name='membro_comissao_update'),
    path('comissao/<int:comissao_pk>/membros/<int:pk>/excluir/', views.membro_comissao_delete, name='membro_comissao_delete'),
    
    # Sessões da Comissão
    path('comissao/sessoes/', views.sessao_comissao_list, name='sessao_comissao_list'),
    path('comissao/sessoes/nova/', views.sessao_comissao_create, name='sessao_comissao_create'),
    path('comissao/sessoes/<int:pk>/', views.sessao_comissao_detail, name='sessao_comissao_detail'),
    path('comissao/sessoes/<int:pk>/editar/', views.sessao_comissao_update, name='sessao_comissao_update'),
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
] 
urlpatterns += [
    path('militar-autocomplete/', militar_autocomplete, name='militar-autocomplete'),
] 
urlpatterns += [
    path('militares/reordenar/', reordenar_numeracoes_view, name='militares_reordenar'),
] 
urlpatterns += [
    path('usuarios/custom/', views.usuarios_custom_list, name='usuarios_custom_list'),
    path('usuarios/novo/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:pk>/', views.usuario_detail, name='usuario_detail'),
    path('usuarios/<int:pk>/editar/', views.usuario_update, name='usuario_update'),
    path('usuarios/<int:pk>/excluir/', views.usuario_delete, name='usuario_delete'),
    path('usuarios/<int:pk>/funcoes/', views.usuario_funcoes_list, name='usuario_funcoes_list'),
    path('usuarios/<int:pk>/funcoes/adicionar/', views.usuario_funcao_add, name='usuario_funcao_add'),
    path('usuarios/<int:pk>/funcoes/<int:funcao_pk>/editar/', views.usuario_funcao_edit, name='usuario_funcao_edit'),
    path('usuarios/<int:pk>/funcoes/<int:funcao_pk>/excluir/', views.usuario_funcao_delete, name='usuario_funcao_delete'),
    path('cargos/<int:cargo_id>/adicionar-usuario/', views.adicionar_usuario_cargo, name='adicionar_usuario_cargo'),
    
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
    path('cargos/', views.cargo_funcao_list, name='cargo_funcao_list'),
    path('cargos/novo/', views.cargo_funcao_create, name='cargo_funcao_create'),
    path('cargos/<int:cargo_id>/', views.cargo_funcao_detail, name='cargo_funcao_detail'),
    path('cargos/<int:cargo_id>/editar/', views.cargo_funcao_update, name='cargo_funcao_update'),
    path('cargos/<int:cargo_id>/excluir/', views.cargo_funcao_delete, name='cargo_funcao_delete'),
]
