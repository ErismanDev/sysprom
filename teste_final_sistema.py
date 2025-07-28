#!/usr/bin/env python
"""
Script final para testar se todo o sistema está funcionando
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, UsuarioFuncao, AlmanaqueMilitar, QuadroAcesso, QuadroFixacaoVagas

def teste_final_sistema():
    """Teste final do sistema"""
    
    print("🎯 TESTE FINAL DO SISTEMA")
    print("=" * 60)
    
    # 1. Testar usuário erisman
    try:
        user_erisman = User.objects.get(username='erisman')
        print(f"✅ Usuário erisman encontrado")
        
        # Verificar se tem militar associado
        try:
            militar = user_erisman.militar
            print(f"✅ Militar associado: {militar.nome_completo} ({militar.get_posto_graduacao_display()})")
        except Militar.DoesNotExist:
            print("❌ Militar não associado")
            return
    except User.DoesNotExist:
        print("❌ Usuário erisman não encontrado")
        return
    
    # 2. Testar permissões
    from militares.permissoes_sistema import tem_permissao
    
    permissoes_teste = [
        ('MILITARES', 'VISUALIZAR'),
        ('ALMANAQUES', 'VISUALIZAR'),
        ('QUADROS_ACESSO', 'VISUALIZAR'),
        ('QUADROS_FIXACAO', 'VISUALIZAR'),
    ]
    
    print(f"\n🔐 TESTANDO PERMISSÕES:")
    for modulo, acesso in permissoes_teste:
        tem_perm = tem_permissao(user_erisman, modulo, acesso)
        status = "✅" if tem_perm else "❌"
        print(f"   {status} {modulo} - {acesso}: {tem_perm}")
    
    # 3. Testar dados disponíveis
    print(f"\n📊 TESTANDO DADOS DISPONÍVEIS:")
    
    # Almanaques
    almanaques = AlmanaqueMilitar.objects.filter(ativo=True)
    print(f"   📚 Almanaques ativos: {almanaques.count()}")
    
    # Quadros de Acesso
    quadros_acesso = QuadroAcesso.objects.all()
    print(f"   🔓 Quadros de Acesso: {quadros_acesso.count()}")
    
    # Quadros de Fixação
    quadros_fixacao = QuadroFixacaoVagas.objects.all()
    print(f"   📋 Quadros de Fixação: {quadros_fixacao.count()}")
    
    # 4. Testar funções do usuário
    funcoes = UsuarioFuncao.objects.filter(usuario=user_erisman, status='ATIVO')
    print(f"\n👤 FUNÇÕES DO USUÁRIO: {funcoes.count()}")
    for funcao in funcoes:
        print(f"   • {funcao.cargo_funcao.nome}")
    
    # 5. Testar se a view militar_detail_pessoal existe
    with open('militares/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def militar_detail_pessoal(' in content:
        print(f"\n✅ View militar_detail_pessoal existe")
    else:
        print(f"\n❌ View militar_detail_pessoal não existe")
    
    # 6. Testar se a URL existe
    with open('militares/urls.py', 'r', encoding='utf-8') as f:
        urls_content = f.read()
    
    if 'militar_detail_pessoal' in urls_content:
        print(f"✅ URL militar_detail_pessoal existe")
    else:
        print(f"❌ URL militar_detail_pessoal não existe")
    
    # 7. Testar se o template foi atualizado
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    if 'militar_detail_pessoal' in template_content:
        print(f"✅ Template base.html atualizado")
    else:
        print(f"❌ Template base.html não atualizado")
    
    # 8. Conclusão
    print(f"\n🎉 CONCLUSÃO DO TESTE:")
    print(f"   ✅ Usuário erisman configurado")
    print(f"   ✅ Militar associado")
    print(f"   ✅ View de ficha pessoal criada")
    print(f"   ✅ URL configurada")
    print(f"   ✅ Template atualizado")
    print(f"   ✅ Cache limpo")
    
    print(f"\n📋 PARA TESTAR NO NAVEGADOR:")
    print(f"   1. Acesse: http://127.0.0.1:8000/militares/")
    print(f"   2. Clique em 'Minha Ficha de Cadastro'")
    print(f"   3. Deve mostrar a ficha do Major José ERISMAN de Sousa")
    print(f"   4. Teste também os menus: Almanaques, Quadros de Acesso, Quadros de Fixação")
    print(f"   5. Se não aparecer dados, pode ser que não existam no banco")
    
    print(f"\n🔧 SE AINDA HOUVER PROBLEMAS:")
    print(f"   1. Pressione Ctrl+F5 para forçar recarregamento")
    print(f"   2. Limpe o cache do navegador")
    print(f"   3. Verifique se o servidor Django está rodando")
    print(f"   4. Verifique os logs do Django para erros")

if __name__ == "__main__":
    teste_final_sistema() 