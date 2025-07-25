#!/usr/bin/env python
"""
Script para remover CPFs duplicados dos dados antes da importação
"""

import json
from datetime import datetime

def remover_duplicatas_cpf():
    """Remove CPFs duplicados dos dados"""
    
    print("🔧 Removendo CPFs duplicados...")
    
    # Ler o arquivo corrigido
    with open('dados_sqlite_corrigidos_20250722_154107.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Separar militares dos outros dados
    militares = []
    outros_dados = []
    cpfs_vistos = set()
    duplicatas_removidas = []
    
    for item in dados:
        if item['model'] == 'militares.militar':
            cpf = item['fields'].get('cpf', '')
            
            if cpf in cpfs_vistos:
                duplicatas_removidas.append(f"CPF duplicado removido: {cpf}")
                continue
            else:
                cpfs_vistos.add(cpf)
                militares.append(item)
        else:
            outros_dados.append(item)
    
    # Combinar dados únicos
    dados_unicos = militares + outros_dados
    
    # Salvar dados sem duplicatas
    nome_arquivo = f"dados_sqlite_sem_duplicatas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados_unicos, f, ensure_ascii=False, indent=2)
    
    # Salvar relatório
    relatorio_nome = f"relatorio_duplicatas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(relatorio_nome, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE REMOÇÃO DE DUPLICATAS\n")
        f.write("=" * 40 + "\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Total de itens originais: {len(dados)}\n")
        f.write(f"Militares únicos: {len(militares)}\n")
        f.write(f"Outros dados: {len(outros_dados)}\n")
        f.write(f"Total final: {len(dados_unicos)}\n")
        f.write(f"Duplicatas removidas: {len(duplicatas_removidas)}\n\n")
        
        if duplicatas_removidas:
            f.write("DUPLICATAS REMOVIDAS:\n")
            f.write("-" * 25 + "\n")
            for duplicata in duplicatas_removidas:
                f.write(f"- {duplicata}\n")
        else:
            f.write("Nenhuma duplicata encontrada!\n")
    
    print(f"✅ Dados sem duplicatas salvos em: {nome_arquivo}")
    print(f"📋 Relatório salvo em: {relatorio_nome}")
    print(f"🔧 Duplicatas removidas: {len(duplicatas_removidas)}")
    print(f"📊 Militares únicos: {len(militares)}")
    
    return nome_arquivo

if __name__ == "__main__":
    remover_duplicatas_cpf() 