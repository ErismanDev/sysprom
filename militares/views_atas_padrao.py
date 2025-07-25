from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate
from .models import AtaSessao, AssinaturaAta, MembroComissao


@login_required
def ata_assinar_padrao(request, pk):
    """Assinar ata usando o padrão do sistema (sem SEI)"""
    
    try:
        ata = AtaSessao.objects.get(sessao_id=pk)
    except AtaSessao.DoesNotExist:
        messages.error(request, 'Ata não encontrada.')
        return redirect('militares:sessao_comissao_detail', pk=pk)
    
    # Verificar se o usuário é membro da comissão
    try:
        membro = MembroComissao.objects.get(
            comissao=ata.sessao.comissao,
            usuario=request.user,
            ativo=True
        )
    except MembroComissao.DoesNotExist:
        messages.error(request, 'Você não é membro desta comissão.')
        return redirect('militares:sessao_comissao_detail', pk=pk)
    
    if request.method == 'POST':
        # Processar assinatura
        membro_id = request.POST.get('membro_id')
        observacoes = request.POST.get('observacoes', '')
        senha = request.POST.get('senha')
        
        if not membro_id:
            messages.error(request, 'Selecione um membro da comissão.')
            return render(request, 'militares/comissao/sessoes/ata_assinaturas_padrao.html', {
                'ata': ata,
                'sessao': ata.sessao,
                'comissao': ata.sessao.comissao,
                'membros_comissao': MembroComissao.objects.filter(
                    comissao=ata.sessao.comissao,
                    ativo=True
                )
            })
        
        if not senha:
            messages.error(request, 'Digite sua senha para confirmar a assinatura.')
            return render(request, 'militares/comissao/sessoes/ata_assinaturas_padrao.html', {
                'ata': ata,
                'sessao': ata.sessao,
                'comissao': ata.sessao.comissao,
                'membros_comissao': MembroComissao.objects.filter(
                    comissao=ata.sessao.comissao,
                    ativo=True
                )
            })
        
        # Verificar senha
        user = authenticate(username=request.user.username, password=senha)
        if not user:
            messages.error(request, 'Senha incorreta.')
            return render(request, 'militares/comissao/sessoes/ata_assinaturas_padrao.html', {
                'ata': ata,
                'sessao': ata.sessao,
                'comissao': ata.sessao.comissao,
                'membros_comissao': MembroComissao.objects.filter(
                    comissao=ata.sessao.comissao,
                    ativo=True
                )
            })
        
        try:
            membro_assinatura = MembroComissao.objects.get(
                id=membro_id,
                comissao=ata.sessao.comissao,
                ativo=True
            )
        except MembroComissao.DoesNotExist:
            messages.error(request, 'Membro da comissão não encontrado.')
            return render(request, 'militares/comissao/sessoes/ata_assinaturas_padrao.html', {
                'ata': ata,
                'sessao': ata.sessao,
                'comissao': ata.sessao.comissao,
                'membros_comissao': MembroComissao.objects.filter(
                    comissao=ata.sessao.comissao,
                    ativo=True
                )
            })
        
        # Verificar se já assinou
        if AssinaturaAta.objects.filter(ata=ata, membro=membro_assinatura).exists():
            messages.error(request, 'Este membro já assinou esta ata.')
            return render(request, 'militares/comissao/sessoes/ata_assinaturas_padrao.html', {
                'ata': ata,
                'sessao': ata.sessao,
                'comissao': ata.sessao.comissao,
                'membros_comissao': MembroComissao.objects.filter(
                    comissao=ata.sessao.comissao,
                    ativo=True
                )
            })
        
        # Criar assinatura
        assinatura = AssinaturaAta.objects.create(
            ata=ata,
            membro=membro_assinatura,
            assinado_por=request.user,
            observacoes=observacoes
        )
        
        messages.success(request, f'Ata assinada com sucesso por {membro_assinatura.militar.nome_completo}.')
        
        # Verificar se todas as assinaturas foram feitas
        total_membros = MembroComissao.objects.filter(
            comissao=ata.sessao.comissao,
            ativo=True
        ).count()
        
        if ata.assinaturas.count() >= total_membros:
            ata.status = 'ASSINADA'
            ata.save()
            messages.info(request, 'Todas as assinaturas foram realizadas. A ata está pronta para finalização.')
        
        return redirect('militares:sessao_comissao_detail', pk=pk)
    
    # GET - mostrar formulário
    context = {
        'ata': ata,
        'sessao': ata.sessao,
        'comissao': ata.sessao.comissao,
        'membros_comissao': MembroComissao.objects.filter(
            comissao=ata.sessao.comissao,
            ativo=True
        )
    }
    
    return render(request, 'militares/comissao/sessoes/ata_assinaturas_padrao.html', context) 