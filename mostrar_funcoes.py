#!/usr/bin/env python
"""
Script para mostrar onde estão as funções e como acessá-las
"""
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao

def mostrar_funcoes():
    """Mostra onde estão as funções e como acessá-las"""
    
    print("🔍 ONDE ESTÃO AS FUNÇÕES?")
    print("=" * 60)
    
    # 1. No banco de dados
    print("📊 1. NO BANCO DE DADOS:")
    print("   - Tabela: militares_usuariofuncao")
    print("   - Modelo: UsuarioFuncao")
    print("   - Localização: db.sqlite3")
    
    # 2. Contar funções
    total_funcoes = UsuarioFuncao.objects.count()
    print(f"\n📈 2. ESTATÍSTICAS:")
    print(f"   - Total de funções: {total_funcoes}")
    
    # 3. Funções por tipo
    print(f"\n📋 3. FUNÇÕES POR TIPO:")
    tipos = UsuarioFuncao.objects.values_list('tipo_funcao', flat=True).distinct()
    for tipo in tipos:
        count = UsuarioFuncao.objects.filter(tipo_funcao=tipo).count()
        print(f"   - {tipo}: {count} funções")
    
    # 4. Funções de comissão
    print(f"\n🎖️  4. FUNÇÕES DE COMISSÃO:")
    
    # CPO
    funcoes_cpo = UsuarioFuncao.objects.filter(nome_funcao__icontains='CPO').order_by('nome_funcao')
    print(f"\n   Comissão de Promoções de Oficiais (CPO):")
    for funcao in funcoes_cpo:
        print(f"     ✅ {funcao.nome_funcao}")
    
    # CPP
    funcoes_cpp = UsuarioFuncao.objects.filter(nome_funcao__icontains='CPP').order_by('nome_funcao')
    print(f"\n   Comissão de Promoções de Praças (CPP):")
    for funcao in funcoes_cpp:
        print(f"     ✅ {funcao.nome_funcao}")
    
    # 5. Como acessar no sistema
    print(f"\n🌐 5. COMO ACESSAR NO SISTEMA:")
    print("   - URL: http://127.0.0.1:8000/militares/usuarios/")
    print("   - Selecione um usuário")
    print("   - Clique em 'Gerenciar Funções'")
    print("   - Adicione as funções desejadas")
    
    # 6. Como acessar via admin
    print(f"\n⚙️  6. VIA ADMIN DO DJANGO:")
    print("   - URL: http://127.0.0.1:8000/admin/")
    print("   - Login: erisman / sua_senha")
    print("   - Seção: Militares > Funções dos Usuários")
    
    # 7. Como acessar via código
    print(f"\n💻 7. VIA CÓDIGO PYTHON:")
    print("   from militares.models import UsuarioFuncao")
    print("   funcoes = UsuarioFuncao.objects.all()")
    print("   for funcao in funcoes:")
    print("       print(funcao.nome_funcao)")
    
    # 8. Mostrar todas as funções
    print(f"\n📝 8. TODAS AS FUNÇÕES DISPONÍVEIS:")
    todas_funcoes = UsuarioFuncao.objects.all().order_by('tipo_funcao', 'nome_funcao')
    
    tipos_agrupados = {}
    for funcao in todas_funcoes:
        tipo = funcao.get_tipo_funcao_display()
        if tipo not in tipos_agrupados:
            tipos_agrupados[tipo] = []
        tipos_agrupados[tipo].append(funcao.nome_funcao)
    
    for tipo, funcoes in tipos_agrupados.items():
        print(f"\n   {tipo}:")
        for funcao in funcoes:
            print(f"     - {funcao}")
    
    return True

if __name__ == '__main__':
    sucesso = mostrar_funcoes()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("✅ Informações exibidas com sucesso!")
        print("\n📝 RESUMO:")
        print("   - As funções estão no banco de dados")
        print("   - Podem ser acessadas via sistema web")
        print("   - Podem ser gerenciadas via admin do Django")
        print("   - Podem ser acessadas via código Python")
    else:
        print("❌ Erro ao exibir informações!") 