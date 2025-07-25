from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import QuadroAcesso, AtaSessao, VotoDeliberacao, QuadroFixacaoVagas


@login_required
def verificar_autenticidade(request):
    """
    View para verificar a autenticidade de documentos
    """
    resultado = None
    documento = None
    erro = None
    
    if request.method == 'POST':
        codigo_verificador = request.POST.get('codigo_verificador', '').strip()
        codigo_crc = request.POST.get('codigo_crc', '').strip()
        tipo_documento = request.POST.get('tipo_documento', '')
        
        if codigo_verificador and codigo_crc:
            try:
                # Extrair o ID do código verificador (primeiros 8 dígitos)
                if len(codigo_verificador) >= 8:
                    documento_id = int(codigo_verificador[:8])
                    
                    # Verificar o código CRC
                    codigo_crc_esperado = f"{hash(str(documento_id)) % 0xFFFFFFF:07X}"
                    
                    if codigo_crc.upper() == codigo_crc_esperado:
                        # Buscar o documento baseado no tipo
                        if tipo_documento == 'quadro':
                            documento = get_object_or_404(QuadroAcesso, pk=documento_id)
                            resultado = {
                                'tipo': 'Quadro de Acesso',
                                'titulo': f'Quadro de Acesso - {documento.get_tipo_display()}',
                                'data_criacao': documento.data_criacao,
                                'assinaturas': documento.assinaturas.count()
                            }
                        elif tipo_documento == 'ata':
                            documento = get_object_or_404(AtaSessao, pk=documento_id)
                            resultado = {
                                'tipo': 'Ata de Sessão',
                                'titulo': f'Ata da Sessão {documento.sessao.numero}',
                                'data_criacao': documento.sessao.data_sessao,
                                'assinaturas': documento.assinaturas.count()
                            }
                        elif tipo_documento == 'voto':
                            documento = get_object_or_404(VotoDeliberacao, pk=documento_id)
                            resultado = {
                                'tipo': 'Voto de Deliberação',
                                'titulo': f'Voto de {documento.membro.militar.nome_completo}',
                                'data_criacao': documento.data_registro,
                                'assinaturas': 1 if documento.assinado else 0
                            }
                        elif tipo_documento == 'quadro_fixacao':
                            documento = get_object_or_404(QuadroFixacaoVagas, pk=documento_id)
                            resultado = {
                                'tipo': 'Quadro de Fixação de Vagas',
                                'titulo': f'Quadro de Fixação - {documento.get_tipo_display()}',
                                'data_criacao': documento.data_criacao,
                                'assinaturas': documento.assinaturas.count()
                            }
                        else:
                            erro = "Tipo de documento não reconhecido."
                    else:
                        erro = "Código CRC inválido. Verifique os códigos informados."
                else:
                    erro = "Código verificador inválido. Deve ter pelo menos 8 dígitos."
                    
            except (ValueError, TypeError):
                erro = "Código verificador inválido. Deve conter apenas números."
            except Exception as e:
                erro = f"Erro ao verificar documento: {str(e)}"
        else:
            erro = "Por favor, informe ambos os códigos."
    
    context = {
        'resultado': resultado,
        'documento': documento,
        'erro': erro,
        'tipos_documento': [
            ('quadro', 'Quadro de Acesso'),
            ('ata', 'Ata de Sessão'),
            ('voto', 'Voto de Deliberação'),
            ('quadro_fixacao', 'Quadro de Fixação de Vagas'),
        ]
    }
    
    return render(request, 'militares/verificar_autenticidade.html', context) 