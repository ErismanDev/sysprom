#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import MembroComissao, UsuarioFuncao, QuadroAcesso

def teste_final():
    """Teste final das permissões"""
    
    usuario = User.objects.get(username='49008382334')
    print(f"=== Teste Final - Usuário: {usuario.username} ===")
    
    # Verificar funções
    funcoes = UsuarioFuncao.objects.filter(usuario=usuario, status='ATIVO')
    print(f"Funções ativas: {funcoes.count()}")
    for funcao in funcoes:
        print(f"  - {funcao.cargo_funcao.nome}")
    
    # Testar lógica de permissão (igual à view)
    cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema']
    funcoes_ativas = funcoes.filter(cargo_funcao__nome__in=cargos_especiais)
    
    print(f"\nFunções especiais encontradas: {funcoes_ativas.count()}")
    for funcao in funcoes_ativas:
        print(f"  - {funcao.cargo_funcao.nome}")
    
    if usuario.is_superuser or usuario.is_staff:
        print("✅ Acesso total (superusuário/staff)")
        quadros = QuadroAcesso.objects.all()
    elif funcoes_ativas.exists():
        print("✅ Acesso total (função especial)")
        quadros = QuadroAcesso.objects.all()
    else:
        print("❌ Sem acesso")
        quadros = QuadroAcesso.objects.none()
    
    print(f"\nQuadros que este usuário pode ver: {quadros.count()}")
    
    if quadros.count() > 0:
        print("Quadros disponíveis:")
        for quadro in quadros:
            print(f"  - {quadro.numero} ({quadro.tipo} - {quadro.categoria})")

if __name__ == '__main__':
    teste_final() 