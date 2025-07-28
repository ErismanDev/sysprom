#!/usr/bin/env python
"""
Debug da senha do Supabase
"""

import urllib.parse

senha = "Erisman@193"
print(f"Senha original: {senha}")
print(f"Senha URL encoded: {urllib.parse.quote(senha)}")

# Testar diferentes variações
senhas_teste = [
    "Erisman@193",
    "Erisman%40193",
    "Erisman%40193",
    "Erisman193",
    "erisman193"
]

for i, senha_teste in enumerate(senhas_teste, 1):
    print(f"\nTeste {i}: {senha_teste}")
    url = f"postgresql://postgres:{senha_teste}@db.vubnekyyfjcrswaufnla.supabase.co:5432/postgres"
    print(f"URL: {url}") 