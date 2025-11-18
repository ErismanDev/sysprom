# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0228_add_missing_fields_to_escalamilitar'),
    ]

    operations = [
        # Verificar e adicionar campos apenas se não existirem
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                -- show_escalas
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'militares_funcaomenuconfig' 
                    AND column_name = 'show_escalas'
                ) THEN
                    ALTER TABLE militares_funcaomenuconfig ADD COLUMN show_escalas BOOLEAN DEFAULT FALSE;
                END IF;
                
                -- show_escalas_dashboard
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'militares_funcaomenuconfig' 
                    AND column_name = 'show_escalas_dashboard'
                ) THEN
                    ALTER TABLE militares_funcaomenuconfig ADD COLUMN show_escalas_dashboard BOOLEAN DEFAULT FALSE;
                END IF;
                
                -- show_escalas_lista
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'militares_funcaomenuconfig' 
                    AND column_name = 'show_escalas_lista'
                ) THEN
                    ALTER TABLE militares_funcaomenuconfig ADD COLUMN show_escalas_lista BOOLEAN DEFAULT FALSE;
                END IF;
                
                -- show_escalas_configuracao
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'militares_funcaomenuconfig' 
                    AND column_name = 'show_escalas_configuracao'
                ) THEN
                    ALTER TABLE militares_funcaomenuconfig ADD COLUMN show_escalas_configuracao BOOLEAN DEFAULT FALSE;
                END IF;
                
                -- show_escalas_banco_horas
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'militares_funcaomenuconfig' 
                    AND column_name = 'show_escalas_banco_horas'
                ) THEN
                    ALTER TABLE militares_funcaomenuconfig ADD COLUMN show_escalas_banco_horas BOOLEAN DEFAULT FALSE;
                END IF;
                
                -- show_escalas_operacoes
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'militares_funcaomenuconfig' 
                    AND column_name = 'show_escalas_operacoes'
                ) THEN
                    ALTER TABLE militares_funcaomenuconfig ADD COLUMN show_escalas_operacoes BOOLEAN DEFAULT FALSE;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
