#!/usr/bin/env python
"""
Script para testar o formulário de membro da comissão
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, ComissaoPromocao, CargoComissao, MembroComissao
from militares.forms import MembroComissaoForm

def testar_formulario_membro_comissao():
    """Testa se o formulário de membro da comissão está funcionando corretamente"""
    
    print("=== Teste do Formulário de Membro da Comissão ===")
    
    try:
        # 1. Verificar se existe pelo menos uma comissão
        comissoes = ComissaoPromocao.objects.all()
        print(f"1. Comissões encontradas: {comissoes.count()}")
        
        if not comissoes.exists():
            print("   Criando comissão de teste...")
            comissao_teste = ComissaoPromocao.objects.create(
                tipo='CPO',
                nome='Comissão de Promoções de Oficiais - Teste',
                data_criacao='2025-01-01',
                status='ATIVA'
            )
        else:
            comissao_teste = comissoes.first()
            print(f"   Usando comissão: {comissao_teste.nome}")
        
        # 2. Verificar se existe pelo menos um militar
        militares = Militar.objects.filter(situacao='AT')
        print(f"2. Militares ativos encontrados: {militares.count()}")
        
        if not militares.exists():
            print("   Criando militar de teste...")
            militar_teste = Militar.objects.create(
                matricula='123456',
                nome_completo='Militar de Teste',
                nome_guerra='Teste',
                cpf='123.456.789-00',
                rg='1234567',
                orgao_expedidor='SSP-PI',
                data_nascimento='1990-01-01',
                sexo='M',
                quadro='COMB',
                posto_graduacao='CP',
                data_ingresso='2010-01-01',
                data_promocao_atual='2020-01-01',
                situacao='AT',
                email='teste@teste.com',
                telefone='(86) 99999-9999',
                celular='(86) 99999-9999'
            )
        else:
            militar_teste = militares.first()
            print(f"   Usando militar: {militar_teste.nome_completo}")
        
        # 3. Verificar se existe pelo menos um cargo da comissão
        cargos = CargoComissao.objects.filter(ativo=True)
        print(f"3. Cargos da comissão encontrados: {cargos.count()}")
        
        if not cargos.exists():
            print("   Criando cargo de teste...")
            cargo_teste = CargoComissao.objects.create(
                nome='Cargo de Teste',
                codigo='CARGO_TESTE',
                descricao='Cargo para teste do sistema',
                ativo=True,
                ordem=1
            )
        else:
            cargo_teste = cargos.first()
            print(f"   Usando cargo: {cargo_teste.nome}")
        
        # 4. Testar o formulário
        print("4. Testando formulário...")
        
        # Criar dados de teste
        form_data = {
            'militar': militar_teste.id,
            'cargo': cargo_teste.id,
            'data_nomeacao': '2025-01-01',
            'ativo': True,
        }
        
        # Criar formulário
        form = MembroComissaoForm(data=form_data, comissao_tipo=comissao_teste.tipo)
        
        if form.is_valid():
            print("   ✅ Formulário válido!")
            print(f"   - Militar: {form.cleaned_data['militar']}")
            print(f"   - Cargo: {form.cleaned_data['cargo']}")
            print(f"   - Data de Nomeação: {form.cleaned_data['data_nomeacao']}")
            print(f"   - Ativo: {form.cleaned_data['ativo']}")
            
            # Testar criação do membro
            membro = form.save(commit=False)
            membro.comissao = comissao_teste
            membro.save()
            print(f"   ✅ Membro criado com sucesso: {membro}")
            
        else:
            print("   ❌ Formulário inválido!")
            for field, errors in form.errors.items():
                print(f"   - {field}: {errors}")
            return False
        
        # 5. Testar campos do formulário
        print("5. Testando campos do formulário...")
        
        # Verificar se o campo cargo está presente
        if 'cargo' in form.fields:
            print("   ✅ Campo 'cargo' presente no formulário")
            print(f"   - Label: {form.fields['cargo'].label}")
            print(f"   - Required: {form.fields['cargo'].required}")
        else:
            print("   ❌ Campo 'cargo' não encontrado no formulário")
            return False
        
        # Verificar se o campo militar está presente
        if 'militar' in form.fields:
            print("   ✅ Campo 'militar' presente no formulário")
            print(f"   - Label: {form.fields['militar'].label}")
            print(f"   - Required: {form.fields['militar'].required}")
        else:
            print("   ❌ Campo 'militar' não encontrado no formulário")
            return False
        
        print("\n=== Teste Concluído com Sucesso! ===")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    sucesso = testar_formulario_membro_comissao()
    sys.exit(0 if sucesso else 1) 