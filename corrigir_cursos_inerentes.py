#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir automaticamente problemas com cursos inerentes
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def corrigir_cursos_inerentes():
    print("=== CORREÇÃO AUTOMÁTICA DE CURSOS INERENTES ===\n")
    militares = Militar.objects.filter(situacao='AT')
    print(f"Total de militares ativos: {militares.count()}")
    correcoes_aplicadas = 0
    for militar in militares:
        mudancas = []
        if militar.quadro == 'COMB':
            if militar.posto_graduacao in ['2T', '1T', 'CP', 'MJ', 'TC']:
                if not militar.curso_formacao_oficial:
                    militar.curso_formacao_oficial = True
                    mudancas.append("curso_formacao_oficial = True")
                if militar.posto_graduacao in ['CP', 'MJ', 'TC'] and not militar.curso_aperfeicoamento_oficial:
                    militar.curso_aperfeicoamento_oficial = True
                    mudancas.append("curso_aperfeicoamento_oficial = True")
                if militar.posto_graduacao == 'TC' and not militar.curso_csbm:
                    militar.curso_csbm = True
                    mudancas.append("curso_csbm = True")
        elif militar.quadro == 'SAUDE':
            if militar.posto_graduacao in ['2T', '1T', 'CP', 'MJ', 'TC']:
                if not militar.curso_formacao_oficial:
                    militar.curso_formacao_oficial = True
                    mudancas.append("curso_formacao_oficial = True")
                if militar.posto_graduacao in ['CP', 'MJ', 'TC'] and not militar.curso_aperfeicoamento_oficial:
                    militar.curso_aperfeicoamento_oficial = True
                    mudancas.append("curso_aperfeicoamento_oficial = True")
                if militar.posto_graduacao == 'TC' and not militar.curso_csbm:
                    militar.curso_csbm = True
                    mudancas.append("curso_csbm = True")
        elif militar.quadro == 'ENG':
            if militar.posto_graduacao == 'AS':
                if not militar.curso_adaptacao_oficial:
                    militar.curso_adaptacao_oficial = True
                    mudancas.append("curso_adaptacao_oficial = True")
            elif militar.posto_graduacao in ['2T', '1T', 'CP', 'MJ', 'TC']:
                if not militar.curso_formacao_oficial:
                    militar.curso_formacao_oficial = True
                    mudancas.append("curso_formacao_oficial = True")
                if militar.posto_graduacao in ['CP', 'MJ', 'TC'] and not militar.curso_aperfeicoamento_oficial:
                    militar.curso_aperfeicoamento_oficial = True
                    mudancas.append("curso_aperfeicoamento_oficial = True")
                if militar.posto_graduacao == 'TC' and not militar.curso_csbm:
                    militar.curso_csbm = True
                    mudancas.append("curso_csbm = True")
        elif militar.quadro == 'COMP':
            if militar.posto_graduacao in ['ST', '2T', '1T', 'CP', 'MJ', 'TC']:
                if not militar.curso_cho:
                    militar.curso_cho = True
                    mudancas.append("curso_cho = True")
                if militar.posto_graduacao in ['CP', 'MJ', 'TC'] and not militar.curso_superior:
                    militar.curso_superior = True
                    mudancas.append("curso_superior = True")
                if militar.posto_graduacao in ['MJ', 'TC'] and not militar.pos_graduacao:
                    militar.pos_graduacao = True
                    mudancas.append("pos_graduacao = True")
                if militar.posto_graduacao == 'TC' and not militar.curso_csbm:
                    militar.curso_csbm = True
                    mudancas.append("curso_csbm = True")
        if mudancas:
            militar.save()
            correcoes_aplicadas += 1
            print(f"{militar.nome_completo} ({militar.matricula}): {', '.join(mudancas)}")
    print(f"\nCorreções aplicadas: {correcoes_aplicadas}")
    print("\n✅ Correção concluída!")

if __name__ == "__main__":
    corrigir_cursos_inerentes() 