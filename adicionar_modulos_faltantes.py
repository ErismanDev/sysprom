#!/usr/bin/env python
"""
Script para adicionar módulos faltantes no sistema de permissões
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import PermissaoFuncao

def adicionar_modulos_faltantes():
    """Adiciona módulos faltantes ao sistema de permissões"""
    
    print("🔧 ADICIONANDO MÓDULOS FALTANTES AO SISTEMA")
    print("=" * 60)
    
    # Módulos atuais do sistema
    modulos_atuais = [
        'MILITARES',
        'FICHAS_CONCEITO', 
        'QUADROS_ACESSO',
        'PROMOCOES',
        'VAGAS',
        'COMISSAO',
        'DOCUMENTOS',
        'USUARIOS',
        'RELATORIOS',
        'CONFIGURACOES'
    ]
    
    # Módulos adicionais identificados no sistema
    modulos_adicionais = [
        'ALMANAQUES',           # Almanaques do sistema
        'CALENDARIOS',          # Calendários de promoções
        'NOTIFICACOES',         # Sistema de notificações
        'MODELOS_ATA',          # Modelos de ata
        'CARGOS_COMISSAO',      # Cargos da comissão
        'QUADROS_FIXACAO',      # Quadros de fixação de vagas
        'ASSINATURAS',          # Sistema de assinaturas
        'ESTATISTICAS',         # Estatísticas do sistema
        'EXPORTACAO',           # Exportação de dados
        'IMPORTACAO',           # Importação de dados
        'BACKUP',               # Backup do sistema
        'AUDITORIA',            # Logs de auditoria
        'DASHBOARD',            # Dashboard principal
        'BUSCA',                # Sistema de busca
        'AJAX',                 # Requisições AJAX
        'API',                  # APIs do sistema
        'SESSAO',               # Gestão de sessões
        'FUNCAO',               # Gestão de funções
        'PERFIL',               # Perfis de acesso
        'SISTEMA'               # Configurações do sistema
    ]
    
    # Todos os módulos
    todos_modulos = modulos_atuais + modulos_adicionais
    
    # Tipos de acesso
    tipos_acesso = [
        'VISUALIZAR',
        'CRIAR', 
        'EDITAR',
        'EXCLUIR',
        'APROVAR',
        'HOMOLOGAR',
        'GERAR_PDF',
        'IMPRIMIR',
        'ASSINAR',
        'ADMINISTRAR'
    ]
    
    print(f"📋 Módulos atuais: {len(modulos_atuais)}")
    for modulo in modulos_atuais:
        print(f"   - {modulo}")
    
    print(f"\n➕ Módulos adicionais: {len(modulos_adicionais)}")
    for modulo in modulos_adicionais:
        print(f"   - {modulo}")
    
    print(f"\n🎯 Total de módulos: {len(todos_modulos)}")
    print(f"🔑 Tipos de acesso: {len(tipos_acesso)}")
    print(f"📊 Total de combinações possíveis: {len(todos_modulos) * len(tipos_acesso)}")
    
    # Atualizar o modelo PermissaoFuncao
    print("\n🔄 Atualizando modelo PermissaoFuncao...")
    
    # Ler o arquivo models.py
    with open('militares/models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar e atualizar MODULOS_CHOICES
    modulos_choices_start = content.find("MODULOS_CHOICES = [")
    if modulos_choices_start != -1:
        # Encontrar o final da lista
        modulos_choices_end = content.find("]", modulos_choices_start)
        
        # Criar nova lista de módulos
        novos_modulos_choices = "MODULOS_CHOICES = [\n"
        for modulo in todos_modulos:
            nome_display = modulo.replace('_', ' ').title()
            novos_modulos_choices += f"        ('{modulo}', '{nome_display}'),\n"
        novos_modulos_choices += "    ]"
        
        # Substituir a lista antiga
        content = content[:modulos_choices_start] + novos_modulos_choices + content[modulos_choices_end+1:]
        
        print("✅ MODULOS_CHOICES atualizado")
    else:
        print("❌ MODULOS_CHOICES não encontrado")
    
    # Salvar o arquivo atualizado
    with open('militares/models.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Atualizar o arquivo de permissões do sistema
    print("\n🔄 Atualizando arquivo de permissões do sistema...")
    
    with open('militares/permissoes_sistema.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Atualizar a lista de módulos na função obter_permissoes_usuario
    modulos_list_start = content.find("modulos = [")
    if modulos_list_start != -1:
        modulos_list_end = content.find("]", modulos_list_start)
        
        novos_modulos_list = "modulos = [\n"
        for modulo in todos_modulos:
            novos_modulos_list += f"                '{modulo}',\n"
        novos_modulos_list += "            ]"
        
        content = content[:modulos_list_start] + novos_modulos_list + content[modulos_list_end+1:]
        
        print("✅ Lista de módulos atualizada")
    else:
        print("❌ Lista de módulos não encontrada")
    
    # Salvar o arquivo atualizado
    with open('militares/permissoes_sistema.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Atualizar o formulário de cargos
    print("\n🔄 Atualizando formulário de cargos...")
    
    with open('militares/forms.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Adicionar choices para novos módulos
    novos_choices = ""
    for modulo in modulos_adicionais:
        nome_display = modulo.replace('_', ' ').title()
        novos_choices += f"""
    {modulo}_CHOICES = [
        ('VISUALIZAR', 'Visualizar'),
        ('CRIAR', 'Criar'),
        ('EDITAR', 'Editar'),
        ('EXCLUIR', 'Excluir'),
        ('APROVAR', 'Aprovar'),
        ('HOMOLOGAR', 'Homologar'),
        ('GERAR_PDF', 'Gerar PDF'),
        ('IMPRIMIR', 'Imprimir'),
        ('ASSINAR', 'Assinar'),
        ('ADMINISTRAR', 'Administrar'),
    ]
