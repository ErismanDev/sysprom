from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AtaSessao, AssinaturaAta, MembroComissao


@login_required
def ata_assinar_melhorada(request, pk):
    """Assinar ata seguindo o padrão dos quadros de acesso"""
    
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
        observacoes = request.POST.get('observacoes', '').strip()
        senha = request.POST.get('senha')
        
        if not membro_id:
            messages.error(request, 'Selecione um membro para assinar.')
            return redirect('militares:ata_assinar_melhorada', pk=pk)
        
        if not senha:
            messages.error(request, 'Digite sua senha para confirmar a assinatura.')
            return redirect('militares:ata_assinar_melhorada', pk=pk)
        
        # Verificar senha do usuário
        if not request.user.check_password(senha):
            messages.error(request, 'Senha incorreta.')
            return redirect('militares:ata_assinar_melhorada', pk=pk)
        
        try:
            membro_para_assinar = MembroComissao.objects.get(id=membro_id)
            # Verificar se o membro estava presente
            if not ata.sessao.presencas.filter(membro=membro_para_assinar, presente=True).exists():
                messages.error(request, 'Apenas membros presentes podem assinar a ata.')
                return redirect('militares:ata_assinar_melhorada', pk=pk)
            
            # Verificar se já não assinou
            if ata.assinaturas.filter(membro=membro_para_assinar).exists():
                messages.error(request, 'Este membro já assinou a ata.')
                return redirect('militares:ata_assinar_melhorada', pk=pk)
            
            # Criar assinatura
            assinatura = AssinaturaAta.objects.create(
                ata=ata,
                membro=membro_para_assinar,
                assinado_por=request.user,
                observacoes=observacoes
            )
            
            messages.success(request, f'Assinatura de {membro_para_assinar.militar.nome_completo} registrada com sucesso!')
            
            # Verificar se todos assinaram
            membros_presentes = ata.sessao.presencas.filter(presente=True).count()
            assinaturas_count = ata.assinaturas.count()
            
            if assinaturas_count >= membros_presentes:
                ata.status = 'ASSINADA'
                ata.save()
                messages.info(request, 'Todos os membros presentes assinaram a ata!')
            
            return redirect('militares:ata_assinar_melhorada', pk=pk)
            
        except MembroComissao.DoesNotExist:
            messages.error(request, 'Membro não encontrado.')
    
    # Obter membros presentes e suas assinaturas
    membros_presentes = ata.sessao.presencas.filter(presente=True).select_related('membro__militar', 'membro__cargo')
    assinaturas = ata.assinaturas.select_related('membro__militar', 'assinado_por')
    
    context = {
        'ata': ata,
        'sessao': ata.sessao,
        'comissao': ata.sessao.comissao,
        'membros_presentes': membros_presentes,
        'assinaturas': assinaturas,
        'membro_usuario': membro,
    }
    return render(request, 'militares/comissao/sessoes/ata_assinaturas_melhorada.html', context) 