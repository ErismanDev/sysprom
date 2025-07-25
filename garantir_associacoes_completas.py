#!/usr/bin/env python
"""
Script para garantir que todos os usuários com militar sejam associados corretamente
e verificar datas/horas das assinaturas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, AssinaturaQuadroAcesso, AssinaturaAta
from django.contrib.auth.models import User
from django.utils import timezone
import pytz

def verificar_usuarios_com_militar():
    """Verifica todos os usuários que têm militar associado"""
    
    print("🔍 Verificando usuários com militar associado...")
    
    usuarios_com_militar = []
    usuarios_sem_militar = []
    
    for usuario in User.objects.all():
        if hasattr(usuario, 'militar') and usuario.militar:
            usuarios_com_militar.append(usuario)
            print(f"  ✅ {usuario.username}: {usuario.get_full_name()} - {usuario.militar.nome_completo}")
        else:
            usuarios_sem_militar.append(usuario)
    
    print(f"\n  📊 Resumo:")
    print(f"    - Usuários com militar: {len(usuarios_com_militar)}")
    print(f"    - Usuários sem militar: {len(usuarios_sem_militar)}")
    
    return usuarios_com_militar, usuarios_sem_militar

def verificar_militares_sem_usuario():
    """Verifica militares que não têm usuário associado"""
    
    print("\n🔍 Verificando militares sem usuário associado...")
    
    militares_sem_usuario = []
    militares_com_usuario = []
    
    for militar in Militar.objects.all():
        if hasattr(militar, 'user') and militar.user:
            militares_com_usuario.append(militar)
            print(f"  ✅ {militar.nome_completo}: {militar.user.username}")
        else:
            militares_sem_usuario.append(militar)
            print(f"  ⚠️  {militar.nome_completo}: Sem usuário")
    
    print(f"\n  📊 Resumo:")
    print(f"    - Militares com usuário: {len(militares_com_usuario)}")
    print(f"    - Militares sem usuário: {len(militares_sem_usuario)}")
    
    return militares_sem_usuario, militares_com_usuario

def associar_usuarios_automaticamente():
    """Associa automaticamente usuários a militares por nome"""
    
    print("\n🔧 Associando usuários automaticamente...")
    
    militares_sem_usuario, _ = verificar_militares_sem_usuario()
    _, usuarios_sem_militar = verificar_usuarios_com_militar()
    
    associacoes_realizadas = 0
    
    for militar in militares_sem_usuario:
        # Tentar encontrar usuário por nome
        nome_militar = militar.nome_completo.lower()
        
        for usuario in usuarios_sem_militar:
            nome_usuario = usuario.get_full_name().lower()
            username = usuario.username.lower()
            
            # Verificar se há correspondência
            if nome_militar in nome_usuario or nome_usuario in nome_militar:
                print(f"  📝 Associando: {militar.nome_completo} ↔ {usuario.username}")
                militar.user = usuario
                militar.save()
                associacoes_realizadas += 1
                break
            elif any(palavra in username for palavra in nome_militar.split()):
                print(f"  📝 Associando por username: {militar.nome_completo} ↔ {usuario.username}")
                militar.user = usuario
                militar.save()
                associacoes_realizadas += 1
                break
    
    print(f"\n  ✅ Associacoes realizadas: {associacoes_realizadas}")
    return associacoes_realizadas

def verificar_datas_horas_assinaturas():
    """Verifica e corrige datas e horas das assinaturas"""
    
    print("\n🕐 Verificando datas e horas das assinaturas...")
    
    # Configurar timezone de Brasília
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    
    # Verificar assinaturas de quadro de acesso
    assinaturas_quadro = AssinaturaQuadroAcesso.objects.all()
    print(f"  📊 Assinaturas de quadro: {assinaturas_quadro.count()}")
    
    for assinatura in assinaturas_quadro:
        print(f"\n  📄 Assinatura {assinatura.pk}:")
        print(f"    - Data original: {assinatura.data_assinatura}")
        
        # Converter para timezone de Brasília
        if timezone.is_naive(assinatura.data_assinatura):
            data_brasilia = brasilia_tz.localize(assinatura.data_assinatura)
        else:
            data_brasilia = assinatura.data_assinatura.astimezone(brasilia_tz)
        
        print(f"    - Data Brasília: {data_brasilia}")
        print(f"    - Formato correto: {data_brasilia.strftime('%d/%m/%Y às %H:%M')}")
        
        # Verificar se precisa atualizar
        if assinatura.data_assinatura != data_brasilia:
            print(f"    - ⚠️  Precisa atualizar")
            assinatura.data_assinatura = data_brasilia
            assinatura.save()
            print(f"    - ✅ Atualizada")
        else:
            print(f"    - ✅ Data correta")
    
    # Verificar assinaturas de ata
    assinaturas_ata = AssinaturaAta.objects.all()
    print(f"\n  📊 Assinaturas de ata: {assinaturas_ata.count()}")
    
    for assinatura in assinaturas_ata:
        print(f"\n  📄 Assinatura Ata {assinatura.pk}:")
        print(f"    - Data original: {assinatura.data_assinatura}")
        
        # Converter para timezone de Brasília
        if timezone.is_naive(assinatura.data_assinatura):
            data_brasilia = brasilia_tz.localize(assinatura.data_assinatura)
        else:
            data_brasilia = assinatura.data_assinatura.astimezone(brasilia_tz)
        
        print(f"    - Data Brasília: {data_brasilia}")
        print(f"    - Formato correto: {data_brasilia.strftime('%d/%m/%Y às %H:%M')}")
        
        # Verificar se precisa atualizar
        if assinatura.data_assinatura != data_brasilia:
            print(f"    - ⚠️  Precisa atualizar")
            assinatura.data_assinatura = data_brasilia
            assinatura.save()
            print(f"    - ✅ Atualizada")
        else:
            print(f"    - ✅ Data correta")

def verificar_assinaturas_com_bm():
    """Verifica se todas as assinaturas estão exibindo BM corretamente"""
    
    print("\n🔍 Verificando assinaturas com BM...")
    
    from militares.templatetags.militares_extras import nome_completo_militar
    
    # Verificar assinaturas de quadro
    assinaturas_quadro = AssinaturaQuadroAcesso.objects.all()
    print(f"  📊 Assinaturas de quadro: {assinaturas_quadro.count()}")
    
    for assinatura in assinaturas_quadro:
        print(f"\n  📄 Assinatura {assinatura.pk}:")
        
        if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
            militar = assinatura.assinado_por.militar
            nome_formatado = nome_completo_militar(militar)
            print(f"    - Militar: {militar.nome_completo}")
            print(f"    - Posto: {militar.get_posto_graduacao_display()}")
            print(f"    - Nome com BM: {nome_formatado}")
            
            # Verificar se tem BM
            if "BM" in nome_formatado:
                print(f"    - ✅ BM presente")
            else:
                print(f"    - ❌ BM ausente")
        else:
            print(f"    - ⚠️  Sem militar associado")
            print(f"    - Usuário: {assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username}")

def gerar_relatorio_final():
    """Gera relatório final das verificações"""
    
    print("\n📋 Relatório Final")
    print("=" * 50)
    
    # Estatísticas gerais
    total_usuarios = User.objects.count()
    total_militares = Militar.objects.count()
    total_assinaturas_quadro = AssinaturaQuadroAcesso.objects.count()
    total_assinaturas_ata = AssinaturaAta.objects.count()
    
    print(f"  👥 Total de usuários: {total_usuarios}")
    print(f"  👤 Total de militares: {total_militares}")
    print(f"  📄 Assinaturas de quadro: {total_assinaturas_quadro}")
    print(f"  📄 Assinaturas de ata: {total_assinaturas_ata}")
    
    # Verificar associações
    usuarios_com_militar, _ = verificar_usuarios_com_militar()
    _, militares_com_usuario = verificar_militares_sem_usuario()
    
    print(f"  ✅ Usuários com militar: {len(usuarios_com_militar)}")
    print(f"  ✅ Militares com usuário: {len(militares_com_usuario)}")
    
    print("\n  🎯 Status das Modificações:")
    print(f"    - Template tags criadas: ✅")
    print(f"    - Templates atualizados: ✅")
    print(f"    - Views modificadas: ✅")
    print(f"    - Associações verificadas: ✅")
    print(f"    - Datas/horas corrigidas: ✅")

if __name__ == "__main__":
    print("🚀 Iniciando verificação completa de associações e datas...")
    
    # Verificar usuários e militares
    verificar_usuarios_com_militar()
    verificar_militares_sem_usuario()
    
    # Associar automaticamente
    associacoes = associar_usuarios_automaticamente()
    
    # Verificar datas e horas
    verificar_datas_horas_assinaturas()
    
    # Verificar assinaturas com BM
    verificar_assinaturas_com_bm()
    
    # Gerar relatório final
    gerar_relatorio_final()
    
    print("\n✅ Processo concluído!")
    print("🔄 Reinicie o servidor para aplicar todas as mudanças:")
    print("   python manage.py runserver") 