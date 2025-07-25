import os
import sys
import django

# Configurar Django ANTES de importar os modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

# Mapeamento de permissões para português
TRADUCOES = {
    # Usuários e Grupos
    'Can add user': 'Pode adicionar usuário',
    'Can change user': 'Pode alterar usuário', 
    'Can delete user': 'Pode excluir usuário',
    'Can view user': 'Pode visualizar usuário',
    'Can add group': 'Pode adicionar grupo',
    'Can change group': 'Pode alterar grupo',
    'Can delete group': 'Pode excluir grupo', 
    'Can view group': 'Pode visualizar grupo',
    'Can add permission': 'Pode adicionar permissão',
    'Can change permission': 'Pode alterar permissão',
    'Can delete permission': 'Pode excluir permissão',
    'Can view permission': 'Pode visualizar permissão',
    
    # Logs
    'Can add log entry': 'Pode adicionar entrada de log',
    'Can change log entry': 'Pode alterar entrada de log',
    'Can delete log entry': 'Pode excluir entrada de log',
    'Can view log entry': 'Pode visualizar entrada de log',
    
    # Content Types
    'Can add content type': 'Pode adicionar tipo de conteúdo',
    'Can change content type': 'Pode alterar tipo de conteúdo',
    'Can delete content type': 'Pode excluir tipo de conteúdo',
    'Can view content type': 'Pode visualizar tipo de conteúdo',
    
    # Militares - Documentos
    'Can add documento': 'Pode adicionar documento',
    'Can change documento': 'Pode alterar documento',
    'Can delete documento': 'Pode excluir documento',
    'Can view documento': 'Pode visualizar documento',
    
    # Militares - Assinatura da Ata
    'Can add assinatura da ata': 'Pode adicionar assinatura da ata',
    'Can change assinatura da ata': 'Pode alterar assinatura da ata',
    'Can delete assinatura da ata': 'Pode excluir assinatura da ata',
    'Can view assinatura da ata': 'Pode visualizar assinatura da ata',
    
    # Militares - Quadro de Acesso
    'Can add quadro de acesso': 'Pode adicionar quadro de acesso',
    'Can change quadro de acesso': 'Pode alterar quadro de acesso',
    'Can delete quadro de acesso': 'Pode excluir quadro de acesso',
    'Can view quadro de acesso': 'Pode visualizar quadro de acesso',
    
    # Militares - Ata da Sessão
    'Can add ata da sessão': 'Pode adicionar ata da sessão',
    'Can change ata da sessão': 'Pode alterar ata da sessão',
    'Can delete ata da sessão': 'Pode excluir ata da sessão',
    'Can view ata da sessão': 'Pode visualizar ata da sessão',
    
    # Militares - Documento da Sessão
    'Can add documento da sessão': 'Pode adicionar documento da sessão',
    'Can change documento da sessão': 'Pode alterar documento da sessão',
    'Can delete documento da sessão': 'Pode excluir documento da sessão',
    'Can view documento da sessão': 'Pode visualizar documento da sessão',
    
    # Militares - Cargo da Comissão
    'Can add cargo da comissão': 'Pode adicionar cargo da comissão',
    'Can change cargo da comissão': 'Pode alterar cargo da comissão',
    'Can delete cargo da comissão': 'Pode excluir cargo da comissão',
    'Can view cargo da comissão': 'Pode visualizar cargo da comissão',
    
    # Militares - Comissão de Promoções
    'Can add comissão de promoções': 'Pode adicionar comissão de promoções',
    'Can change comissão de promoções': 'Pode alterar comissão de promoções',
    'Can delete comissão de promoções': 'Pode excluir comissão de promoções',
    'Can view comissão de promoções': 'Pode visualizar comissão de promoções',
    
    # Militares - Comissão de Promoções de Oficiais
    'Can add comissão de promoções de oficiais': 'Pode adicionar comissão de promoções de oficiais',
    'Can change comissão de promoções de oficiais': 'Pode alterar comissão de promoções de oficiais',
    'Can delete comissão de promoções de oficiais': 'Pode excluir comissão de promoções de oficiais',
    'Can view comissão de promoções de oficiais': 'Pode visualizar comissão de promoções de oficiais',
    
    # Militares - Deliberação da Comissão
    'Can add deliberação da comissão': 'Pode adicionar deliberação da comissão',
    'Can change deliberação da comissão': 'Pode alterar deliberação da comissão',
    'Can delete deliberação da comissão': 'Pode excluir deliberação da comissão',
    'Can view deliberação da comissão': 'Pode visualizar deliberação da comissão',
    
    # Militares - Curso
    'Can add curso': 'Pode adicionar curso',
    'Can change curso': 'Pode alterar curso',
    'Can delete curso': 'Pode excluir curso',
    'Can view curso': 'Pode visualizar curso',
    
    # Militares - Ficha de Conceito
    'Can add ficha de conceito': 'Pode adicionar ficha de conceito',
    'Can change ficha de conceito': 'Pode alterar ficha de conceito',
    'Can delete ficha de conceito': 'Pode excluir ficha de conceito',
    'Can view ficha de conceito': 'Pode visualizar ficha de conceito',
    
    # Militares - Ficha de Conceito de Oficiais
    'Can add ficha de conceito de oficiais': 'Pode adicionar ficha de conceito de oficiais',
    'Can change ficha de conceito de oficiais': 'Pode alterar ficha de conceito de oficiais',
    'Can delete ficha de conceito de oficiais': 'Pode excluir ficha de conceito de oficiais',
    'Can view ficha de conceito de oficiais': 'Pode visualizar ficha de conceito de oficiais',
    
    # Militares - Ficha de Conceito de Praças
    'Can add ficha de conceito de praças': 'Pode adicionar ficha de conceito de praças',
    'Can change ficha de conceito de praças': 'Pode alterar ficha de conceito de praças',
    'Can delete ficha de conceito de praças': 'Pode excluir ficha de conceito de praças',
    'Can view ficha de conceito de praças': 'Pode visualizar ficha de conceito de praças',
    
    # Militares - Interstício
    'Can add interstício': 'Pode adicionar interstício',
    'Can change interstício': 'Pode alterar interstício',
    'Can delete interstício': 'Pode excluir interstício',
    'Can view interstício': 'Pode visualizar interstício',
    
    # Militares - Item do Quadro de Acesso
    'Can add item do quadro de acesso': 'Pode adicionar item do quadro de acesso',
    'Can change item do quadro de acesso': 'Pode alterar item do quadro de acesso',
    'Can delete item do quadro de acesso': 'Pode excluir item do quadro de acesso',
    'Can view item do quadro de acesso': 'Pode visualizar item do quadro de acesso',
    
    # Militares - Item do Quadro de Fixação de Vagas
    'Can add item do quadro de fixação de vagas': 'Pode adicionar item do quadro de fixação de vagas',
    'Can change item do quadro de fixação de vagas': 'Pode alterar item do quadro de fixação de vagas',
    'Can delete item do quadro de fixação de vagas': 'Pode excluir item do quadro de fixação de vagas',
    'Can view item do quadro de fixação de vagas': 'Pode visualizar item do quadro de fixação de vagas',
    
    # Militares - Justificativa de Encerramento
    'Can add justificativa de encerramento': 'Pode adicionar justificativa de encerramento',
    'Can change justificativa de encerramento': 'Pode alterar justificativa de encerramento',
    'Can delete justificativa de encerramento': 'Pode excluir justificativa de encerramento',
    'Can view justificativa de encerramento': 'Pode visualizar justificativa de encerramento',
    
    # Militares - Medalha/Condecoração
    'Can add medalha/condecoração': 'Pode adicionar medalha/condecoração',
    'Can change medalha/condecoração': 'Pode alterar medalha/condecoração',
    'Can delete medalha/condecoração': 'Pode excluir medalha/condecoração',
    'Can view medalha/condecoração': 'Pode visualizar medalha/condecoração',
    
    # Militares - Quadro de Fixação de Vagas
    'Can add quadro de fixação de vagas': 'Pode adicionar quadro de fixação de vagas',
    'Can change quadro de fixação de vagas': 'Pode alterar quadro de fixação de vagas',
    'Can delete quadro de fixação de vagas': 'Pode excluir quadro de fixação de vagas',
    'Can view quadro de fixação de vagas': 'Pode visualizar quadro de fixação de vagas',
}

def traduzir_permissoes():
    """Traduz as permissões do Django para português brasileiro"""
    with transaction.atomic():
        for perm in Permission.objects.all():
            if perm.name in TRADUCOES:
                perm.name = TRADUCOES[perm.name]
                perm.save()
                print(f'Traduzido: {perm.name}')
    
    print('Tradução concluída!')

if __name__ == '__main__':
    traduzir_permissoes() 