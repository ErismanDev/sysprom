import os
import mimetypes
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings
from .models import Publicacao, AnexoNota


@login_required
@require_http_methods(["POST"])
def upload_anexo_nota(request, nota_id):
    """
    Upload de anexo para uma nota específica
    """
    try:
        # Buscar a nota
        nota = get_object_or_404(Publicacao, pk=nota_id, tipo='NOTA')
        
        # Verificar permissões
        if not nota.can_edit(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para adicionar anexos a esta nota'
            }, status=403)
        
        # Verificar se foi enviado arquivo
        if 'arquivo' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Nenhum arquivo foi enviado'
            }, status=400)
        
        arquivo = request.FILES['arquivo']
        descricao = request.POST.get('descricao', '').strip()
        
        # Validar tamanho do arquivo (máximo 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if arquivo.size > max_size:
            return JsonResponse({
                'success': False,
                'error': f'Arquivo muito grande. Tamanho máximo permitido: 10MB'
            }, status=400)
        
        # Validar tipo de arquivo - apenas PDF
        nome_arquivo = arquivo.name.lower()
        extensao = nome_arquivo.split('.')[-1] if '.' in nome_arquivo else ''
        
        if extensao != 'pdf':
            return JsonResponse({
                'success': False,
                'error': f'Apenas arquivos PDF são permitidos. O arquivo "{arquivo.name}" não é um PDF.'
            }, status=400)
        
        # Obter tipo MIME
        tipo_mime, _ = mimetypes.guess_type(arquivo.name)
        if not tipo_mime:
            tipo_mime = 'application/octet-stream'
        
        # Criar anexo
        anexo = AnexoNota.objects.create(
            publicacao=nota,
            arquivo=arquivo,
            nome_original=arquivo.name,
            descricao=descricao,
            tamanho=arquivo.size,
            tipo_mime=tipo_mime,
            upload_por=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Anexo adicionado com sucesso!',
            'anexo': {
                'id': anexo.id,
                'nome_original': anexo.nome_original,
                'descricao': anexo.descricao or '',
                'tamanho': anexo.get_tamanho_display(),
                'tipo_mime': anexo.tipo_mime,
                'icone_tipo': anexo.get_icone_tipo(),
                'data_upload': anexo.data_upload.strftime('%d/%m/%Y %H:%M'),
                'upload_por': anexo.upload_por.get_full_name() or anexo.upload_por.username
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao fazer upload do anexo: {str(e)}'
        }, status=500)


@login_required
def listar_anexos_nota(request, nota_id):
    """
    Lista todos os anexos de uma nota
    """
    print(f"📋 LISTAR ANEXOS: Listando anexos para nota ID: {nota_id}")
    try:
        nota = get_object_or_404(Publicacao, pk=nota_id, tipo='NOTA')
        print(f"📋 LISTAR ANEXOS: Nota encontrada: {nota.titulo}")
        
        # Verificar permissões de visualização
        can_view = True
        if nota.status != 'PUBLICADA':
            if not nota.can_edit(request.user) and not nota.can_publish(request.user):
                can_view = False
        
        if not can_view:
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para visualizar os anexos desta nota'
            }, status=403)
        
        anexos = nota.anexos.filter(ativo=True).order_by('-data_upload')
        
        anexos_data = []
        for anexo in anexos:
            anexos_data.append({
                'id': anexo.id,
                'nome_original': anexo.nome_original,
                'descricao': anexo.descricao or '',
                'tamanho': anexo.get_tamanho_display(),
                'tipo_mime': anexo.tipo_mime,
                'icone_tipo': anexo.get_icone_tipo(),
                'data_upload': anexo.data_upload.strftime('%d/%m/%Y %H:%M'),
                'upload_por': anexo.upload_por.get_full_name() if anexo.upload_por else 'Usuário removido',
                'url_download': anexo.arquivo.url if anexo.arquivo else None
            })
        
        print(f"📋 LISTAR ANEXOS: Retornando {len(anexos_data)} anexos ativos")
        return JsonResponse({
            'success': True,
            'anexos': anexos_data,
            'nota_status': nota.status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao listar anexos: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["DELETE"])
def excluir_anexo_nota(request, anexo_id):
    """
    Exclui um anexo de nota
    """
    print(f"🔍 EXCLUIR ANEXO: Iniciando exclusão do anexo ID: {anexo_id}")
    print(f"🔍 EXCLUIR ANEXO: Usuário: {request.user}")
    print(f"🔍 EXCLUIR ANEXO: Método: {request.method}")
    
    try:
        anexo = get_object_or_404(AnexoNota, pk=anexo_id, ativo=True)
        print(f"🔍 EXCLUIR ANEXO: Anexo encontrado: {anexo.nome_original}")
        print(f"🔍 EXCLUIR ANEXO: Status da publicação: {anexo.publicacao.status}")
        
        # Verificar se a nota está publicada
        if anexo.publicacao.status == 'PUBLICADA':
            return JsonResponse({
                'success': False,
                'error': 'Não é possível excluir anexos de notas já publicadas. Apenas anexos de notas em rascunho podem ser excluídos.'
            }, status=403)
        
        # Verificar permissões
        if not anexo.publicacao.can_edit(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para excluir este anexo'
            }, status=403)
        
        # Marcar como inativo (soft delete)
        anexo.ativo = False
        anexo.save()
        print(f"✅ EXCLUIR ANEXO: Anexo marcado como inativo com sucesso")
        
        return JsonResponse({
            'success': True,
            'message': 'Anexo excluído com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao excluir anexo: {str(e)}'
        }, status=500)


@login_required
def download_anexo_nota(request, anexo_id):
    """
    Download de um anexo de nota
    """
    try:
        anexo = get_object_or_404(AnexoNota, pk=anexo_id, ativo=True)
        
        # Verificar permissões de visualização
        can_view = True
        if anexo.publicacao.status != 'PUBLICADA':
            if not anexo.publicacao.can_edit(request.user) and not anexo.publicacao.can_publish(request.user):
                can_view = False
        
        if not can_view:
            raise Http404("Anexo não encontrado")
        
        # Verificar se o arquivo existe
        if not anexo.arquivo or not default_storage.exists(anexo.arquivo.name):
            raise Http404("Arquivo não encontrado")
        
        # Preparar resposta
        response = HttpResponse(
            default_storage.open(anexo.arquivo.name).read(),
            content_type=anexo.tipo_mime
        )
        
        # Configurar headers para download
        response['Content-Disposition'] = f'attachment; filename="{anexo.nome_original}"'
        response['Content-Length'] = anexo.tamanho
        
        return response
        
    except Exception as e:
        raise Http404("Erro ao fazer download do anexo")


@login_required
@require_http_methods(["POST"])
def atualizar_descricao_anexo(request, anexo_id):
    """
    Atualiza a descrição de um anexo
    """
    try:
        anexo = get_object_or_404(AnexoNota, pk=anexo_id, ativo=True)
        
        # Verificar permissões
        if not anexo.publicacao.can_edit(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para editar este anexo'
            }, status=403)
        
        descricao = request.POST.get('descricao', '').strip()
        
        anexo.descricao = descricao
        anexo.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Descrição atualizada com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao atualizar descrição: {str(e)}'
        }, status=500)
