#!/usr/bin/env python
"""
Script para verificar todos os target="_blank" no sistema
e identificar quais devem ser mantidos (PDFs) e quais devem ser removidos
"""

import os
import re

def verificar_target_blank():
    """Verifica todos os target="_blank" nos templates"""
    
    # Diretórios para verificar
    diretorios = [
        'militares/templates',
        'templates'
    ]
    
    resultados = {
        'pdfs': [],  # target="_blank" que devem ser mantidos (PDFs)
        'outros': [],  # target="_blank" que devem ser removidos
        'total': 0
    }
    
    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            continue
            
        for root, dirs, files in os.walk(diretorio):
            for file in files:
                if file.endswith('.html'):
                    filepath = os.path.join(root, file)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Encontrar todos os target="_blank"
                        pattern = r'target="_blank"'
                        matches = re.finditer(pattern, content)
                        
                        for match in matches:
                            resultados['total'] += 1
                            
                            # Pegar o contexto ao redor do target="_blank"
                            start = max(0, match.start() - 200)
                            end = min(len(content), match.end() + 200)
                            context = content[start:end]
                            
                            # Verificar se é um PDF
                            is_pdf = False
                            if 'pdf' in context.lower() or 'file-pdf' in context.lower():
                                is_pdf = True
                            
                            info = {
                                'arquivo': filepath,
                                'linha': content[:match.start()].count('\n') + 1,
                                'contexto': context.strip(),
                                'is_pdf': is_pdf
                            }
                            
                            if is_pdf:
                                resultados['pdfs'].append(info)
                            else:
                                resultados['outros'].append(info)
                                
                    except Exception as e:
                        print(f"Erro ao ler {filepath}: {e}")
    
    return resultados

def main():
    print("🔍 Verificando target=\"_blank\" no sistema...")
    print("=" * 60)
    
    resultados = verificar_target_blank()
    
    print(f"📊 Total de target=\"_blank\" encontrados: {resultados['total']}")
    print(f"📄 PDFs (devem manter target=\"_blank\"): {len(resultados['pdfs'])}")
    print(f"🔗 Outros (devem remover target=\"_blank\"): {len(resultados['outros'])}")
    print()
    
    if resultados['outros']:
        print("❌ TARGET=\"_BLANK\" QUE DEVEM SER REMOVIDOS:")
        print("=" * 60)
        for i, item in enumerate(resultados['outros'], 1):
            print(f"{i}. {item['arquivo']} (linha {item['linha']})")
            print(f"   Contexto: {item['contexto'][:100]}...")
            print()
    
    if resultados['pdfs']:
        print("✅ TARGET=\"_BLANK\" QUE DEVEM SER MANTIDOS (PDFs):")
        print("=" * 60)
        for i, item in enumerate(resultados['pdfs'], 1):
            print(f"{i}. {item['arquivo']} (linha {item['linha']})")
            print(f"   Contexto: {item['contexto'][:100]}...")
            print()
    
    print("=" * 60)
    print("💡 RESUMO:")
    print(f"   - Total: {resultados['total']}")
    print(f"   - Manter (PDFs): {len(resultados['pdfs'])}")
    print(f"   - Remover: {len(resultados['outros'])}")
    
    if resultados['outros']:
        print("\n⚠️  ATENÇÃO: Existem target=\"_blank\" que devem ser removidos!")
        print("   Execute as correções necessárias para páginas HTML abrirem na mesma guia.")
    else:
        print("\n✅ PERFEITO! Todos os target=\"_blank\" são para PDFs.")

if __name__ == "__main__":
    main() 