import json

try:
    with open('backups/backup_completo_20250724_130613.json', 'r', encoding='utf-16') as f:
        data = json.load(f)
    
    print(f"Tipo de dados: {type(data)}")
    
    if isinstance(data, dict):
        print(f"Total de modelos: {len(data)}")
        
        # Procurar por modelos de militares
        militares = []
        usuarios = []
        
        for key in data.keys():
            if 'militar' in key.lower():
                militares.append(key)
            elif 'user' in key.lower():
                usuarios.append(key)
        
        print(f"\nModelos de militares encontrados:")
        for m in militares:
            print(f"  {m}: {len(data[m])} registros")
        
        print(f"\nModelos de usuários encontrados:")
        for u in usuarios:
            print(f"  {u}: {len(data[u])} registros")
    
    elif isinstance(data, list):
        print(f"Total de itens na lista: {len(data)}")
        if len(data) > 0:
            print(f"Primeiro item: {type(data[0])}")
            if isinstance(data[0], dict):
                print(f"Chaves do primeiro item: {list(data[0].keys())}")
        
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc() 