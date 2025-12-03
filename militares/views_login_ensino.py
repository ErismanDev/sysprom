# -*- coding: utf-8 -*-
"""
Views de Login para o Módulo de Ensino
Sistema de autenticação unificado para Alunos, Instrutores e Monitores
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.db import transaction
from militares.models import AlunoEnsino, InstrutorEnsino, MonitorEnsino, Militar, PessoaExterna
from django.contrib.auth.hashers import check_password, make_password


def login_ensino(request):
    """View unificada de login para alunos, instrutores e monitores"""
    ua = request.META.get('HTTP_USER_AGENT', '') or ''
    qs_apk = request.GET.get('apk') in ('1', 'true', 'True')
    is_apk = qs_apk or ('Android' in ua and 'Mobile' in ua) or ('wv' in ua) or ('okhttp' in ua) or ('Dalvik' in ua)
    if request.user.is_authenticated and request.method != 'POST':
        # Evitar loops: sempre renderizar a tela de login do ensino para usuários autenticados
        # quando não for submissão de formulário explícita.
        request.session.pop('ensino_login_bypass_auto', None)
        return render(request, 'militares/ensino/login_ensino.html')
    
    if request.method == 'POST':
        tipo_usuario = request.POST.get('tipo_usuario', '').strip()
        identificador = request.POST.get('identificador', '').strip()
        senha = request.POST.get('senha', '')
        nao_sou_robo = request.POST.get('nao_sou_robo')
        
        if not nao_sou_robo:
            messages.error(request, 'Você deve confirmar que não é um robô para continuar.')
            return render(request, 'militares/ensino/login_ensino.html')
        
        if not identificador or not senha:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return render(request, 'militares/ensino/login_ensino.html')
        
        if tipo_usuario in ['aluno', 'instrutor', 'monitor']:
            if tipo_usuario == 'aluno':
                return _processar_login_aluno(request, identificador, senha)
            if tipo_usuario == 'instrutor':
                return _processar_login_instrutor(request, identificador, senha)
            if tipo_usuario == 'monitor':
                return _processar_login_monitor(request, identificador, senha)
        
        id_digits = ''.join([c for c in identificador if c.isdigit()])
        def _format_cpf(d):
            d = ''.join([c for c in d if c.isdigit()])
            if len(d) == 11:
                return f"{d[0:3]}.{d[3:6]}.{d[6:9]}-{d[9:11]}"
            return ''
        cpf_mask = _format_cpf(id_digits)
        cpf_variants = [identificador]
        if id_digits:
            cpf_variants.append(id_digits)
        if cpf_mask:
            cpf_variants.append(cpf_mask)

        matches = []
        aluno = AlunoEnsino.objects.filter(matricula=identificador, situacao='ATIVO').first()
        if aluno:
            matches.append(('aluno', aluno))
        else:
            militar = Militar.objects.filter(cpf__in=cpf_variants).first()
            if militar:
                aluno_militar = AlunoEnsino.objects.filter(militar=militar, situacao='ATIVO').first()
                if aluno_militar:
                    matches.append(('aluno', aluno_militar))
                instrutor_militar = InstrutorEnsino.objects.filter(militar=militar, ativo=True).first()
                if instrutor_militar:
                    matches.append(('instrutor', instrutor_militar))
                monitor_militar = MonitorEnsino.objects.filter(militar=militar, ativo=True).first()
                if monitor_militar:
                    matches.append(('monitor', monitor_militar))
            else:
                aluno = AlunoEnsino.objects.filter(situacao='ATIVO').filter(
                    Q(cpf_outra_forca__in=cpf_variants) |
                    Q(cpf_civil__in=cpf_variants) |
                    Q(pessoa_externa__cpf__in=cpf_variants)
                ).first()
                if aluno:
                    matches.append(('aluno', aluno))
                instrutor = InstrutorEnsino.objects.filter(ativo=True).filter(
                    Q(cpf_outra_forca__in=cpf_variants) |
                    Q(cpf_civil__in=cpf_variants)
                ).first()
                if instrutor:
                    matches.append(('instrutor', instrutor))
                monitor = MonitorEnsino.objects.filter(ativo=True).filter(
                    Q(cpf_outra_forca__in=cpf_variants) |
                    Q(cpf_civil__in=cpf_variants)
                ).first()
                if monitor:
                    matches.append(('monitor', monitor))
        if not matches:
            messages.error(request, 'Usuário não encontrado. Verifique seus dados.')
            return render(request, 'militares/ensino/login_ensino.html')
        if len(matches) > 1:
            messages.error(request, 'Identificador corresponde a mais de um cadastro. Selecione o tipo de usuário.')
            return render(request, 'militares/ensino/login_ensino.html')
        unico_tipo, unico_obj = matches[0]
        if unico_tipo == 'aluno':
            return _processar_login_aluno(request, identificador, senha)
        if unico_tipo == 'instrutor':
            return _processar_login_instrutor(request, identificador, senha)
        return _processar_login_monitor(request, identificador, senha)
    
    return render(request, 'militares/ensino/login_ensino.html')


def _processar_login_aluno(request, identificador, senha):
    """Processa login de aluno"""
    id_digits = ''.join([c for c in identificador if c.isdigit()])
    def _format_cpf(d):
        d = ''.join([c for c in d if c.isdigit()])
        if len(d) == 11:
            return f"{d[0:3]}.{d[3:6]}.{d[6:9]}-{d[9:11]}"
        return ''
    cpf_mask = _format_cpf(id_digits)
    cpf_variants = [identificador]
    if id_digits:
        cpf_variants.append(id_digits)
    if cpf_mask:
        cpf_variants.append(cpf_mask)

    aluno = AlunoEnsino.objects.filter(situacao='ATIVO').filter(
        Q(matricula=identificador) |
        Q(militar__cpf__in=cpf_variants) |
        Q(cpf_outra_forca__in=cpf_variants) |
        Q(cpf_civil__in=cpf_variants) |
        Q(pessoa_externa__cpf__in=cpf_variants)
    ).first()
    
    if not aluno:
        messages.error(request, 'Aluno não encontrado ou inativo.')
        return render(request, 'militares/ensino/login_ensino.html')
    
    # Verificar senha
    if not aluno.senha_hash:
        messages.error(request, 'Senha não configurada. Entre em contato com o administrador.')
        return render(request, 'militares/ensino/login_ensino.html')
    
    if not check_password(senha, aluno.senha_hash):
        messages.error(request, 'Senha incorreta.')
        return render(request, 'militares/ensino/login_ensino.html')
    
    # Criar ou obter usuário Django para o aluno
    username = f"aluno_{aluno.pk}"
    nome_completo = aluno.get_pessoa_nome() or 'Aluno'
    nome_parts = nome_completo.split()
    first_name = nome_parts[0] if nome_parts else 'Aluno'
    last_name = ' '.join(nome_parts[1:]) if len(nome_parts) > 1 else ''
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'email': aluno.get_email(),
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        }
    )
    
    # Se o usuário já existia, atualizar informações se necessário
    if not created:
        updated = False
        if user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if user.last_name != last_name:
            user.last_name = last_name
            updated = True
        email_aluno = aluno.get_email()
        if user.email != email_aluno:
            user.email = email_aluno
            updated = True
        if not user.is_active:
            user.is_active = True
            updated = True
        if updated:
            user.save()
    
    if created:
        user.save()
    
    # Fazer login
    login(request, user)
    request.session['ensino_tipo'] = 'aluno'
    request.session['ensino_id'] = aluno.pk
    
    # Forçar troca de senha no primeiro login se estiver usando o CPF como senha
    try:
        cpf = aluno.get_cpf()
        cpf_digits = ''.join([c for c in cpf or '' if c.isdigit()])
        if cpf_digits and check_password(cpf_digits, aluno.senha_hash):
            messages.warning(request, 'Por segurança, altere sua senha. A senha atual é temporária (CPF).')
            return redirect('militares:ensino_alterar_senha_primeiro_login')
    except Exception:
        pass

    messages.success(request, f'Login realizado com sucesso! Bem-vindo, {nome_completo}.')
    url = reverse('militares:ensino_dashboard_aluno')
    ua = request.META.get('HTTP_USER_AGENT', '') or ''
    qs_apk = request.GET.get('apk') in ('1', 'true', 'True')
    is_apk = qs_apk or ('Android' in ua and 'Mobile' in ua) or ('wv' in ua) or ('okhttp' in ua) or ('Dalvik' in ua)
    if is_apk:
        url = f"{url}?apk=1"
    return redirect(url)


@login_required
def alterar_senha_primeiro_login(request):
    """Alunos: alterar senha no primeiro login quando estiver usando CPF padrão"""
    if request.session.get('ensino_tipo') != 'aluno':
        messages.error(request, 'Apenas alunos podem acessar esta página.')
        return redirect('militares:ensino_login')
    aluno_id = request.session.get('ensino_id')
    aluno = get_object_or_404(AlunoEnsino, pk=aluno_id)

    if request.method == 'POST':
        senha = request.POST.get('senha', '').strip()
        confirmar_senha = request.POST.get('confirmar_senha', '').strip()
        if not senha or not confirmar_senha:
            messages.error(request, 'Informe e confirme a nova senha.')
        elif senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
        elif len(senha) < 6:
            messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
        else:
            aluno.senha_hash = make_password(senha)
            aluno.save(update_fields=['senha_hash'])
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('militares:ensino_dashboard_aluno')

    nome = aluno.get_pessoa_nome()
    context = {
        'usuario': aluno,
        'tipo': 'aluno',
        'nome': nome,
        'tem_senha': bool(aluno.senha_hash),
    }
    return render(request, 'militares/ensino/usuarios/definir_senha.html', context)


@login_required
def alterar_senha_ensino(request):
    ensino_tipo = request.session.get('ensino_tipo')
    ensino_id = request.session.get('ensino_id')
    if not ensino_tipo or not ensino_id:
        messages.error(request, 'Você não está autenticado no módulo de ensino.')
        return redirect('militares:ensino_login')

    if ensino_tipo == 'aluno':
        usuario = get_object_or_404(AlunoEnsino, pk=ensino_id)
        nome = usuario.get_pessoa_nome()
        redirect_ok = 'militares:ensino_dashboard_aluno'
    elif ensino_tipo == 'instrutor':
        usuario = get_object_or_404(InstrutorEnsino, pk=ensino_id)
        nome = usuario.get_nome_completo()
        redirect_ok = 'militares:ensino_dashboard_instrutor'
    elif ensino_tipo == 'monitor':
        usuario = get_object_or_404(MonitorEnsino, pk=ensino_id)
        nome = usuario.get_nome_completo()
        redirect_ok = 'militares:ensino_dashboard_instrutor'
    else:
        messages.error(request, 'Tipo de usuário do ensino inválido.')
        return redirect('militares:ensino_login')

    if request.method == 'POST':
        senha = request.POST.get('senha', '').strip()
        confirmar_senha = request.POST.get('confirmar_senha', '').strip()
        if not senha or not confirmar_senha:
            messages.error(request, 'Informe e confirme a nova senha.')
        elif senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
        elif len(senha) < 6:
            messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
        else:
            usuario.senha_hash = make_password(senha)
            usuario.save(update_fields=['senha_hash'])
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect(redirect_ok)

    context = {
        'usuario': usuario,
        'tipo': ensino_tipo,
        'nome': nome,
        'tem_senha': bool(usuario.senha_hash),
    }
    return render(request, 'militares/ensino/usuarios/definir_senha.html', context)


def _processar_login_instrutor(request, identificador, senha):
    """Processa login de instrutor"""
    id_digits = ''.join([c for c in identificador if c.isdigit()])
    def _format_cpf(d):
        d = ''.join([c for c in d if c.isdigit()])
        if len(d) == 11:
            return f"{d[0:3]}.{d[3:6]}.{d[6:9]}-{d[9:11]}"
        return ''
    cpf_mask = _format_cpf(id_digits)
    cpf_variants = [identificador]
    if id_digits:
        cpf_variants.append(id_digits)
    if cpf_mask:
        cpf_variants.append(cpf_mask)
    instrutor = InstrutorEnsino.objects.filter(ativo=True).filter(
        Q(militar__cpf__in=cpf_variants) |
        Q(cpf_outra_forca__in=cpf_variants) |
        Q(cpf_civil__in=cpf_variants)
    ).select_related('militar').first()
    
    if not instrutor:
        messages.error(request, 'Instrutor não encontrado ou inativo.')
        return render(request, 'militares/ensino/login_ensino.html')
    
    # Verificar senha
    if not instrutor.senha_hash:
        messages.error(request, 'Senha não configurada. Entre em contato com o administrador.')
        return render(request, 'militares/ensino/login_ensino.html')
    
    if not check_password(senha, instrutor.senha_hash):
        messages.error(request, 'Senha incorreta.')
        return render(request, 'militares/ensino/login_ensino.html')
    
    # Criar ou obter usuário Django para o instrutor
    username = f"instrutor_{instrutor.pk}"
    nome_completo = instrutor.get_nome_completo() or 'Instrutor'
    nome_parts = nome_completo.split()
    first_name = nome_parts[0] if nome_parts else 'Instrutor'
    last_name = ' '.join(nome_parts[1:]) if len(nome_parts) > 1 else ''
    
    # Obter email
    email = ''
    if instrutor.tipo_instrutor == 'BOMBEIRO' and instrutor.militar:
        email = instrutor.militar.email or instrutor.email_bombeiro or ''
    elif instrutor.tipo_instrutor == 'OUTRA_FORCA':
        email = instrutor.email_outra_forca or ''
    elif instrutor.tipo_instrutor == 'CIVIL':
        email = instrutor.email_civil or ''
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        }
    )
    
    # Se o usuário já existia, atualizar informações se necessário
    if not created:
        updated = False
        if user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if user.last_name != last_name:
            user.last_name = last_name
            updated = True
        if user.email != email:
            user.email = email
            updated = True
        if not user.is_active:
            user.is_active = True
            updated = True
        if updated:
            # Salvar sem update_fields para garantir que todos os campos sejam salvos
            user.save()
    
    if created:
        user.save()
    
    # Fazer login
    login(request, user)
    request.session['ensino_tipo'] = 'instrutor'
    request.session['ensino_id'] = instrutor.pk
    
    messages.success(request, f'Login realizado com sucesso! Bem-vindo, {nome_completo}.')
    url = reverse('militares:ensino_dashboard_instrutor')
    ua = request.META.get('HTTP_USER_AGENT', '') or ''
    qs_apk = request.GET.get('apk') in ('1', 'true', 'True')
    is_apk = qs_apk or ('Android' in ua and 'Mobile' in ua) or ('wv' in ua) or ('okhttp' in ua) or ('Dalvik' in ua)
    if is_apk:
        url = f"{url}?apk=1"
    return redirect(url)


def _processar_login_monitor(request, identificador, senha):
    """Processa login de monitor"""
    id_digits = ''.join([c for c in identificador if c.isdigit()])
    def _format_cpf(d):
        d = ''.join([c for c in d if c.isdigit()])
        if len(d) == 11:
            return f"{d[0:3]}.{d[3:6]}.{d[6:9]}-{d[9:11]}"
        return ''
    cpf_mask = _format_cpf(id_digits)
    cpf_variants = [identificador]
    if id_digits:
        cpf_variants.append(id_digits)
    if cpf_mask:
        cpf_variants.append(cpf_mask)
    monitor = MonitorEnsino.objects.filter(ativo=True).filter(
        Q(militar__cpf__in=cpf_variants) |
        Q(cpf_outra_forca__in=cpf_variants) |
        Q(cpf_civil__in=cpf_variants)
    ).select_related('militar').first()
    
    if not monitor:
        messages.error(request, 'Monitor não encontrado ou inativo.')
        return render(request, 'militares/ensino/login_ensino.html')
    
    # Verificar senha
    if not monitor.senha_hash:
        messages.error(request, 'Senha não configurada. Entre em contato com o administrador.')
        return render(request, 'militares/ensino/login_ensino.html')
    
    if not check_password(senha, monitor.senha_hash):
        messages.error(request, 'Senha incorreta.')
        return render(request, 'militares/ensino/login_ensino.html')
    
    # Criar ou obter usuário Django para o monitor
    username = f"monitor_{monitor.pk}"
    nome_completo = monitor.get_nome_completo() or 'Monitor'
    nome_parts = nome_completo.split()
    first_name = nome_parts[0] if nome_parts else 'Monitor'
    last_name = ' '.join(nome_parts[1:]) if len(nome_parts) > 1 else ''
    
    # Obter email
    email = ''
    if monitor.tipo_monitor == 'BOMBEIRO' and monitor.militar:
        email = monitor.militar.email or monitor.email_bombeiro or ''
    elif monitor.tipo_monitor == 'OUTRA_FORCA':
        email = monitor.email_outra_forca or ''
    elif monitor.tipo_monitor == 'CIVIL':
        email = monitor.email_civil or ''
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        }
    )
    
    # Se o usuário já existia, atualizar informações se necessário
    if not created:
        updated = False
        if user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if user.last_name != last_name:
            user.last_name = last_name
            updated = True
        if user.email != email:
            user.email = email
            updated = True
        if not user.is_active:
            user.is_active = True
            updated = True
        if updated:
            # Salvar sem update_fields para garantir que todos os campos sejam salvos
            user.save()
    
    if created:
        user.save()
    
    # Fazer login
    login(request, user)
    request.session['ensino_tipo'] = 'monitor'
    request.session['ensino_id'] = monitor.pk
    
    messages.success(request, f'Login realizado com sucesso! Bem-vindo, {nome_completo}.')
    url = reverse('militares:ensino_dashboard_instrutor')
    ua = request.META.get('HTTP_USER_AGENT', '') or ''
    qs_apk = request.GET.get('apk') in ('1', 'true', 'True')
    is_apk = qs_apk or ('Android' in ua and 'Mobile' in ua) or ('wv' in ua) or ('okhttp' in ua) or ('Dalvik' in ua)
    if is_apk:
        url = f"{url}?apk=1"
    return redirect(url)
