#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import MembroComissao, Militar, ComissaoPromocao
from datetime import date

def teste_simples():
    print("=== TESTE SIMPLES ===\n")
    
    try:
        # Verificar se temos usuários
        usuarios = User.objects.all()
        print(f"Usuários disponíveis: {usuarios.count()}")
        
        # Verificar se temos comissões
        comissoes = ComissaoPromocao.objects.all()
        print(f"Comissões disponíveis: {comissoes.count()}")
        
        # Verificar se temos militares
        militares = Militar.objects.all()
        print(f"Militares disponíveis: {militares.count()}")
        
        # Verificar membros de comissões
        membros = MembroComissao.objects.all()
        print(f"Membros de comissões: {membros.count()}")
        
        # Se não temos militares, criar um de teste
        if militares.count() == 0:
            print("\nCriando militar de teste...")
            try:
                usuario = User.objects.first()
                if usuario:
                    militar = Militar.objects.create(
                        nome_guerra="TESTE",
                        cpf="123.456.789-00",
                        nome_completo="Militar de Teste",
                        posto_graduacao="CB",
                        data_nascimento=date(1980, 1, 1),
                        data_ingresso=date(2020, 1, 1),
                        data_promocao_atual=date(2020, 1, 1),
                        user=usuario
                    )
                    print(f"✅ Militar criado: {militar.nome_guerra}")
                else:
                    print("❌ Nenhum usuário disponível")
            except Exception as e:
                print(f"❌ Erro ao criar militar: {e}")
        
        # Se temos comissões e militares, tentar criar um membro
        if comissoes.count() > 0 and militares.count() > 0:
            print("\nTentando criar membro de comissão...")
            try:
                comissao = comissoes.first()
                militar = militares.first()
                usuario = militar.user
                
                membro = MembroComissao.objects.create(
                    usuario=usuario,
                    militar=militar,
                    comissao=comissao,
                    ativo=True
                )
                print(f"✅ Membro criado: {membro.id}")
            except Exception as e:
                print(f"❌ Erro ao criar membro: {e}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == '__main__':
    teste_simples() 