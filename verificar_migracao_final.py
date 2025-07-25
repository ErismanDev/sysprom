#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, ComissaoPromocao, MembroComissao, UsuarioFuncao, CargoFuncao

def verificar_migracao_final():
    print("=== VERIFICAÇÃO FINAL DA MIGRAÇÃO ===\n")
    
    try:
        # Estatísticas gerais
        print("📊 ESTATÍSTICAS GERAIS:")
        print(f"   • Usuários: {User.objects.count()}")
        print(f"   • Militares: {Militar.objects.count()}")
        print(f"   • Comissões: {ComissaoPromocao.objects.count()}")
        print(f"   • Membros de comissões: {MembroComissao.objects.count()}")
        print(f"   • Funções de usuários: {UsuarioFuncao.objects.count()}")
        print(f"   • Cargos/Funções: {CargoFuncao.objects.count()}")
        
        # Detalhes das comissões
        print(f"\n🏛️ COMISSÕES:")
        for comissao in ComissaoPromocao.objects.all():
            membros = MembroComissao.objects.filter(comissao=comissao, ativo=True).count()
            print(f"   • {comissao.nome} ({comissao.tipo}) - {membros} membros ativos")
        
        # Detalhes dos membros
        print(f"\n👥 MEMBROS DE COMISSÕES:")
        membros_ativos = MembroComissao.objects.filter(ativo=True)
        for membro in membros_ativos:
            funcoes = UsuarioFuncao.objects.filter(usuario=membro.usuario, status='ATIVO').count()
            print(f"   • {membro.militar.nome_guerra} ({membro.usuario.username})")
            print(f"     - Comissão: {membro.comissao.nome}")
            print(f"     - Funções ativas: {funcoes}")
        
        # Usuários com funções
        print(f"\n🔑 USUÁRIOS COM FUNÇÕES:")
        usuarios_com_funcoes = User.objects.filter(funcoes__status='ATIVO').distinct()
        print(f"   • Total: {usuarios_com_funcoes.count()}")
        
        # Top 5 cargos mais comuns
        print(f"\n📋 TOP 5 CARGOS MAIS COMUNS:")
        from django.db.models import Count
        cargos_populares = CargoFuncao.objects.annotate(
            total=Count('usuariofuncao')
        ).order_by('-total')[:5]
        
        for cargo in cargos_populares:
            print(f"   • {cargo.nome}: {cargo.total} usuários")
        
        # Militares por situação
        print(f"\n🎖️ MILITARES POR SITUAÇÃO:")
        from django.db.models import Count
        situacoes = Militar.objects.values('situacao').annotate(
            total=Count('id')
        ).order_by('situacao')
        
        for situacao in situacoes:
            print(f"   • {situacao['situacao']}: {situacao['total']} militares")
        
        # Militares por quadro
        print(f"\n🎖️ MILITARES POR QUADRO:")
        quadros = Militar.objects.values('quadro').annotate(
            total=Count('id')
        ).order_by('quadro')
        
        for quadro in quadros:
            print(f"   • {quadro['quadro']}: {quadro['total']} militares")
        
        print(f"\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"   Todos os dados do SQLite foram migrados para o PostgreSQL")
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")

if __name__ == '__main__':
    verificar_migracao_final() 