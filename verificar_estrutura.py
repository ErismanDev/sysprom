import psycopg2

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'database': 'sepromcbmepi',
    'user': 'postgres',
    'password': '11322361',
    'port': '5432'
}

def verificar_estrutura():
    """Verifica a estrutura da tabela militares_militar"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Query para verificar campos com limite de tamanho
        query = """
        SELECT column_name, data_type, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = 'militares_militar' 
        AND character_maximum_length IS NOT NULL
        ORDER BY character_maximum_length, column_name;
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        print("Campos com limite de tamanho:")
        for row in resultados:
            print(f"- {row[0]}: {row[1]} (max: {row[2]})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    verificar_estrutura() 