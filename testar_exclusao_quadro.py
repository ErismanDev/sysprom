#!/usr/bin/env python
"""
Script para testar a exclusão de quadros de fixação de vagas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import QuadroFixacaoVagas, UsuarioFuncao

def testar_exclusao_quadro(quadro_id, username):
    """Testa a exclusão de um quadro específico"""
    print(f"🧪 TESTANDO EXCLUSÃO DO QUADRO ID: {quadro_id}")
    print("=" * 60)
    
    try:
        # Buscar o usuário
        usuario = User.objects.get(username=username)
        print(f"👤 Usuário: {usuario.get_full_name()} ({usuario.username})")
        
        # Buscar o quadro
        quadro = QuadroFixacaoVagas.objects.get(pk=quadro_id)
        print(f"📋 Quadro: {quadro.titulo} (ID: {quadro.pk})")
        print(f"   Tipo: {quadro.tipo}")
        print(f"   Status: {quadro.status}")
        
        # Verificar permissões do usuário
        print(f"\n🔐 VERIFICANDO PERMISSÕES:")
        
        # Verificar se é superusuário
        eh_superuser = usuario.is_superuser
        print(f"   É superusuário: {eh_superuser}")
        
        # Verificar se é staff
        eh_staff = usuario.is_staff
        print(f"   É staff: {eh_staff}")
        
        # Verificar cargos especiais
        cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        funcoes_especiais = UsuarioFuncao.objects.filter(
            usuario=usuario,
            status='ATIVO',
            cargo_funcao__nome__in=cargos_especiais
        )
        tem_cargo_especial = funcoes_especiais.exists()
        print(f"   Tem cargo especial: {tem_cargo_especial}")
        
        if funcoes_especiais.exists():
            for funcao in funcoes_especiais:
                print(f"     - {funcao.cargo_funcao.nome}")
        
        # Verificar se deveria ter acesso
        deveria_ter_acesso = eh_superuser or eh_staff or tem_cargo_especial
        print(f"   Deveria ter acesso: {deveria_ter_acesso}")
        
        if not deveria_ter_acesso:
            print("   ❌ PROBLEMA: Usuário não tem permissão!")
            return False
        
        # Simular a exclusão
        print(f"\n🗑️ SIMULANDO EXCLUSÃO:")
        try:
            # Verificar se o quadro existe antes
            quadro_existe = QuadroFixacaoVagas.objects.filter(pk=quadro_id).exists()
            print(f"   Quadro existe antes da exclusão: {quadro_existe}")
            
            if quadro_existe:
                # Tentar excluir
                quadro.delete()
                print("   ✅ Quadro excluído com sucesso!")
                
                # Verificar se foi realmente excluído
                quadro_existe_depois = QuadroFixacaoVagas.objects.filter(pk=quadro_id).exists()
                print(f"   Quadro existe depois da exclusão: {quadro_existe_depois}")
                
                if not quadro_existe_depois:
                    print("   ✅ Confirmação: Quadro foi realmente excluído!")
                    return True
                else:
                    print("   ❌ PROBLEMA: Quadro não foi excluído!")
                    return False
            else:
                print("   ❌ PROBLEMA: Quadro não encontrado!")
                return False
                
        except Exception as e:
            print(f"   ❌ ERRO na exclusão: {str(e)}")
            return False
            
    except User.DoesNotExist:
        print(f"❌ Usuário '{username}' não encontrado!")
        return False
    except QuadroFixacaoVagas.DoesNotExist:
        print(f"❌ Quadro com ID {quadro_id} não encontrado!")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

def listar_quadros_disponiveis():
    """Lista todos os quadros disponíveis"""
    print(f"\n📋 QUADROS DISPONÍVEIS PARA TESTE:")
    print("=" * 60)
    
    quadros = QuadroFixacaoVagas.objects.all().order_by('-data_criacao')
    
    if quadros.exists():
        for quadro in quadros:
            print(f"   • ID {quadro.pk}: {quadro.titulo} ({quadro.tipo}) - {quadro.status}")
    else:
        print("   Nenhum quadro encontrado")
    
    return quadros

def main():
    print("🧪 TESTADOR DE EXCLUSÃO DE QUADROS")
    print("=" * 70)
    
    # Listar quadros disponíveis
    quadros = listar_quadros_disponiveis()
    
    if not quadros.exists():
        print("❌ Nenhum quadro disponível para teste!")
        return
    
    # Solicitar dados do teste
    try:
        quadro_id = int(input("\nDigite o ID do quadro para testar: "))
        username = input("Digite o username do usuário: ").strip()
        
        if not username:
            print("❌ Username não informado!")
            return
        
        # Executar teste
        sucesso = testar_exclusao_quadro(quadro_id, username)
        
        print(f"\n" + "=" * 70)
        if sucesso:
            print("✅ TESTE CONCLUÍDO COM SUCESSO!")
            print("   A exclusão funcionou corretamente.")
        else:
            print("❌ TESTE FALHOU!")
            print("   Verifique as permissões e tente novamente.")
            
    except ValueError:
        print("❌ ID do quadro deve ser um número!")
    except KeyboardInterrupt:
        print("\n\n⏹️ Teste interrompido pelo usuário.")

if __name__ == "__main__":
    main() 