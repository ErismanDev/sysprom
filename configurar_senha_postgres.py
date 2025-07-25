#!/usr/bin/env python
"""
Script para configurar a senha do PostgreSQL no settings.py
"""

import re

def configurar_senha():
    """Configura a senha do PostgreSQL no settings.py"""
    
    print("🔧 Configuração da Senha PostgreSQL")
    print("=" * 40)
    
    # Ler o arquivo settings.py
    with open('sepromcbmepi/settings.py', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Encontrar a linha com a senha
    padrao = r'("PASSWORD":\s*)"[^"]*"'
    match = re.search(padrao, conteudo)
    
    if match:
        print("📝 Senha atual encontrada no settings.py")
        print("💡 Digite a senha que você definiu durante a instalação do PostgreSQL:")
        
        senha = input("Senha: ").strip()
        
        if senha:
            # Substituir a senha
            nova_senha = f'{match.group(1)}"{senha}"'
            novo_conteudo = re.sub(padrao, nova_senha, conteudo)
            
            # Salvar o arquivo
            with open('sepromcbmepi/settings.py', 'w', encoding='utf-8') as f:
                f.write(novo_conteudo)
            
            print("✅ Senha atualizada com sucesso!")
            print("🔄 Agora você pode executar: python manage.py migrate")
        else:
            print("❌ Senha não pode estar vazia")
    else:
        print("❌ Configuração de senha não encontrada no settings.py")

if __name__ == "__main__":
    configurar_senha() 