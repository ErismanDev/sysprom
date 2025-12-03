from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from militares.models import UsuarioFuncaoMilitar
import os
import json




def login_view(request):
    """View para login do usuário com captcha moderno simples"""
    if request.user.is_authenticated:
        return redirect('militares:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        nao_sou_robo = request.POST.get('nao_sou_robo')
        
        # Debug: imprimir valores para verificar
        print(f"DEBUG - Username: {username}")
        print(f"DEBUG - Password: {'*' * len(password) if password else 'None'}")
        print(f"DEBUG - Não sou robô: {nao_sou_robo}")
        
        # Validar captcha simples
        if not nao_sou_robo:
            print("DEBUG - Erro: Captcha não marcado")
            messages.error(request, 'Você deve confirmar que não é um robô para continuar.')
            return render(request, 'registration/login.html')
        
        # Autenticar usuário
        user = authenticate(request, username=username, password=password)
        print(f"DEBUG - User authenticated: {user}")
        
        if user is not None:
            if user.is_active:
                print("DEBUG - User ativo, fazendo login")
                # Fazer login do usuário
                login(request, user)
                
                # Superusuários podem acessar sem função
                if user.is_superuser:
                    messages.success(request, 'Login realizado com sucesso!')
                    return redirect('militares:home')
                
                # Usuários normais precisam de função
                from militares.models import UsuarioFuncaoMilitar
                funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(usuario=user)
                
                if not funcoes_usuario.exists():
                    messages.error(request, 'Você não possui funções cadastradas no sistema.')
                    logout(request)
                    return render(request, 'registration/login.html')
                
                # Buscar função principal
                funcao_principal = funcoes_usuario.filter(tipo_funcao='PRINCIPAL').first()
                
                if not funcao_principal:
                    # Se não tem função principal, usar a primeira disponível e marcar como principal
                    funcao_principal = funcoes_usuario.first()
                    funcao_principal.tipo_funcao = 'PRINCIPAL'
                    funcao_principal.save()
                
                # Desativar todas as funções do usuário
                UsuarioFuncaoMilitar.objects.filter(usuario=user).update(ativo=False)
                
                # Ativar a função principal
                funcao_principal.ativo = True
                funcao_principal.save()
                
                # Configurar função ativa na sessão
                request.session['funcao_atual_id'] = funcao_principal.id
                request.session['funcao_atual_nome'] = funcao_principal.funcao_militar.nome
                
                # Desativar sessões anteriores
                from militares.models import UsuarioSessao
                UsuarioSessao.objects.filter(usuario=user, ativo=True).update(ativo=False)
                
                # Criar nova sessão
                sessao = UsuarioSessao.objects.create(
                    usuario=user,
                    funcao_militar_usuario=funcao_principal
                )
                
                # Verificar se tem lotação definida
                lotacao = sessao.get_nivel_lotacao()
                if lotacao and lotacao != "Sem lotação definida":
                    messages.success(request, f'Login realizado com sucesso! Função principal: {funcao_principal.funcao_militar.nome} - Lotação: {lotacao}')
                else:
                    messages.success(request, f'Login realizado com sucesso! Função principal: {funcao_principal.funcao_militar.nome}')
                
                return redirect('militares:home')
            else:
                print("DEBUG - User inativo")
                messages.error(request, 'Sua conta está inativa. Entre em contato com o administrador.')
        else:
            print("DEBUG - Falha na autenticação")
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    """View para logout do usuário"""
    # Limpar dados da sessão relacionados às funções
    session_keys_to_remove = [
        'funcao_atual_id', 
        'funcao_atual_nome', 
        'funcoes_disponiveis'
    ]
    for key in session_keys_to_remove:
        request.session.pop(key, None)
    
    # Garantir que a sessão seja completamente encerrada e o cookie invalidado
    try:
        request.session.flush()
    except Exception:
        pass
    
    # Deletar a sessão atual explicitamente para atualizar status online imediatamente
    if hasattr(request, 'session') and request.session.session_key:
        from django.contrib.sessions.models import Session
        try:
            Session.objects.filter(session_key=request.session.session_key).delete()
        except Exception:
            pass
    
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    ensino_tipo = request.session.get('ensino_tipo')
    if ensino_tipo in ['aluno', 'instrutor', 'monitor']:
        return redirect('militares:ensino_login')
    return redirect('login')


@csrf_exempt
@require_http_methods(["POST"])
def api_funcoes_usuario(request):
    """API para buscar funções de um usuário"""
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        
        if not username:
            return JsonResponse({
                'success': False,
                'message': 'Username é obrigatório'
            })
        
        # Buscar usuário
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Usuário não encontrado'
            })
        
        # Buscar funções do usuário
        funcoes = UsuarioFuncaoMilitar.objects.filter(
            usuario=user
        ).select_related('funcao_militar', 'orgao', 'grande_comando', 'unidade', 'sub_unidade')
        
        funcoes_data = []
        for funcao in funcoes:
            funcoes_data.append({
                'id': funcao.id,
                'funcao_militar_nome': funcao.funcao_militar.nome,
                'lotacao': funcao.get_nivel_lotacao(),
                'ativo': funcao.ativo,
                'nivel': funcao.funcao_militar.nivel,
                'grupo': funcao.funcao_militar.get_grupo_display()
            })
        
        return JsonResponse({
            'success': True,
            'funcoes': funcoes_data
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados inválidos'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def api_user_email(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        if not username:
            return JsonResponse({'success': False, 'message': 'Username é obrigatório'})
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=username)
            return JsonResponse({'success': True, 'email': user.email or ''})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Usuário não encontrado'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Dados inválidos'})


@login_required
def home_view(request):
    """View da página inicial - redireciona baseado no tipo de usuário"""
    # Verificar se é login do módulo de ensino através da sessão
    ensino_tipo = request.session.get('ensino_tipo')
    
    if ensino_tipo == 'aluno':
        return redirect('militares:ensino_dashboard_aluno')
    elif ensino_tipo in ['instrutor', 'monitor']:
        return redirect('militares:ensino_dashboard_instrutor')
    
    # Se não for usuário do ensino, verificar através do militar
    from militares.views_dashboard_ensino import identificar_tipo_usuario_ensino
    
    tipo_usuario = identificar_tipo_usuario_ensino(request.user)
    
    if tipo_usuario == 'aluno':
        return redirect('militares:ensino_dashboard_aluno')
    elif tipo_usuario == 'instrutor':
        return redirect('militares:ensino_dashboard_instrutor')
    elif tipo_usuario == 'supervisor':
        return redirect('militares:ensino_dashboard_supervisor')
    elif tipo_usuario == 'coordenador':
        return redirect('militares:ensino_dashboard_coordenador')
    else:
        # Redirecionar para home padrão se não for nenhum tipo específico
        return redirect('/militares/')


def teste_modal_view(request):
    """View temporária para testar o modal"""
    try:
        with open('teste_modal_simples.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse("Arquivo de teste não encontrado", status=404)


def health_view(request):
    return HttpResponse("ok", content_type='text/plain')
