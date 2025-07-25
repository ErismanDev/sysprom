from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.db import transaction

class Command(BaseCommand):
    help = 'Traduz as permissões do Django para português brasileiro'

    def handle(self, *args, **options):
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
            'Can add Assinatura da Ata': 'Pode adicionar assinatura da ata',
            'Can change Assinatura da Ata': 'Pode alterar assinatura da ata',
            'Can delete Assinatura da Ata': 'Pode excluir assinatura da ata',
            'Can view Assinatura da Ata': 'Pode visualizar assinatura da ata',
            
            # Militares - Quadro de Acesso
            'Can add quadro de acesso': 'Pode adicionar quadro de acesso',
            'Can change quadro de acesso': 'Pode alterar quadro de acesso',
            'Can delete quadro de acesso': 'Pode excluir quadro de acesso',
            'Can view quadro de acesso': 'Pode visualizar quadro de acesso',
            
            # Militares - Assinatura do Quadro de Acesso
            'Can add Assinatura do Quadro de Acesso': 'Pode adicionar assinatura do quadro de acesso',
            'Can change Assinatura do Quadro de Acesso': 'Pode alterar assinatura do quadro de acesso',
            'Can delete Assinatura do Quadro de Acesso': 'Pode excluir assinatura do quadro de acesso',
            'Can view Assinatura do Quadro de Acesso': 'Pode visualizar assinatura do quadro de acesso',
            
            # Militares - Assinatura do Quadro de Fixação de Vagas
            'Can add Assinatura do Quadro de Fixação de Vagas': 'Pode adicionar assinatura do quadro de fixação de vagas',
            'Can change Assinatura do Quadro de Fixação de Vagas': 'Pode alterar assinatura do quadro de fixação de vagas',
            'Can delete Assinatura do Quadro de Fixação de Vagas': 'Pode excluir assinatura do quadro de fixação de vagas',
            'Can view Assinatura do Quadro de Fixação de Vagas': 'Pode visualizar assinatura do quadro de fixação de vagas',
            
            # Militares - Ata da Sessão
            'Can add ata da sessão': 'Pode adicionar ata da sessão',
            'Can change ata da sessão': 'Pode alterar ata da sessão',
            'Can delete ata da sessão': 'Pode excluir ata da sessão',
            'Can view ata da sessão': 'Pode visualizar ata da sessão',
            'Can add Ata da Sessão': 'Pode adicionar ata da sessão',
            'Can change Ata da Sessão': 'Pode alterar ata da sessão',
            'Can delete Ata da Sessão': 'Pode excluir ata da sessão',
            'Can view Ata da Sessão': 'Pode visualizar ata da sessão',
            
            # Militares - Documento da Sessão
            'Can add documento da sessão': 'Pode adicionar documento da sessão',
            'Can change documento da sessão': 'Pode alterar documento da sessão',
            'Can delete documento da sessão': 'Pode excluir documento da sessão',
            'Can view documento da sessão': 'Pode visualizar documento da sessão',
            'Can add Documento da Sessão': 'Pode adicionar documento da sessão',
            'Can change Documento da Sessão': 'Pode alterar documento da sessão',
            'Can delete Documento da Sessão': 'Pode excluir documento da sessão',
            'Can view Documento da Sessão': 'Pode visualizar documento da sessão',
            
            # Militares - Cargo da Comissão
            'Can add cargo da comissão': 'Pode adicionar cargo da comissão',
            'Can change cargo da comissão': 'Pode alterar cargo da comissão',
            'Can delete cargo da comissão': 'Pode excluir cargo da comissão',
            'Can view cargo da comissão': 'Pode visualizar cargo da comissão',
            'Can add Cargo da Comissão': 'Pode adicionar cargo da comissão',
            'Can change Cargo da Comissão': 'Pode alterar cargo da comissão',
            'Can delete Cargo da Comissão': 'Pode excluir cargo da comissão',
            'Can view Cargo da Comissão': 'Pode visualizar cargo da comissão',
            
            # Militares - Cargo/Função do Sistema
            'Can add Cargo/Função do Sistema': 'Pode adicionar cargo/função do sistema',
            'Can change Cargo/Função do Sistema': 'Pode alterar cargo/função do sistema',
            'Can delete Cargo/Função do Sistema': 'Pode excluir cargo/função do sistema',
            'Can view Cargo/Função do Sistema': 'Pode visualizar cargo/função do sistema',
            
            # Militares - Comissão de Promoções
            'Can add Comissão de Promoções': 'Pode adicionar comissão de promoções',
            'Can change Comissão de Promoções': 'Pode alterar comissão de promoções',
            'Can delete Comissão de Promoções': 'Pode excluir comissão de promoções',
            'Can view Comissão de Promoções': 'Pode visualizar comissão de promoções',
            'Can add Comissão de Promoção': 'Pode adicionar comissão de promoção',
            'Can change Comissão de Promoção': 'Pode alterar comissão de promoção',
            'Can delete Comissão de Promoção': 'Pode excluir comissão de promoção',
            'Can view Comissão de Promoção': 'Pode visualizar comissão de promoção',
            
            # Militares - Comissão de Promoções de Oficiais
            'Can add Comissão de Promoções de Oficiais': 'Pode adicionar comissão de promoções de oficiais',
            'Can change Comissão de Promoções de Oficiais': 'Pode alterar comissão de promoções de oficiais',
            'Can delete Comissão de Promoções de Oficiais': 'Pode excluir comissão de promoções de oficiais',
            'Can view Comissão de Promoções de Oficiais': 'Pode visualizar comissão de promoções de oficiais',
            'Can add Comissão de Promoção de Oficiais': 'Pode adicionar comissão de promoção de oficiais',
            'Can change Comissão de Promoção de Oficiais': 'Pode alterar comissão de promoção de oficiais',
            'Can delete Comissão de Promoção de Oficiais': 'Pode excluir comissão de promoção de oficiais',
            'Can view Comissão de Promoção de Oficiais': 'Pode visualizar comissão de promoção de oficiais',
            
            # Militares - Deliberação da Comissão
            'Can add deliberação da comissão': 'Pode adicionar deliberação da comissão',
            'Can change deliberação da comissão': 'Pode alterar deliberação da comissão',
            'Can delete deliberação da comissão': 'Pode excluir deliberação da comissão',
            'Can view deliberação da comissão': 'Pode visualizar deliberação da comissão',
            'Can add Deliberação da Comissão': 'Pode adicionar deliberação da comissão',
            'Can change Deliberação da Comissão': 'Pode alterar deliberação da comissão',
            'Can delete Deliberação da Comissão': 'Pode excluir deliberação da comissão',
            'Can view Deliberação da Comissão': 'Pode visualizar deliberação da comissão',
            
            # Militares - Curso
            'Can add curso': 'Pode adicionar curso',
            'Can change curso': 'Pode alterar curso',
            'Can delete curso': 'Pode excluir curso',
            'Can view curso': 'Pode visualizar curso',
            'Can add Curso': 'Pode adicionar curso',
            'Can change Curso': 'Pode alterar curso',
            'Can delete Curso': 'Pode excluir curso',
            'Can view Curso': 'Pode visualizar curso',
            
            # Militares - Ficha de Conceito
            'Can add ficha de conceito': 'Pode adicionar ficha de conceito',
            'Can change ficha de conceito': 'Pode alterar ficha de conceito',
            'Can delete ficha de conceito': 'Pode excluir ficha de conceito',
            'Can view ficha de conceito': 'Pode visualizar ficha de conceito',
            'Can add Ficha de Conceito': 'Pode adicionar ficha de conceito',
            'Can change Ficha de Conceito': 'Pode alterar ficha de conceito',
            'Can delete Ficha de Conceito': 'Pode excluir ficha de conceito',
            'Can view Ficha de Conceito': 'Pode visualizar ficha de conceito',
            
            # Militares - Ficha de Conceito de Oficiais
            'Can add ficha de conceito de oficiais': 'Pode adicionar ficha de conceito de oficiais',
            'Can change ficha de conceito de oficiais': 'Pode alterar ficha de conceito de oficiais',
            'Can delete ficha de conceito de oficiais': 'Pode excluir ficha de conceito de oficiais',
            'Can view ficha de conceito de oficiais': 'Pode visualizar ficha de conceito de oficiais',
            'Can add Ficha de Conceito de Oficiais': 'Pode adicionar ficha de conceito de oficiais',
            'Can change Ficha de Conceito de Oficiais': 'Pode alterar ficha de conceito de oficiais',
            'Can delete Ficha de Conceito de Oficiais': 'Pode excluir ficha de conceito de oficiais',
            'Can view Ficha de Conceito de Oficiais': 'Pode visualizar ficha de conceito de oficiais',
            
            # Militares - Ficha de Conceito de Praças
            'Can add ficha de conceito de praças': 'Pode adicionar ficha de conceito de praças',
            'Can change ficha de conceito de praças': 'Pode alterar ficha de conceito de praças',
            'Can delete ficha de conceito de praças': 'Pode excluir ficha de conceito de praças',
            'Can view ficha de conceito de praças': 'Pode visualizar ficha de conceito de praças',
            'Can add Ficha de Conceito de Praças': 'Pode adicionar ficha de conceito de praças',
            'Can change Ficha de Conceito de Praças': 'Pode alterar ficha de conceito de praças',
            'Can delete Ficha de Conceito de Praças': 'Pode excluir ficha de conceito de praças',
            'Can view Ficha de Conceito de Praças': 'Pode visualizar ficha de conceito de praças',
            
            # Militares - Interstício
            'Can add interstício': 'Pode adicionar interstício',
            'Can change interstício': 'Pode alterar interstício',
            'Can delete interstício': 'Pode excluir interstício',
            'Can view interstício': 'Pode visualizar interstício',
            'Can add Interstício': 'Pode adicionar interstício',
            'Can change Interstício': 'Pode alterar interstício',
            'Can delete Interstício': 'Pode excluir interstício',
            'Can view Interstício': 'Pode visualizar interstício',
            
            # Militares - Item do Quadro de Acesso
            'Can add item do quadro de acesso': 'Pode adicionar item do quadro de acesso',
            'Can change item do quadro de acesso': 'Pode alterar item do quadro de acesso',
            'Can delete item do quadro de acesso': 'Pode excluir item do quadro de acesso',
            'Can view item do quadro de acesso': 'Pode visualizar item do quadro de acesso',
            'Can add Item do Quadro de Acesso': 'Pode adicionar item do quadro de acesso',
            'Can change Item do Quadro de Acesso': 'Pode alterar item do quadro de acesso',
            'Can delete Item do Quadro de Acesso': 'Pode excluir item do quadro de acesso',
            'Can view Item do Quadro de Acesso': 'Pode visualizar item do quadro de acesso',
            
            # Militares - Item do Quadro de Fixação de Vagas
            'Can add item do quadro de fixação de vagas': 'Pode adicionar item do quadro de fixação de vagas',
            'Can change item do quadro de fixação de vagas': 'Pode alterar item do quadro de fixação de vagas',
            'Can delete item do quadro de fixação de vagas': 'Pode excluir item do quadro de fixação de vagas',
            'Can view item do quadro de fixação de vagas': 'Pode visualizar item do quadro de fixação de vagas',
            'Can add Item do Quadro de Fixação de Vagas': 'Pode adicionar item do quadro de fixação de vagas',
            'Can change Item do Quadro de Fixação de Vagas': 'Pode alterar item do quadro de fixação de vagas',
            'Can delete Item do Quadro de Fixação de Vagas': 'Pode excluir item do quadro de fixação de vagas',
            'Can view Item do Quadro de Fixação de Vagas': 'Pode visualizar item do quadro de fixação de vagas',
            
            # Militares - Justificativa de Encerramento
            'Can add justificativa de encerramento': 'Pode adicionar justificativa de encerramento',
            'Can change justificativa de encerramento': 'Pode alterar justificativa de encerramento',
            'Can delete justificativa de encerramento': 'Pode excluir justificativa de encerramento',
            'Can view justificativa de encerramento': 'Pode visualizar justificativa de encerramento',
            'Can add Justificativa de Encerramento': 'Pode adicionar justificativa de encerramento',
            'Can change Justificativa de Encerramento': 'Pode alterar justificativa de encerramento',
            'Can delete Justificativa de Encerramento': 'Pode excluir justificativa de encerramento',
            'Can view Justificativa de Encerramento': 'Pode visualizar justificativa de encerramento',
            
            # Militares - Medalha/Condecoração
            'Can add medalha/condecoração': 'Pode adicionar medalha/condecoração',
            'Can change medalha/condecoração': 'Pode alterar medalha/condecoração',
            'Can delete medalha/condecoração': 'Pode excluir medalha/condecoração',
            'Can view medalha/condecoração': 'Pode visualizar medalha/condecoração',
            'Can add Medalha/Condecoração': 'Pode adicionar medalha/condecoração',
            'Can change Medalha/Condecoração': 'Pode alterar medalha/condecoração',
            'Can delete Medalha/Condecoração': 'Pode excluir medalha/condecoração',
            'Can view Medalha/Condecoração': 'Pode visualizar medalha/condecoração',
            
            # Militares - Quadro de Fixação de Vagas
            'Can add quadro de fixação de vagas': 'Pode adicionar quadro de fixação de vagas',
            'Can change quadro de fixação de vagas': 'Pode alterar quadro de fixação de vagas',
            'Can delete quadro de fixação de vagas': 'Pode excluir quadro de fixação de vagas',
            'Can view quadro de fixação de vagas': 'Pode visualizar quadro de fixação de vagas',
            'Can add Quadro de Fixação de Vagas': 'Pode adicionar quadro de fixação de vagas',
            'Can change Quadro de Fixação de Vagas': 'Pode alterar quadro de fixação de vagas',
            'Can delete Quadro de Fixação de Vagas': 'Pode excluir quadro de fixação de vagas',
            'Can view Quadro de Fixação de Vagas': 'Pode visualizar quadro de fixação de vagas',
            
            # Militares - Perfil de Acesso
            'Can add Perfil de Acesso': 'Pode adicionar perfil de acesso',
            'Can change Perfil de Acesso': 'Pode alterar perfil de acesso',
            'Can delete Perfil de Acesso': 'Pode excluir perfil de acesso',
            'Can view Perfil de Acesso': 'Pode visualizar perfil de acesso',
            
            # Militares - Permissão de Função
            'Can add Permissão de Função': 'Pode adicionar permissão de função',
            'Can change Permissão de Função': 'Pode alterar permissão de função',
            'Can delete Permissão de Função': 'Pode excluir permissão de função',
            'Can view Permissão de Função': 'Pode visualizar permissão de função',
            
            # Militares - Usuário Função
            'Can add Usuário Função': 'Pode adicionar usuário função',
            'Can change Usuário Função': 'Pode alterar usuário função',
            'Can delete Usuário Função': 'Pode excluir usuário função',
            'Can view Usuário Função': 'Pode visualizar usuário função',
        }

        with transaction.atomic():
            for perm in Permission.objects.all():
                if perm.name in TRADUCOES:
                    perm.name = TRADUCOES[perm.name]
                    perm.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Traduzido: {perm.name}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS('Tradução de permissões concluída!')
        ) 