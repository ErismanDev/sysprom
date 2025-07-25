#!/usr/bin/env python
"""
Script para testar o formulário simplificado de membros da comissão
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from militares.models import Militar, ComissaoPromocao, MembroComissao, CargoComissao, CargoFuncao, UsuarioFuncao
from militares.forms import MembroComissaoForm
from datetime import date

def testar_formulario_simplificado():
    """Testa o formulário simplificado de membros da comissão"""
    print("=== TESTE DO FORMULÁRIO SIMPLIFICADO ===")
    
    # Criar dados de teste
    try:
        # Criar usuário de teste
        user, created = User.objects.get_or_create(
            username='teste_admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Teste',
                'email': 'admin@teste.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # Criar cargo/função
        cargo_funcao, created = CargoFuncao.objects.get_or_create(
            nome='ADMINISTRADOR',
            defaults={
                'descricao': 'Administrador do sistema',
                'ativo': True,
                'ordem': 1
            }
        )
        
        # Criar função do usuário
        funcao_usuario, created = UsuarioFuncao.objects.get_or_create(
            usuario=user,
            cargo_funcao=cargo_funcao,
            defaults={
                'tipo_funcao': 'ADMINISTRATIVO',
                'status': 'ATIVO',
                'data_inicio': date.today()
            }
        )
        
        # Criar militar de teste
        militar, created = Militar.objects.get_or_create(
            matricula='TESTE001',
            defaults={
                'nome_completo': 'Militar Teste',
                'nome_guerra': 'Teste',
                'cpf': '12345678901',
                'rg': '1234567',
                'orgao_expedidor': 'SSP',
                'data_nascimento': date(1990, 1, 1),
                'sexo': 'M',
                'quadro': 'COMB',
                'posto_graduacao': 'CP',
                'data_ingresso': date(2010, 1, 1),
                'data_promocao_atual': date(2020, 1, 1),
                'situacao': 'AT',
                'email': 'militar@teste.com',
                'telefone': '123456789',
                'celular': '987654321',
                'user': user
            }
        )
        
        # Criar comissão de teste
        comissao, created = ComissaoPromocao.objects.get_or_create(
            nome='Comissão Teste CPO',
            defaults={
                'tipo': 'CPO',
                'data_criacao': date.today(),
                'status': 'ATIVA'
            }
        )
        
        # Criar cargo da comissão
        cargo_comissao, created = CargoComissao.objects.get_or_create(
            nome='Membro Efetivo',
            defaults={
                'codigo': 'MEMBRO_EFETIVO',
                'descricao': 'Membro efetivo da comissão',
                'ativo': True,
                'ordem': 1
            }
        )
        
        print(f"✓ Dados de teste criados:")
        print(f"  - Usuário: {user.username}")
        print(f"  - Militar: {militar.nome_completo}")
        print(f"  - Comissão: {comissao.nome}")
        print(f"  - Cargo: {cargo_comissao.nome}")
        
        # Testar formulário
        print("\n=== TESTANDO FORMULÁRIO ===")
        
        # Simular dados do formulário
        form_data = {
            'militar': militar.id,
            'cargo': cargo_comissao.id,
            'data_nomeacao': date.today(),
            'ativo': True,
            'observacoes': 'Teste do formulário simplificado'
        }
        
        # Criar formulário
        form = MembroComissaoForm(data=form_data, comissao_tipo=comissao.tipo)
        
        print(f"✓ Formulário criado com sucesso")
        print(f"✓ Campos do formulário: {list(form.fields.keys())}")
        
        # Verificar se o campo 'usuario' não está presente
        if 'usuario' not in form.fields:
            print("✓ Campo 'usuario' não está presente no formulário (correto)")
        else:
            print("✗ Campo 'usuario' ainda está presente no formulário (erro)")
        
        # Verificar se o campo 'cargo' está presente
        if 'cargo' in form.fields:
            print("✓ Campo 'cargo' está presente no formulário (correto)")
        else:
            print("✗ Campo 'cargo' não está presente no formulário (erro)")
        
        # Validar formulário
        if form.is_valid():
            print("✓ Formulário é válido")
            print(f"✓ Dados validados: {form.cleaned_data}")
            
            # Testar salvamento
            membro = form.save(commit=False)
            membro.comissao = comissao
            
            # Definir usuário automaticamente
            if membro.militar and membro.militar.user:
                membro.usuario = membro.militar.user
                print(f"✓ Usuário definido automaticamente: {membro.usuario.username}")
            
            membro.save()
            print(f"✓ Membro salvo com sucesso: {membro}")
            print(f"✓ Usuário do membro: {membro.usuario}")
            print(f"✓ Militar do membro: {membro.militar}")
            print(f"✓ Cargo do membro: {membro.cargo}")
            
        else:
            print("✗ Formulário inválido")
            print(f"✗ Erros: {form.errors}")
        
        # Limpar dados de teste
        print("\n=== LIMPANDO DADOS DE TESTE ===")
        MembroComissao.objects.filter(comissao=comissao).delete()
        comissao.delete()
        militar.delete()
        funcao_usuario.delete()
        cargo_funcao.delete()
        user.delete()
        cargo_comissao.delete()
        print("✓ Dados de teste removidos")
        
        print("\n=== TESTE CONCLUÍDO COM SUCESSO ===")
        return True
        
    except Exception as e:
        print(f"✗ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = testar_formulario_simplificado()
    sys.exit(0 if success else 1) 