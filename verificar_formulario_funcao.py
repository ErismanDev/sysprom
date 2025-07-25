#!/usr/bin/env python
"""
Script para verificar se o formulário UsuarioFuncaoForm está funcionando
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

try:
    from militares.forms import UsuarioFuncaoForm
    from militares.models import UsuarioFuncao
    from django.contrib.auth.models import User
    
    print("🔍 VERIFICANDO FORMULÁRIO USUARIOFUNCAOFORM")
    print("=" * 60)
    
    # Verificar se o modelo tem as choices definidas
    print("📋 Choices do modelo UsuarioFuncao:")
    for choice in UsuarioFuncao.TIPO_FUNCAO_CHOICES:
        print(f"   - {choice[0]}: {choice[1]}")
    
    print("\n📋 Choices do status:")
    for choice in UsuarioFuncao.STATUS_CHOICES:
        print(f"   - {choice[0]}: {choice[1]}")
    
    # Criar formulário
    form = UsuarioFuncaoForm()
    
    print(f"\n✅ Formulário criado com sucesso!")
    print(f"📝 Campos do formulário:")
    for field_name, field in form.fields.items():
        print(f"   - {field_name}: {type(field).__name__}")
        if hasattr(field, 'choices') and field.choices:
            print(f"     Choices: {len(field.choices)} opções")
            # Verificar especificamente o campo tipo_funcao
            if field_name == 'tipo_funcao':
                print("     ✅ Campo tipo_funcao encontrado!")
                for choice in field.choices:
                    print(f"       {choice[0]}: {choice[1]}")
    
    # Verificar se há usuários disponíveis
    usuarios = User.objects.filter(is_active=True).count()
    print(f"\n👥 Usuários ativos disponíveis: {usuarios}")
    
    # Testar criação de função
    if usuarios > 0:
        usuario = User.objects.filter(is_active=True).first()
        print(f"\n🧪 Testando criação de função para usuário: {usuario.get_full_name()}")
        
        data = {
            'usuario': usuario.id,
            'nome_funcao': 'Teste de Função',
            'tipo_funcao': 'ADMINISTRATIVO',
            'status': 'ATIVO',
            'data_inicio': '2025-01-01',
        }
        
        form = UsuarioFuncaoForm(data)
        if form.is_valid():
            print("✅ Formulário válido!")
            funcao = form.save(commit=False)
            print(f"📝 Função criada: {funcao}")
        else:
            print("❌ Formulário inválido!")
            print("Erros:", form.errors)
    
    # Verificar se o campo tipo_funcao está no template
    print(f"\n🔍 Verificando se o campo tipo_funcao está no formulário:")
    if 'tipo_funcao' in form.fields:
        print("✅ Campo tipo_funcao está presente no formulário")
        field = form.fields['tipo_funcao']
        print(f"   Tipo: {type(field).__name__}")
        print(f"   Widget: {type(field.widget).__name__}")
        print(f"   Choices: {len(field.choices)} opções")
    else:
        print("❌ Campo tipo_funcao NÃO está presente no formulário")
    
except ImportError as e:
    print(f"❌ Erro no import: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")

print("\nVerificação concluída!") 