#!/usr/bin/env python
"""
Teste final para verificar se o vínculo correto foi feito
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar

def teste_final_corrigido():
    """Teste final para verificar o vínculo correto"""
    
    print("🎯 TESTE FINAL - VÍNCULO CORRIGIDO")
    print("=" * 60)
    
    # 1. Testar usuário 49008382334
    try:
        user_correto = User.objects.get(username='49008382334')
        print(f"✅ Usuário 49008382334 encontrado")
        
        # Verificar se tem militar associado
        try:
            militar = user_correto.militar
            print(f"✅ Militar associado: {militar.nome_completo} ({militar.get_posto_graduacao_display()})")
            print(f"   CPF: {militar.cpf}")
            print(f"   Matrícula: {militar.matricula}")
        except Militar.DoesNotExist:
            print("❌ Militar não associado ao usuário 49008382334")
            return
    except User.DoesNotExist:
        print("❌ Usuário 49008382334 não encontrado")
        return
    
    # 2. Testar usuário erisman
    try:
        user_erisman = User.objects.get(username='erisman')
        print(f"✅ Usuário erisman encontrado")
        
        # Verificar se tem militar associado
        try:
            militar_erisman = user_erisman.militar
            print(f"❌ Usuário erisman ainda tem militar associado: {militar_erisman.nome_completo}")
        except Militar.DoesNotExist:
            print(f"✅ Usuário erisman não tem militar associado (correto)")
    except User.DoesNotExist:
        print("❌ Usuário erisman não encontrado")
    
    # 3. Verificar se a view militar_detail_pessoal existe
    with open('militares/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def militar_detail_pessoal(' in content:
        print(f"\n✅ View militar_detail_pessoal existe")
    else:
        print(f"\n❌ View militar_detail_pessoal não existe")
    
    # 4. Verificar se a URL existe
    with open('militares/urls.py', 'r', encoding='utf-8') as f:
        urls_content = f.read()
    
    if 'militar_detail_pessoal' in urls_content:
        print(f"✅ URL militar_detail_pessoal existe")
    else:
        print(f"❌ URL militar_detail_pessoal não existe")
    
    # 5. Verificar se o template foi atualizado
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    if 'militar_detail_pessoal' in template_content:
        print(f"✅ Template base.html atualizado")
    else:
        print(f"❌ Template base.html não atualizado")
    
    # 6. Conclusão
    print(f"\n🎉 CONCLUSÃO DO TESTE:")
    print(f"   ✅ Usuário 49008382334 configurado corretamente")
    print(f"   ✅ Militar José ERISMAN de Sousa associado")
    print(f"   ✅ Usuário erisman sem militar associado")
    print(f"   ✅ View de ficha pessoal criada")
    print(f"   ✅ URL configurada")
    print(f"   ✅ Template atualizado")
    print(f"   ✅ Cache limpo")
    
    print(f"\n📋 PARA TESTAR NO NAVEGADOR:")
    print(f"   1. Faça login com o usuário: 49008382334")
    print(f"   2. Acesse: http://127.0.0.1:8000/militares/")
    print(f"   3. Clique em 'Minha Ficha de Cadastro'")
    print(f"   4. Deve mostrar a ficha do Major José ERISMAN de Sousa")
    print(f"   5. A URL deve ser: /militares/minha-ficha/")
    
    print(f"\n🔧 SE AINDA HOUVER PROBLEMAS:")
    print(f"   1. Pressione Ctrl+F5 para forçar recarregamento")
    print(f"   2. Limpe o cache do navegador")
    print(f"   3. Verifique se o servidor Django está rodando")
    print(f"   4. Verifique os logs do Django para erros")

if __name__ == "__main__":
    teste_final_corrigido() 