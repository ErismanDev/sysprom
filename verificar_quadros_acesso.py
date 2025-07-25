#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from militares.models import Militar, ComissaoPromocao, MembroComissao, UsuarioFuncao, CargoFuncao

def verificar_quadros_acesso():
    print("=== VERIFICAÇÃO DOS QUADROS DE ACESSO ===\n")
    
    try:
        # 1. Grupos do sistema
        print("🏛️ GRUPOS DO SISTEMA:")
        grupos = Group.objects.all()
        for grupo in grupos:
            membros = grupo.user_set.count()
            permissoes = grupo.permissions.count()
            print(f"   • {grupo.name}")
            print(f"     - Membros: {membros}")
            print(f"     - Permissões: {permissoes}")
        
        # 2. Usuários por grupo
        print(f"\n👥 USUÁRIOS POR GRUPO:")
        for grupo in grupos:
            usuarios = grupo.user_set.all()
            if usuarios:
                print(f"   • {grupo.name}:")
                for usuario in usuarios[:5]:  # Mostrar apenas os 5 primeiros
                    militar = Militar.objects.filter(user=usuario).first()
                    nome = militar.nome_guerra if militar else usuario.username
                    print(f"     - {nome} ({usuario.username})")
                if usuarios.count() > 5:
                    print(f"     ... e mais {usuarios.count() - 5} usuários")
        
        # 3. Permissões por grupo
        print(f"\n🔐 PERMISSÕES POR GRUPO:")
        for grupo in grupos:
            permissoes = grupo.permissions.all()
            if permissoes:
                print(f"   • {grupo.name}:")
                for permissao in permissoes[:10]:  # Mostrar apenas as 10 primeiras
                    print(f"     - {permissao.codename} ({permissao.content_type.app_label}.{permissao.content_type.model})")
                if permissoes.count() > 10:
                    print(f"     ... e mais {permissoes.count() - 10} permissões")
        
        # 4. Usuários com permissões especiais
        print(f"\n⭐ USUÁRIOS COM PERMISSÕES ESPECIAIS:")
        superusers = User.objects.filter(is_superuser=True)
        staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        
        if superusers:
            print(f"   • Superusuários ({superusers.count()}):")
            for user in superusers:
                militar = Militar.objects.filter(user=user).first()
                nome = militar.nome_guerra if militar else user.username
                print(f"     - {nome} ({user.username})")
        
        if staff_users:
            print(f"   • Staff (não superuser) ({staff_users.count()}):")
            for user in staff_users:
                militar = Militar.objects.filter(user=user).first()
                nome = militar.nome_guerra if militar else user.username
                print(f"     - {nome} ({user.username})")
        
        # 5. Usuários sem grupos
        usuarios_sem_grupos = User.objects.filter(groups__isnull=True)
        print(f"\n❌ USUÁRIOS SEM GRUPOS ({usuarios_sem_grupos.count()}):")
        for user in usuarios_sem_grupos[:10]:
            militar = Militar.objects.filter(user=user).first()
            nome = militar.nome_guerra if militar else user.username
            print(f"   • {nome} ({user.username})")
        if usuarios_sem_grupos.count() > 10:
            print(f"   ... e mais {usuarios_sem_grupos.count() - 10} usuários")
        
        # 6. Permissões por modelo
        print(f"\n📋 PERMISSÕES POR MODELO:")
        content_types = ContentType.objects.filter(app_label='militares')
        for ct in content_types:
            permissoes = Permission.objects.filter(content_type=ct)
            if permissoes:
                print(f"   • {ct.model}:")
                for permissao in permissoes:
                    grupos_com_permissao = permissao.group_set.count()
                    print(f"     - {permissao.codename}: {grupos_com_permissao} grupos")
        
        # 7. Resumo de acesso
        print(f"\n📊 RESUMO DE ACESSO:")
        total_usuarios = User.objects.count()
        usuarios_com_grupos = User.objects.filter(groups__isnull=False).distinct().count()
        usuarios_sem_grupos = User.objects.filter(groups__isnull=True).count()
        
        print(f"   • Total de usuários: {total_usuarios}")
        print(f"   • Usuários com grupos: {usuarios_com_grupos}")
        print(f"   • Usuários sem grupos: {usuarios_sem_grupos}")
        print(f"   • Superusuários: {superusers.count()}")
        print(f"   • Staff: {staff_users.count()}")
        
        # 8. Verificar permissões específicas das comissões
        print(f"\n🏛️ PERMISSÕES DAS COMISSÕES:")
        for comissao in ComissaoPromocao.objects.all():
            membros = MembroComissao.objects.filter(comissao=comissao, ativo=True)
            print(f"   • {comissao.nome}:")
            for membro in membros:
                grupos_usuario = membro.usuario.groups.all()
                funcoes = UsuarioFuncao.objects.filter(usuario=membro.usuario, status='ATIVO')
                print(f"     - {membro.militar.nome_guerra}:")
                print(f"       Grupos: {', '.join([g.name for g in grupos_usuario]) if grupos_usuario else 'Nenhum'}")
                print(f"       Funções: {', '.join([f.nome for f in funcoes]) if funcoes else 'Nenhuma'}")
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")

if __name__ == '__main__':
    verificar_quadros_acesso() 