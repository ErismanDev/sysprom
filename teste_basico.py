#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste básico de conectividade
"""

import socket
import ssl

def testar_conectividade():
    """Testa conectividade básica com o host"""
    
    host = 'db.vubnekyyfjcrswaufnla.supabase.co'
    port = 5432
    
    print(f"Testando conectividade com {host}:{port}")
    
    try:
        # Teste básico de socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        print("Tentando conectar via socket...")
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print("SUCESSO: Socket conectado!")
            sock.close()
            return True
        else:
            print(f"ERRO: Socket falhou com código {result}")
            sock.close()
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

if __name__ == "__main__":
    testar_conectividade() 