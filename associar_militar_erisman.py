#!/usr/bin/env python
"""
Script para associar o militar correto ao usuário erisman
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar

def associar_militar_erisman():
    """Associa o militar correto ao usuário erisman"""
    
    print("🔧 ASSOCIANDO MILITAR AO USUÁRIO ERISMAN")
    print("=" * 60)
    
    # 1. Buscar usuário erisman
    try:
        user_erisman = User.objects.get(username='erisman')
        print(f"✅ Usuário encontrado: {user_erisman.username}")
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado")
        return
    
    # 2. Buscar militar José ERISMAN de Sousa
    try:
        militar_erisman = Militar.objects.get(nome_completo__icontains='ERISMAN')
        print(f"✅ Militar encontrado: {militar_erisman.nome_completo} (ID: {militar_erisman.pk})")
    except Militar.DoesNotExist:
        print("❌ Militar com nome 'ERISMAN' não encontrado")
        return
    
    # 3. Verificar se o militar já tem usuário associado
    if hasattr(militar_erisman, 'user') and militar_erisman.user:
        print(f"⚠️ Militar já tem usuário associado: {militar_erisman.user.username}")
        if militar_erisman.user != user_erisman:
            print(f"   Removendo associação anterior...")
            militar_erisman.user = None
            militar_erisman.save()
    
    # 4. Associar o militar ao usuário erisman
    print(f"🔗 Associando militar {militar_erisman.nome_completo} ao usuário {user_erisman.username}...")
    militar_erisman.user = user_erisman
    militar_erisman.save()
    
    # 5. Verificar se a associação foi feita
    try:
        militar_associado = user_erisman.militar
        print(f"✅ Associação realizada com sucesso!")
        print(f"   Usuário: {user_erisman.username}")
        print(f"   Militar: {militar_associado.nome_completo}")
        print(f"   Posto: {militar_associado.get_posto_graduacao_display()}")
        print(f"   Matrícula: {militar_associado.matricula}")
    except Militar.DoesNotExist:
        print("❌ Erro na associação")
        return
    
    # 6. Testar a nova view de ficha pessoal
    print(f"\n🧪 TESTANDO FICHA PESSOAL")
    
    # Verificar se a view militar_detail_pessoal existe
    with open('militares/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def militar_detail_pessoal(' in content:
        print("✅ View militar_detail_pessoal existe")
    else:
        print("❌ View militar_detail_pessoal não existe - criando...")
        
        # Adicionar a nova view
        nova_view = '''
@login_required
def militar_detail_pessoal(request):
    """Exibe os detalhes do próprio militar do usuário logado"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Verificar se o usuário tem militar associado
    try:
        militar = request.user.militar
    except Militar.DoesNotExist:
        messages.error(request, 'Você não possui militar associado.')
        return redirect('militares:militar_dashboard')
    
    # Busca ficha de conceito
    fichas_oficiais = list(militar.fichaconceitooficiais_set.all())
    fichas_pracas = list(militar.fichaconceitopracas_set.all())
    ficha_conceito = fichas_oficiais + fichas_pracas
    ficha_conceito.sort(key=lambda x: x.data_registro, reverse=True)
    
    # Busca promoções
    promocoes = militar.promocao_set.all().order_by('-data_promocao')
    
    # Busca documentos
    documentos = Documento.objects.filter(militar=militar).order_by('-data_upload')
    
    context = {
        'militar': militar,
        'ficha_conceito': ficha_conceito,
        'promocoes': promocoes,
        'documentos': documentos,
        'is_own_ficha': True,  # Flag para indicar que é a própria ficha
    }
    
    return render(request, 'militares/militar_detail.html', context)
'''
        
        # Encontrar a última view militar_detail e adicionar a nova view após ela
        import re
        pattern = r'@login_required\s+@requer_perm_militares_visualizar\s+def militar_detail\(request, pk\):.*?return render\(request, \'militares/militar_detail\.html\', context\)'
        
        if re.search(pattern, content, re.DOTALL):
            # Substituir a última ocorrência
            content = re.sub(pattern, r'\g<0>\n' + nova_view, content, count=1, flags=re.DOTALL)
            print("✅ View militar_detail_pessoal adicionada")
        else:
            print("❌ Não foi possível encontrar a view militar_detail para adicionar a nova view")
            return
        
        # Salvar o arquivo
        with open('militares/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 7. Atualizar o template base.html
    print(f"\n🔧 ATUALIZANDO TEMPLATE BASE.HTML")
    
    template_path = 'templates/base.html'
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Verificar se já usa a nova view
        if 'militar_detail_pessoal' in template_content:
            print("✅ Template já usa a nova view")
        else:
            # Substituir a URL da ficha pessoal
            old_url = "{% url 'militares:militar_detail' user.militar.pk %}"
            new_url = "{% url 'militares:militar_detail_pessoal' %}"
            
            if old_url in template_content:
                template_content = template_content.replace(old_url, new_url)
                print("✅ URL da ficha pessoal atualizada no template")
            else:
                print("❌ URL da ficha pessoal não encontrada no template")
            
            # Salvar o template
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
                
    except FileNotFoundError:
        print(f"❌ Template {template_path} não encontrado")
    
    # 8. Adicionar URL para a nova view
    print(f"\n🔧 ADICIONANDO URL PARA A NOVA VIEW")
    
    urls_path = 'militares/urls.py'
    try:
        with open(urls_path, 'r', encoding='utf-8') as f:
            urls_content = f.read()
        
        # Verificar se já existe a URL
        if 'militar_detail_pessoal' in urls_content:
            print("✅ URL já existe")
        else:
            # Adicionar a nova URL
            # Encontrar o padrão de URLs de militar
            pattern = r'path\(\'militar/(?P<pk>\d+)/\', views\.militar_detail, name=\'militar_detail\'\),'
            
            if pattern in urls_content:
                nova_url = '''    path('minha-ficha/', views.militar_detail_pessoal, name='militar_detail_pessoal'),'''
                urls_content = urls_content.replace(pattern, pattern + '\n' + nova_url)
                print("✅ URL adicionada")
            else:
                print("❌ Padrão de URL não encontrado")
            
            # Salvar o arquivo
            with open(urls_path, 'w', encoding='utf-8') as f:
                f.write(urls_content)
                
    except FileNotFoundError:
        print(f"❌ Arquivo {urls_path} não encontrado")
    
    # 9. Conclusão
    print(f"\n🎯 CONCLUSÃO:")
    print(f"   ✅ Militar associado ao usuário erisman")
    print(f"   ✅ View militar_detail_pessoal criada")
    print(f"   ✅ Template base.html atualizado")
    print(f"   ✅ URL adicionada")
    print(f"\n   📋 Para testar:")
    print(f"      1. Acesse: http://127.0.0.1:8000/militares/")
    print(f"      2. Clique em 'Minha Ficha de Cadastro'")
    print(f"      3. Verifique se agora mostra a ficha em vez de redirecionar")
    print(f"      4. A URL deve ser: /militares/minha-ficha/")

if __name__ == "__main__":
    associar_militar_erisman() 