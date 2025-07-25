#!/usr/bin/env python
"""
Script para testar a busca AJAX de militares
"""
import requests
import json

def test_ajax_search():
    """Testa a busca AJAX de militares"""
    
    # URL base do servidor
    base_url = "http://127.0.0.1:8000"
    
    # URL da busca AJAX
    search_url = f"{base_url}/militares/busca-militares/"
    
    # Parâmetros de teste
    test_queries = ["João", "Silva", "123", "TC"]
    
    print("🔍 Testando busca AJAX de militares...")
    print(f"🌐 URL: {search_url}")
    print("-" * 50)
    
    for query in test_queries:
        print(f"\n📝 Testando query: '{query}'")
        
        try:
            # Fazer requisição GET
            response = requests.get(
                search_url,
                params={'q': query},
                headers={
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                },
                timeout=10
            )
            
            print(f"📡 Status Code: {response.status_code}")
            print(f"📡 Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Resposta JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    if 'results' in data:
                        print(f"👥 Militares encontrados: {len(data['results'])}")
                        for i, militar in enumerate(data['results'], 1):
                            print(f"  {i}. {militar.get('nome', 'N/A')} ({militar.get('posto', 'N/A')})")
                    else:
                        print("⚠️ Campo 'results' não encontrado na resposta")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Erro ao decodificar JSON: {e}")
                    print(f"📄 Resposta bruta: {response.text}")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                print(f"📄 Resposta: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")

if __name__ == "__main__":
    test_ajax_search() 