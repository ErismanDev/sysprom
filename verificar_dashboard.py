#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import *
from django.db.models import Q, Count
from datetime import date

def verificar_dashboard():
    print("=== VERIFICANDO DADOS DO DASHBOARD ===\n")
    
    try:
        # 1. Dados básicos
        total_militares = Militar.objects.count()
        militares_ativos = Militar.objects.filter(situacao='AT').count()
        militares_inativos = total_militares - militares_ativos
        
        print(f"📊 Total de militares: {total_militares}")
        print(f"📊 Militares ativos: {militares_ativos}")
        print(f"📊 Militares inativos: {militares_inativos}")
        
        # 2. Fichas de conceito
        militares_com_ficha = Militar.objects.filter(
            Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
        ).distinct().count()
        
        militares_sem_ficha = militares_ativos - militares_com_ficha
        
        print(f"\n📋 Militares com ficha: {militares_com_ficha}")
        print(f"📋 Militares sem ficha: {militares_sem_ficha}")
        
        # 3. Documentos
        documentos_pendentes = Documento.objects.filter(status='PENDENTE').count()
        total_documentos = Documento.objects.count()
        
        print(f"\n📄 Documentos pendentes: {documentos_pendentes}")
        print(f"📄 Total de documentos: {total_documentos}")
        
        # 4. Quadros de acesso
        total_quadros = QuadroAcesso.objects.count()
        print(f"\n📋 Total de quadros de acesso: {total_quadros}")
        
        # 5. Notificações
        total_notificacoes = NotificacaoSessao.objects.filter(lida=False).count()
        notificacoes_urgentes = NotificacaoSessao.objects.filter(lida=False, prioridade='URGENTE').count()
        
        print(f"\n🔔 Total de notificações não lidas: {total_notificacoes}")
        print(f"🔔 Notificações urgentes: {notificacoes_urgentes}")
        
        # 6. Militares aptos a quadro
        hoje = date.today()
        intersticios_minimos = {
            '2T': 2, '1T': 3, 'CP': 4, 'MJ': 4, 'TC': 4,
            'ST': 3, '1S': 3, '2S': 3, '3S': 3, 'CAB': 2,
        }
        
        militares_aptos_candidatos = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=intersticios_minimos.keys()
        ).filter(
            Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
        ).distinct()
        
        militares_aptos_por_posto = {}
        for militar in militares_aptos_candidatos:
            posto = militar.posto_graduacao
            if posto in intersticios_minimos:
                anos_no_posto = (hoje - militar.data_promocao_atual).days / 365.25
                if anos_no_posto >= intersticios_minimos[posto]:
                    if posto not in militares_aptos_por_posto:
                        militares_aptos_por_posto[posto] = 0
                    militares_aptos_por_posto[posto] += 1
        
        total_aptos = sum(militares_aptos_por_posto.values())
        print(f"\n✅ Total de militares aptos a quadro: {total_aptos}")
        
        for posto, total in militares_aptos_por_posto.items():
            print(f"   {posto}: {total}")
        
        # 7. Estatísticas por quadro
        print(f"\n📊 Estatísticas por quadro:")
        estatisticas_quadro = Militar.objects.filter(situacao='AT').values('quadro').annotate(
            total=Count('id')
        ).order_by('quadro')
        
        for stat in estatisticas_quadro:
            print(f"   {stat['quadro']}: {stat['total']}")
        
        # 8. Estatísticas por posto
        print(f"\n📊 Estatísticas por posto:")
        estatisticas_posto = Militar.objects.filter(situacao='AT').values('posto_graduacao').annotate(
            total=Count('id')
        ).order_by('posto_graduacao')
        
        for stat in estatisticas_posto:
            print(f"   {stat['posto_graduacao']}: {stat['total']}")
        
        # 9. Documentos por status
        print(f"\n📄 Documentos por status:")
        documentos_por_status = Documento.objects.values('status').annotate(
            total=Count('id')
        ).order_by('status')
        
        for stat in documentos_por_status:
            print(f"   {stat['status']}: {stat['total']}")
        
        # 10. Verificar se há dados recentes
        print(f"\n🕒 Dados recentes:")
        documentos_recentes = Documento.objects.select_related('militar').order_by('-data_upload')[:5]
        print(f"   Documentos recentes: {documentos_recentes.count()}")
        
        quadros_recentes = QuadroAcesso.objects.all().order_by('-data_criacao')[:5]
        print(f"   Quadros recentes: {quadros_recentes.count()}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    verificar_dashboard() 