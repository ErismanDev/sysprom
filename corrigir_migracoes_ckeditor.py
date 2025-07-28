#!/usr/bin/env python3
"""
Script para corrigir migrações do CKEditor para django-ckeditor-5
"""

import os
import re
import glob

def corrigir_migracoes_ckeditor():
    """Corrige migrações que ainda usam ckeditor_uploader"""
    
    # Padrões para encontrar e substituir
    padroes = [
        (r'import ckeditor_uploader\.fields', 'from django_ckeditor_5.fields import CKEditor5Field'),
        (r'ckeditor_uploader\.fields\.RichTextUploadingField', 'CKEditor5Field'),
        (r'ckeditor_uploader\.fields\.RichTextField', 'CKEditor5Field'),
    ]
    
    # Encontrar todas as migrações
    migracoes = glob.glob('militares/migrations/*.py')
    
    corrigidas = 0
    
    for migracao in migracoes:
        if os.path.basename(migracao) == '__init__.py':
            continue
            
        try:
            with open(migracao, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            conteudo_original = conteudo
            
            # Aplicar correções
            for padrao, substituicao in padroes:
                conteudo = re.sub(padrao, substituicao, conteudo)
            
            # Se houve mudanças, salvar o arquivo
            if conteudo != conteudo_original:
                with open(migracao, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                print(f"✓ Corrigida: {migracao}")
                corrigidas += 1
                
        except Exception as e:
            print(f"✗ Erro ao processar {migracao}: {e}")
    
    print(f"\nTotal de migrações corrigidas: {corrigidas}")
    return corrigidas

def verificar_imports_ckeditor():
    """Verifica se há imports problemáticos nos modelos"""
    
    arquivos = [
        'militares/models.py',
        'militares/forms.py',
        'militares/admin.py'
    ]
    
    problemas = []
    
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                if 'ckeditor_uploader' in conteudo:
                    problemas.append(arquivo)
                    
            except Exception as e:
                print(f"Erro ao verificar {arquivo}: {e}")
    
    if problemas:
        print("⚠️  Arquivos com imports problemáticos do ckeditor_uploader:")
        for problema in problemas:
            print(f"   - {problema}")
    else:
        print("✓ Todos os arquivos estão usando django-ckeditor-5 corretamente")
    
    return problemas

if __name__ == '__main__':
    print("🔧 Corrigindo migrações do CKEditor...")
    print("=" * 50)
    
    # Verificar imports nos modelos
    problemas = verificar_imports_ckeditor()
    
    print("\n" + "=" * 50)
    
    # Corrigir migrações
    corrigidas = corrigir_migracoes_ckeditor()
    
    print("\n" + "=" * 50)
    
    if corrigidas > 0 or problemas:
        print("⚠️  Recomendações:")
        print("   1. Execute 'python manage.py makemigrations' para verificar")
        print("   2. Execute 'python manage.py migrate' para aplicar as mudanças")
        print("   3. Teste o sistema localmente antes do deploy")
    else:
        print("✅ Todas as migrações estão corretas!") 