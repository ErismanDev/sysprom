#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Corrigir código duplicado no views.py
"""

def corrigir_duplicado():
    """Remove código duplicado no arquivo views.py"""
    
    print("🔧 Corrigindo código duplicado...")
    
    try:
        # Ler o arquivo
        with open('militares/views.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Fazer backup
        with open('militares/views.py.backup_duplicado', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("✅ Backup criado")
        
        # Remover linhas duplicadas
        new_lines = []
        skip = False
        
        for line in lines:
            # Se encontrar a linha problemática, começar a pular
            if 'hierarquia_postos.get(x.posto_graduacao, 999),' in line:
                skip = True
                continue
            
            # Se estiver pulando e encontrar o final do sorted, parar de pular
            if skip and 'x.nome_completo' in line:
                skip = False
                continue
            
            # Se estiver pulando, continuar pulando
            if skip:
                continue
            
            # Adicionar linha normal
            new_lines.append(line)
        
        # Salvar arquivo corrigido
        with open('militares/views.py', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print("✅ Código duplicado removido!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir: {e}")
        return False

if __name__ == '__main__':
    corrigir_duplicado() 