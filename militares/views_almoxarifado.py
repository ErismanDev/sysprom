"""
Views para o módulo de Almoxarifado
Gerencia o cadastro e controle de itens, entradas e saídas do almoxarifado
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from io import BytesIO
from decimal import Decimal, InvalidOperation
import qrcode
import json
import logging

from .models import (
    ProdutoAlmoxarifado, EntradaAlmoxarifado, SaidaAlmoxarifado, HistoricoAlmoxarifado, 
    RequisicaoAlmoxarifado, Orgao, GrandeComando, Unidade, SubUnidade, Militar, 
    CategoriaMaterial, Categoria, Subcategoria, 
    EntradaAlmoxarifadoProduto, SaidaAlmoxarifadoProduto, AssinaturaSaidaAlmoxarifado,
    ProdutoAlmoxarifadoLocalizacao
)
from .forms import ProdutoAlmoxarifadoForm, EntradaAlmoxarifadoForm, SaidaAlmoxarifadoForm, RequisicaoAlmoxarifadoForm
from .permissoes_sistema import tem_permissao
from .views_almoxarifado_pdf import entrada_almoxarifado_pdf, saida_almoxarifado_pdf, produto_almoxarifado_pdf
from .permissoes_militares import obter_sessao_ativa_usuario
from .filtros_hierarquicos import (
    aplicar_filtro_hierarquico_entradas_almoxarifado, 
    aplicar_filtro_hierarquico_saidas_almoxarifado,
    aplicar_filtro_hierarquico_itens_almoxarifado
)
from .filtros_hierarquicos_pesquisa import obter_opcoes_filtro_hierarquico_itens_almoxarifado


# ============================================================================
# VIEWS PARA ITENS DO ALMOXARIFADO
# ============================================================================

class ProdutoAlmoxarifadoListView(LoginRequiredMixin, ListView):
    model = ProdutoAlmoxarifado
    template_name = 'militares/item_almoxarifado_list.html'
    context_object_name = 'itens'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Permite que todos os usuários autenticados visualizem
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Listar todos os itens - sem filtro hierárquico para permitir que todos visualizem
        queryset = ProdutoAlmoxarifado.objects.select_related('criado_por').order_by('codigo')
        
        # Filtro hierárquico removido para permitir que todos vejam todos os produtos
        # funcao_usuario = obter_sessao_ativa_usuario(self.request.user)
        # if funcao_usuario:
        #     queryset = aplicar_filtro_hierarquico_itens_almoxarifado(queryset, funcao_usuario, self.request.user)

        search = self.request.GET.get('search', '')
        categoria = self.request.GET.get('categoria', '')
        status_estoque = self.request.GET.get('status_estoque', '')
        ativo = self.request.GET.get('ativo', '')
        om_filtro = self.request.GET.get('om', '')

        # Quando há filtro de OM, não filtrar por OM padrão do produto
        # Em vez disso, vamos listar todos os produtos e calcular o estoque por OM depois
        # Isso permite ver produtos que têm estoque na OM através de transferências
        # (o filtro será aplicado no get_context_data calculando estoque por OM)

        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search) |
                Q(descricao__icontains=search) |
                Q(marca__icontains=search) |
                Q(modelo__icontains=search) |
                Q(tamanho__icontains=search)
            )

        if categoria:
            try:
                queryset = queryset.filter(categoria_id=categoria)
            except:
                pass

        # Status de estoque será calculado por OM no get_context_data se houver filtro de OM
        if status_estoque and not om_filtro:
            if status_estoque == 'ESGOTADO':
                queryset = queryset.filter(quantidade_atual__lte=0)
            elif status_estoque == 'CRITICO':
                queryset = queryset.filter(quantidade_atual__lte=F('estoque_minimo')).exclude(quantidade_atual__lte=0)
            elif status_estoque == 'NORMAL':
                queryset = queryset.filter(
                    quantidade_atual__gt=F('estoque_minimo'),
                    quantidade_atual__lt=F('estoque_maximo')
                )

        if ativo == '1':
            queryset = queryset.filter(ativo=True)
        elif ativo == '0':
            queryset = queryset.filter(ativo=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['categoria'] = self.request.GET.get('categoria', '')
        context['status_estoque'] = self.request.GET.get('status_estoque', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        context['om'] = self.request.GET.get('om', '')
        
        # Permissões e usuário
        user = self.request.user
        
        # Obter opções de filtro hierárquico para OM
        funcao_usuario = obter_sessao_ativa_usuario(user)
        if funcao_usuario:
            context['opcoes_om'] = obter_opcoes_filtro_hierarquico_itens_almoxarifado(funcao_usuario, user)
        else:
            context['opcoes_om'] = []

        try:
            context['categorias'] = Categoria.objects.filter(ativo=True).order_by('nome')
        except Exception as e:
            # Se a tabela ainda não existir ou houver erro, usar lista vazia
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao buscar categorias: {e}")
            context['categorias'] = []

        # Obter informações da OM selecionada para cálculo de estoque
        om_filtro = self.request.GET.get('om', '')
        orgao_om = None
        grande_comando_om = None
        unidade_om = None
        sub_unidade_om = None
        nome_om_filtro = None
        om_dentro_escopo = False
        
        if om_filtro:
            from .models import Orgao, GrandeComando, Unidade, SubUnidade
            try:
                if om_filtro.startswith('orgao_'):
                    orgao_id = int(om_filtro.split('_')[1])
                    orgao_om = Orgao.objects.get(pk=orgao_id)
                    nome_om_filtro = str(orgao_om)
                elif om_filtro.startswith('gc_'):
                    gc_id = int(om_filtro.split('_')[1])
                    grande_comando_om = GrandeComando.objects.get(pk=gc_id)
                    nome_om_filtro = str(grande_comando_om)
                elif om_filtro.startswith('unidade_'):
                    unidade_id = int(om_filtro.split('_')[1])
                    unidade_om = Unidade.objects.get(pk=unidade_id)
                    nome_om_filtro = str(unidade_om)
                elif om_filtro.startswith('sub_'):
                    sub_id = int(om_filtro.split('_')[1])
                    sub_unidade_om = SubUnidade.objects.get(pk=sub_id)
                    nome_om_filtro = str(sub_unidade_om)
                
                # Verificar se a OM selecionada está dentro do escopo hierárquico do usuário
                if funcao_usuario:
                    om_dentro_escopo = funcao_usuario.pode_acessar_lotacao(
                        orgao=orgao_om,
                        grande_comando=grande_comando_om,
                        unidade=unidade_om,
                        sub_unidade=sub_unidade_om
                    )
                elif user and user.is_superuser:
                    # Superusuário tem acesso a todas as OMs
                    om_dentro_escopo = True
                    
            except (ValueError, Orgao.DoesNotExist, GrandeComando.DoesNotExist, Unidade.DoesNotExist, SubUnidade.DoesNotExist):
                pass
        
        context['orgao_om'] = orgao_om
        context['grande_comando_om'] = grande_comando_om
        context['unidade_om'] = unidade_om
        context['sub_unidade_om'] = sub_unidade_om
        context['nome_om_filtro'] = nome_om_filtro
        context['om_dentro_escopo'] = om_dentro_escopo
        
        # Calcular estoque por OM para cada item se houver filtro de OM E a OM estiver dentro do escopo
        if om_filtro and (orgao_om or grande_comando_om or unidade_om or sub_unidade_om):
            if om_dentro_escopo:
                itens_com_estoque = []
                status_estoque_filtro = context['status_estoque']
                
                for item in context['itens']:
                    try:
                        # Calcular estoque total (soma de todas as OMs)
                        item.estoque_total = item.get_estoque_total()
                        
                        # Calcular estoque na OM filtrada
                        estoque_om = item.get_estoque_por_om(
                            orgao=orgao_om,
                            grande_comando=grande_comando_om,
                            unidade=unidade_om,
                            sub_unidade=sub_unidade_om
                        )
                        # Adicionar estoque calculado como atributo do item
                        item.estoque_om = estoque_om
                        
                        # Filtrar por status de estoque se solicitado
                        if status_estoque_filtro:
                            if status_estoque_filtro == 'ESGOTADO' and estoque_om > 0:
                                continue
                            elif status_estoque_filtro == 'CRITICO' and (estoque_om <= 0 or estoque_om > item.estoque_minimo):
                                continue
                            elif status_estoque_filtro == 'NORMAL' and (estoque_om <= item.estoque_minimo or estoque_om >= item.estoque_maximo):
                                continue
                        
                        # Incluir todos os itens (mesmo com estoque 0) para mostrar que existem mas não têm estoque na OM
                        itens_com_estoque.append(item)
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f'Erro ao calcular estoque por OM para item {item.id}: {e}')
                        # Em caso de erro, usar quantidade_atual padrão
                        item.estoque_om = item.quantidade_atual
                        itens_com_estoque.append(item)
                
                # Buscar localização específica da OM filtrada para cada item
                for item in itens_com_estoque:
                    try:
                        if sub_unidade_om:
                            localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.filter(
                                produto=item,
                                sub_unidade=sub_unidade_om
                            ).first()
                        elif unidade_om:
                            localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.filter(
                                produto=item,
                                unidade=unidade_om,
                                sub_unidade__isnull=True
                            ).first()
                        elif grande_comando_om:
                            localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.filter(
                                produto=item,
                                grande_comando=grande_comando_om,
                                unidade__isnull=True,
                                sub_unidade__isnull=True
                            ).first()
                        elif orgao_om:
                            localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.filter(
                                produto=item,
                                orgao=orgao_om,
                                grande_comando__isnull=True,
                                unidade__isnull=True,
                                sub_unidade__isnull=True
                            ).first()
                        else:
                            localizacao_om = None
                        
                        # Atribuir localização da OM ou usar a localização padrão do produto
                        item.localizacao_om = localizacao_om.localizacao if localizacao_om and localizacao_om.localizacao else (item.localizacao or None)
                    except Exception:
                        # Em caso de erro, usar localização padrão
                        item.localizacao_om = item.localizacao or None
                
                # Atualizar a lista de itens com estoque calculado por OM
                context['itens'] = itens_com_estoque
            else:
                # Se a OM selecionada não está dentro do escopo hierárquico, não mostrar nenhum item
                context['itens'] = []
                from django.contrib import messages
                messages.warning(self.request, "Você não tem acesso para visualizar o estoque da OM selecionada.")
        else:
            # Quando não há filtro de OM, calcular estoque baseado no tipo de acesso
            if funcao_usuario and funcao_usuario.funcao_militar:
                from decimal import Decimal
                from .models import GrandeComando, Unidade, SubUnidade
                
                funcao_militar = funcao_usuario.funcao_militar
                acesso = funcao_militar.acesso
                
                # Determinar OMs dentro do escopo baseado no tipo de acesso
                orgaos_escopo = []
                grandes_comandos_escopo = []
                unidades_escopo = []
                subunidades_escopo = []
                nome_om_usuario = None
                
                if acesso == 'TOTAL':
                    # Acesso total - não calcular por OM específica
                    # Mas ainda assim, tentar usar a OM da sessão do usuário se disponível
                    context['nome_om_usuario'] = None
                    orgao_usuario = None
                    grande_comando_usuario = None
                    unidade_usuario = None
                    sub_unidade_usuario = None
                    
                    # Tentar obter a OM mais específica da função do usuário
                    if funcao_usuario.sub_unidade:
                        sub_unidade_usuario = funcao_usuario.sub_unidade
                        context['nome_om_usuario'] = str(sub_unidade_usuario)
                    elif funcao_usuario.unidade:
                        unidade_usuario = funcao_usuario.unidade
                        context['nome_om_usuario'] = str(unidade_usuario)
                    elif funcao_usuario.grande_comando:
                        grande_comando_usuario = funcao_usuario.grande_comando
                        context['nome_om_usuario'] = str(grande_comando_usuario)
                    elif funcao_usuario.orgao:
                        orgao_usuario = funcao_usuario.orgao
                        context['nome_om_usuario'] = str(orgao_usuario)
                    
                    context['orgao_usuario'] = orgao_usuario
                    context['grande_comando_usuario'] = grande_comando_usuario
                    context['unidade_usuario'] = unidade_usuario
                    context['sub_unidade_usuario'] = sub_unidade_usuario
                    
                    # Calcular estoque total e na OM do usuário para cada item
                    for item in context['itens']:
                        try:
                            # Calcular estoque total (soma de todas as OMs)
                            item.estoque_total = item.get_estoque_total()
                            
                            # Calcular estoque na OM do usuário
                            if sub_unidade_usuario:
                                item.estoque_om = item.get_estoque_por_om(sub_unidade=sub_unidade_usuario)
                            elif unidade_usuario:
                                item.estoque_om = item.get_estoque_por_om(unidade=unidade_usuario)
                            elif grande_comando_usuario:
                                item.estoque_om = item.get_estoque_por_om(grande_comando=grande_comando_usuario)
                            elif orgao_usuario:
                                item.estoque_om = item.get_estoque_por_om(orgao=orgao_usuario)
                            else:
                                # Se não tem OM do usuário, não calcular estoque_om (será None)
                                item.estoque_om = None
                        except Exception as e:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f'Erro ao calcular estoque para item {item.id}: {e}')
                            # Em caso de erro, calcular estoque total
                            try:
                                item.estoque_total = item.get_estoque_total()
                            except:
                                item.estoque_total = item.quantidade_atual
                            item.estoque_om = None
                        
                        item.estoque_total_hierarquia = item.estoque_total if item.estoque_total is not None else item.quantidade_atual
                        
                        # Buscar localização específica da OM do usuário
                        try:
                            if sub_unidade_usuario:
                                localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.filter(
                                    produto=item,
                                    sub_unidade=sub_unidade_usuario
                                ).first()
                            elif unidade_usuario:
                                localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.filter(
                                    produto=item,
                                    unidade=unidade_usuario,
                                    sub_unidade__isnull=True
                                ).first()
                            elif grande_comando_usuario:
                                localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.filter(
                                    produto=item,
                                    grande_comando=grande_comando_usuario,
                                    unidade__isnull=True,
                                    sub_unidade__isnull=True
                                ).first()
                            elif orgao_usuario:
                                localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.filter(
                                    produto=item,
                                    orgao=orgao_usuario,
                                    grande_comando__isnull=True,
                                    unidade__isnull=True,
                                    sub_unidade__isnull=True
                                ).first()
                            else:
                                localizacao_om = None
                            
                            # Atribuir localização da OM ou usar a localização padrão do produto
                            item.localizacao_om = localizacao_om.localizacao if localizacao_om and localizacao_om.localizacao else (item.localizacao or None)
                        except Exception:
                            # Em caso de erro, usar localização padrão
                            item.localizacao_om = item.localizacao or None
                elif acesso == 'ORGAO':
                    # Acesso ao órgão + todas descendências
                    # Se está lotado em qualquer nível mas tem acesso de órgão, usar o órgão da lotação
                    if funcao_usuario.sub_unidade and funcao_usuario.sub_unidade.unidade and funcao_usuario.sub_unidade.unidade.grande_comando and funcao_usuario.sub_unidade.unidade.grande_comando.orgao:
                        orgao_principal = funcao_usuario.sub_unidade.unidade.grande_comando.orgao
                    elif funcao_usuario.unidade and funcao_usuario.unidade.grande_comando and funcao_usuario.unidade.grande_comando.orgao:
                        orgao_principal = funcao_usuario.unidade.grande_comando.orgao
                    elif funcao_usuario.grande_comando and funcao_usuario.grande_comando.orgao:
                        orgao_principal = funcao_usuario.grande_comando.orgao
                    elif funcao_usuario.orgao:
                        orgao_principal = funcao_usuario.orgao
                    else:
                        orgao_principal = None
                    
                    if orgao_principal:
                        orgaos_escopo = [orgao_principal]
                        grandes_comandos_escopo = list(GrandeComando.objects.filter(orgao=orgao_principal, ativo=True))
                        unidades_escopo = list(Unidade.objects.filter(grande_comando__in=grandes_comandos_escopo, ativo=True))
                        subunidades_escopo = list(SubUnidade.objects.filter(unidade__in=unidades_escopo, ativo=True))
                        nome_om_usuario = str(orgao_principal)
                elif acesso == 'GRANDE_COMANDO':
                    # Acesso ao grande comando + todas descendências
                    # Se está lotado em unidade/subunidade mas tem acesso de grande comando, usar o GC da unidade
                    if funcao_usuario.sub_unidade and funcao_usuario.sub_unidade.unidade and funcao_usuario.sub_unidade.unidade.grande_comando:
                        gc_principal = funcao_usuario.sub_unidade.unidade.grande_comando
                    elif funcao_usuario.unidade and funcao_usuario.unidade.grande_comando:
                        gc_principal = funcao_usuario.unidade.grande_comando
                    elif funcao_usuario.grande_comando:
                        gc_principal = funcao_usuario.grande_comando
                    else:
                        gc_principal = None
                    
                    if gc_principal:
                        grandes_comandos_escopo = [gc_principal]
                        unidades_escopo = list(Unidade.objects.filter(grande_comando=gc_principal, ativo=True))
                        subunidades_escopo = list(SubUnidade.objects.filter(unidade__in=unidades_escopo, ativo=True))
                        nome_om_usuario = str(gc_principal)
                elif acesso == 'UNIDADE':
                    # Acesso à unidade + todas subunidades
                    # Se está lotado em subunidade mas tem acesso de unidade, usar a unidade da subunidade
                    if funcao_usuario.sub_unidade and funcao_usuario.sub_unidade.unidade:
                        unidade_principal = funcao_usuario.sub_unidade.unidade
                    elif funcao_usuario.unidade:
                        unidade_principal = funcao_usuario.unidade
                    else:
                        unidade_principal = None
                    
                    if unidade_principal:
                        unidades_escopo = [unidade_principal]
                        subunidades_escopo = list(SubUnidade.objects.filter(unidade=unidade_principal, ativo=True))
                        nome_om_usuario = str(unidade_principal)
                elif acesso == 'SUBUNIDADE' and funcao_usuario.sub_unidade:
                    # Acesso apenas à subunidade
                    subunidades_escopo = [funcao_usuario.sub_unidade]
                    nome_om_usuario = str(funcao_usuario.sub_unidade)
                
                context['nome_om_usuario'] = nome_om_usuario
                
                # Adicionar informações da OM do usuário ao contexto para passar nos links
                orgao_usuario = None
                grande_comando_usuario = None
                unidade_usuario = None
                sub_unidade_usuario = None
                
                if acesso == 'ORGAO' and orgaos_escopo:
                    orgao_usuario = orgaos_escopo[0]
                elif acesso == 'GRANDE_COMANDO' and grandes_comandos_escopo:
                    grande_comando_usuario = grandes_comandos_escopo[0]
                elif acesso == 'UNIDADE' and unidades_escopo:
                    unidade_usuario = unidades_escopo[0]
                elif acesso == 'SUBUNIDADE' and subunidades_escopo:
                    sub_unidade_usuario = subunidades_escopo[0]
                
                context['orgao_usuario'] = orgao_usuario
                context['grande_comando_usuario'] = grande_comando_usuario
                context['unidade_usuario'] = unidade_usuario
                context['sub_unidade_usuario'] = sub_unidade_usuario
                
                # Calcular estoque total e por OM para cada item
                for item in context['itens']:
                    try:
                        from .models import EntradaAlmoxarifado
                        from django.db.models import Sum, Q
                        from django.db import ProgrammingError
                        
                        # Calcular estoque total (soma de todas as OMs)
                        estoque_total = item.get_estoque_total()
                        estoque_om_principal = None
                        
                        # Determinar OM principal baseada no nível de acesso
                        # IMPORTANTE: Sempre usar a OM do usuário (não a OM de criação do produto)
                        if acesso == 'ORGAO' and orgao_usuario:
                            # Estoque na OM principal (órgão do usuário)
                            estoque_om_principal = item.get_estoque_por_om(orgao=orgao_usuario)
                        elif acesso == 'GRANDE_COMANDO' and grande_comando_usuario:
                            # Estoque na OM principal (grande comando do usuário)
                            estoque_om_principal = item.get_estoque_por_om(grande_comando=grande_comando_usuario)
                        elif acesso == 'UNIDADE' and unidade_usuario:
                            # Estoque na OM principal (unidade do usuário)
                            estoque_om_principal = item.get_estoque_por_om(unidade=unidade_usuario)
                        elif acesso == 'SUBUNIDADE' and sub_unidade_usuario:
                            # Estoque na OM principal (subunidade do usuário)
                            estoque_om_principal = item.get_estoque_por_om(sub_unidade=sub_unidade_usuario)
                        
                        # Buscar todas as OMs únicas onde o produto tem entradas (estoque) dentro do escopo
                        # Identificar todas as OMs onde o produto realmente tem estoque através de entradas
                        oms_com_estoque = set()
                        
                        # Buscar entradas legadas com destino nas OMs do escopo
                        entradas_legadas = item.entradas.filter(ativo=True, quantidade__isnull=False)
                        
                        # Filtrar entradas que têm destino nas OMs do escopo
                        filtro_destino = Q()
                        if subunidades_escopo:
                            sub_ids = [s.id for s in subunidades_escopo]
                            filtro_destino |= Q(sub_unidade_destino_id__in=sub_ids)
                        if unidades_escopo:
                            unidade_ids = [u.id for u in unidades_escopo]
                            filtro_destino |= Q(unidade_destino_id__in=unidade_ids)
                        if grandes_comandos_escopo:
                            gc_ids = [gc.id for gc in grandes_comandos_escopo]
                            filtro_destino |= Q(grande_comando_destino_id__in=gc_ids)
                        if orgaos_escopo:
                            orgao_ids = [o.id for o in orgaos_escopo]
                            filtro_destino |= Q(orgao_destino_id__in=orgao_ids)
                        
                        if filtro_destino:
                            entradas_no_escopo = entradas_legadas.filter(filtro_destino)
                            for entrada in entradas_no_escopo:
                                # Identificar a OM mais específica (prioridade: sub > unidade > gc > orgao)
                                if entrada.sub_unidade_destino:
                                    oms_com_estoque.add(('sub', entrada.sub_unidade_destino_id))
                                elif entrada.unidade_destino:
                                    oms_com_estoque.add(('unidade', entrada.unidade_destino_id))
                                elif entrada.grande_comando_destino:
                                    oms_com_estoque.add(('gc', entrada.grande_comando_destino_id))
                                elif entrada.orgao_destino:
                                    oms_com_estoque.add(('orgao', entrada.orgao_destino_id))
                        
                        # Também verificar entradas via produtos_entrada (múltiplos produtos)
                        try:
                            entradas_produtos = item.entradas_produtos.filter(entrada__ativo=True)
                            if filtro_destino:
                                # Aplicar o mesmo filtro nas entradas de produtos
                                for ep in entradas_produtos.filter(filtro_destino):
                                    entrada = ep.entrada
                                    if entrada.sub_unidade_destino:
                                        oms_com_estoque.add(('sub', entrada.sub_unidade_destino_id))
                                    elif entrada.unidade_destino:
                                        oms_com_estoque.add(('unidade', entrada.unidade_destino_id))
                                    elif entrada.grande_comando_destino:
                                        oms_com_estoque.add(('gc', entrada.grande_comando_destino_id))
                                    elif entrada.orgao_destino:
                                        oms_com_estoque.add(('orgao', entrada.orgao_destino_id))
                        except (ProgrammingError, Exception):
                            pass
                        
                        # Verificar se a OM de criação do produto está no escopo
                        # Se estiver, adicionar à lista (para incluir quantidade_inicial)
                        if item.sub_unidade and item.sub_unidade in subunidades_escopo:
                            oms_com_estoque.add(('sub', item.sub_unidade_id))
                        elif item.unidade and item.unidade in unidades_escopo:
                            oms_com_estoque.add(('unidade', item.unidade_id))
                        elif item.grande_comando and item.grande_comando in grandes_comandos_escopo:
                            oms_com_estoque.add(('gc', item.grande_comando_id))
                        elif item.orgao and item.orgao in orgaos_escopo:
                            oms_com_estoque.add(('orgao', item.orgao_id))
                        
                        # Calcular estoque de cada OM identificada e somar para o total
                        # IMPORTANTE: quantidade_inicial só deve ser contado na OM de criação
                        quantidade_inicial = Decimal(str(item.quantidade_inicial)) if item.quantidade_inicial else Decimal('0')
                        
                        # Identificar qual é a OM de criação do produto
                        om_criacao_tipo = None
                        om_criacao_id = None
                        if item.sub_unidade:
                            om_criacao_tipo = 'sub'
                            om_criacao_id = item.sub_unidade_id
                        elif item.unidade:
                            om_criacao_tipo = 'unidade'
                            om_criacao_id = item.unidade_id
                        elif item.grande_comando:
                            om_criacao_tipo = 'gc'
                            om_criacao_id = item.grande_comando_id
                        elif item.orgao:
                            om_criacao_tipo = 'orgao'
                            om_criacao_id = item.orgao_id
                        
                        for tipo_om, om_id in oms_com_estoque:
                            if tipo_om == 'sub':
                                from .models import SubUnidade
                                sub = SubUnidade.objects.get(pk=om_id)
                                estoque = item.get_estoque_por_om(sub_unidade=sub)
                            elif tipo_om == 'unidade':
                                from .models import Unidade
                                unidade = Unidade.objects.get(pk=om_id)
                                estoque = item.get_estoque_por_om(unidade=unidade)
                            elif tipo_om == 'gc':
                                from .models import GrandeComando
                                gc = GrandeComando.objects.get(pk=om_id)
                                estoque = item.get_estoque_por_om(grande_comando=gc)
                            elif tipo_om == 'orgao':
                                from .models import Orgao
                                orgao = Orgao.objects.get(pk=om_id)
                                estoque = item.get_estoque_por_om(orgao=orgao)
                            else:
                                estoque = Decimal('0')
                            
                            # Verificar se é a OM de criação
                            e_om_criacao = (tipo_om == om_criacao_tipo and om_id == om_criacao_id)
                            
                            # O método get_estoque_por_om sempre inclui quantidade_inicial
                            # Mas quantidade_inicial só deve ser contado na OM de criação
                            # Se NÃO é a OM de criação, subtrair o quantidade_inicial que foi incluído incorretamente
                            if not e_om_criacao and quantidade_inicial > 0:
                                estoque = estoque - quantidade_inicial
                                # Garantir que não fique negativo
                                if estoque < 0:
                                    estoque = Decimal('0')
                            
                            estoque_total += estoque
                        
                        # Se não encontrou nenhuma OM com estoque, usar método get_estoque_total
                        if estoque_total == 0 and not oms_com_estoque:
                            estoque_total = item.get_estoque_total()
                        
                        item.estoque_total = estoque_total
                        item.estoque_total_hierarquia = estoque_total
                        item.estoque_om = estoque_om_principal
                        
                        # Buscar localização específica da OM do usuário
                        try:
                            if sub_unidade_usuario:
                                localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.filter(
                                    produto=item,
                                    sub_unidade=sub_unidade_usuario
                                ).first()
                            elif unidade_usuario:
                                localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.filter(
                                    produto=item,
                                    unidade=unidade_usuario,
                                    sub_unidade__isnull=True
                                ).first()
                            elif grande_comando_usuario:
                                localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.filter(
                                    produto=item,
                                    grande_comando=grande_comando_usuario,
                                    unidade__isnull=True,
                                    sub_unidade__isnull=True
                                ).first()
                            elif orgao_usuario:
                                localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.filter(
                                    produto=item,
                                    orgao=orgao_usuario,
                                    grande_comando__isnull=True,
                                    unidade__isnull=True,
                                    sub_unidade__isnull=True
                                ).first()
                            else:
                                localizacao_om = None
                            
                            # Atribuir localização da OM ou usar a localização padrão do produto
                            item.localizacao_om = localizacao_om.localizacao if localizacao_om and localizacao_om.localizacao else (item.localizacao or None)
                        except Exception:
                            # Em caso de erro, usar localização padrão
                            item.localizacao_om = item.localizacao or None
                        
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f'Erro ao calcular estoque por hierarquia para item {item.id}: {e}')
                        item.estoque_total_hierarquia = item.quantidade_atual
                        item.estoque_om = None
                        item.localizacao_om = item.localizacao or None
            else:
                # Se não há função do usuário, calcular estoque total do produto
                context['nome_om_usuario'] = None
                for item in context['itens']:
                    try:
                        # Calcular estoque total (soma de todas as OMs)
                        item.estoque_total = item.get_estoque_total()
                        item.estoque_total_hierarquia = item.estoque_total
                        # estoque_om será None para indicar que não há filtro de OM
                        item.estoque_om = None
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f'Erro ao calcular estoque total para item {item.id}: {e}')
                        item.estoque_total = item.quantidade_atual
                        item.estoque_total_hierarquia = item.quantidade_atual
                        item.estoque_om = None
                    
                    # Sem OM do usuário, usar localização padrão
                    item.localizacao_om = item.localizacao or None
        
        # Estatísticas (com filtro hierárquico baseado no tipo de acesso)
        queryset_stats = ProdutoAlmoxarifado.objects.all()
        
        # Aplicar filtro hierárquico nas estatísticas também
        funcao_usuario = obter_sessao_ativa_usuario(user)
        if funcao_usuario:
            queryset_stats = aplicar_filtro_hierarquico_itens_almoxarifado(queryset_stats, funcao_usuario, user)
        
        context['total_itens'] = queryset_stats.count()
        context['itens_ativos'] = queryset_stats.filter(ativo=True).count()
        context['itens_esgotados'] = queryset_stats.filter(quantidade_atual__lte=0, ativo=True).count()
        context['itens_criticos'] = queryset_stats.filter(
            quantidade_atual__lte=F('estoque_minimo'),
            quantidade_atual__gt=0,
            ativo=True
        ).count()
        context['pode_criar'] = tem_permissao(user, 'ALMOXARIFADO', 'CRIAR')
        context['pode_editar'] = tem_permissao(user, 'ALMOXARIFADO', 'EDITAR')
        context['pode_excluir'] = tem_permissao(user, 'ALMOXARIFADO', 'EXCLUIR')
        context['pode_visualizar'] = True  # Permite que todos visualizem
        
        # Obter nome da OM do usuário
        sessao = obter_sessao_ativa_usuario(user)
        if sessao and sessao.funcao_militar_usuario:
            funcao = sessao.funcao_militar_usuario
            if funcao.sub_unidade:
                context['nome_om'] = str(funcao.sub_unidade)
            elif funcao.unidade:
                context['nome_om'] = str(funcao.unidade)
            elif funcao.grande_comando:
                context['nome_om'] = str(funcao.grande_comando)
            elif funcao.orgao:
                context['nome_om'] = str(funcao.orgao)
            else:
                context['nome_om'] = None
        else:
            context['nome_om'] = None

        return context


@login_required
def produto_almoxarifado_create(request):
    """Cria um novo produto do almoxarifado via modal"""
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'CRIAR'):
        messages.error(request, "Você não tem permissão para criar produtos.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)

    if request.method == 'POST':
        form = ProdutoAlmoxarifadoForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            item = form.save(commit=False)
            item.criado_por = request.user
            
            # Preencher OM baseado na seleção do formulário ou na função logada do usuário
            # Se o usuário não selecionou uma OM no formulário, usar a OM da função
            if not item.orgao and not item.grande_comando and not item.unidade and not item.sub_unidade:
                sessao = obter_sessao_ativa_usuario(request.user)
                if sessao and sessao.funcao_militar_usuario:
                    funcao = sessao.funcao_militar_usuario
                    item.orgao = funcao.orgao
                    item.grande_comando = funcao.grande_comando
                    item.unidade = funcao.unidade
                    item.sub_unidade = funcao.sub_unidade
            
            # Usar código de barras como código se código não foi fornecido e código de barras existe
            if not item.codigo:
                if item.codigo_barras:
                    item.codigo = item.codigo_barras
                else:
                    # Se não tiver código nem código de barras, gerar um código único baseado no ID
                    # Mas como ainda não temos ID, vamos usar timestamp
                    from django.utils import timezone
                    import hashlib
                    timestamp = str(timezone.now().timestamp()).replace('.', '')
                    item.codigo = timestamp[-10:]
            item.save()
            
            # Gerar código de barras automaticamente se não foi fornecido
            if not item.codigo_barras:
                # Usar o código do produto como código de barras
                item.codigo_barras = item.codigo
                item.save(update_fields=['codigo_barras'])
            
            # Após salvar, garantir que quantidade_atual seja recalculado
            # Isso é importante porque quantidade_atual = quantidade_inicial + entradas - saídas
            item.recalcular_quantidade_atual()
            item.refresh_from_db()
            
            # Tamanho agora é um campo direto do item, não precisa processar separadamente
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Item criado com sucesso!',
                    'redirect': reverse('militares:produto_almoxarifado_list')
                })
            messages.success(request, 'Item criado com sucesso!')
            return redirect('militares:produto_almoxarifado_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/item_almoxarifado_form_modal.html', {
                    'form': form,
                    'is_create': True
                }, request=request)
                return JsonResponse({'status': 'error', 'message': 'Erro de validação', 'html': html}, status=400)
    else:
        # Inicializar formulário com valores iniciais da OM do usuário (se houver função ativa)
        # Para superusuários sem função ativa, os campos ficam vazios mas todas as OMs estarão disponíveis
        initial = {}
        sessao = obter_sessao_ativa_usuario(request.user)
        if sessao and sessao.funcao_militar_usuario:
            funcao = sessao.funcao_militar_usuario
            if funcao.orgao:
                initial['orgao'] = funcao.orgao.pk
            if funcao.grande_comando:
                initial['grande_comando'] = funcao.grande_comando.pk
            if funcao.unidade:
                initial['unidade'] = funcao.unidade.pk
            if funcao.sub_unidade:
                initial['sub_unidade'] = funcao.sub_unidade.pk
        
        form = ProdutoAlmoxarifadoForm(request=request, initial=initial)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/item_almoxarifado_form_modal.html', {
            'form': form,
            'is_create': True
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    # Se não for AJAX, redirecionar para a lista
    return redirect('militares:produto_almoxarifado_list')


@login_required
def produto_almoxarifado_update(request, pk):
    """Atualiza um item do almoxarifado via modal"""
    item = get_object_or_404(ProdutoAlmoxarifado, pk=pk)
    
    # Verificar se o usuário é o criador do item (ou superusuário)
    if not request.user.is_superuser and item.criado_por != request.user:
        messages.error(request, "Você não tem permissão para editar este item. Apenas o criador pode editar.")
        return JsonResponse({'status': 'error', 'message': 'Você não tem permissão para editar este item. Apenas o criador pode editar.'}, status=403)
    
    if request.method == 'POST':
        # Verificar se deve remover a imagem
        remover_imagem = request.POST.get('remover_imagem') == 'on'
        if remover_imagem and item.imagem:
            item.imagem.delete()
        
        form = ProdutoAlmoxarifadoForm(request.POST, request.FILES, instance=item, request=request)
        if form.is_valid():
            item = form.save(commit=False)
            # Se o código não foi preenchido no formulário, usar código de barras ou gerar um
            if not item.codigo:
                if item.codigo_barras:
                    item.codigo = item.codigo_barras
                else:
                    # Se não tiver código nem código de barras, gerar um código único
                    from django.utils import timezone
                    timestamp = str(timezone.now().timestamp()).replace('.', '')
                    item.codigo = timestamp[-10:]
            item.save()
            
            # Após salvar, garantir que quantidade_atual seja recalculado
            # Isso é importante porque quantidade_atual = quantidade_inicial + entradas - saídas
            item.recalcular_quantidade_atual()
            item.refresh_from_db()
            
            # Tamanho agora é um campo direto do item, não precisa processar separadamente
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Item atualizado com sucesso!',
                    'redirect': reverse('militares:produto_almoxarifado_list')
                })
            messages.success(request, 'Item atualizado com sucesso!')
            return redirect('militares:produto_almoxarifado_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/item_almoxarifado_form_modal.html', {
                    'form': form,
                    'item': item,
                    'is_create': False
                }, request=request)
                return JsonResponse({'status': 'error', 'message': 'Erro de validação', 'html': html}, status=400)
    else:
        form = ProdutoAlmoxarifadoForm(instance=item, request=request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/item_almoxarifado_form_modal.html', {
            'form': form,
            'item': item,
            'is_create': False
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    # Se não for AJAX, redirecionar para a lista
    return redirect('militares:produto_almoxarifado_list')


@login_required
def produto_almoxarifado_update_localizacao(request, pk):
    """Atualiza apenas a localização do produto via AJAX - específica por OM"""
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'EDITAR'):
        return JsonResponse({'status': 'error', 'message': 'Você não tem permissão para editar.'}, status=403)
    
    produto = get_object_or_404(ProdutoAlmoxarifado, pk=pk)
    
    # Obter a OM do usuário da sessão ativa
    sessao = obter_sessao_ativa_usuario(request.user)
    if not sessao or not sessao.funcao_militar_usuario:
        return JsonResponse({'status': 'error', 'message': 'Não foi possível identificar a OM do usuário.'}, status=400)
    
    funcao = sessao.funcao_militar_usuario
    
    # Determinar a OM mais específica
    orgao_om = None
    grande_comando_om = None
    unidade_om = None
    sub_unidade_om = None
    
    if funcao.sub_unidade:
        sub_unidade_om = funcao.sub_unidade
    elif funcao.unidade:
        unidade_om = funcao.unidade
    elif funcao.grande_comando:
        grande_comando_om = funcao.grande_comando
    elif funcao.orgao:
        orgao_om = funcao.orgao
    else:
        return JsonResponse({'status': 'error', 'message': 'Não foi possível identificar a OM do usuário.'}, status=400)
    
    if request.method == 'POST':
        try:
            localizacao = request.POST.get('localizacao', '').strip()
            
            # Buscar ou criar a localização para esta OM
            try:
                localizacao_obj, created = ProdutoAlmoxarifadoLocalizacao.objects.get_or_create(
                    produto=produto,
                    orgao=orgao_om,
                    grande_comando=grande_comando_om,
                    unidade=unidade_om,
                    sub_unidade=sub_unidade_om,
                    defaults={
                        'localizacao': localizacao,
                        'criado_por': request.user
                    }
                )
                
                if not created:
                    # Atualizar localização existente
                    localizacao_obj.localizacao = localizacao
                    localizacao_obj.save(update_fields=['localizacao'])
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Localização atualizada com sucesso para esta OM!',
                    'localizacao': localizacao_obj.localizacao or ''
                })
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Erro ao salvar localização: {e}")
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro ao salvar localização: {str(e)}'
                }, status=500)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Erro no método POST de localização: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao processar requisição: {str(e)}'
            }, status=500)
    else:
        # Buscar localização existente para esta OM
        localizacao_om = None
        try:
            localizacao_om = ProdutoAlmoxarifadoLocalizacao.objects.get(
                produto=produto,
                orgao=orgao_om,
                grande_comando=grande_comando_om,
                unidade=unidade_om,
                sub_unidade=sub_unidade_om
            )
        except ProdutoAlmoxarifadoLocalizacao.DoesNotExist:
            pass
        except Exception as e:
            # Log do erro para debug
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao buscar localização: {e}")
        
        # Obter nome da OM de forma segura
        try:
            nome_om = funcao.get_nivel_lotacao() if funcao else "OM não identificada"
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao obter nível de lotação: {e}")
            nome_om = "OM não identificada"
        
        # Retornar formulário para editar localização
        try:
            html = render_to_string('militares/produto_almoxarifado_localizacao_modal.html', {
                'produto': produto,
                'localizacao_om': localizacao_om,
                'nome_om': nome_om
            }, request=request)
            return JsonResponse({'status': 'success', 'html': html})
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao renderizar template de localização: {e}")
            return JsonResponse({
                'status': 'error', 
                'message': f'Erro ao carregar formulário de localização: {str(e)}'
            }, status=500)


@login_required
def produto_almoxarifado_delete(request, pk):
    """Deleta um item do almoxarifado - apenas superusuários podem deletar"""
    if not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para excluir itens. Apenas superusuários podem deletar.")
        return JsonResponse({'status': 'error', 'message': 'Você não tem permissão para excluir itens. Apenas superusuários podem deletar.'}, status=403)

    produto = get_object_or_404(ProdutoAlmoxarifado, pk=pk)
    
    if request.method == 'POST':
        item.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Item deletado com sucesso!'
            })
        messages.success(request, 'Item deletado com sucesso!')
        return redirect('militares:produto_almoxarifado_list')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/item_almoxarifado_delete_modal.html', {
            'item': item
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return render(request, 'militares/item_almoxarifado_delete.html', {'item': item})


@login_required
def produto_almoxarifado_duplicate(request, pk):
    """Duplica um item do almoxarifado para criar uma cópia editável"""
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'CRIAR'):
        messages.error(request, "Você não tem permissão para criar produtos.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
    
    # Buscar o item original
    item_original = get_object_or_404(ProdutoAlmoxarifado, pk=pk)
    
    # Criar uma cópia do item
    # Gerar um código único temporário (o usuário pode alterar na edição)
    from django.utils import timezone
    timestamp = str(timezone.now().timestamp()).replace('.', '')
    codigo_temporario = f'COPY-{timestamp[-10:]}'
    
    item_copia = ProdutoAlmoxarifado(
        codigo=codigo_temporario,  # Código temporário único, usuário pode alterar na edição
        codigo_barras='',  # Código de barras vazio
        descricao=item_original.descricao,
        categoria_antiga=item_original.categoria_antiga,
        categoria=item_original.categoria,
        subcategoria=item_original.subcategoria,
        unidade_medida=item_original.unidade_medida,
        marca=item_original.marca,
        modelo=item_original.modelo,
        tamanho=item_original.tamanho,
        estoque_minimo=item_original.estoque_minimo,
        estoque_maximo=item_original.estoque_maximo,
        quantidade_inicial=0,  # Quantidade inicial zerada
        quantidade_atual=0,  # Quantidade atual zerada
        localizacao=item_original.localizacao,
        valor_unitario=item_original.valor_unitario,
        fornecedor_principal=item_original.fornecedor_principal,
        orgao=item_original.orgao,
        grande_comando=item_original.grande_comando,
        unidade=item_original.unidade,
        sub_unidade=item_original.sub_unidade,
        ativo=item_original.ativo,
        observacoes=item_original.observacoes,
        criado_por=request.user,
    )
    
    # Não copiar a imagem (deixar vazio para o usuário escolher)
    # item_copia.imagem = item_original.imagem
    
    # Gerar código automaticamente se estiver vazio (será gerado no save ou no formulário)
    # O código será gerado automaticamente quando o item for salvo
    item_copia.save()
    
    # Redirecionar para edição do item copiado
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Item duplicado com sucesso! Redirecionando para edição...',
            'redirect': reverse('militares:produto_almoxarifado_update', args=[item_copia.pk])
        })
    
    messages.success(request, 'Item duplicado com sucesso! Você pode editá-lo agora.')
    return redirect('militares:produto_almoxarifado_update', pk=item_copia.pk)


@login_required
def produto_almoxarifado_detail(request, pk):
    """Detalhes de um item do almoxarifado"""
    # Permite que todos os usuários autenticados visualizem

    from django.db.models import Q, Prefetch
    from django.db import ProgrammingError, connection
    from .models import (
        EntradaAlmoxarifadoProduto, 
        SaidaAlmoxarifadoProduto,
        EntradaAlmoxarifado,
        SaidaAlmoxarifado,
        Orgao,
        GrandeComando,
        Unidade,
        SubUnidade
    )
    
    produto = get_object_or_404(ProdutoAlmoxarifado, pk=pk)
    
    # Obter parâmetros de OM da query string (se houver filtro de OM na lista)
    orgao_id = request.GET.get('orgao', '').strip()
    grande_comando_id = request.GET.get('grande_comando', '').strip()
    unidade_id = request.GET.get('unidade', '').strip()
    sub_unidade_id = request.GET.get('sub_unidade', '').strip()
    
    # Determinar qual OM usar para calcular o estoque
    orgao_visualizacao = None
    grande_comando_visualizacao = None
    unidade_visualizacao = None
    sub_unidade_visualizacao = None
    nome_om_visualizacao = None
    
    # Se houver parâmetros de OM na query string, usar esses
    parametro_om_valido = False
    if orgao_id or grande_comando_id or unidade_id or sub_unidade_id:
        try:
            if sub_unidade_id:
                sub_unidade_visualizacao = SubUnidade.objects.get(pk=sub_unidade_id)
                nome_om_visualizacao = str(sub_unidade_visualizacao)
                parametro_om_valido = True
            elif unidade_id:
                unidade_visualizacao = Unidade.objects.get(pk=unidade_id)
                nome_om_visualizacao = str(unidade_visualizacao)
                parametro_om_valido = True
                # Debug: log para verificar qual unidade está sendo usada
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f'Unidade da URL: ID={unidade_id}, Nome={nome_om_visualizacao}')
            elif grande_comando_id:
                grande_comando_visualizacao = GrandeComando.objects.get(pk=grande_comando_id)
                nome_om_visualizacao = str(grande_comando_visualizacao)
                parametro_om_valido = True
            elif orgao_id:
                orgao_visualizacao = Orgao.objects.get(pk=orgao_id)
                nome_om_visualizacao = str(orgao_visualizacao)
                parametro_om_valido = True
        except (ValueError, Orgao.DoesNotExist, GrandeComando.DoesNotExist, Unidade.DoesNotExist, SubUnidade.DoesNotExist):
            # Se o parâmetro foi passado mas a OM não foi encontrada, não fazer detecção automática
            # Vamos usar a OM de criação do produto
            parametro_om_valido = False
    
    # Verificar se as tabelas de produtos existem no banco (antes de usar os relacionamentos)
    tabela_entrada_produto_existe = False
    tabela_saida_produto_existe = False
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'militares_entradaalmoxarifadoproduto'
                );
            """)
            tabela_entrada_produto_existe = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'militares_saidaalmoxarifadoproduto'
                );
            """)
            tabela_saida_produto_existe = cursor.fetchone()[0]
    except Exception:
        # Se houver erro ao verificar, assumir que as tabelas não existem
        pass
    
    # Se não houver parâmetros de OM válidos, usar a OM da sessão ativa do usuário
    # Só fazer detecção automática se não houver parâmetro válido na URL E não houver OM do usuário
    if not parametro_om_valido and not (orgao_visualizacao or grande_comando_visualizacao or unidade_visualizacao or sub_unidade_visualizacao):
        # Primeiro, tentar usar a OM da sessão ativa do usuário
        sessao = obter_sessao_ativa_usuario(request.user)
        if sessao and sessao.funcao_militar_usuario:
            funcao = sessao.funcao_militar_usuario
            if funcao.sub_unidade:
                sub_unidade_visualizacao = funcao.sub_unidade
                nome_om_visualizacao = str(sub_unidade_visualizacao)
            elif funcao.unidade:
                unidade_visualizacao = funcao.unidade
                nome_om_visualizacao = str(unidade_visualizacao)
            elif funcao.grande_comando:
                grande_comando_visualizacao = funcao.grande_comando
                nome_om_visualizacao = str(grande_comando_visualizacao)
            elif funcao.orgao:
                orgao_visualizacao = funcao.orgao
                nome_om_visualizacao = str(orgao_visualizacao)
        
        # Se ainda não tiver OM definida, tentar detectar automaticamente pela entrada mais recente
        if not (orgao_visualizacao or grande_comando_visualizacao or unidade_visualizacao or sub_unidade_visualizacao):
            # Buscar a entrada mais recente (transferência) para detectar qual OM recebeu
            if tabela_entrada_produto_existe:
                # Se a tabela existe, buscar incluindo produtos_entrada
                entrada_recente = EntradaAlmoxarifado.objects.filter(
                    Q(produto=produto) | Q(produtos_entrada__produto=produto),
                    ativo=True,
                    tipo_entrada='TRANSFERENCIA'
                ).order_by('-data_entrada').first()
            else:
                # Se a tabela não existir, buscar apenas entradas legadas
                entrada_recente = EntradaAlmoxarifado.objects.filter(
                    produto=produto,
                    ativo=True,
                    tipo_entrada='TRANSFERENCIA'
                ).order_by('-data_entrada').first()
            
            if entrada_recente:
                # Se encontrou uma entrada de transferência recente, usar a OM de destino
                if entrada_recente.sub_unidade_destino:
                    sub_unidade_visualizacao = entrada_recente.sub_unidade_destino
                    nome_om_visualizacao = str(sub_unidade_visualizacao)
                elif entrada_recente.unidade_destino:
                    unidade_visualizacao = entrada_recente.unidade_destino
                    nome_om_visualizacao = str(unidade_visualizacao)
                elif entrada_recente.grande_comando_destino:
                    grande_comando_visualizacao = entrada_recente.grande_comando_destino
                    nome_om_visualizacao = str(grande_comando_visualizacao)
                elif entrada_recente.orgao_destino:
                    orgao_visualizacao = entrada_recente.orgao_destino
                    nome_om_visualizacao = str(orgao_visualizacao)
    
    # Filtrar entradas e saídas pela OM especificada (se houver)
    # Se houver OM especificada, mostrar apenas movimentações dessa OM
    filtro_entradas_destino = Q()
    filtro_saidas_origem = Q()
    
    if orgao_visualizacao or grande_comando_visualizacao or unidade_visualizacao or sub_unidade_visualizacao:
        # Filtrar entradas por destino = OM especificada
        if sub_unidade_visualizacao:
            filtro_entradas_destino = Q(sub_unidade_destino=sub_unidade_visualizacao)
        elif unidade_visualizacao:
            filtro_entradas_destino = Q(unidade_destino=unidade_visualizacao)
        elif grande_comando_visualizacao:
            filtro_entradas_destino = Q(grande_comando_destino=grande_comando_visualizacao)
        elif orgao_visualizacao:
            filtro_entradas_destino = Q(orgao_destino=orgao_visualizacao)
        
        # Filtrar saídas por origem = OM especificada
        if sub_unidade_visualizacao:
            filtro_saidas_origem = Q(sub_unidade_origem=sub_unidade_visualizacao)
        elif unidade_visualizacao:
            filtro_saidas_origem = Q(unidade_origem=unidade_visualizacao)
        elif grande_comando_visualizacao:
            filtro_saidas_origem = Q(grande_comando_origem=grande_comando_visualizacao)
        elif orgao_visualizacao:
            filtro_saidas_origem = Q(orgao_origem=orgao_visualizacao)
    
    # Buscar entradas legadas (produto direto)
    entradas_legadas = EntradaAlmoxarifado.objects.filter(
        produto=produto, ativo=True
    )
    
    # Aplicar filtro de destino se houver OM especificada
    if filtro_entradas_destino:
        entradas_legadas = entradas_legadas.filter(filtro_entradas_destino)
    
    entradas_legadas = entradas_legadas.select_related(
        'responsavel', 'criado_por',
        'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino'
    ).order_by('-data_entrada')
    
    # Buscar entradas via produtos_entrada (se a tabela existir)
    entradas_produtos = EntradaAlmoxarifado.objects.none()
    if tabela_entrada_produto_existe:
        try:
            entradas_produtos = EntradaAlmoxarifado.objects.filter(
                produtos_entrada__produto=produto, ativo=True
            )
            
            # Aplicar filtro de destino se houver OM especificada
            if filtro_entradas_destino:
                entradas_produtos = entradas_produtos.filter(filtro_entradas_destino)
            
            entradas_produtos = entradas_produtos.select_related(
                'responsavel', 'criado_por',
                'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino'
            ).prefetch_related(
                Prefetch(
                    'produtos_entrada',
                    queryset=EntradaAlmoxarifadoProduto.objects.filter(produto=produto).select_related('produto')
                )
            ).distinct().order_by('-data_entrada')
        except (ProgrammingError, Exception):
            entradas_produtos = EntradaAlmoxarifado.objects.none()
    
    # Buscar saídas legadas (produto direto)
    saidas_legadas = SaidaAlmoxarifado.objects.filter(
        produto=produto, ativo=True
    )
    
    # Aplicar filtro de origem se houver OM especificada
    if filtro_saidas_origem:
        saidas_legadas = saidas_legadas.filter(filtro_saidas_origem)
    
    saidas_legadas = saidas_legadas.select_related(
        'requisitante', 'responsavel_entrega', 'criado_por',
        'orgao_origem', 'grande_comando_origem', 'unidade_origem', 'sub_unidade_origem',
        'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino'
    ).order_by('-data_saida')
    
    # Buscar saídas via produtos_saida (se a tabela existir)
    saidas_produtos = SaidaAlmoxarifado.objects.none()
    if tabela_saida_produto_existe:
        try:
            saidas_produtos = SaidaAlmoxarifado.objects.filter(
                produtos_saida__produto=produto, ativo=True
            )
            
            # Aplicar filtro de origem se houver OM especificada
            if filtro_saidas_origem:
                saidas_produtos = saidas_produtos.filter(filtro_saidas_origem)
            
            saidas_produtos = saidas_produtos.select_related(
                'requisitante', 'responsavel_entrega', 'criado_por',
                'orgao_origem', 'grande_comando_origem', 'unidade_origem', 'sub_unidade_origem',
                'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino'
            ).prefetch_related(
                Prefetch(
                    'produtos_saida',
                    queryset=SaidaAlmoxarifadoProduto.objects.filter(produto=produto).select_related('produto')
                )
            ).distinct().order_by('-data_saida')
        except (ProgrammingError, Exception):
            saidas_produtos = SaidaAlmoxarifado.objects.none()
    
    # Combinar todas as entradas e saídas para o histórico
    todas_entradas = list(entradas_legadas) + list(entradas_produtos)
    todas_saidas = list(saidas_legadas) + list(saidas_produtos)
    
    # Criar lista de movimentações ordenada por data
    movimentacoes = []
    
    # Adicionar entradas
    for entrada in todas_entradas:
        quantidade = entrada.quantidade if entrada.quantidade else 0
        
        # Verificar se tem produtos_entrada (se a tabela existir)
        if tabela_entrada_produto_existe:
            try:
                if entrada.produtos_entrada.exists():
                    # Múltiplos itens - buscar quantidade específica deste item
                    produto_entrada = entrada.produtos_entrada.filter(produto=produto).first()
                    if produto_entrada:
                        quantidade = produto_entrada.quantidade
                    else:
                        continue  # Se não tem este produto, pular esta entrada
            except (ProgrammingError, Exception):
                # Se houver erro ao acessar produtos_entrada, usar quantidade legada
                pass
        
        movimentacoes.append({
            'tipo': 'ENTRADA',
            'data': entrada.data_entrada,
            'quantidade': quantidade,
            'objeto': entrada,
            'tipo_mov': entrada.get_tipo_entrada_display(),
            'observacoes': entrada.observacoes,
        })
    
    # Adicionar saídas
    for saida in todas_saidas:
        quantidade = saida.quantidade if saida.quantidade else 0
        
        # Verificar se tem produtos_saida (se a tabela existir)
        if tabela_saida_produto_existe:
            try:
                if saida.produtos_saida.exists():
                    # Múltiplos itens - buscar quantidade específica deste item
                    produto_saida = saida.produtos_saida.filter(produto=produto).first()
                    if produto_saida:
                        quantidade = produto_saida.quantidade
                    else:
                        continue  # Se não tem este produto, pular esta saída
            except (ProgrammingError, Exception):
                # Se houver erro ao acessar produtos_saida, usar quantidade legada
                pass
        
        movimentacoes.append({
            'tipo': 'SAIDA',
            'data': saida.data_saida,
            'quantidade': quantidade,
            'objeto': saida,
            'tipo_mov': saida.get_tipo_saida_display(),
            'observacoes': saida.observacoes,
        })
    
    # Adicionar criação inicial do produto (se houver quantidade_inicial e estiver visualizando a OM de criação)
    # Verificar se está visualizando a OM de criação
    e_om_criacao_visualizacao = False
    if produto.quantidade_inicial and produto.quantidade_inicial > 0:
        if produto.sub_unidade and sub_unidade_visualizacao and produto.sub_unidade.id == sub_unidade_visualizacao.id:
            e_om_criacao_visualizacao = True
        elif produto.unidade and unidade_visualizacao and produto.unidade.id == unidade_visualizacao.id and not produto.sub_unidade:
            e_om_criacao_visualizacao = True
        elif produto.grande_comando and grande_comando_visualizacao and produto.grande_comando.id == grande_comando_visualizacao.id and not produto.unidade and not produto.sub_unidade:
            e_om_criacao_visualizacao = True
        elif produto.orgao and orgao_visualizacao and produto.orgao.id == orgao_visualizacao.id and not produto.grande_comando and not produto.unidade and not produto.sub_unidade:
            e_om_criacao_visualizacao = True
        # Se não há OM especificada, assumir que está visualizando a OM de criação
        elif not (orgao_visualizacao or grande_comando_visualizacao or unidade_visualizacao or sub_unidade_visualizacao):
            e_om_criacao_visualizacao = True
        
        if e_om_criacao_visualizacao:
            # Usar data_criacao do produto ou data atual se não houver
            from django.utils import timezone
            from datetime import datetime, date
            data_criacao = produto.data_criacao if hasattr(produto, 'data_criacao') and produto.data_criacao else timezone.now()
            
            # Garantir que data_criacao seja datetime.datetime (não date)
            if isinstance(data_criacao, date) and not isinstance(data_criacao, datetime):
                data_criacao = timezone.make_aware(datetime.combine(data_criacao, datetime.min.time()))
            
            movimentacoes.append({
                'tipo': 'CRIACAO',
                'data': data_criacao,
                'quantidade': produto.quantidade_inicial,
                'objeto': produto,
                'tipo_mov': 'Criação do Produto',
                'observacoes': f'Produto criado com quantidade inicial de {produto.quantidade_inicial} {produto.get_unidade_medida_display()}',
            })
    
    # Ordenar por data (mais recente primeiro)
    # Garantir que todas as datas sejam datetime.datetime para comparação
    from datetime import datetime, date
    from django.utils import timezone
    
    def normalizar_data(d):
        """Converte date para datetime se necessário"""
        if isinstance(d, date) and not isinstance(d, datetime):
            return timezone.make_aware(datetime.combine(d, datetime.min.time()))
        return d
    
    # Normalizar todas as datas antes de ordenar
    for mov in movimentacoes:
        mov['data'] = normalizar_data(mov['data'])
    
    movimentacoes.sort(key=lambda x: x['data'], reverse=True)
    
    historico = HistoricoAlmoxarifado.objects.filter(produto=produto).order_by('-data_alteracao')
    
    # Criar lista de todas as OMs onde o produto tem estoque
    # IMPORTANTE: Buscar TODAS as entradas (sem filtro) para identificar todas as OMs com estoque
    oms_com_estoque_lista = []
    
    # Identificar OMs únicas onde há estoque (baseado em entradas e OM de criação)
    oms_identificadas = set()
    
    # Adicionar OM de criação se tiver quantidade_inicial
    if produto.quantidade_inicial and produto.quantidade_inicial > 0:
        if produto.sub_unidade:
            oms_identificadas.add(('sub', produto.sub_unidade.id, produto.sub_unidade))
        elif produto.unidade:
            oms_identificadas.add(('unidade', produto.unidade.id, produto.unidade))
        elif produto.grande_comando:
            oms_identificadas.add(('gc', produto.grande_comando.id, produto.grande_comando))
        elif produto.orgao:
            oms_identificadas.add(('orgao', produto.orgao.id, produto.orgao))
    
    # Buscar TODAS as entradas (sem filtro de OM) para identificar todas as OMs com estoque
    todas_entradas_completas = EntradaAlmoxarifado.objects.filter(
        produto=produto, ativo=True
    ).select_related(
        'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino'
    )
    
    # Adicionar entradas via produtos_entrada (se a tabela existir)
    if tabela_entrada_produto_existe:
        try:
            entradas_produtos_completas = EntradaAlmoxarifado.objects.filter(
                produtos_entrada__produto=produto, ativo=True
            ).select_related(
                'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino'
            ).prefetch_related(
                Prefetch(
                    'produtos_entrada',
                    queryset=EntradaAlmoxarifadoProduto.objects.filter(produto=produto).select_related('produto')
                )
            ).distinct()
            todas_entradas_completas = list(todas_entradas_completas) + list(entradas_produtos_completas)
        except (ProgrammingError, Exception):
            todas_entradas_completas = list(todas_entradas_completas)
    else:
        todas_entradas_completas = list(todas_entradas_completas)
    
    # Adicionar OMs de destino de TODAS as entradas (não apenas as filtradas)
    for entrada in todas_entradas_completas:
        if entrada.sub_unidade_destino:
            oms_identificadas.add(('sub', entrada.sub_unidade_destino.id, entrada.sub_unidade_destino))
        elif entrada.unidade_destino:
            oms_identificadas.add(('unidade', entrada.unidade_destino.id, entrada.unidade_destino))
        elif entrada.grande_comando_destino:
            oms_identificadas.add(('gc', entrada.grande_comando_destino.id, entrada.grande_comando_destino))
        elif entrada.orgao_destino:
            oms_identificadas.add(('orgao', entrada.orgao_destino.id, entrada.orgao_destino))
    
    # Calcular estoque para cada OM identificada
    from decimal import Decimal
    for tipo_om, om_id, om_obj in oms_identificadas:
        try:
            if tipo_om == 'sub':
                estoque_om = produto.get_estoque_por_om(sub_unidade=om_obj)
            elif tipo_om == 'unidade':
                estoque_om = produto.get_estoque_por_om(unidade=om_obj)
            elif tipo_om == 'gc':
                estoque_om = produto.get_estoque_por_om(grande_comando=om_obj)
            elif tipo_om == 'orgao':
                estoque_om = produto.get_estoque_por_om(orgao=om_obj)
            else:
                estoque_om = Decimal('0')
            
            # Só adicionar se tiver estoque > 0
            if estoque_om and estoque_om > 0:
                oms_com_estoque_lista.append({
                    'tipo': tipo_om,
                    'id': om_id,
                    'nome': str(om_obj),
                    'estoque': estoque_om,
                    'e_om_criacao': (
                        (tipo_om == 'sub' and produto.sub_unidade and produto.sub_unidade.id == om_id) or
                        (tipo_om == 'unidade' and produto.unidade and produto.unidade.id == om_id and not produto.sub_unidade) or
                        (tipo_om == 'gc' and produto.grande_comando and produto.grande_comando.id == om_id and not produto.unidade and not produto.sub_unidade) or
                        (tipo_om == 'orgao' and produto.orgao and produto.orgao.id == om_id and not produto.grande_comando and not produto.unidade and not produto.sub_unidade)
                    )
                })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Erro ao calcular estoque para OM {om_id}: {e}')
            continue
    
    # Ordenar por estoque (maior primeiro)
    oms_com_estoque_lista.sort(key=lambda x: x['estoque'], reverse=True)
    
    # Calcular o total do produto (soma de todos os estoques)
    estoque_total_produto = Decimal('0')
    for om_estoque in oms_com_estoque_lista:
        estoque_total_produto += Decimal(str(om_estoque['estoque']))
    
    # Calcular estoque na OM especificada (ou na OM de criação se não houver parâmetro)
    estoque_om_visualizacao = None
    nome_om_visualizacao_final = None
    status_estoque_om = None
    status_estoque_color_om = None
    e_om_criacao = False
    
    try:
        # Se houver OM especificada na query string ou detectada automaticamente, usar essa
        if orgao_visualizacao or grande_comando_visualizacao or unidade_visualizacao or sub_unidade_visualizacao:
            estoque_om_visualizacao = produto.get_estoque_por_om(
                orgao=orgao_visualizacao,
                grande_comando=grande_comando_visualizacao,
                unidade=unidade_visualizacao,
                sub_unidade=sub_unidade_visualizacao
            )
            nome_om_visualizacao_final = nome_om_visualizacao
            
            # Debug: log para verificar o cálculo
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'Estoque calculado para produto {produto.id} na OM {nome_om_visualizacao_final} (ID unidade={unidade_visualizacao.id if unidade_visualizacao else None}): {estoque_om_visualizacao}')
        # Caso contrário, usar a OM de criação
        else:
            if produto.sub_unidade:
                estoque_om_visualizacao = produto.get_estoque_por_om(sub_unidade=produto.sub_unidade)
                nome_om_visualizacao_final = str(produto.sub_unidade)
                e_om_criacao = True
            elif produto.unidade:
                estoque_om_visualizacao = produto.get_estoque_por_om(unidade=produto.unidade)
                nome_om_visualizacao_final = str(produto.unidade)
                e_om_criacao = True
            elif produto.grande_comando:
                estoque_om_visualizacao = produto.get_estoque_por_om(grande_comando=produto.grande_comando)
                nome_om_visualizacao_final = str(produto.grande_comando)
                e_om_criacao = True
            elif produto.orgao:
                estoque_om_visualizacao = produto.get_estoque_por_om(orgao=produto.orgao)
                nome_om_visualizacao_final = str(produto.orgao)
                e_om_criacao = True
        
        # Calcular status do estoque baseado no estoque calculado
        if estoque_om_visualizacao is not None:
            from decimal import Decimal
            estoque = Decimal(str(estoque_om_visualizacao))
            if estoque <= 0:
                status_estoque_om = 'Esgotado'
                status_estoque_color_om = 'danger'
            elif estoque <= produto.estoque_minimo:
                status_estoque_om = 'Crítico'
                status_estoque_color_om = 'warning'
            elif estoque >= produto.estoque_maximo:
                status_estoque_om = 'Acima do Máximo'
                status_estoque_color_om = 'info'
            else:
                status_estoque_om = 'Normal'
                status_estoque_color_om = 'success'
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao calcular estoque: {e}')
        estoque_om_visualizacao = produto.quantidade_atual
    
    # Permissões
    user = request.user
    pode_criar = tem_permissao(user, 'ALMOXARIFADO', 'CRIAR')
    pode_editar = tem_permissao(user, 'ALMOXARIFADO', 'EDITAR')
    
    context = {
        'item': produto,  # Usar 'item' para manter compatibilidade com o template
        'pode_criar': pode_criar,
        'pode_editar': pode_editar,
        'entradas': todas_entradas[:10],  # Últimas 10 para sidebar
        'saidas': todas_saidas[:10],  # Últimas 10 para sidebar
        'movimentacoes': movimentacoes,  # Histórico completo
        'historico': historico,  # Histórico completo de alterações
        'estoque_om_visualizacao': estoque_om_visualizacao,  # Estoque na OM de visualização
        'nome_om_visualizacao': nome_om_visualizacao_final,  # Nome da OM de visualização
        'status_estoque_om': status_estoque_om,  # Status do estoque na OM
        'status_estoque_color_om': status_estoque_color_om,  # Cor do status do estoque na OM
        'e_om_criacao': e_om_criacao,  # Indica se está visualizando a OM de criação
        'oms_com_estoque': oms_com_estoque_lista,  # Lista de todas as OMs com estoque
        'estoque_total_produto': estoque_total_produto,  # Total do produto (soma de todos os estoques)
    }
    
    return render(request, 'militares/item_almoxarifado_detail.html', context)


@login_required
def produto_almoxarifado_om(request, pk):
    """Retorna a OM (Organização Militar) de um item em formato JSON"""
    # Permite que todos os usuários autenticados visualizem
    
    produto = get_object_or_404(ProdutoAlmoxarifado, pk=pk)
    
    return JsonResponse({
        'orgao_id': item.orgao.id if item.orgao else None,
        'grande_comando_id': item.grande_comando.id if item.grande_comando else None,
        'unidade_id': item.unidade.id if item.unidade else None,
        'sub_unidade_id': item.sub_unidade.id if item.sub_unidade else None,
    })


@login_required
def produto_almoxarifado_info(request, pk):
    """Retorna informações do item em formato JSON, incluindo se requer tamanhos e estoque por OM"""
    # Permite que todos os usuários autenticados visualizem
    
    produto = get_object_or_404(ProdutoAlmoxarifado, pk=pk)
    
    # Obter parâmetros de OM para calcular estoque específico
    orgao_id = request.GET.get('orgao', '').strip()
    grande_comando_id = request.GET.get('grande_comando', '').strip()
    unidade_id = request.GET.get('unidade', '').strip()
    sub_unidade_id = request.GET.get('sub_unidade', '').strip()
    
    # Calcular quantidade disponível
    quantidade_disponivel = produto.quantidade_atual
    
    # Se houver parâmetros de OM, calcular estoque específico da OM
    if orgao_id or grande_comando_id or unidade_id or sub_unidade_id:
        from .models import Orgao, GrandeComando, Unidade, SubUnidade
        
        orgao = None
        grande_comando = None
        unidade = None
        sub_unidade = None
        
        if sub_unidade_id:
            try:
                sub_unidade = SubUnidade.objects.get(pk=sub_unidade_id)
            except (SubUnidade.DoesNotExist, ValueError):
                pass
        elif unidade_id:
            try:
                unidade = Unidade.objects.get(pk=unidade_id)
            except (Unidade.DoesNotExist, ValueError):
                pass
        elif grande_comando_id:
            try:
                grande_comando = GrandeComando.objects.get(pk=grande_comando_id)
            except (GrandeComando.DoesNotExist, ValueError):
                pass
        elif orgao_id:
            try:
                orgao = Orgao.objects.get(pk=orgao_id)
            except (Orgao.DoesNotExist, ValueError):
                pass
        
        # Calcular estoque na OM específica apenas se pelo menos uma OM foi encontrada
        if orgao or grande_comando or unidade or sub_unidade:
            try:
                quantidade_disponivel = produto.get_estoque_por_om(
                    orgao=orgao,
                    grande_comando=grande_comando,
                    unidade=unidade,
                    sub_unidade=sub_unidade
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao calcular estoque por OM: {e}')
                # Em caso de erro, usar quantidade_atual padrão
                quantidade_disponivel = produto.quantidade_atual
    
    return JsonResponse({
        'status': 'success',
        'item': {
            'id': produto.id,
            'codigo': produto.get_codigo_limpo(),
            'descricao': produto.descricao,
            'tamanho': produto.tamanho or '',
            'quantidade_atual': float(produto.quantidade_atual) if produto.quantidade_atual else 0,
            'quantidade_disponivel': float(quantidade_disponivel) if quantidade_disponivel is not None else None,
            'unidade_medida': str(produto.unidade_medida) if produto.unidade_medida else '',
            'get_unidade_medida_display': produto.get_unidade_medida_display() if produto.unidade_medida else '',
        }
    })


@login_required
def produto_almoxarifado_list_json(request):
    """Retorna lista de itens em formato JSON para uso em selects dinâmicos"""
    # Permite que todos os usuários autenticados visualizem
    
    # Buscar apenas itens ativos
    itens = ProdutoAlmoxarifado.objects.filter(ativo=True).order_by('codigo', 'descricao')
    
    # Filtrar por OM se fornecida (prioridade: sub_unidade > unidade > grande_comando > orgao)
    # Incluir produtos que foram criados na OM OU que têm estoque na OM através de entradas
    orgao_id = request.GET.get('orgao')
    grande_comando_id = request.GET.get('grande_comando')
    unidade_id = request.GET.get('unidade')
    sub_unidade_id = request.GET.get('sub_unidade')
    
    if orgao_id or grande_comando_id or unidade_id or sub_unidade_id:
        from django.db.models import Q
        from django.db import ProgrammingError
        
        # Construir filtro para produtos criados na OM
        filtro_om_criacao = Q()
        
        # Construir filtro para produtos com estoque na OM (através de entradas)
        filtro_entradas = Q()
        
        try:
            if sub_unidade_id:
                # Produtos criados na subunidade
                filtro_om_criacao = Q(sub_unidade_id=sub_unidade_id)
                # Produtos com entradas destinadas à subunidade
                filtro_entradas = Q(entradas__sub_unidade_destino_id=sub_unidade_id, entradas__ativo=True)
                
                # Também verificar entradas via produtos_entrada (múltiplos produtos)
                try:
                    filtro_entradas |= Q(entradas_produtos__entrada__sub_unidade_destino_id=sub_unidade_id, entradas_produtos__entrada__ativo=True)
                except (ProgrammingError, Exception):
                    pass
                    
            elif unidade_id:
                # Produtos criados na unidade (sem subunidade)
                filtro_om_criacao = Q(unidade_id=unidade_id, sub_unidade__isnull=True)
                # Produtos com entradas destinadas à unidade
                filtro_entradas = Q(entradas__unidade_destino_id=unidade_id, entradas__ativo=True)
                
                # Também verificar entradas via produtos_entrada
                try:
                    filtro_entradas |= Q(entradas_produtos__entrada__unidade_destino_id=unidade_id, entradas_produtos__entrada__ativo=True)
                except (ProgrammingError, Exception):
                    pass
                    
            elif grande_comando_id:
                # Produtos criados no grande comando (sem unidade/subunidade)
                filtro_om_criacao = Q(grande_comando_id=grande_comando_id, unidade__isnull=True, sub_unidade__isnull=True)
                # Produtos com entradas destinadas ao grande comando
                filtro_entradas = Q(entradas__grande_comando_destino_id=grande_comando_id, entradas__ativo=True)
                
                # Também verificar entradas via produtos_entrada
                try:
                    filtro_entradas |= Q(entradas_produtos__entrada__grande_comando_destino_id=grande_comando_id, entradas_produtos__entrada__ativo=True)
                except (ProgrammingError, Exception):
                    pass
                    
            elif orgao_id:
                # Produtos criados no órgão (sem grande comando/unidade/subunidade)
                filtro_om_criacao = Q(orgao_id=orgao_id, grande_comando__isnull=True, unidade__isnull=True, sub_unidade__isnull=True)
                # Produtos com entradas destinadas ao órgão
                filtro_entradas = Q(entradas__orgao_destino_id=orgao_id, entradas__ativo=True)
                
                # Também verificar entradas via produtos_entrada
                try:
                    filtro_entradas |= Q(entradas_produtos__entrada__orgao_destino_id=orgao_id, entradas_produtos__entrada__ativo=True)
                except (ProgrammingError, Exception):
                    pass
            
            # Combinar: produto criado na OM OU tem estoque (entradas) na OM
            filtro_final = filtro_om_criacao | filtro_entradas
            itens = itens.filter(filtro_final).distinct()
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Erro ao filtrar produtos por OM: {e}')
            # Em caso de erro, usar filtro simples por OM de criação
            if sub_unidade_id:
                itens = itens.filter(sub_unidade_id=sub_unidade_id)
            elif unidade_id:
                itens = itens.filter(unidade_id=unidade_id)
            elif grande_comando_id:
                itens = itens.filter(grande_comando_id=grande_comando_id)
            elif orgao_id:
                itens = itens.filter(orgao_id=orgao_id)
    
    # Filtrar por busca se fornecida
    search = request.GET.get('search', '')
    if search:
        itens = itens.filter(
            Q(codigo__icontains=search) |
            Q(descricao__icontains=search) |
            Q(marca__icontains=search) |
            Q(modelo__icontains=search)
        )
    
    # Obter objetos da OM uma única vez (se OM foi fornecida)
    orgao_obj = None
    grande_comando_obj = None
    unidade_obj = None
    sub_unidade_obj = None
    
    if orgao_id or grande_comando_id or unidade_id or sub_unidade_id:
        try:
            from .models import Orgao, GrandeComando, Unidade, SubUnidade
            
            if sub_unidade_id:
                sub_unidade_obj = SubUnidade.objects.get(pk=sub_unidade_id)
            elif unidade_id:
                unidade_obj = Unidade.objects.get(pk=unidade_id)
            elif grande_comando_id:
                grande_comando_obj = GrandeComando.objects.get(pk=grande_comando_id)
            elif orgao_id:
                orgao_obj = Orgao.objects.get(pk=orgao_id)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Erro ao obter objetos da OM: {e}')
    
    # Converter para formato JSON
    # Filtrar apenas produtos que têm estoque > 0 na OM selecionada (se OM foi fornecida)
    itens_list = []
    for item in itens:
        # Se há OM selecionada, verificar se o produto tem estoque na OM
        if orgao_obj or grande_comando_obj or unidade_obj or sub_unidade_obj:
            try:
                # Calcular estoque na OM
                estoque_om = item.get_estoque_por_om(
                    orgao=orgao_obj,
                    grande_comando=grande_comando_obj,
                    unidade=unidade_obj,
                    sub_unidade=sub_unidade_obj
                )
                
                # Incluir apenas se tiver estoque > 0
                if estoque_om <= 0:
                    continue
                    
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao verificar estoque do produto {item.id} na OM: {e}')
                # Em caso de erro, incluir o produto mesmo assim
                pass
        
        codigo_limpo = item.get_codigo_limpo()
        tamanho_texto = f" - Tamanho {item.tamanho}" if item.tamanho else ""
        itens_list.append({
            'id': item.id,
            'codigo': codigo_limpo,
            'descricao': item.descricao,
            'tamanho': item.tamanho or '',
            'marca': item.marca or '',
            'modelo': item.modelo or '',
            'quantidade_atual': float(item.quantidade_atual) if item.quantidade_atual else 0,
            'unidade_medida': str(item.unidade_medida) if item.unidade_medida else '',
            'get_unidade_medida_display': item.get_unidade_medida_display() if item.unidade_medida else '',
            'text': f"{codigo_limpo} - {item.descricao}{tamanho_texto}"  # Para compatibilidade com Select2
        })
    
    return JsonResponse({
        'status': 'success',
        'itens': itens_list,
        'total': len(itens_list)
    })


@login_required
def produto_almoxarifado_barcode(request, pk):
    """Gera código de barras do produto"""
    produto = get_object_or_404(ProdutoAlmoxarifado, pk=pk)
    
    # Usar código de barras ou código do produto
    codigo = produto.codigo_barras or produto.codigo
    
    # Tentar gerar código de barras usando python-barcode
    try:
        import barcode
        from barcode.writer import ImageWriter
        
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(codigo, writer=ImageWriter())
        
        buffer = BytesIO()
        barcode_instance.write(buffer)
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="produto_{produto.codigo}_barcode.png"'
        return response
    except ImportError:
        # Se python-barcode não estiver instalado, usar QR Code como alternativa
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(codigo)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="produto_{produto.codigo}_barcode.png"'
        return response


@login_required
def produto_almoxarifado_qrcode(request, pk):
    """Gera QR Code do produto com URL de acesso"""
    produto = get_object_or_404(ProdutoAlmoxarifado, pk=pk)
    
    # Criar URL completa para o produto
    from django.contrib.sites.shortcuts import get_current_site
    current_site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'
    url_produto = f"{protocol}://{current_site.domain}{reverse('militares:produto_almoxarifado_detail', kwargs={'pk': produto.pk})}"
    
    # Colocar a URL completa no QR Code
    qr_data = url_produto
    
    # Gerar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Criar imagem do QR Code
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para BytesIO
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Verificar se é uma requisição para baixar apenas a imagem (usado no template como src)
    format_param = request.GET.get('format', '')
    if format_param == 'image':
        # Retornar apenas a imagem PNG
        response = HttpResponse(buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="produto_{produto.codigo}_qrcode.png"'
        return response
    
    # Retornar imagem por padrão
    response = HttpResponse(buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'inline; filename="produto_{produto.codigo}_qrcode.png"'
    return response


@login_required
def buscar_item_por_codigo_barras(request):
    """Busca item por código de barras (usado em entradas e saídas)"""
    if request.method == 'GET':
        codigo_barras = request.GET.get('codigo_barras', '').strip()
        
        if not codigo_barras:
            return JsonResponse({'status': 'error', 'message': 'Código de barras não informado'}, status=400)
        
        try:
            # Buscar por código de barras ou código
            item = ProdutoAlmoxarifado.objects.filter(
                Q(codigo_barras=codigo_barras) | Q(codigo=codigo_barras)
            ).first()
            
            if not item:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Item não encontrado com código de barras: {codigo_barras}'
                }, status=404)
            
            if not item.ativo:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Item está inativo'
                }, status=400)
            
            return JsonResponse({
                'status': 'success',
                'item': {
                    'id': item.pk,
                    'codigo': item.get_codigo_limpo(),
                    'codigo_barras': item.codigo_barras or item.get_codigo_limpo(),
                    'descricao': item.descricao,
                    'quantidade_atual': str(item.quantidade_atual),
                    'unidade_medida': item.get_unidade_medida_display(),
                    'status_estoque': item.get_status_estoque_display(),
                }
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Erro ao buscar item: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)


# ============================================================================
# VIEWS PARA ENTRADAS DO ALMOXARIFADO
# ============================================================================

class EntradaAlmoxarifadoListView(LoginRequiredMixin, ListView):
    model = EntradaAlmoxarifado
    template_name = 'militares/entrada_almoxarifado_list.html'
    context_object_name = 'entradas'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Verificar permissão de visualizar antes de permitir acesso
        if not tem_permissao(request.user, 'ALMOXARIFADO', 'VISUALIZAR'):
            from django.contrib import messages
            messages.error(request, "Você não tem permissão para visualizar entradas do almoxarifado.")
            from django.shortcuts import redirect
            return redirect('militares:home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        from django.db.models import Prefetch
        from django.db import connection, ProgrammingError
        from .models import EntradaAlmoxarifadoProduto
        
        # Verificar se a tabela de múltiplos produtos existe
        tabela_entrada_produto_existe = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'militares_entradaalmoxarifadoproduto'
                    );
                """)
                tabela_entrada_produto_existe = cursor.fetchone()[0]
        except Exception:
            pass
        
        queryset = EntradaAlmoxarifado.objects.select_related(
            'produto', 'responsavel', 'criado_por'
        )
        
        # Fazer prefetch dos produtos da entrada
        try:
            queryset = queryset.prefetch_related(
                Prefetch(
                    'produtos_entrada',
                    queryset=EntradaAlmoxarifadoProduto.objects.select_related('produto')
                )
            )
        except (ProgrammingError, Exception):
            # Se houver erro, tentar sem prefetch (pode ser que a tabela não exista ainda)
            pass
        
        queryset = queryset.order_by('-data_entrada', '-data_criacao')

        # SEMPRE aplicar filtro hierárquico baseado no tipo de acesso da função militar
        # As entradas devem ser listadas apenas nas OMs de acordo com os filtros
        funcao_usuario = obter_sessao_ativa_usuario(self.request.user)
        if funcao_usuario:
            queryset = aplicar_filtro_hierarquico_entradas_almoxarifado(queryset, funcao_usuario, self.request.user)
        else:
            # Se não há função ativa, não mostrar nenhuma entrada
            queryset = queryset.none()

        search = self.request.GET.get('search', '')
        tipo_entrada = self.request.GET.get('tipo_entrada', '')
        item_id = self.request.GET.get('item', '')

        if search:
            search_q = Q(produto__codigo__icontains=search) | Q(produto__descricao__icontains=search) | Q(fornecedor__icontains=search) | Q(nota_fiscal__icontains=search)
            # Adicionar filtro de produtos_entrada
            try:
                search_q |= Q(produtos_entrada__produto__codigo__icontains=search) | Q(produtos_entrada__produto__descricao__icontains=search)
            except (ProgrammingError, Exception):
                pass
            queryset = queryset.filter(search_q).distinct()

        if tipo_entrada:
            queryset = queryset.filter(tipo_entrada=tipo_entrada)

        if item_id:
            item_q = Q(produto_id=item_id)
            # Adicionar filtro de produtos_entrada
            try:
                item_q |= Q(produtos_entrada__produto_id=item_id)
            except (ProgrammingError, Exception):
                pass
            queryset = queryset.filter(item_q).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['tipo_entrada'] = self.request.GET.get('tipo_entrada', '')
        context['item_id'] = self.request.GET.get('item', '')

        context['tipos'] = EntradaAlmoxarifado.TIPO_ENTRADA_CHOICES
        context['itens'] = ProdutoAlmoxarifado.objects.filter(ativo=True).order_by('codigo')

        # Estatísticas (aplicar filtro hierárquico também nas estatísticas)
        queryset_stats = EntradaAlmoxarifado.objects.all()
        funcao_usuario = obter_sessao_ativa_usuario(self.request.user)
        if funcao_usuario:
            queryset_stats = aplicar_filtro_hierarquico_entradas_almoxarifado(queryset_stats, funcao_usuario, self.request.user)
        
        context['total_entradas'] = queryset_stats.count()
        context['entradas_mes'] = queryset_stats.filter(
            data_entrada__month=timezone.now().month,
            data_entrada__year=timezone.now().year
        ).count()

        # Permissões
        user = self.request.user
        context['pode_criar'] = tem_permissao(user, 'ALMOXARIFADO', 'CRIAR')
        context['pode_editar'] = tem_permissao(user, 'ALMOXARIFADO', 'EDITAR')
        context['pode_excluir'] = tem_permissao(user, 'ALMOXARIFADO', 'EXCLUIR')
        
        # Adicionar informações sobre quais entradas podem ser editadas/excluídas
        # Adicionar métodos pode_editar e pode_excluir diretamente aos objetos entrada
        for entrada in context['entradas']:
            entrada.pode_editar = entrada.pode_editar(user)
            entrada.pode_excluir = entrada.pode_excluir(user)

        return context


