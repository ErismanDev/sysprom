"""
Utilitários para migrações do Django
Funções helper para evitar erros comuns em migrações
"""


def remove_constraint_if_exists(schema_editor, table_name, constraint_name):
    """
    Remove uma constraint apenas se ela existir no banco de dados.
    
    Args:
        schema_editor: O schema editor do Django
        table_name: Nome da tabela (ex: 'militares_escalaservico')
        constraint_name: Nome da constraint a ser removida
    
    Returns:
        True se a constraint foi removida, False se não existia
    """
    with schema_editor.connection.cursor() as cursor:
        # Verificar se a constraint existe
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = %s 
            AND constraint_name = %s
            AND constraint_type IN ('UNIQUE', 'PRIMARY KEY', 'FOREIGN KEY', 'CHECK')
        """, [table_name, constraint_name])
        
        if cursor.fetchone():
            # Remover a constraint
            cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name};")
            return True
    return False


def safe_remove_constraint_migration(table_name, constraint_name):
    """
    Cria uma função de migração que remove uma constraint de forma segura.
    
    Args:
        table_name: Nome da tabela
        constraint_name: Nome da constraint
    
    Returns:
        Uma função que pode ser usada em migrations.RunPython
    """
    def remove_constraint(apps, schema_editor):
        remove_constraint_if_exists(schema_editor, table_name, constraint_name)
    
    return remove_constraint


def get_add_field_if_not_exists_sql(table_name, column_name, column_type="BOOLEAN", default_value="FALSE"):
    """
    Gera SQL para adicionar uma coluna apenas se ela não existir.
    
    Args:
        table_name: Nome da tabela (ex: 'militares_funcaomenuconfig')
        column_name: Nome da coluna a ser adicionada
        column_type: Tipo da coluna (padrão: 'BOOLEAN')
        default_value: Valor padrão (padrão: 'FALSE')
    
    Returns:
        String SQL que pode ser usada em migrations.RunSQL
    """
    return f"""
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='{table_name}' 
                       AND column_name='{column_name}') THEN
            ALTER TABLE {table_name} 
            ADD COLUMN {column_name} {column_type} DEFAULT {default_value};
        END IF;
    """


def get_add_fields_if_not_exists_sql(table_name, fields_config):
    """
    Gera SQL para adicionar múltiplas colunas apenas se elas não existirem.
    
    Args:
        table_name: Nome da tabela (ex: 'militares_funcaomenuconfig')
        fields_config: Lista de dicionários com configuração dos campos.
                      Cada dicionário deve ter: 'name', 'type' (opcional, padrão 'BOOLEAN'),
                      'default' (opcional, padrão 'FALSE')
    
    Returns:
        String SQL completa que pode ser usada em migrations.RunSQL
    
    Example:
        fields = [
            {'name': 'show_criar_ficha_conceito_oficial'},
            {'name': 'show_criar_ficha_conceito_praca'},
            {'name': 'valor_total', 'type': 'DECIMAL(12,2)', 'default': '0.00'}
        ]
        sql = get_add_fields_if_not_exists_sql('militares_funcaomenuconfig', fields)
    """
    sql_parts = []
    for field in fields_config:
        field_name = field['name']
        field_type = field.get('type', 'BOOLEAN')
        field_default = field.get('default', 'FALSE')
        
        sql_parts.append(f"""
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='{table_name}' 
                                   AND column_name='{field_name}') THEN
                        ALTER TABLE {table_name} 
                        ADD COLUMN {field_name} {field_type} DEFAULT {field_default};
                    END IF;""")
    
    return f"""
                DO $$ 
                BEGIN
                    {''.join(sql_parts)}
                END $$;
            """
