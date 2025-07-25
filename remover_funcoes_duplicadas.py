#!/usr/bin/env python
"""
Script para remover funções duplicadas (usuario, cargo_funcao, data_inicio) mantendo apenas uma
"""
import os
import django
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import UsuarioFuncao

def remover_duplicadas():
    print('🔍 Buscando funções duplicadas...')
    # Agrupar por (usuario, cargo_funcao, data_inicio)
    agrupados = defaultdict(list)
    for funcao in UsuarioFuncao.objects.all():
        chave = (funcao.usuario_id, funcao.cargo_funcao_id, funcao.data_inicio)
        agrupados[chave].append(funcao)
    total_removidos = 0
    for chave, funcoes in agrupados.items():
        if len(funcoes) > 1:
            # Mantém a primeira, remove as demais
            for funcao in funcoes[1:]:
                print(f'Removendo duplicada: usuario={funcao.usuario_id}, cargo={funcao.cargo_funcao_id}, data_inicio={funcao.data_inicio}, id={funcao.id}')
                funcao.delete()
                total_removidos += 1
    print(f'✅ Remoção concluída. Total de duplicadas removidas: {total_removidos}')

if __name__ == "__main__":
    remover_duplicadas() 