"""
    
    # Encontrar onde adicionar os novos choices
    choices_end = content.find("    # Campos de permissões")
    if choices_end != -1:
        content = content[:choices_end] + novos_choices + content[choices_end:]
        print("✅ Choices adicionados")
    else:
        print("❌ Local para adicionar choices não encontrado")
    
    # Adicionar campos para novos módulos
    novos_campos = ""
    for modulo in modulos_adicionais:
        nome_display = modulo.replace('_', ' ').title()
        novos_campos += f"""
    permissoes_{modulo.lower()} = forms.MultipleChoiceField(
        choices={modulo}_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={{'class': 'form-check-input'}}),
        label='Permissões - {nome_display}'
    )
"""
    
    # Encontrar onde adicionar os novos campos
    campos_end = content.find("    class Meta:")
    if campos_end != -1:
        content = content[:campos_end] + novos_campos + content[campos_end:]
        print("✅ Campos adicionados")
    else:
        print("❌ Local para adicionar campos não encontrado")
    
    # Salvar o arquivo atualizado
    with open('militares/forms.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Criar migração para atualizar o banco
    print("\n🔄 Criando migração...")
    
    # Executar makemigrations
    os.system('python manage.py makemigrations militares --name adicionar_modulos_permissao')
    
    print("\n✅ Módulos adicionados com sucesso!")
    print("=" * 60)
    print("📋 Resumo das alterações:")
    print(f"   - Módulos adicionados: {len(modulos_adicionais)}")
    print(f"   - Total de módulos: {len(todos_modulos)}")
    print(f"   - Arquivos atualizados: models.py, permissoes_sistema.py, forms.py")
    print("\n🎯 Próximos passos:")
    print("   1. Execute: python manage.py migrate")
    print("   2. Execute: python manage.py runserver")
    print("   3. Acesse /militares/cargos/ para ver os novos módulos")
    print("   4. Teste marcando/desmarcando permissões")

if __name__ == "__main__":
    adicionar_modulos_faltantes() 