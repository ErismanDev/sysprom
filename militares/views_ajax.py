from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from .models import Militar


def get_posto_display(posto_code):
    """Retorna o display de um posto baseado no código"""
    POSTO_CHOICES = {
        'AS': 'Aspirante a Oficial',
        'AA': 'Aluno de Adaptação',
        '2T': '2º Tenente',
        '1T': '1º Tenente',
        'CP': 'Capitão',
        'MJ': 'Major',
        'TC': 'Tenente-Coronel',
        'CB': 'Coronel',
        'ST': 'Subtenente',
        '1S': '1º Sargento',
        '2S': '2º Sargento',
        '3S': '3º Sargento',
        'CAB': 'Cabo',
        'SD': 'Soldado',
    }
    return POSTO_CHOICES.get(posto_code, '')


@require_GET
@login_required
def militar_info_ajax(request):
    """Retorna informações do militar para o formulário de promoção (posto atual e próxima promoção)"""
    militar_id = request.GET.get('militar_id')
    if not militar_id:
        return JsonResponse({'error': 'ID não informado'}, status=400)
    try:
        militar = Militar.objects.get(pk=militar_id)
        
        # Verificar se é coronel (último posto)
        if militar.posto_graduacao == 'CB':
            return JsonResponse({
                'error': 'Coronéis não podem ser promovidos (último posto na hierarquia)',
                'posto_atual': militar.posto_graduacao,
                'posto_atual_display': militar.get_posto_graduacao_display(),
                'proxima_promocao': None,
                'proxima_promocao_display': ''
            })
        
        proxima = militar.proxima_promocao()
        return JsonResponse({
            'posto_atual': militar.posto_graduacao,
            'posto_atual_display': militar.get_posto_graduacao_display(),
            'proxima_promocao': proxima,
            'proxima_promocao_display': get_posto_display(proxima) if proxima else ''
        })
    except Militar.DoesNotExist:
        return JsonResponse({'error': 'Militar não encontrado'}, status=404) 