#!/usr/bin/env python
"""
Script para corrigir dados antes da importação para PostgreSQL
"""

import json
import re
from datetime import datetime

def corrigir_dados_importacao():
    """Corrige dados antes da importação"""
    
    print("🔧 Corrigindo dados para importação...")
    
    # Ler o arquivo original
    with open('dados_sqlite_utf8.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    dados_corrigidos = []
    problemas_encontrados = []
    
    for item in dados:
        try:
            # Verificar se é um militar
            if item['model'] == 'militares.militar':
                # Corrigir CPF se necessário
                if 'fields' in item and 'cpf' in item['fields']:
                    cpf = item['fields']['cpf']
                    
                    # Remover caracteres especiais e verificar tamanho
                    cpf_limpo = re.sub(r'[^\d]', '', str(cpf))
                    
                    if len(cpf_limpo) > 11:
                        problemas_encontrados.append(f"CPF muito longo: {cpf} -> {cpf_limpo[:11]}")
                        item['fields']['cpf'] = cpf_limpo[:11]
                    elif len(cpf_limpo) < 11:
                        problemas_encontrados.append(f"CPF muito curto: {cpf} -> {cpf_limpo.zfill(11)}")
                        item['fields']['cpf'] = cpf_limpo.zfill(11)
                    else:
                        item['fields']['cpf'] = cpf_limpo
            
            # Verificar outros campos que podem ter problemas
            if 'fields' in item:
                for campo, valor in item['fields'].items():
                    # Verificar campos de texto que podem estar muito longos
                    if isinstance(valor, str):
                        # Limitar tamanho de campos específicos
                        if campo == 'matricula' and len(valor) > 20:
                            item['fields'][campo] = valor[:20]
                            problemas_encontrados.append(f"Matrícula truncada: {valor} -> {valor[:20]}")
                        
                        elif campo == 'nome_completo' and len(valor) > 200:
                            item['fields'][campo] = valor[:200]
                            problemas_encontrados.append(f"Nome truncado: {valor} -> {valor[:200]}")
                        
                        elif campo == 'nome_guerra' and len(valor) > 100:
                            item['fields'][campo] = valor[:100]
                            problemas_encontrados.append(f"Nome de guerra truncado: {valor} -> {valor[:100]}")
                        
                        elif campo == 'email' and len(valor) > 254:
                            item['fields'][campo] = valor[:254]
                            problemas_encontrados.append(f"Email truncado: {valor} -> {valor[:254]}")
                        
                        elif campo == 'telefone' and len(valor) > 20:
                            item['fields'][campo] = valor[:20]
                            problemas_encontrados.append(f"Telefone truncado: {valor} -> {valor[:20]}")
                        
                        elif campo == 'celular' and len(valor) > 20:
                            item['fields'][campo] = valor[:20]
                            problemas_encontrados.append(f"Celular truncado: {valor} -> {valor[:20]}")
                        
                        elif campo == 'orgao_expedidor' and len(valor) > 20:
                            item['fields'][campo] = valor[:20]
                            problemas_encontrados.append(f"Órgão expedidor truncado: {valor} -> {valor[:20]}")
            
            dados_corrigidos.append(item)
            
        except Exception as e:
            problemas_encontrados.append(f"Erro ao processar item: {e}")
            continue
    
    # Salvar dados corrigidos
    nome_arquivo = f"dados_sqlite_corrigidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados_corrigidos, f, ensure_ascii=False, indent=2)
    
    # Salvar relatório de problemas
    relatorio_nome = f"relatorio_correcoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(relatorio_nome, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE CORREÇÕES DE DADOS\n")
        f.write("=" * 50 + "\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Total de itens originais: {len(dados)}\n")
        f.write(f"Total de itens corrigidos: {len(dados_corrigidos)}\n")
        f.write(f"Problemas encontrados: {len(problemas_encontrados)}\n\n")
        
        if problemas_encontrados:
            f.write("PROBLEMAS ENCONTRADOS:\n")
            f.write("-" * 30 + "\n")
            for problema in problemas_encontrados:
                f.write(f"- {problema}\n")
        else:
            f.write("Nenhum problema encontrado!\n")
    
    print(f"✅ Dados corrigidos salvos em: {nome_arquivo}")
    print(f"📋 Relatório salvo em: {relatorio_nome}")
    print(f"🔧 Problemas corrigidos: {len(problemas_encontrados)}")
    
    return nome_arquivo

if __name__ == "__main__":
    corrigir_dados_importacao() 