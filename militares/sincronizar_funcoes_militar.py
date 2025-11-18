"""
Sistema para sincronizar funções do militar logado com suas funções exercidas
"""

from django.contrib.auth.models import User
from militares.models import Militar, MilitarFuncao, UsuarioFuncaoMilitar, FuncaoMilitar
from datetime import date


def sincronizar_funcoes_militar(usuario):
    """
    Sincroniza as funções do usuário com as funções exercidas do militar associado
    
    Args:
        usuario: Usuario Django
        
    Returns:
        dict: Resultado da sincronização
    """
    try:
        # Verificar se o usuário tem militar associado
        if not hasattr(usuario, 'militar') or not usuario.militar:
            return {
                'sucesso': False,
                'mensagem': 'Usuário não possui militar associado',
                'funcoes_criadas': 0,
                'funcoes_atualizadas': 0
            }
        
        militar = usuario.militar
        
        # Buscar funções atuais do militar (status ATUAL)
        funcoes_militar = MilitarFuncao.objects.filter(
            militar=militar,
            status='ATUAL',
            ativo=True
        ).select_related('funcao_militar')
        
        if not funcoes_militar.exists():
            return {
                'sucesso': False,
                'mensagem': 'Militar não possui funções ativas cadastradas',
                'funcoes_criadas': 0,
                'funcoes_atualizadas': 0
            }
        
        funcoes_criadas = 0
        funcoes_atualizadas = 0
        
        # Processar cada função do militar
        for militar_funcao in funcoes_militar:
            funcao_militar = militar_funcao.funcao_militar
            
            # Verificar se já existe UsuarioFuncaoMilitar para esta função
            usuario_funcao, created = UsuarioFuncaoMilitar.objects.get_or_create(
                usuario=usuario,
                funcao_militar=funcao_militar,
                defaults={
                    'tipo_funcao': militar_funcao.tipo_funcao,
                    'nivel_acesso': 'NENHUM',  # Será definido pela função militar
                    'ativo': True,
                }
            )
            
            if created:
                funcoes_criadas += 1
                print(f"Função criada: {funcao_militar.nome} para {usuario.username}")
            else:
                # Atualizar função existente se necessário
                if usuario_funcao.tipo_funcao != militar_funcao.tipo_funcao:
                    usuario_funcao.tipo_funcao = militar_funcao.tipo_funcao
                    usuario_funcao.save()
                    funcoes_atualizadas += 1
                    print(f"Função atualizada: {funcao_militar.nome} para {usuario.username}")
        
        # Garantir que há apenas uma função principal
        funcoes_principais = UsuarioFuncaoMilitar.objects.filter(
            usuario=usuario,
            tipo_funcao='PRINCIPAL'
        )
        
        if funcoes_principais.count() > 1:
            # Manter apenas a primeira função principal, desativar as outras
            primeira_principal = funcoes_principais.first()
            outras_principais = funcoes_principais.exclude(id=primeira_principal.id)
            
            for funcao in outras_principais:
                funcao.tipo_funcao = 'ADICIONAL'  # Converter para adicional
                funcao.save()
                print(f"Função {funcao.funcao_militar.nome} convertida de Principal para Adicional")
        
        # Se não há função principal, converter a primeira função para principal
        elif funcoes_principais.count() == 0 and funcoes_militar.exists():
            primeira_funcao = UsuarioFuncaoMilitar.objects.filter(
                usuario=usuario
            ).first()
            
            if primeira_funcao:
                primeira_funcao.tipo_funcao = 'PRINCIPAL'
                primeira_funcao.save()
                print(f"Função {primeira_funcao.funcao_militar.nome} definida como Principal")
        
        # Desativar funções que não estão mais ativas no militar
        funcoes_usuario_ids = [uf.funcao_militar.id for uf in UsuarioFuncaoMilitar.objects.filter(usuario=usuario)]
        funcoes_militar_ids = [mf.funcao_militar.id for mf in funcoes_militar]
        
        funcoes_para_desativar = set(funcoes_usuario_ids) - set(funcoes_militar_ids)
        
        if funcoes_para_desativar:
            UsuarioFuncaoMilitar.objects.filter(
                usuario=usuario,
                funcao_militar_id__in=funcoes_para_desativar
            ).update(ativo=False)
            
            print(f"Funções desativadas: {len(funcoes_para_desativar)} para {usuario.username}")
        
        return {
            'sucesso': True,
            'mensagem': f'Sincronização concluída: {funcoes_criadas} criadas, {funcoes_atualizadas} atualizadas',
            'funcoes_criadas': funcoes_criadas,
            'funcoes_atualizadas': funcoes_atualizadas,
            'funcoes_desativadas': len(funcoes_para_desativar)
        }
        
    except Exception as e:
        return {
            'sucesso': False,
            'mensagem': f'Erro na sincronização: {str(e)}',
            'funcoes_criadas': 0,
            'funcoes_atualizadas': 0
        }


def sincronizar_todos_militares():
    """
    Sincroniza funções de todos os militares que possuem usuário associado
    """
    resultados = []
    
    # Buscar todos os usuários que possuem militar associado
    usuarios_com_militar = User.objects.filter(
        militar__isnull=False
    ).select_related('militar')
    
    for usuario in usuarios_com_militar:
        resultado = sincronizar_funcoes_militar(usuario)
        resultado['usuario'] = usuario.username
        resultado['militar'] = usuario.militar.nome_guerra if usuario.militar else 'N/A'
        resultados.append(resultado)
    
    return resultados


