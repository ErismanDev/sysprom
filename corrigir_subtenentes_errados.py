#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

# Encontrar subtenentes no quadro Combatente
errados = Militar.objects.filter(posto_graduacao='ST', quadro='COMB')
print(f"Encontrados {errados.count()} subtenentes no quadro Combatente.")

for st in errados:
    print(f"Corrigindo: {st.nome_completo} (matrícula: {st.matricula})")
    st.quadro = 'COMP'  # Corrigindo para Complementar
    st.save()
print("Correção concluída.") 