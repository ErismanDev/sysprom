import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.forms import UsuarioForm
from militares.models import CargoFuncao

# Verificar se há cargos/funções cadastrados
cargos = CargoFuncao.objects.filter(ativo=True).order_by('nome')
print(f"Total de cargos/funções ativos: {cargos.count()}")
for cargo in cargos:
    print(f"- {cargo.nome} (ID: {cargo.id})")

# Criar formulário e verificar o campo
form = UsuarioForm()
print(f"\nCampo cargo_funcao existe: {'cargo_funcao' in form.fields}")
if 'cargo_funcao' in form.fields:
    campo = form.fields['cargo_funcao']
    print(f"Tipo do campo: {type(campo)}")
    print(f"Label: {campo.label}")
    print(f"Required: {campo.required}")
    print(f"Widget: {campo.widget}")
    print(f"Choices disponíveis: {len(campo.choices)}")
    for choice in campo.choices[:5]:  # Mostrar apenas os primeiros 5
        print(f"  - {choice}")

# Verificar se o campo está sendo renderizado
html = form['cargo_funcao'].as_widget()
print(f"\nHTML do campo:")
print(html) 