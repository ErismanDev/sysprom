from django.core.management.base import BaseCommand
from militares.models import PermissaoFuncao
from django.contrib.auth.models import Permission

class Command(BaseCommand):
    help = 'Aplica permissões padrão às funções existentes no sistema'

    def handle(self, *args, **options):
        # Definir permissões padrão para cada tipo de função
        PERMISSOES_PADRAO = {
            'Administrador': [
                ('USUARIOS', 'ADMINISTRAR'),
                ('MILITARES', 'ADMINISTRAR'),
                ('FICHAS_CONCEITO', 'ADMINISTRAR'),
                ('QUADROS_ACESSO', 'ADMINISTRAR'),
                ('PROMOCOES', 'ADMINISTRAR'),
                ('VAGAS', 'ADMINISTRAR'),
                ('COMISSAO', 'ADMINISTRAR'),
                ('DOCUMENTOS', 'ADMINISTRAR'),
                ('RELATORIOS', 'ADMINISTRAR'),
                ('CONFIGURACOES', 'ADMINISTRAR'),
            ],
            'Operador do Sistema': [
                ('MILITARES', 'CRIAR'),
                ('MILITARES', 'VISUALIZAR'),
                ('MILITARES', 'EDITAR'),
                ('MILITARES', 'EXCLUIR'),
                ('FICHAS_CONCEITO', 'CRIAR'),
                ('FICHAS_CONCEITO', 'VISUALIZAR'),
                ('FICHAS_CONCEITO', 'EDITAR'),
                ('FICHAS_CONCEITO', 'EXCLUIR'),
                ('QUADROS_ACESSO', 'EDITAR'),
                ('PROMOCOES', 'CRIAR'),
                ('PROMOCOES', 'VISUALIZAR'),
                ('PROMOCOES', 'EDITAR'),
                ('PROMOCOES', 'EXCLUIR'),
                ('VAGAS', 'EDITAR'),
                ('COMISSAO', 'EDITAR'),
                ('DOCUMENTOS', 'EDITAR'),
                ('RELATORIOS', 'EDITAR'),
                ('CONFIGURACOES', 'EDITAR'),
                ('CALENDARIOS', 'CRIAR'),
                ('CALENDARIOS', 'VISUALIZAR'),
                ('CALENDARIOS', 'EDITAR'),
                ('CALENDARIOS', 'EXCLUIR'),
            ],
            'Coordenador': [
                ('MILITARES', 'EDITAR'),
                ('FICHAS_CONCEITO', 'EDITAR'),
                ('QUADROS_ACESSO', 'EDITAR'),
                ('PROMOCOES', 'EDITAR'),
                ('VAGAS', 'EDITAR'),
                ('COMISSAO', 'EDITAR'),
                ('DOCUMENTOS', 'EDITAR'),
                ('RELATORIOS', 'VISUALIZAR'),
            ],
            'Secretário': [
                ('MILITARES', 'CRIAR'),
                ('FICHAS_CONCEITO', 'CRIAR'),
                ('QUADROS_ACESSO', 'VISUALIZAR'),
                ('PROMOCOES', 'VISUALIZAR'),
                ('VAGAS', 'VISUALIZAR'),
                ('COMISSAO', 'VISUALIZAR'),
                ('DOCUMENTOS', 'CRIAR'),
                ('RELATORIOS', 'VISUALIZAR'),
            ],
            'Membro da Comissão': [
                ('MILITARES', 'VISUALIZAR'),
                ('FICHAS_CONCEITO', 'VISUALIZAR'),
                ('QUADROS_ACESSO', 'VISUALIZAR'),
                ('PROMOCOES', 'VISUALIZAR'),
                ('VAGAS', 'VISUALIZAR'),
                ('COMISSAO', 'VISUALIZAR'),
                ('DOCUMENTOS', 'VISUALIZAR'),
            ],
        }

        for cargo in FuncaoMilitar.objects.all():
            # Limpar permissões existentes
            PermissaoFuncao.objects.filter(funcao_militar=cargo).delete()
            
            # Aplicar permissões padrão baseadas no nome da função
            permissoes_a_aplicar = []
            for nome_funcao, permissoes in PERMISSOES_PADRAO.items():
                if nome_funcao.lower() in cargo.nome.lower():
                    permissoes_a_aplicar = permissoes
                    break
            
            # Se não encontrou correspondência, aplicar permissões básicas
            if not permissoes_a_aplicar:
                permissoes_a_aplicar = [
                    ('MILITARES', 'VISUALIZAR'),
                    ('DOCUMENTOS', 'VISUALIZAR'),
                ]
            
            # Criar permissões para a função
            for modulo, acesso in permissoes_a_aplicar:
                PermissaoFuncao.objects.create(
                    funcao_militar=cargo,
                    modulo=modulo,
                    acesso=acesso,
                    observacoes=f'Permissão padrão aplicada automaticamente'
                )
                self.stdout.write(f'Permissão "{modulo} - {acesso}" adicionada à função "{cargo.nome}"')
            
            self.stdout.write(
                self.style.SUCCESS(f'Função "{cargo.nome}" configurada com {len(permissoes_a_aplicar)} permissões')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Permissões padrão aplicadas com sucesso!')
        ) 