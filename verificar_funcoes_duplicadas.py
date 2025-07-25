#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao

def verificar_funcoes_duplicadas():
    """Verifica e corrige funções duplicadas"""
    print("🔍 VERIFICANDO FUNÇÕES DUPLICADAS")
    print("=" * 50)
    
    # Verificar todas as funções do usuário erisman
    user = User.objects.get(username='erisman')
    funcoes = UsuarioFuncao.objects.filter(usuario=user).order_by('cargo_funcao__nome', 'data_inicio')
    
    print(f"Funções do usuário {user.username}:")
    for funcao in funcoes:
        print(f"  - {funcao.cargo_funcao.nome} (Status: {funcao.status}, Data: {funcao.data_inicio}, ID: {funcao.id})")
    
    # Verificar duplicatas
    funcoes_por_cargo = {}
    for funcao in funcoes:
        cargo_nome = funcao.cargo_funcao.nome
        if cargo_nome not in funcoes_por_cargo:
            funcoes_por_cargo[cargo_nome] = []
        funcoes_por_cargo[cargo_nome].append(funcao)
    
    print(f"\nFunções duplicadas encontradas:")
    for cargo_nome, funcoes_list in funcoes_por_cargo.items():
        if len(funcoes_list) > 1:
            print(f"  {cargo_nome}: {len(funcoes_list)} funções")
            for i, funcao in enumerate(funcoes_list):
                print(f"    {i+1}. ID: {funcao.id}, Status: {funcao.status}, Data: {funcao.data_inicio}")
    
    return funcoes_por_cargo

def corrigir_funcoes_duplicadas():
    """Corrige funções duplicadas mantendo apenas uma ativa"""
    print("\n🔧 CORRIGINDO FUNÇÕES DUPLICADAS")
    print("=" * 50)
    
    user = User.objects.get(username='erisman')
    funcoes_por_cargo = verificar_funcoes_duplicadas()
    
    for cargo_nome, funcoes_list in funcoes_por_cargo.items():
        if len(funcoes_list) > 1:
            print(f"\nCorrigindo {cargo_nome}:")
            
            # Manter apenas a primeira função e excluir as outras
            funcao_principal = funcoes_list[0]
            funcoes_para_excluir = funcoes_list[1:]
            
            # Atualizar a função principal para status AT
            funcao_principal.status = 'AT'
            funcao_principal.save()
            print(f"  ✅ Mantida: ID {funcao_principal.id} (Status: AT)")
            
            # Excluir as duplicatas
            for funcao in funcoes_para_excluir:
                print(f"  ❌ Excluída: ID {funcao.id}")
                funcao.delete()
    
    print("\n✅ Correção concluída!")

if __name__ == "__main__":
    corrigir_funcoes_duplicadas() 