@login_required
def entrada_almoxarifado_create(request):
    """
    Cria uma entrada de mercadoria no almoxarifado da OM do usuário.
    Adiciona itens ao estoque da OM atual.
    """
    import traceback
    import logging
    
    logger = logging.getLogger(__name__)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        # Verificar permissão
        if not tem_permissao(request.user, 'ALMOXARIFADO', 'CRIAR'):
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
            messages.error(request, "Você não tem permissão para criar entradas.")
            return redirect('militares:entrada_almoxarifado_list')
    except Exception as perm_error:
        logger.error(f'Erro ao verificar permissão: {str(perm_error)}')
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'Erro ao verificar permissão'}, status=500)
        messages.error(request, 'Erro ao verificar permissão.')
        return redirect('militares:entrada_almoxarifado_list')

    if request.method == 'POST':
        try:
            form = EntradaAlmoxarifadoForm(request.POST, request=request)
        except Exception as form_error:
            logger.error(f'Erro ao criar formulário: {str(form_error)}\n{traceback.format_exc()}')
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro ao processar formulário: {str(form_error)}'
                }, status=500)
            messages.error(request, f'Erro ao processar formulário: {str(form_error)}')
            return redirect('militares:entrada_almoxarifado_list')
        
        # Validar formulário
        if not form.is_valid():
            # Log dos erros de validação para debug
            logger.warning(f'Formulário inválido. Erros: {form.errors}')
            logger.warning(f'Dados POST: {dict(request.POST)}')
            
            if is_ajax:
                try:
                    html = render_to_string('militares/entrada_almoxarifado_form_modal.html', {
                        'form': form,
                        'is_create': True
                    }, request=request)
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Erro de validação do formulário',
                        'html': html,
                        'errors': form.errors,
                        'form_data': dict(request.POST) if settings.DEBUG else None
                    }, status=400)
                except Exception as render_error:
                    logger.error(f'Erro ao renderizar formulário: {str(render_error)}\n{traceback.format_exc()}')
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Erro de validação do formulário',
                        'errors': form.errors,
                        'render_error': str(render_error) if settings.DEBUG else None
                    }, status=400)
            messages.error(request, 'Erro de validação do formulário.')
            return redirect('militares:entrada_almoxarifado_list')
        
        # Formulário válido, processar criação
        entrada = None
        try:
            with transaction.atomic():
                # 1. Criar entrada básica
                entrada = form.save(commit=False)
                entrada.criado_por = request.user
                entrada.produto = None  # Múltiplos produtos via produtos_entrada
                
                # 2. Validar OM de destino
                if not (entrada.orgao_destino or entrada.grande_comando_destino or 
                        entrada.unidade_destino or entrada.sub_unidade_destino):
                    raise ValueError('É necessário informar a Organização Militar de destino.')
                
                # 3. Validar campos obrigatórios do modelo
                if not entrada.tipo_entrada:
                    raise ValueError('Tipo de entrada é obrigatório.')
                if not entrada.data_entrada:
                    raise ValueError('Data de entrada é obrigatória.')
                
                # 4. Definir quantidade padrão (campo obrigatório no banco, mas não usado com múltiplos produtos)
                # Usar 0 como valor padrão já que a quantidade real está em produtos_entrada
                if not entrada.quantidade:
                    entrada.quantidade = Decimal('0')
                
                # 5. Salvar entrada (antes de criar produtos_entrada)
                try:
                    entrada.save()
                except Exception as save_error:
                    logger.error(f'Erro ao salvar entrada: {str(save_error)}\n{traceback.format_exc()}')
                    raise ValueError(f'Erro ao salvar entrada: {str(save_error)}')
                
                # 6. Processar produtos/itens
                itens_data_str = request.POST.get('itens_data', '[]').strip()
                if not itens_data_str:
                    itens_data_str = '[]'
                
                try:
                    itens_list = json.loads(itens_data_str)
                except json.JSONDecodeError as e:
                    raise ValueError(f'Erro ao processar lista de produtos: {str(e)}')
                
                if not itens_list or not isinstance(itens_list, list) or len(itens_list) == 0:
                    raise ValueError('É necessário adicionar pelo menos um produto à entrada.')
                
                # 7. Processar cada produto
                produtos_processados = 0
                
                for item_data in itens_list:
                    if not isinstance(item_data, dict):
                        continue
                    
                    produto_id = item_data.get('item_id') or item_data.get('produto_id')
                    quantidade_str = item_data.get('quantidade', '0')
                    valor_unitario_str = item_data.get('valor_unitario')
                    valor_total_str = item_data.get('valor_total')
                    
                    if not produto_id:
                        continue
                    
                    try:
                        quantidade = Decimal(str(quantidade_str))
                    except (ValueError, TypeError, InvalidOperation):
                        logger.warning(f'Quantidade inválida para produto {produto_id}: {quantidade_str}')
                        continue
                    
                    if quantidade <= 0:
                        continue
                    
                    try:
                        produto = ProdutoAlmoxarifado.objects.get(pk=produto_id, ativo=True)
                    except ProdutoAlmoxarifado.DoesNotExist:
                        raise ValueError(f'Produto com ID {produto_id} não encontrado ou inativo.')
                    
                    # Processar valores (apenas se for COMPRA)
                    valor_unitario = None
                    valor_total = None
                    if entrada.tipo_entrada == 'COMPRA':
                        if valor_unitario_str:
                            try:
                                valor_unitario = Decimal(str(valor_unitario_str))
                            except (ValueError, TypeError, InvalidOperation):
                                pass
                        
                        if valor_total_str:
                            try:
                                valor_total = Decimal(str(valor_total_str))
                            except (ValueError, TypeError, InvalidOperation):
                                pass
                        
                        # Se não houver valor_total mas houver valor_unitario e quantidade, calcular
                        if not valor_total and valor_unitario and quantidade:
                            valor_total = valor_unitario * quantidade
                    
                    # Criar relação entrada-produto (cada produto tem sua própria quantidade)
                    EntradaAlmoxarifadoProduto.objects.create(
                        entrada=entrada,
                        produto=produto,
                        quantidade=quantidade,
                        valor_unitario=valor_unitario,
                        valor_total=valor_total
                    )
                    produtos_processados += 1
                
                if produtos_processados == 0:
                    raise ValueError('Nenhum produto válido foi processado. Verifique os produtos adicionados.')
                
                # 8. Processar upload de documentos (opcional)
                from .models import DocumentoEntradaAlmoxarifado
                documentos_upload = request.FILES.getlist('documentos_upload', [])
                tipos_documentos = request.POST.getlist('tipos_documentos[]', [])
                titulos_documentos = request.POST.getlist('titulos_documentos[]', [])
                
                for idx, arquivo in enumerate(documentos_upload):
                    if not arquivo:
                        continue
                    
                    try:
                        # Obter tipo e título do documento
                        tipo_doc = 'OUTROS'
                        if idx < len(tipos_documentos) and tipos_documentos[idx]:
                            tipo_valido = tipos_documentos[idx]
                            tipos_validos = [choice[0] for choice in DocumentoEntradaAlmoxarifado.TIPO_CHOICES]
                            if tipo_valido in tipos_validos:
                                tipo_doc = tipo_valido
                        
                        titulo_doc = arquivo.name
                        if idx < len(titulos_documentos) and titulos_documentos[idx]:
                            titulo_doc = str(titulos_documentos[idx])[:200]
                        
                        # Criar documento
                        DocumentoEntradaAlmoxarifado.objects.create(
                            entrada=entrada,
                            tipo=tipo_doc,
                            titulo=titulo_doc,
                            arquivo=arquivo,
                            upload_por=request.user
                        )
                    except Exception as doc_error:
                        logger.error(f'Erro ao processar documento {idx}: {str(doc_error)}')
                        # Continuar com outros documentos
                        continue
                
                # Sucesso!
                if is_ajax:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Entrada registrada com sucesso!',
                        'redirect': reverse('militares:entrada_almoxarifado_list')
                    })
                
                messages.success(request, 'Entrada registrada com sucesso!')
                return redirect('militares:entrada_almoxarifado_list')
                
        except ValueError as e:
            # Erros de validação esperados
            error_msg = str(e)
            logger.warning(f'Erro de validação ao criar entrada: {error_msg}')
            
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': error_msg
                }, status=400)
            
            messages.error(request, error_msg)
            return redirect('militares:entrada_almoxarifado_list')
            
        except (json.JSONDecodeError, ProdutoAlmoxarifado.DoesNotExist) as e:
            # Erros específicos conhecidos
            error_msg = f'Erro ao processar dados: {str(e)}'
            logger.error(f'Erro ao criar entrada: {error_msg}')
            
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': error_msg
                }, status=400)
            
            messages.error(request, error_msg)
            return redirect('militares:entrada_almoxarifado_list')
            
        except Exception as e:
            # Erro inesperado
            error_trace = traceback.format_exc()
            error_type = type(e).__name__
            error_msg = str(e)
            
            logger.error(f'Erro inesperado ao criar entrada ({error_type}): {error_msg}\n{error_trace}')
            
            # Mensagem amigável para o usuário
            error_message = f'Erro ao processar entrada: {error_msg}'
            
            if 'IntegrityError' in error_type:
                error_message = 'Erro de integridade de dados. Verifique se todos os campos foram preenchidos corretamente.'
            elif 'ValidationError' in error_type:
                error_message = f'Erro de validação: {error_msg}'
            elif 'PermissionError' in error_type or 'OSError' in error_type:
                error_message = 'Erro ao salvar arquivo. Verifique as permissões do servidor.'
            elif 'DoesNotExist' in error_type:
                error_message = f'Registro não encontrado: {error_msg}'
            elif 'AttributeError' in error_type:
                error_message = f'Erro de atributo: {error_msg}'
            
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': error_message,
                    'error_type': error_type,
                    'error_detail': error_msg if settings.DEBUG else None
                }, status=500)
            
            messages.error(request, error_message)
            return redirect('militares:entrada_almoxarifado_list')
    
    # GET request - mostrar formulário
    form = EntradaAlmoxarifadoForm(request=request)
    
    if is_ajax:
        html = render_to_string('militares/entrada_almoxarifado_form_modal.html', {
            'form': form,
            'is_create': True
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return render(request, 'militares/entrada_almoxarifado_form.html', {'form': form})


@login_required
def entrada_almoxarifado_update(request, pk):
    """Atualiza uma entrada via modal"""
    logger = logging.getLogger(__name__)
    
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'EDITAR'):
        messages.error(request, "Você não tem permissão para editar entradas.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)

    from django.db.models import Prefetch
    from .models import EntradaAlmoxarifadoProduto
    
    entrada = get_object_or_404(
        EntradaAlmoxarifado.objects.prefetch_related(
            Prefetch(
                'produtos_entrada',
                queryset=EntradaAlmoxarifadoProduto.objects.select_related('produto')
            ),
            'documentos__upload_por'
        ),
        pk=pk
    )
    
    # Verificar se pode editar
    if not entrada.pode_editar(request.user):
        messages.error(request, "Esta entrada não pode ser editada. Transferências não podem ser editadas.")
        return JsonResponse({'status': 'error', 'message': 'Não é possível editar esta entrada'}, status=403)
    
    if request.method == 'POST':
        form = EntradaAlmoxarifadoForm(request.POST, instance=entrada, request=request)
        if form.is_valid():
            from django.db import transaction
            from .models import EntradaAlmoxarifadoProduto, ProdutoAlmoxarifado
            
            with transaction.atomic():
                entrada = form.save(commit=False)
                
                # Processar múltiplos itens
                itens_data = request.POST.get('itens_data')
                if itens_data:
                    # Se houver múltiplos itens, definir produto como None
                    # Quantidade será calculada após processar os produtos
                    entrada.produto = None
                    entrada.quantidade = Decimal('0')  # Valor temporário, será atualizado
                
                # Garantir que quantidade não seja None (campo obrigatório no banco)
                if not entrada.quantidade:
                    entrada.quantidade = Decimal('0')
                
                entrada.save()
                
                # Importar modelos necessários
                from .models import DocumentoEntradaAlmoxarifado
                import json
                
                try:
                    if itens_data:
                        itens_list = json.loads(itens_data)
                        
                        # Obter IDs dos itens que devem ser mantidos
                        itens_ids_manter = [item.get('id') for item in itens_list if item.get('id')]
                        
                        # Remover itens que não estão mais na lista
                        EntradaAlmoxarifadoProduto.objects.filter(entrada=entrada).exclude(id__in=itens_ids_manter).delete()
                        
                        quantidade_total = Decimal('0')
                        
                        for item_data in itens_list:
                            produto_entrada_id = item_data.get('id')
                            item_id = item_data.get('item_id') or item_data.get('produto_id')
                            quantidade = Decimal(str(item_data.get('quantidade', 0)))
                            valor_unitario_str = item_data.get('valor_unitario')
                            valor_total_str = item_data.get('valor_total')
                            
                            if not item_id or quantidade <= 0:
                                continue
                            
                            try:
                                produto = ProdutoAlmoxarifado.objects.get(pk=item_id)
                            except ProdutoAlmoxarifado.DoesNotExist:
                                raise ValueError(f'Produto com ID {item_id} não encontrado.')
                            
                            # Processar valores (apenas se for COMPRA)
                            valor_unitario = None
                            valor_total = None
                            if entrada.tipo_entrada == 'COMPRA':
                                if valor_unitario_str is not None and valor_unitario_str != '':
                                    try:
                                        valor_unitario = Decimal(str(valor_unitario_str))
                                    except (ValueError, TypeError, InvalidOperation):
                                        logger.warning(f'Erro ao converter valor_unitario: {valor_unitario_str}')
                                        pass
                                
                                if valor_total_str is not None and valor_total_str != '':
                                    try:
                                        valor_total = Decimal(str(valor_total_str))
                                    except (ValueError, TypeError, InvalidOperation):
                                        logger.warning(f'Erro ao converter valor_total: {valor_total_str}')
                                        pass
                                
                                # Se não houver valor_total mas houver valor_unitario e quantidade, calcular
                                if not valor_total and valor_unitario and quantidade:
                                    valor_total = valor_unitario * quantidade
                                
                                logger.info(f'Produto {produto.codigo}: valor_unitario={valor_unitario}, valor_total={valor_total}, quantidade={quantidade}')
                            
                            # Atualizar ou criar produto da entrada
                            if produto_entrada_id:
                                try:
                                    produto_entrada = EntradaAlmoxarifadoProduto.objects.get(
                                        id=produto_entrada_id,
                                        entrada=entrada
                                    )
                                    produto_entrada.produto = produto
                                    produto_entrada.quantidade = quantidade
                                    produto_entrada.valor_unitario = valor_unitario
                                    produto_entrada.valor_total = valor_total
                                    produto_entrada.save()
                                except EntradaAlmoxarifadoProduto.DoesNotExist:
                                    produto_entrada = EntradaAlmoxarifadoProduto.objects.create(
                                        entrada=entrada,
                                        produto=produto,
                                        quantidade=quantidade,
                                        valor_unitario=valor_unitario,
                                        valor_total=valor_total
                                    )
                            else:
                                produto_entrada, created = EntradaAlmoxarifadoProduto.objects.get_or_create(
                                    entrada=entrada,
                                    produto=produto,
                                    defaults={
                                        'quantidade': quantidade,
                                        'valor_unitario': valor_unitario,
                                        'valor_total': valor_total
                                    }
                                )
                                if not created:
                                    produto_entrada.quantidade = quantidade
                                    produto_entrada.valor_unitario = valor_unitario
                                    produto_entrada.valor_total = valor_total
                                    produto_entrada.save()
                            
                            quantidade_total += quantidade
                            
                            # Atualizar estoque do produto
                            if produto:
                                produto.recalcular_quantidade_atual()
                        
                        # Atualizar quantidade total na entrada (campo obrigatório no banco)
                        entrada.quantidade = quantidade_total
                        entrada.save(update_fields=['quantidade'])
                    
                    # Processar upload de novos documentos
                    documentos_upload = request.FILES.getlist('documentos_upload')
                    tipos_documentos = request.POST.getlist('tipos_documentos[]')
                    titulos_documentos = request.POST.getlist('titulos_documentos[]')
                    
                    for idx, arquivo in enumerate(documentos_upload):
                        if arquivo:
                            tipo_doc = tipos_documentos[idx] if idx < len(tipos_documentos) else 'OUTROS'
                            titulo_doc = titulos_documentos[idx] if idx < len(titulos_documentos) else arquivo.name
                            
                            DocumentoEntradaAlmoxarifado.objects.create(
                                entrada=entrada,
                                tipo=tipo_doc,
                                titulo=titulo_doc,
                                arquivo=arquivo,
                                upload_por=request.user
                            )
                    
                    # Processar remoção de documentos
                    documentos_remover = request.POST.getlist('documentos_remover[]')
                    if documentos_remover:
                        DocumentoEntradaAlmoxarifado.objects.filter(
                            id__in=documentos_remover,
                            entrada=entrada
                        ).delete()
                        
                except (json.JSONDecodeError, ProdutoAlmoxarifado.DoesNotExist) as e:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Erro ao processar itens: {str(e)}'
                        }, status=400)
                    messages.error(request, f'Erro ao processar itens: {str(e)}')
                    return redirect('militares:entrada_almoxarifado_list')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Entrada atualizada com sucesso!',
                    'redirect': reverse('militares:entrada_almoxarifado_list')
                })
            messages.success(request, 'Entrada atualizada com sucesso!')
            return redirect('militares:entrada_almoxarifado_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/entrada_almoxarifado_form_modal.html', {
                    'form': form,
                    'entrada': entrada,
                    'is_create': False,
                    'pode_editar': entrada.pode_editar(request.user)
                }, request=request)
                return JsonResponse({'status': 'error', 'message': 'Erro de validação', 'html': html}, status=400)
    else:
        form = EntradaAlmoxarifadoForm(instance=entrada, request=request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Debug: verificar produtos_entrada
        produtos_entrada_list = list(entrada.produtos_entrada.all())
        logger = logging.getLogger(__name__)
        logger.info(f'Entrada {entrada.pk} - Produtos: {[(p.produto.codigo, p.quantidade) for p in produtos_entrada_list]}')
        
        html = render_to_string('militares/entrada_almoxarifado_form_modal.html', {
            'form': form,
            'entrada': entrada,
            'is_create': False,
            'pode_editar': entrada.pode_editar(request.user)
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return render(request, 'militares/entrada_almoxarifado_form.html', {'form': form, 'entrada': entrada})


@login_required
def entrada_almoxarifado_detail(request, pk):
    """Visualiza os detalhes de uma entrada"""
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'VISUALIZAR'):
        messages.error(request, "Você não tem permissão para visualizar entradas.")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
        return redirect('militares:entrada_almoxarifado_list')
    
    from django.db.models import Prefetch
    from .models import EntradaAlmoxarifadoProduto, AssinaturaEntradaAlmoxarifado
    
    entrada = get_object_or_404(
        EntradaAlmoxarifado.objects.select_related(
            'produto', 'responsavel', 'criado_por',
            'orgao_origem', 'grande_comando_origem', 'unidade_origem', 'sub_unidade_origem',
            'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino'
        ).prefetch_related(
            Prefetch(
                'produtos_entrada',
                queryset=EntradaAlmoxarifadoProduto.objects.select_related('produto')
            ),
            'assinaturas__assinado_por',
            'assinaturas__militar',
            'documentos__upload_por'
        ),
        pk=pk
    )
    
    # Buscar assinaturas se existirem
    assinaturas = AssinaturaEntradaAlmoxarifado.objects.filter(
        entrada=entrada
    ).select_related('assinado_por', 'militar').order_by('data_assinatura')
    
    context = {
        'entrada': entrada,
        'assinaturas': assinaturas,
        'pode_editar': entrada.pode_editar(request.user),
        'pode_excluir': entrada.pode_excluir(request.user),
    }
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if is_ajax:
        html = render_to_string('militares/entrada_almoxarifado_detail_modal.html', context, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return render(request, 'militares/entrada_almoxarifado_detail.html', context)


@login_required
def entrada_almoxarifado_delete(request, pk):
    """Deleta uma entrada"""
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'EXCLUIR'):
        messages.error(request, "Você não tem permissão para excluir entradas.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)

    entrada = get_object_or_404(EntradaAlmoxarifado, pk=pk)
    
    # Verificar se pode excluir
    if not entrada.pode_excluir(request.user):
        messages.error(request, "Esta entrada não pode ser excluída. Transferências não podem ser excluídas.")
        return JsonResponse({'status': 'error', 'message': 'Não é possível excluir esta entrada'}, status=403)
    
    if request.method == 'POST':
        entrada.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Entrada deletada com sucesso!'
            })
        messages.success(request, 'Entrada deletada com sucesso!')
        return redirect('militares:entrada_almoxarifado_list')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/entrada_almoxarifado_delete_modal.html', {
            'entrada': entrada,
            'pode_excluir': entrada.pode_excluir(request.user)
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return render(request, 'militares/entrada_almoxarifado_delete.html', {'entrada': entrada})


# ============================================================================
# VIEWS PARA SAÍDAS DO ALMOXARIFADO
# ============================================================================

class SaidaAlmoxarifadoListView(LoginRequiredMixin, ListView):
    model = SaidaAlmoxarifado
    template_name = 'militares/saida_almoxarifado_list.html'
    context_object_name = 'saidas'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Verificar permissão de visualizar antes de permitir acesso
        if not tem_permissao(request.user, 'ALMOXARIFADO', 'VISUALIZAR'):
            from django.contrib import messages
            messages.error(request, "Você não tem permissão para visualizar saídas do almoxarifado.")
            from django.shortcuts import redirect
            return redirect('militares:home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        from django.db.models import Prefetch
        from django.db import ProgrammingError
        from .models import SaidaAlmoxarifadoProduto
        
        queryset = SaidaAlmoxarifado.objects.select_related(
            'produto', 'requisitante', 'responsavel_entrega', 'criado_por'
        )
        
        # Fazer prefetch dos produtos da saída
        try:
            queryset = queryset.prefetch_related(
                Prefetch(
                    'produtos_saida',
                    queryset=SaidaAlmoxarifadoProduto.objects.select_related('produto')
                )
            )
        except (ProgrammingError, Exception):
            # Se houver erro, tentar sem prefetch (pode ser que a tabela não exista ainda)
            pass
        
        queryset = queryset.order_by('-data_saida', '-data_criacao')

        # SEMPRE aplicar filtro hierárquico baseado no tipo de acesso da função militar
        # As saídas devem ser listadas apenas nas OMs de acordo com os filtros
        funcao_usuario = obter_sessao_ativa_usuario(self.request.user)
        if funcao_usuario:
            queryset = aplicar_filtro_hierarquico_saidas_almoxarifado(queryset, funcao_usuario, self.request.user)
        else:
            # Se não há função ativa, não mostrar nenhuma saída
            queryset = queryset.none()

        search = self.request.GET.get('search', '')
        tipo_saida = self.request.GET.get('tipo_saida', '')
        item_id = self.request.GET.get('item', '')

        if search:
            search_q = Q(produto__codigo__icontains=search) | Q(produto__descricao__icontains=search) | Q(numero_requisicao__icontains=search)
            # Adicionar filtro de produtos_saida
            try:
                search_q |= Q(produtos_saida__produto__codigo__icontains=search) | Q(produtos_saida__produto__descricao__icontains=search)
            except (ProgrammingError, Exception):
                pass
            queryset = queryset.filter(search_q).distinct()

        if tipo_saida:
            queryset = queryset.filter(tipo_saida=tipo_saida)

        if item_id:
            item_q = Q(produto_id=item_id)
            # Adicionar filtro de produtos_saida
            try:
                item_q |= Q(produtos_saida__produto_id=item_id)
            except (ProgrammingError, Exception):
                pass
            queryset = queryset.filter(item_q).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['tipo_saida'] = self.request.GET.get('tipo_saida', '')
        context['item_id'] = self.request.GET.get('item', '')

        context['tipos'] = SaidaAlmoxarifado.TIPO_SAIDA_CHOICES
        context['itens'] = ProdutoAlmoxarifado.objects.filter(ativo=True).order_by('codigo')

        # Estatísticas (aplicar filtro hierárquico também nas estatísticas)
        queryset_stats = SaidaAlmoxarifado.objects.all()
        funcao_usuario = obter_sessao_ativa_usuario(self.request.user)
        if funcao_usuario:
            queryset_stats = aplicar_filtro_hierarquico_saidas_almoxarifado(queryset_stats, funcao_usuario, self.request.user)
        
        context['total_saidas'] = queryset_stats.count()
        context['saidas_mes'] = queryset_stats.filter(
            data_saida__month=timezone.now().month,
            data_saida__year=timezone.now().year
        ).count()

        # Permissões
        user = self.request.user
        context['pode_criar'] = tem_permissao(user, 'ALMOXARIFADO', 'CRIAR')
        context['pode_editar'] = tem_permissao(user, 'ALMOXARIFADO', 'EDITAR')
        # Apenas superusuários podem excluir
        context['pode_excluir'] = user.is_superuser
        
        # Adicionar informações sobre quais saídas podem ser editadas/excluídas
        saidas_com_permissao = {}
        for saida in context['saidas']:
            saidas_com_permissao[saida.pk] = {
                'pode_editar': saida.pode_editar(user),
                # Apenas superusuários podem excluir (e não pode ter assinatura de recebimento)
                'pode_excluir': user.is_superuser and saida.pode_excluir(user)
            }
        context['saidas_com_permissao'] = saidas_com_permissao
        
        # Verificar quais saídas já têm assinatura de recebimento
        saidas_com_assinatura = set(
            AssinaturaSaidaAlmoxarifado.objects.filter(
                saida__in=context['saidas'],
                tipo_assinatura='RECEBIMENTO'
            ).values_list('saida_id', flat=True)
        )
        context['saidas_com_assinatura'] = saidas_com_assinatura

        return context


@login_required
def saida_almoxarifado_create(request):
    """
    Cria uma saída de mercadoria do almoxarifado da OM do usuário.
    Remove itens do estoque da OM atual.
    Pode ser:
    - Saída para militar (uso direto)
    - Transferência para outra OM
    """
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'CRIAR'):
        messages.error(request, "Você não tem permissão para criar saídas.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)

    if request.method == 'POST':
        form = SaidaAlmoxarifadoForm(request.POST, request=request)
        if form.is_valid():
            try:
                # Validar que a OM de origem foi informada
                saida_data = form.cleaned_data
                if not (saida_data.get('orgao_origem') or saida_data.get('unidade_origem') or saida_data.get('grande_comando_origem')):
                    raise ValueError('É necessário informar a Organização Militar de origem (de onde a mercadoria vai sair).')
                
                # Se for transferência, validar que a OM de destino foi informada
                if saida_data.get('tipo_saida') == 'TRANSFERENCIA':
                    if not (saida_data.get('orgao_destino') or saida_data.get('unidade_destino') or saida_data.get('grande_comando_destino')):
                        raise ValueError('É necessário informar a Organização Militar de destino para transferências.')
                
                # Processar itens ANTES de criar a saída
                itens_data = request.POST.get('itens_data', '[]')
                itens_list = json.loads(itens_data)
                
                if not itens_list or not isinstance(itens_list, list) or len(itens_list) == 0:
                    raise ValueError('É necessário adicionar pelo menos um item à saída.')
                
                # Validar estoque de todos os itens antes de criar a saída
                itens_validados = []
                for item_data in itens_list:
                    if not isinstance(item_data, dict):
                        continue
                    
                    item_id = item_data.get('item_id') or item_data.get('produto_id')
                    quantidade_str = item_data.get('quantidade', '0')
                    
                    if not item_id:
                        continue
                    
                    try:
                        quantidade = Decimal(str(quantidade_str))
                    except (ValueError, TypeError, InvalidOperation):
                        continue
                    
                    if quantidade <= 0:
                        continue
                    
                    try:
                        item = ProdutoAlmoxarifado.objects.get(pk=item_id, ativo=True)
                    except ProdutoAlmoxarifado.DoesNotExist:
                        raise ValueError(f'Item com ID {item_id} não encontrado ou inativo.')
                    
                    # Calcular estoque disponível na OM de origem
                    estoque_disponivel = item.get_estoque_por_om(
                        orgao=saida_data.get('orgao_origem'),
                        grande_comando=saida_data.get('grande_comando_origem'),
                        unidade=saida_data.get('unidade_origem'),
                        sub_unidade=saida_data.get('sub_unidade_origem')
                    )
                    
                    # Validar estoque
                    if estoque_disponivel < quantidade:
                        raise ValueError(
                            f'Estoque insuficiente para o item {item.get_codigo_limpo()} na OM de origem. '
                            f'Disponível: {estoque_disponivel}, Solicitado: {quantidade}.'
                        )
                    
                    itens_validados.append({
                        'item': item,
                        'quantidade': quantidade,
                        'item_data': item_data
                    })
                
                if not itens_validados:
                    raise ValueError('Nenhum item válido foi encontrado. Verifique os itens adicionados.')
                
                # Agora sim, criar a saída dentro da transação
                with transaction.atomic():
                    from .models import SaidaAlmoxarifadoProduto
                    from django.db import ProgrammingError, connection
                    
                    # Verificar se a tabela de múltiplos produtos existe
                    tabela_saida_produto_existe = False
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("""
                                SELECT EXISTS (
                                    SELECT FROM information_schema.tables 
                                    WHERE table_name = 'militares_saidaalmoxarifadoproduto'
                                );
                            """)
                            tabela_saida_produto_existe = cursor.fetchone()[0]
                    except Exception:
                        pass
                    
                    # Calcular quantidade total (para compatibilidade com campo legado)
                    quantidade_total = sum(item['quantidade'] for item in itens_validados)
                    
                    # Criar saída (usar primeiro item para campos legados se necessário)
                    primeiro_item = itens_validados[0]
                    saida = SaidaAlmoxarifado(
                        produto=primeiro_item['item'] if not tabela_saida_produto_existe else None,
                        quantidade=quantidade_total,  # Sempre preencher quantidade (campo obrigatório)
                        tipo_saida=saida_data.get('tipo_saida'),
                        data_saida=saida_data.get('data_saida'),
                        numero_requisicao=saida_data.get('numero_requisicao', ''),
                        requisitante=saida_data.get('requisitante'),
                        responsavel_entrega=saida_data.get('responsavel_entrega'),
                        orgao_origem=saida_data.get('orgao_origem'),
                        grande_comando_origem=saida_data.get('grande_comando_origem'),
                        unidade_origem=saida_data.get('unidade_origem'),
                        sub_unidade_origem=saida_data.get('sub_unidade_origem'),
                        orgao_destino=saida_data.get('orgao_destino'),
                        grande_comando_destino=saida_data.get('grande_comando_destino'),
                        unidade_destino=saida_data.get('unidade_destino'),
                        sub_unidade_destino=saida_data.get('sub_unidade_destino'),
                        observacoes=saida_data.get('observacoes', ''),
                        ativo=True,
                        criado_por=request.user
                    )
                    saida.save()
                    
                    # Processar todos os itens
                    for item_validado in itens_validados:
                        item = item_validado['item']
                        quantidade = item_validado['quantidade']
                        
                        # Criar relação saída-produto (se a tabela existir)
                        if tabela_saida_produto_existe:
                            try:
                                SaidaAlmoxarifadoProduto.objects.create(
                                    saida=saida,
                                    produto=item,
                                    quantidade=quantidade
                                )
                            except (ProgrammingError, Exception) as e:
                                import logging
                                logger = logging.getLogger(__name__)
                                logger.error(f'Erro ao criar SaidaAlmoxarifadoProduto: {e}')
                                # Se falhar, usar campos legados para o primeiro item
                                if not saida.produto:
                                    saida.produto = item
                                    saida.quantidade = quantidade
                                    saida.save(update_fields=['produto', 'quantidade'])
                        
                        # Se for transferência, criar entrada automática na OM destino para cada item
                        if saida.tipo_saida == 'TRANSFERENCIA' and (saida.orgao_destino or saida.unidade_destino or saida.grande_comando_destino):
                            try:
                                from .models import EntradaAlmoxarifadoProduto
                                
                                # Criar entrada na OM destino
                                entrada = EntradaAlmoxarifado.objects.create(
                                    tipo_entrada='TRANSFERENCIA',
                                    data_entrada=saida.data_saida,
                                    quantidade=quantidade,  # Para compatibilidade
                                    orgao_origem=saida.orgao_origem,
                                    grande_comando_origem=saida.grande_comando_origem,
                                    unidade_origem=saida.unidade_origem,
                                    sub_unidade_origem=saida.sub_unidade_origem,
                                    orgao_destino=saida.orgao_destino,
                                    grande_comando_destino=saida.grande_comando_destino,
                                    unidade_destino=saida.unidade_destino,
                                    sub_unidade_destino=saida.sub_unidade_destino,
                                    observacoes=f'Transferência automática gerada a partir da saída #{saida.pk}',
                                    ativo=True,
                                    criado_por=saida.criado_por
                                )
                                
                                # Criar relação entrada-produto (se a tabela existir)
                                try:
                                    EntradaAlmoxarifadoProduto.objects.create(
                                        entrada=entrada,
                                        produto=item,
                                        quantidade=quantidade
                                    )
                                except (ProgrammingError, Exception):
                                    # Se falhar, usar campo legado
                                    entrada.produto = item
                                    entrada.save(update_fields=['produto'])
                                    
                            except Exception as e:
                                import logging
                                logger = logging.getLogger(__name__)
                                logger.error(f'Erro ao criar entrada automática para transferência: {e}')
                                # Continuar com outros itens mesmo se falhar
                                pass
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Saída registrada com sucesso!',
                        'redirect': reverse('militares:saida_almoxarifado_list')
                    })
                messages.success(request, 'Saída registrada com sucesso!')
                return redirect('militares:saida_almoxarifado_list')
                
            except (json.JSONDecodeError, ProdutoAlmoxarifado.DoesNotExist, ValueError) as e:
                import traceback
                import logging
                from django.conf import settings
                logger = logging.getLogger(__name__)
                error_msg = str(e)
                error_trace = traceback.format_exc()
                logger.error(f'Erro ao criar saída: {error_msg}')
                logger.error(error_trace)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Erro ao processar saída: {error_msg}',
                        'traceback': error_trace if settings.DEBUG else None
                    }, status=400)
                messages.error(request, f'Erro ao processar saída: {error_msg}')
                return redirect('militares:saida_almoxarifado_list')
            except Exception as e:
                import traceback
                import logging
                from django.conf import settings
                logger = logging.getLogger(__name__)
                error_msg = str(e)
                error_trace = traceback.format_exc()
                logger.error(f'Erro inesperado ao criar saída: {error_msg}')
                logger.error(error_trace)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Erro inesperado: {error_msg}',
                        'traceback': error_trace if settings.DEBUG else None
                    }, status=500)
                messages.error(request, f'Erro inesperado: {error_msg}')
                return redirect('militares:saida_almoxarifado_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/saida_almoxarifado_form_modal.html', {
                    'form': form,
                    'is_create': True
                }, request=request)
                # Incluir erros do formulário na resposta para debug
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(e) for e in error_list]
                
                # Log dos erros para debug
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erros de validação: {errors}')
                logger.error(f'Dados do formulário: {form.data}')
                
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Erro de validação', 
                    'html': html,
                    'errors': errors,
                    'form_data': dict(form.data) if hasattr(form, 'data') else {}
                }, status=400)
    else:
        form = SaidaAlmoxarifadoForm(request=request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/saida_almoxarifado_form_modal.html', {
            'form': form,
            'is_create': True
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return render(request, 'militares/saida_almoxarifado_form.html', {'form': form})


@login_required
def saida_almoxarifado_update(request, pk):
    """Atualiza uma saída via modal"""
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'EDITAR'):
        messages.error(request, "Você não tem permissão para editar saídas.")
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)

    from django.db.models import Prefetch
    from .models import SaidaAlmoxarifadoProduto
    
    saida = get_object_or_404(
        SaidaAlmoxarifado.objects.prefetch_related(
            Prefetch(
                'produtos_saida',
                queryset=SaidaAlmoxarifadoProduto.objects.select_related('produto')
            )
        ),
        pk=pk
    )
    
    # Verificar se pode editar
    if not saida.pode_editar(request.user):
        if saida.assinaturas.filter(tipo_assinatura='RECEBIMENTO').exists():
            error_msg = "Esta saída não pode ser editada pois já possui assinatura de recebimento."
        else:
            error_msg = "Esta saída não pode ser editada. Apenas transferências podem ser editadas por superusuários."
        messages.error(request, error_msg)
        return JsonResponse({'status': 'error', 'message': error_msg}, status=403)
    
    if request.method == 'POST':
        form = SaidaAlmoxarifadoForm(request.POST, instance=saida, request=request)
        if form.is_valid():
            from django.db import transaction
            from .models import SaidaAlmoxarifadoProduto, ProdutoAlmoxarifado
            
            with transaction.atomic():
                saida = form.save(commit=False)
                
                # Processar múltiplos itens
                itens_data = request.POST.get('itens_data')
                if itens_data:
                    # Se houver múltiplos itens, definir quantidade e item como None
                    saida.quantidade = None
                    saida.item = None
                
                saida.save()
                
                if itens_data:
                    import json
                    try:
                        itens_list = json.loads(itens_data)
                        
                        # Obter IDs dos itens que devem ser mantidos
                        itens_ids_manter = [item.get('id') for item in itens_list if item.get('id')]
                        
                        # Verificar se a tabela de múltiplos produtos existe
                        from django.db import connection, ProgrammingError
                        tabela_saida_produto_existe = False
                        try:
                            with connection.cursor() as cursor:
                                cursor.execute("""
                                    SELECT EXISTS (
                                        SELECT FROM information_schema.tables 
                                        WHERE table_name = 'militares_saidaalmoxarifadoproduto'
                                    );
                                """)
                                tabela_saida_produto_existe = cursor.fetchone()[0]
                        except Exception:
                            pass
                        
                        # Remover itens que não estão mais na lista (se a tabela existir)
                        if tabela_saida_produto_existe:
                            try:
                                SaidaAlmoxarifadoProduto.objects.filter(saida=saida).exclude(id__in=itens_ids_manter).delete()
                            except (ProgrammingError, Exception):
                                tabela_saida_produto_existe = False
                        
                        for item_data in itens_list:
                            produto_saida_id = item_data.get('id')
                            item_id = item_data.get('item_id')
                            quantidade = Decimal(str(item_data.get('quantidade', 0)))
                            
                            if not item_id or quantidade <= 0:
                                continue
                            
                            try:
                                item = ProdutoAlmoxarifado.objects.get(pk=item_id)
                            except ProdutoAlmoxarifado.DoesNotExist:
                                raise ValueError(f'Item com ID {item_id} não encontrado.')
                            
                            # Em uma saída, o item não pode ser None
                            if not item:
                                raise ValueError(f'Item com ID {item_id} é inválido. Não é possível processar saída sem item válido.')
                            
                            # Atualizar ou criar item da saída
                            if tabela_saida_produto_existe:
                                try:
                                    if produto_saida_id:
                                        try:
                                            produto_saida = SaidaAlmoxarifadoProduto.objects.get(
                                                id=produto_saida_id,
                                                saida=saida
                                            )
                                            produto_saida.produto = item  # Usar 'produto' em vez de 'item'
                                            produto_saida.quantidade = quantidade
                                            produto_saida.save()
                                        except SaidaAlmoxarifadoProduto.DoesNotExist:
                                            produto_saida = SaidaAlmoxarifadoProduto.objects.create(
                                                saida=saida,
                                                produto=item,  # Usar 'produto' em vez de 'item'
                                                quantidade=quantidade
                                            )
                                    else:
                                        produto_saida, created = SaidaAlmoxarifadoProduto.objects.get_or_create(
                                            saida=saida,
                                            produto=item,  # Usar 'produto' em vez de 'item'
                                            defaults={'quantidade': quantidade}
                                        )
                                        if not created:
                                            produto_saida.quantidade = quantidade
                                            produto_saida.save()
                                except (ProgrammingError, Exception) as e:
                                    # Se houver erro, usar campos legados
                                    import logging
                                    logger = logging.getLogger(__name__)
                                    logger.warning(f'Erro ao atualizar SaidaAlmoxarifadoProduto, usando campos legados: {e}')
                                    # Usar campos legados para o primeiro item
                                    if not saida.produto:
                                        saida.produto = item
                                        saida.quantidade = quantidade
                                        saida.save(update_fields=['produto', 'quantidade'])
                            else:
                                # Se a tabela não existir, usar campos legados
                                # Usar campos legados para o primeiro item
                                if not saida.produto:
                                    saida.produto = item
                                    saida.quantidade = quantidade
                                    saida.save(update_fields=['produto', 'quantidade'])
                            
                            # Atualizar estoque do item
                            if item:
                                item.recalcular_quantidade_atual()
                    except (json.JSONDecodeError, ProdutoAlmoxarifado.DoesNotExist) as e:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'status': 'error',
                                'message': f'Erro ao processar itens: {str(e)}'
                            }, status=400)
                        messages.error(request, f'Erro ao processar itens: {str(e)}')
                        return redirect('militares:saida_almoxarifado_list')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Saída atualizada com sucesso!',
                    'redirect': reverse('militares:saida_almoxarifado_list')
                })
            messages.success(request, 'Saída atualizada com sucesso!')
            return redirect('militares:saida_almoxarifado_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/saida_almoxarifado_form_modal.html', {
                    'form': form,
                    'saida': saida,
                    'is_create': False
                }, request=request)
                return JsonResponse({'status': 'error', 'message': 'Erro de validação', 'html': html}, status=400)
    else:
        form = SaidaAlmoxarifadoForm(instance=saida, request=request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/saida_almoxarifado_form_modal.html', {
            'form': form,
            'saida': saida,
            'is_create': False
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return render(request, 'militares/saida_almoxarifado_form.html', {'form': form, 'saida': saida})


@login_required
def saida_almoxarifado_delete(request, pk):
    """
    Deleta uma saída e reverte o estoque dos itens para a origem
    
    REGRAS:
    - Verifica permissões antes de permitir exclusão
    - Não permite excluir se já tiver assinatura de recebimento
    - Ao excluir, os itens voltam automaticamente para o estoque de origem
    - Se for transferência, também exclui a entrada automática no destino
    - Usa transação para garantir atomicidade da operação
    """
    from django.db import transaction
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Verificar se é superusuário - apenas superusuários podem deletar
    if not request.user.is_superuser:
        error_msg = "Apenas superusuários podem excluir saídas do almoxarifado."
        messages.error(request, error_msg)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': error_msg}, status=403)
        return redirect('militares:saida_almoxarifado_list')

    # Otimizar consultas para evitar N+1 queries e erros ao acessar relacionamentos
    from django.db.models import Prefetch
    saida = get_object_or_404(
        SaidaAlmoxarifado.objects.select_related(
            'item',
            'orgao_origem', 'grande_comando_origem', 'unidade_origem', 'sub_unidade_origem',
            'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino'
        ).prefetch_related(
            Prefetch(
                'produtos_saida',
                queryset=SaidaAlmoxarifadoProduto.objects.select_related('produto')
            ),
            'assinaturas'
        ),
        pk=pk
    )
    
    # Verificar se pode excluir (apenas superusuários podem excluir)
    # Verificar também se já tem assinatura de recebimento
    if saida.assinaturas.filter(tipo_assinatura='RECEBIMENTO').exists():
        error_msg = "Esta saída não pode ser excluída pois já possui assinatura de recebimento."
        messages.error(request, error_msg)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': error_msg}, status=403)
        return redirect('militares:saida_almoxarifado_list')
    
    # Se for GET, mostrar modal de confirmação
    if request.method != 'POST':
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Preparar contexto com informações de debug se necessário
                context = {
                    'saida': saida
                }
                html = render_to_string('militares/saida_almoxarifado_delete_modal.html', context, request=request)
                return JsonResponse({'status': 'success', 'html': html})
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                logger.error(
                    f"Erro ao renderizar modal de exclusão de saída {pk}: {str(e)}\n"
                    f"Traceback:\n{error_trace}",
                    exc_info=True
                )
                # Retornar mensagem de erro mais detalhada em desenvolvimento
                error_message = f'Erro ao carregar confirmação de exclusão: {str(e)}'
                if settings.DEBUG:
                    error_message += f'\n\nDetalhes: {error_trace}'
                return JsonResponse({
                    'status': 'error',
                    'message': error_message
                }, status=500)
        return render(request, 'militares/saida_almoxarifado_delete.html', {'saida': saida})
    
    # POST - Processar exclusão
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        # Coletar informações antes de excluir para logs
        saida_id = saida.pk
        tipo_saida = saida.get_tipo_saida_display()
        data_saida = saida.data_saida
        
        # Coletar informações dos produtos que serão afetados
        produtos_info = []
        for produto_saida in saida.produtos_saida.all():
            if produto_saida.produto:
                # unidade_medida é um CharField, não ForeignKey, então acessar diretamente
                unidade = produto_saida.produto.unidade_medida if produto_saida.produto.unidade_medida else ''
                produtos_info.append({
                    'codigo': produto_saida.produto.get_codigo_limpo(),
                    'descricao': produto_saida.produto.descricao,
                    'quantidade': float(produto_saida.quantidade),
                    'unidade': unidade,
                })
        
        # Se tiver produto legado, adicionar também
        if saida.produto:
            # unidade_medida é um CharField, não ForeignKey, então acessar diretamente
            unidade = saida.produto.unidade_medida if saida.produto.unidade_medida else ''
            produtos_info.append({
                'codigo': saida.produto.get_codigo_limpo(),
                'descricao': saida.produto.descricao,
                'quantidade': float(saida.quantidade) if saida.quantidade else 0,
                'unidade': unidade,
            })
        
        # Obter origem e destino para mensagem
        origem = None
        if saida.sub_unidade_origem:
            origem = str(saida.sub_unidade_origem)
        elif saida.unidade_origem:
            origem = str(saida.unidade_origem)
        elif saida.grande_comando_origem:
            origem = str(saida.grande_comando_origem)
        elif saida.orgao_origem:
            origem = str(saida.orgao_origem)
        
        destino = None
        if saida.sub_unidade_destino:
            destino = str(saida.sub_unidade_destino)
        elif saida.unidade_destino:
            destino = str(saida.unidade_destino)
        elif saida.grande_comando_destino:
            destino = str(saida.grande_comando_destino)
        elif saida.orgao_destino:
            destino = str(saida.orgao_destino)
        
        # Executar exclusão dentro de uma transação
        with transaction.atomic():
            # O método delete() do modelo já trata de:
            # 1. Excluir entrada automática se for transferência
            # 2. Recalcular estoque de todos os itens afetados
            # 3. Fazer os itens voltarem para a origem
            saida.delete()
        
        # Log da operação
        logger.info(
            f"Saída {saida_id} excluída por {request.user.username}. "
            f"Tipo: {tipo_saida}, Data: {data_saida}, "
            f"Origem: {origem}, Destino: {destino}, "
            f"Produtos afetados: {len(produtos_info)}"
        )
        
        # Mensagem de sucesso detalhada
        if len(produtos_info) == 1:
            produto_info = produtos_info[0]
            mensagem = (
                f"Saída excluída com sucesso! "
                f"O produto {produto_info['codigo']} ({produto_info['quantidade']} {produto_info['unidade']}) "
                f"foi devolvido ao estoque de origem."
            )
        else:
            mensagem = (
                f"Saída excluída com sucesso! "
                f"{len(produtos_info)} produtos foram devolvidos ao estoque de origem."
            )
        
        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': mensagem
            })
        
        messages.success(request, mensagem)
        return redirect('militares:saida_almoxarifado_list')
        
    except Exception as e:
        # Log do erro
        logger.error(
            f"Erro ao excluir saída {pk} por {request.user.username}: {str(e)}",
            exc_info=True
        )
        
        error_msg = f"Erro ao excluir saída: {str(e)}"
        
        if is_ajax:
            return JsonResponse({
                'status': 'error',
                'message': error_msg
            }, status=500)
        
        messages.error(request, error_msg)
        return redirect('militares:saida_almoxarifado_list')