def obter_funcoes_militar_logado(usuario):
    """
    Obtém as funções do militar logado baseadas nas funções exercidas
    
    Args:
        usuario: Usuario Django logado
        
    Returns:
        QuerySet: Funções do militar logado
    """
    if not hasattr(usuario, 'militar') or not usuario.militar:
        return UsuarioFuncaoMilitar.objects.none()
    
    # Sincronizar funções primeiro
    sincronizar_funcoes_militar(usuario)
    
    # Retornar TODAS as funções do usuário (ativas e inativas) para o dropdown
    return UsuarioFuncaoMilitar.objects.filter(
        usuario=usuario
    ).select_related('funcao_militar').order_by('funcao_militar__nome')


def obter_funcoes_ativas_militar_logado(usuario):
    """
    Obtém apenas as funções ATIVAS do militar logado
    
    Args:
        usuario: Usuario Django logado
        
    Returns:
        QuerySet: Funções ativas do militar logado
    """
    if not hasattr(usuario, 'militar') or not usuario.militar:
        return UsuarioFuncaoMilitar.objects.none()
    
    # Sincronizar funções primeiro
    sincronizar_funcoes_militar(usuario)
    
    # Retornar apenas funções ativas do usuário
    return UsuarioFuncaoMilitar.objects.filter(
        usuario=usuario,
        ativo=True
    ).select_related('funcao_militar').order_by('funcao_militar__nome')


def validar_funcoes_principais():
    """
    Valida e corrige funções principais em todo o sistema
    Garante que cada militar tenha apenas uma função principal
    """
    print("🔍 Validando funções principais...")
    
    # Buscar todos os usuários com múltiplas funções principais
    usuarios_com_multiplas_principais = User.objects.filter(
        funcoes_militares__tipo_funcao='PRINCIPAL'
    ).annotate(
        total_principais=models.Count('funcoes_militares', filter=models.Q(funcoes_militares__tipo_funcao='PRINCIPAL'))
    ).filter(total_principais__gt=1)
    
    print(f"👥 Usuários com múltiplas funções principais: {usuarios_com_multiplas_principais.count()}")
    
    for usuario in usuarios_com_multiplas_principais:
        print(f"🔧 Corrigindo usuário: {usuario.username}")
        
        # Buscar todas as funções principais do usuário
        funcoes_principais = UsuarioFuncaoMilitar.objects.filter(
            usuario=usuario,
            tipo_funcao='PRINCIPAL'
        ).order_by('id')
        
        # Manter apenas a primeira, converter as outras para adicional
        primeira_principal = funcoes_principais.first()
        outras_principais = funcoes_principais.exclude(id=primeira_principal.id)
        
        for funcao in outras_principais:
            funcao.tipo_funcao = 'ADICIONAL'
            funcao.save()
            print(f"  ✅ {funcao.funcao_militar.nome} convertida para Adicional")
    
    # Buscar usuários sem função principal
    usuarios_sem_principal = User.objects.filter(
        funcoes_militares__isnull=False
    ).exclude(
        funcoes_militares__tipo_funcao='PRINCIPAL'
    ).distinct()
    
    print(f"👥 Usuários sem função principal: {usuarios_sem_principal.count()}")
    
    for usuario in usuarios_sem_principal:
        print(f"🔧 Definindo função principal para: {usuario.username}")
        
        # Buscar primeira função do usuário
        primeira_funcao = UsuarioFuncaoMilitar.objects.filter(
            usuario=usuario
        ).first()
        
        if primeira_funcao:
            primeira_funcao.tipo_funcao = 'PRINCIPAL'
            primeira_funcao.save()
            print(f"  ✅ {primeira_funcao.funcao_militar.nome} definida como Principal")
    
    print("✅ Validação de funções principais concluída!")


def corrigir_todas_funcoes_principais():
    """
    Corrige todas as funções principais do sistema
    """
    from django.db import models
    
    print("🚀 Iniciando correção de todas as funções principais...")
    
    # Buscar todos os usuários com funções
    usuarios_com_funcoes = User.objects.filter(
        funcoes_militares__isnull=False
    ).distinct()
    
    print(f"👥 Usuários com funções: {usuarios_com_funcoes.count()}")
    
    for usuario in usuarios_com_funcoes:
        print(f"\n🔧 Processando usuário: {usuario.username}")
        
        # Buscar funções principais
        funcoes_principais = UsuarioFuncaoMilitar.objects.filter(
            usuario=usuario,
            tipo_funcao='PRINCIPAL'
        )
        
        if funcoes_principais.count() > 1:
            print(f"  ⚠️  {funcoes_principais.count()} funções principais encontradas")
            
            # Manter apenas a primeira
            primeira_principal = funcoes_principais.first()
            outras_principais = funcoes_principais.exclude(id=primeira_principal.id)
            
            for funcao in outras_principais:
                funcao.tipo_funcao = 'ADICIONAL'
                funcao.save()
                print(f"    ✅ {funcao.funcao_militar.nome} → Adicional")
        
        elif funcoes_principais.count() == 0:
            print(f"  ⚠️  Nenhuma função principal encontrada")
            
            # Definir primeira função como principal
            primeira_funcao = UsuarioFuncaoMilitar.objects.filter(
                usuario=usuario
            ).first()
            
            if primeira_funcao:
                primeira_funcao.tipo_funcao = 'PRINCIPAL'
                primeira_funcao.save()
                print(f"    ✅ {primeira_funcao.funcao_militar.nome} → Principal")
        
        else:
            print(f"  ✅ 1 função principal encontrada")
    
    print("\n🎉 Correção de funções principais concluída!")
