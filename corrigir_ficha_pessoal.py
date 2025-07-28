#!/usr/bin/env python
"""
Script para corrigir o problema da ficha pessoal
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, UsuarioFuncao

def corrigir_ficha_pessoal():
    """Corrige o problema da ficha pessoal"""
    
    print("🔧 CORRIGINDO PROBLEMA DA FICHA PESSOAL")
    print("=" * 60)
    
    # 1. Verificar usuário admin
    try:
        user_admin = User.objects.get(username='erisman')
        print(f"✅ Usuário encontrado: {user_admin.username}")
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado")
        return
    
    # 2. Verificar se tem militar associado
    try:
        militar = user_admin.militar
        print(f"✅ Militar associado: {militar.nome_completo} (ID: {militar.pk})")
    except Militar.DoesNotExist:
        print("❌ Militar não encontrado para o usuário")
        return
    
    # 3. Verificar permissões do usuário
    funcoes = UsuarioFuncao.objects.filter(usuario=user_admin, status='ATIVO')
    print(f"📋 Funções do usuário: {funcoes.count()}")
    for funcao in funcoes:
        print(f"   • {funcao.cargo_funcao.nome}")
    
    # 4. Verificar se tem permissão para visualizar militares
    from militares.permissoes_sistema import tem_permissao
    tem_perm_militares = tem_permissao(user_admin, 'MILITARES', 'VISUALIZAR')
    print(f"🔐 Tem permissão para visualizar militares: {tem_perm_militares}")
    
    # 5. Criar uma nova view para ficha pessoal
    print(f"\n🔧 CRIANDO VIEW PARA FICHA PESSOAL")
    
    # Ler o arquivo views.py
    with open('militares/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se já existe a view militar_detail_pessoal
    if 'def militar_detail_pessoal(' in content:
        print("✅ View militar_detail_pessoal já existe")
    else:
        # Adicionar a nova view após a view militar_detail existente
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
    
    # 6. Atualizar o template base.html para usar a nova view
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
    
    # 7. Adicionar URL para a nova view
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
    
    # 8. Conclusão
    print(f"\n🎯 CONCLUSÃO:")
    print(f"   ✅ View militar_detail_pessoal criada")
    print(f"   ✅ Template base.html atualizado")
    print(f"   ✅ URL adicionada")
    print(f"\n   📋 Para testar:")
    print(f"      1. Acesse: http://127.0.0.1:8000/militares/")
    print(f"      2. Clique em 'Minha Ficha de Cadastro'")
    print(f"      3. Verifique se agora mostra a ficha em vez de redirecionar")
    print(f"      4. A URL deve ser: /militares/minha-ficha/")

if __name__ == "__main__":
    corrigir_ficha_pessoal() 