@login_required
def saida_almoxarifado_detail(request, pk):
    """Visualiza detalhes de uma saída"""
    from django.db.models import Prefetch
    
    # Não incluir requisicao_origem no select_related pois pode não existir
    # O campo será acessado de forma segura usando getattr se necessário
    saida = get_object_or_404(
        SaidaAlmoxarifado.objects.select_related(
            'produto', 'requisitante', 'responsavel_entrega', 'criado_por',
            'orgao_origem', 'grande_comando_origem', 'unidade_origem', 'sub_unidade_origem',
            'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino'
        ).prefetch_related(
            Prefetch(
                'produtos_saida',
                queryset=SaidaAlmoxarifadoProduto.objects.select_related('produto')
            ),
            'assinaturas__assinado_por',
            'assinaturas__militar'
        ),
        pk=pk
    )
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if is_ajax:
        html = render_to_string('militares/saida_almoxarifado_detail_modal.html', {
            'saida': saida
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return render(request, 'militares/saida_almoxarifado_detail.html', {'saida': saida})


@login_required
def assinar_saida_almoxarifado(request, pk):
    """Assinar saída como recebedor - permite login do requisitante"""
    saida = get_object_or_404(SaidaAlmoxarifado, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        senha = request.POST.get('senha', '')
        
        # Verificar se há um requisitante na saída
        if not saida.requisitante:
            error_msg = 'Esta saída não possui requisitante definido.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('militares:saida_almoxarifado_list')
        
        # Verificar se o requisitante tem usuário vinculado
        requisitante = saida.requisitante
        user_requisitante = requisitante.user if requisitante.user else None
        
        if not user_requisitante:
            error_msg = 'O requisitante desta saída não possui usuário vinculado no sistema.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('militares:saida_almoxarifado_list')
        
        # Verificar senha do usuário do requisitante
        if not user_requisitante.check_password(senha):
            error_msg = 'Senha incorreta. Tente novamente.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('militares:saida_almoxarifado_list')
        
        # Verificar se já existe uma assinatura deste tipo
        assinatura_existente = AssinaturaSaidaAlmoxarifado.objects.filter(
            saida=saida,
            tipo_assinatura='RECEBIMENTO'
        ).first()
        
        if assinatura_existente:
            error_msg = 'Esta saída já possui assinatura de recebimento.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('militares:saida_almoxarifado_list')
        
        # Obter função do usuário
        funcao_assinatura = None
        sessao = obter_sessao_ativa_usuario(user_requisitante)
        if sessao and sessao.funcao_militar_usuario:
            funcao = sessao.funcao_militar_usuario.funcao_militar
            if funcao:
                funcao_assinatura = str(funcao)
        
        # Criar a assinatura
        try:
            assinatura = AssinaturaSaidaAlmoxarifado.objects.create(
                saida=saida,
                assinado_por=user_requisitante,
                militar=requisitante,
                tipo_assinatura='RECEBIMENTO',
                funcao_assinatura=funcao_assinatura,
                observacoes=''
            )
            success_msg = 'Assinatura de recebimento registrada com sucesso!'
            if is_ajax:
                return JsonResponse({'success': True, 'message': success_msg})
            messages.success(request, success_msg)
        except Exception as e:
            error_msg = f'Erro ao assinar saída: {str(e)}'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
        
        if not is_ajax:
            return redirect('militares:saida_almoxarifado_list')
        return JsonResponse({'success': True, 'message': success_msg})
    
    # Se for GET, retornar para a lista
    return redirect('militares:saida_almoxarifado_list')


@login_required
def subcategorias_ajax(request):
    """Retorna subcategorias de uma categoria via AJAX"""
    categoria_id = request.GET.get('categoria')
    
    if not categoria_id:
        return JsonResponse({'subcategorias': []})
    
    try:
        subcategorias = Subcategoria.objects.filter(
            categoria_id=categoria_id,
            ativo=True
        ).order_by('nome').values('id', 'nome')
        
        return JsonResponse({
            'subcategorias': list(subcategorias)
        })
    except Exception as e:
        return JsonResponse({'subcategorias': [], 'error': str(e)})


@login_required
def get_subcategorias(request):
    """Retorna subcategorias de uma categoria (formato alternativo)"""
    categoria_id = request.GET.get('categoria_id')
    
    if not categoria_id:
        return JsonResponse([], safe=False)
    
    try:
        subcategorias = Subcategoria.objects.filter(
            categoria_id=categoria_id,
            ativo=True
        ).order_by('nome').values('id', 'nome')
        
        return JsonResponse(list(subcategorias), safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)


@login_required
def criar_subcategoria(request):
    """Cria uma nova subcategoria vinculada a uma categoria."""
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria_id')
        nome = request.POST.get('nome')
        
        if not categoria_id or not nome:
            return JsonResponse({'erro': 'Categoria ID e nome são obrigatórios'}, status=400)
        
        try:
            # Verificar se a categoria existe
            categoria = Categoria.objects.get(pk=categoria_id, ativo=True)
            
            # Criar ou obter subcategoria
            sub, created = Subcategoria.objects.get_or_create(
                categoria_id=categoria_id,
                nome=nome.strip().title(),
                defaults={'ativo': True}
            )
            
            return JsonResponse({
                'id': sub.id,
                'nome': sub.nome,
                'nova': created,
                'success': True
            })
        except Categoria.DoesNotExist:
            return JsonResponse({'erro': 'Categoria não encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


# ============================================================================
# VIEWS PARA CATEGORIAS E SUBCATEGORIAS
# ============================================================================

class CategoriaListView(LoginRequiredMixin, ListView):
    """Lista todas as categorias"""
    model = Categoria
    template_name = 'militares/categoria_list.html'
    context_object_name = 'categorias'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Categoria.objects.all().order_by('nome')
        
        search = self.request.GET.get('search', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(descricao__icontains=search)
            )
        
        if ativo == '1':
            queryset = queryset.filter(ativo=True)
        elif ativo == '0':
            queryset = queryset.filter(ativo=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        return context


@login_required
def categoria_create(request):
    """Cria uma nova categoria"""
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        ativo = request.POST.get('ativo') == 'on'
        
        if not nome:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Nome é obrigatório'})
            messages.error(request, 'Nome é obrigatório')
            return redirect('militares:categoria_list')
        
        try:
            categoria = Categoria.objects.create(
                nome=nome,
                descricao=descricao if descricao else None,
                ativo=ativo
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Categoria criada com sucesso!',
                    'categoria_id': categoria.id
                })
            
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('militares:categoria_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)})
            messages.error(request, f'Erro ao criar categoria: {str(e)}')
            return redirect('militares:categoria_list')
    
    # GET request - retornar formulário via AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/categoria_form_modal.html', {
            'is_create': True
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return redirect('militares:categoria_list')


@login_required
def categoria_update(request, pk):
    """Atualiza uma categoria"""
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        ativo = request.POST.get('ativo') == 'on'
        
        if not nome:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Nome é obrigatório'})
            messages.error(request, 'Nome é obrigatório')
            return redirect('militares:categoria_list')
        
        try:
            categoria.nome = nome
            categoria.descricao = descricao if descricao else None
            categoria.ativo = ativo
            categoria.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Categoria atualizada com sucesso!'
                })
            
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('militares:categoria_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)})
            messages.error(request, f'Erro ao atualizar categoria: {str(e)}')
            return redirect('militares:categoria_list')
    
    # GET request - retornar formulário via AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/categoria_form_modal.html', {
            'categoria': categoria,
            'is_create': False
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return redirect('militares:categoria_list')


@login_required
def categoria_delete(request, pk):
    """Exclui uma categoria"""
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        try:
            # Verificar se há itens vinculados
            if categoria.itens_almoxarifado.exists():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Não é possível excluir categoria com itens vinculados. Desative a categoria ao invés de excluir.'
                    })
                messages.error(request, 'Não é possível excluir categoria com itens vinculados.')
                return redirect('militares:categoria_list')
            
            categoria.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Categoria excluída com sucesso!'
                })
            
            messages.success(request, 'Categoria excluída com sucesso!')
            return redirect('militares:categoria_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)})
            messages.error(request, f'Erro ao excluir categoria: {str(e)}')
            return redirect('militares:categoria_list')
    
    # GET request - retornar confirmação via AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/categoria_delete_modal.html', {
            'categoria': categoria
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return redirect('militares:categoria_list')


class SubcategoriaListView(LoginRequiredMixin, ListView):
    """Lista todas as subcategorias"""
    model = Subcategoria
    template_name = 'militares/subcategoria_list.html'
    context_object_name = 'subcategorias'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Subcategoria.objects.select_related('categoria').order_by('categoria__nome', 'nome')
        
        search = self.request.GET.get('search', '')
        categoria_id = self.request.GET.get('categoria', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(descricao__icontains=search) |
                Q(categoria__nome__icontains=search)
            )
        
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        if ativo == '1':
            queryset = queryset.filter(ativo=True)
        elif ativo == '0':
            queryset = queryset.filter(ativo=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['categoria'] = self.request.GET.get('categoria', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        context['categorias'] = Categoria.objects.filter(ativo=True).order_by('nome')
        return context


@login_required
def subcategoria_create(request):
    """Cria uma nova subcategoria"""
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria', '').strip()
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        ativo = request.POST.get('ativo') == 'on'
        
        if not categoria_id or not nome:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Categoria e nome são obrigatórios'})
            messages.error(request, 'Categoria e nome são obrigatórios')
            return redirect('militares:subcategoria_list')
        
        try:
            categoria = Categoria.objects.get(pk=categoria_id)
            subcategoria = Subcategoria.objects.create(
                categoria=categoria,
                nome=nome,
                descricao=descricao if descricao else None,
                ativo=ativo
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Subcategoria criada com sucesso!',
                    'subcategoria_id': subcategoria.id
                })
            
            messages.success(request, 'Subcategoria criada com sucesso!')
            return redirect('militares:subcategoria_list')
        except Categoria.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Categoria não encontrada'})
            messages.error(request, 'Categoria não encontrada')
            return redirect('militares:subcategoria_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)})
            messages.error(request, f'Erro ao criar subcategoria: {str(e)}')
            return redirect('militares:subcategoria_list')
    
    # GET request - retornar formulário via AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/subcategoria_form_modal.html', {
            'is_create': True,
            'categorias': Categoria.objects.filter(ativo=True).order_by('nome')
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return redirect('militares:subcategoria_list')


@login_required
def subcategoria_update(request, pk):
    """Atualiza uma subcategoria"""
    subcategoria = get_object_or_404(Subcategoria, pk=pk)
    
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria', '').strip()
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        ativo = request.POST.get('ativo') == 'on'
        
        if not categoria_id or not nome:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Categoria e nome são obrigatórios'})
            messages.error(request, 'Categoria e nome são obrigatórios')
            return redirect('militares:subcategoria_list')
        
        try:
            categoria = Categoria.objects.get(pk=categoria_id)
            subcategoria.categoria = categoria
            subcategoria.nome = nome
            subcategoria.descricao = descricao if descricao else None
            subcategoria.ativo = ativo
            subcategoria.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Subcategoria atualizada com sucesso!'
                })
            
            messages.success(request, 'Subcategoria atualizada com sucesso!')
            return redirect('militares:subcategoria_list')
        except Categoria.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Categoria não encontrada'})
            messages.error(request, 'Categoria não encontrada')
            return redirect('militares:subcategoria_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)})
            messages.error(request, f'Erro ao atualizar subcategoria: {str(e)}')
            return redirect('militares:subcategoria_list')
    
    # GET request - retornar formulário via AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/subcategoria_form_modal.html', {
            'subcategoria': subcategoria,
            'is_create': False,
            'categorias': Categoria.objects.filter(ativo=True).order_by('nome')
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return redirect('militares:subcategoria_list')


@login_required
def subcategoria_delete(request, pk):
    """Exclui uma subcategoria"""
    subcategoria = get_object_or_404(Subcategoria, pk=pk)
    
    if request.method == 'POST':
        try:
            # Verificar se há itens vinculados
            if subcategoria.itens_almoxarifado.exists():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Não é possível excluir subcategoria com itens vinculados. Desative a subcategoria ao invés de excluir.'
                    })
                messages.error(request, 'Não é possível excluir subcategoria com itens vinculados.')
                return redirect('militares:subcategoria_list')
            
            subcategoria.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Subcategoria excluída com sucesso!'
                })
            
            messages.success(request, 'Subcategoria excluída com sucesso!')
            return redirect('militares:subcategoria_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)})
            messages.error(request, f'Erro ao excluir subcategoria: {str(e)}')
            return redirect('militares:subcategoria_list')
    
    # GET request - retornar confirmação via AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/subcategoria_delete_modal.html', {
            'subcategoria': subcategoria
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return redirect('militares:subcategoria_list')


# ============================================================================
# FUNÇÕES AUXILIARES PARA TRANSFERÊNCIAS
# ============================================================================

def _criar_entrada_transferencia(saida):
    """
    Cria automaticamente uma entrada na OM destino quando há uma transferência.
    Sistema de supermercado: produto único, estoque por OM.
    """
    if not saida.orgao_destino and not saida.unidade_destino:
        return
    
    # Criar entrada na OM destino
    entrada = EntradaAlmoxarifado.objects.create(
        tipo_entrada='TRANSFERENCIA',
        data_entrada=saida.data_saida,
        fornecedor=None,
        nota_fiscal=None,
        # Origem = OM de origem da saída
        orgao_origem=saida.orgao_origem,
        grande_comando_origem=saida.grande_comando_origem,
        unidade_origem=saida.unidade_origem,
        sub_unidade_origem=saida.sub_unidade_origem,
        # Destino = OM destino da saída
        orgao_destino=saida.orgao_destino,
        grande_comando_destino=saida.grande_comando_destino,
        unidade_destino=saida.unidade_destino,
        sub_unidade_destino=saida.sub_unidade_destino,
        responsavel=None,
        observacoes=f'Transferência automática gerada a partir da saída #{saida.pk}',
        ativo=True,
        criado_por=saida.criado_por
    )
    
    # Copiar todos os itens da saída para a entrada
    # SISTEMA DE SUPERMERCADO: Produto único, não cria item duplicado
    # Usa o mesmo item (produto único), apenas cria entrada na OM destino
    for produto_saida in saida.produtos_saida.all():
        produto = produto_saida.produto
        
        # Validar que o produto existe
        if not produto:
            raise ValueError(f'Produto da saída {produto_saida.id} não tem produto associado. Dados inconsistentes.')
        
        # Criar produto da entrada usando o mesmo produto (produto único)
        # A entrada já tem a OM de destino definida, então o estoque será calculado corretamente
        produto_entrada = EntradaAlmoxarifadoProduto.objects.create(
            entrada=entrada,
            produto=produto,  # Mesmo produto, não cria duplicado
            quantidade=produto_saida.quantidade
        )
        
        # Não precisa recalcular estoque - será calculado dinamicamente por OM quando necessário

