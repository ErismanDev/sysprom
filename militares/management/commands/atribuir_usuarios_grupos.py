from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from militares.models import Militar


class Command(BaseCommand):
    help = 'Atribui usuários aos grupos de permissões simplificadas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Username do usuário a ser atribuído'
        )
        parser.add_argument(
            '--grupo',
            type=str,
            choices=['admin', 'superusuario', 'membro_cpo', 'membro_cpp', 
                    'comandante_geral', 'subcomandante_geral', 'diretor_gestao_pessoas',
                    'chefe_secao_promocoes', 'digitador', 'usuario'],
            help='Grupo ao qual atribuir o usuário'
        )
        parser.add_argument(
            '--listar',
            action='store_true',
            help='Lista todos os usuários e grupos disponíveis'
        )

    def handle(self, *args, **options):
        if options['listar']:
            self.listar_usuarios_grupos()
            return

        if not options['usuario'] or not options['grupo']:
            self.stdout.write(
                self.style.ERROR(
                    'Uso: python manage.py atribuir_usuarios_grupos --usuario USERNAME --grupo GRUPO\n'
                    'Para listar: python manage.py atribuir_usuarios_grupos --listar'
                )
            )
            return

        username = options['usuario']
        grupo_codigo = options['grupo']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário "{username}" não encontrado!')
            )
            return

        # Mapeamento de códigos para nomes de grupos
        grupos_nomes = {
            'admin': 'Administrador - Acesso total',
            'superusuario': 'Super Usuário - Acesso total',
            'membro_cpo': 'Membro CPO - Acesso a oficiais e comissões',
            'membro_cpp': 'Membro CPP - Acesso a praças e comissões',
            'comandante_geral': 'Comandante Geral - Acesso total exceto usuários e administração',
            'subcomandante_geral': 'Subcomandante Geral - Acesso total exceto usuários e administração',
            'diretor_gestao_pessoas': 'Diretor de Gestão de Pessoas - Acesso total exceto usuários e administração',
            'chefe_secao_promocoes': 'Chefe da Seção de Promoções - Acesso total exceto usuários e administração',
            'digitador': 'Digitador - Acesso total sem exclusão e sem usuários/administração',
            'usuario': 'Usuário - Acesso a documentos específicos e visualização'
        }

        try:
            grupo = Group.objects.get(name=grupos_nomes[grupo_codigo])
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Grupo "{grupos_nomes[grupo_codigo]}" não encontrado!')
            )
            return

        # Remover usuário de todos os grupos primeiro
        user.groups.clear()
        
        # Adicionar ao grupo especificado
        user.groups.add(grupo)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Usuário "{username}" atribuído ao grupo "{grupos_nomes[grupo_codigo]}"'
            )
        )

    def listar_usuarios_grupos(self):
        """Lista todos os usuários e grupos disponíveis"""
        self.stdout.write('\n📋 USUÁRIOS DISPONÍVEIS:')
        self.stdout.write('=' * 50)
        
        usuarios = User.objects.all().order_by('username')
        for user in usuarios:
            grupos = ', '.join([g.name for g in user.groups.all()]) or 'Nenhum grupo'
            status = '✅ Ativo' if user.is_active else '❌ Inativo'
            self.stdout.write(f'{user.username:<20} | {user.get_full_name():<30} | {status} | {grupos}')
        
        self.stdout.write('\n📋 GRUPOS DISPONÍVEIS:')
        self.stdout.write('=' * 50)
        
        grupos = Group.objects.all().order_by('name')
        for grupo in grupos:
            usuarios_count = grupo.user_set.count()
            self.stdout.write(f'{grupo.name:<50} | {usuarios_count} usuário(s)')
        
        self.stdout.write('\n📋 COMANDOS ÚTEIS:')
        self.stdout.write('=' * 50)
        self.stdout.write('• Atribuir usuário: python manage.py atribuir_usuarios_grupos --usuario USERNAME --grupo GRUPO')
        self.stdout.write('• Grupos disponíveis: admin, superusuario, membro_cpo, membro_cpp, comandante_geral, subcomandante_geral, diretor_gestao_pessoas, chefe_secao_promocoes, digitador, usuario')
        self.stdout.write('• Exemplo: python manage.py atribuir_usuarios_grupos --usuario joao.silva --grupo digitador') 