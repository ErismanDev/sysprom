#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, ItemQuadroAcesso

def verificar_debug():
    """Verifica se a lógica de debug está sendo executada"""
    
    try:
        quadro = QuadroAcesso.objects.get(pk=367)
        print(f"=== Quadro 367 ===")
        print(f"Tipo: {quadro.tipo}")
        
        # Simular a lógica do PDF
        if quadro.tipo == 'MERECIMENTO':
            print("✅ Quadro é do tipo MERECIMENTO")
            
            # Buscar militares como no PDF
            todos_militares = quadro.itemquadroacesso_set.all()
            
            # Testar uma transição
            aptos = todos_militares.filter(
                militar__posto_graduacao='MJ'
            ).order_by('posicao')
            
            print(f"Militares aptos para MJ: {aptos.count()}")
            
            if aptos.exists():
                print("✅ Militares encontrados - bloco de tabela será executado")
                
                # Simular criação da tabela
                header_data = [['ORD', 'IDENT.', 'POSTO', 'NOME', 'PONTUAÇÃO']]
                header_data.append(['DEBUG', 'MERECIMENTO', '', '', ''])
                
                print("✅ Linha DEBUG adicionada à tabela")
                print(f"Header data: {header_data}")
                
                for idx, item in enumerate(aptos, 1):
                    pontuacao_str = f"{item.pontuacao:.2f}" if item.pontuacao else "-"
                    print(f"  {idx}. {item.militar.nome_completo}: {pontuacao_str}")
            else:
                print("❌ Nenhum militar apto encontrado")
        else:
            print(f"❌ Quadro NÃO é do tipo MERECIMENTO, é: {quadro.tipo}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    verificar_debug() 