from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from militares.models import Militar


class Command(BaseCommand):
    help = 'Configura permissões simplificadas do sistema'

    def handle(self, *args, **options):
        self.stdout.write('Configurando permissões simplificadas...')
        
        with transaction.atomic():
            # Limpar grupos existentes
            Group.objects.all().delete()
            self.stdout.write('✓ Grupos existentes removidos')
            
            # Criar grupos
            grupos = {
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
            
            grupos_criados = {}
            for codigo, nome in grupos.items():
                grupo, created = Group.objects.get_or_create(name=codigo)
                grupo.name = nome
                grupo.save()
                grupos_criados[codigo] = grupo
                self.stdout.write(f'✓ Grupo "{nome}" criado')
            
            # Obter content types
            content_types = ContentType.objects.all()
            
            # Permissões por grupo
            permissoes_grupos = {
                'admin': {
                    'description': 'Acesso total ao sistema',
                    'permissions': ['add', 'change', 'delete', 'view'],
                    'models': ['user', 'group', 'permission', 'militar', 'fichaconceito', 'quadroacesso', 
                              'promocao', 'comissao', 'sessaocomissao', 'membrocomissao', 'deliberacaocomissao',
                              'documentosessao', 'atasessao', 'modeloata', 'notificacaosessao', 'intersticio',
                              'previsaovaga', 'quadrofixacaovagas', 'cargocomissao', 'votodeliberacao',
                              'presencasessao', 'justificativaencerramento', 'assinaturaata']
                },
                'superusuario': {
                    'description': 'Acesso total ao sistema',
                    'permissions': ['add', 'change', 'delete', 'view'],
                    'models': ['user', 'group', 'permission', 'militar', 'fichaconceito', 'quadroacesso', 
                              'promocao', 'comissao', 'sessaocomissao', 'membrocomissao', 'deliberacaocomissao',
                              'documentosessao', 'atasessao', 'modeloata', 'notificacaosessao', 'intersticio',
                              'previsaovaga', 'quadrofixacaovagas', 'cargocomissao', 'votodeliberacao',
                              'presencasessao', 'justificativaencerramento', 'assinaturaata']
                },
                'membro_cpo': {
                    'description': 'Acesso a oficiais e comissões relacionadas',
                    'permissions': ['add', 'change', 'delete', 'view'],
                    'models': ['militar', 'fichaconceito', 'comissao', 'sessaocomissao', 'membrocomissao', 
                              'deliberacaocomissao', 'documentosessao', 'atasessao', 'modeloata', 
                              'votodeliberacao', 'presencasessao', 'justificativaencerramento', 
                              'assinaturaata', 'cargocomissao', 'notificacaosessao']
                },
                'membro_cpp': {
                    'description': 'Acesso a praças e comissões relacionadas',
                    'permissions': ['add', 'change', 'delete', 'view'],
                    'models': ['militar', 'fichaconceito', 'comissao', 'sessaocomissao', 'membrocomissao', 
                              'deliberacaocomissao', 'documentosessao', 'atasessao', 'modeloata', 
                              'votodeliberacao', 'presencasessao', 'justificativaencerramento', 
                              'assinaturaata', 'cargocomissao', 'notificacaosessao']
                },
                'comandante_geral': {
                    'description': 'Acesso total exceto usuários e administração',
                    'permissions': ['add', 'change', 'delete', 'view'],
                    'models': ['militar', 'fichaconceito', 'quadroacesso', 'promocao', 'comissao', 
                              'sessaocomissao', 'membrocomissao', 'deliberacaocomissao', 'documentosessao', 
                              'atasessao', 'modeloata', 'notificacaosessao', 'intersticio', 'previsaovaga', 
                              'quadrofixacaovagas', 'cargocomissao', 'votodeliberacao', 'presencasessao', 
                              'justificativaencerramento', 'assinaturaata']
                },
                'subcomandante_geral': {
                    'description': 'Acesso total exceto usuários e administração',
                    'permissions': ['add', 'change', 'delete', 'view'],
                    'models': ['militar', 'fichaconceito', 'quadroacesso', 'promocao', 'comissao', 
                              'sessaocomissao', 'membrocomissao', 'deliberacaocomissao', 'documentosessao', 
                              'atasessao', 'modeloata', 'notificacaosessao', 'intersticio', 'previsaovaga', 
                              'quadrofixacaovagas', 'cargocomissao', 'votodeliberacao', 'presencasessao', 
                              'justificativaencerramento', 'assinaturaata']
                },
                'diretor_gestao_pessoas': {
                    'description': 'Acesso total exceto usuários e administração',
                    'permissions': ['add', 'change', 'delete', 'view'],
                    'models': ['militar', 'fichaconceito', 'quadroacesso', 'promocao', 'comissao', 
                              'sessaocomissao', 'membrocomissao', 'deliberacaocomissao', 'documentosessao', 
                              'atasessao', 'modeloata', 'notificacaosessao', 'intersticio', 'previsaovaga', 
                              'quadrofixacaovagas', 'cargocomissao', 'votodeliberacao', 'presencasessao', 
                              'justificativaencerramento', 'assinaturaata']
                },
                'chefe_secao_promocoes': {
                    'description': 'Acesso total exceto usuários e administração',
                    'permissions': ['add', 'change', 'delete', 'view'],
                    'models': ['militar', 'fichaconceito', 'quadroacesso', 'promocao', 'comissao', 
                              'sessaocomissao', 'membrocomissao', 'deliberacaocomissao', 'documentosessao', 
                              'atasessao', 'modeloata', 'notificacaosessao', 'intersticio', 'previsaovaga', 
                              'quadrofixacaovagas', 'cargocomissao', 'votodeliberacao', 'presencasessao', 
                              'justificativaencerramento', 'assinaturaata']
                },
                'digitador': {
                    'description': 'Acesso total sem exclusão e sem usuários/administração',
                    'permissions': ['add', 'change', 'view'],  # Sem delete
                    'models': ['militar', 'fichaconceito', 'quadroacesso', 'promocao', 'comissao', 
                              'sessaocomissao', 'membrocomissao', 'deliberacaocomissao', 'documentosessao', 
                              'atasessao', 'modeloata', 'notificacaosessao', 'intersticio', 'previsaovaga', 
                              'quadrofixacaovagas', 'cargocomissao', 'votodeliberacao', 'presencasessao', 
                              'justificativaencerramento', 'assinaturaata']
                },
                'usuario': {
                    'description': 'Acesso a documentos específicos e visualização',
                    'permissions': ['view'],  # Apenas visualização
                    'models': ['militar', 'fichaconceito']  # Apenas ficha de cadastro e conceito
                }
            }
            
            # Atribuir permissões aos grupos
            for codigo_grupo, config in permissoes_grupos.items():
                grupo = grupos_criados[codigo_grupo]
                permissoes_atribuidas = []
                
                for modelo in config['models']:
                    # Buscar content type
                    try:
                        content_type = ContentType.objects.get(model=modelo)
                        
                        for permissao_codigo in config['permissions']:
                            try:
                                permissao = Permission.objects.get(
                                    codename=f'{permissao_codigo}_{modelo}',
                                    content_type=content_type
                                )
                                grupo.permissions.add(permissao)
                                permissoes_atribuidas.append(permissao)
                            except Permission.DoesNotExist:
                                self.stdout.write(f'⚠ Permissão {permissao_codigo}_{modelo} não encontrada')
                                
                    except ContentType.DoesNotExist:
                        self.stdout.write(f'⚠ ContentType para {modelo} não encontrado')
                
                self.stdout.write(f'✓ {len(permissoes_atribuidas)} permissões atribuídas ao grupo "{grupo.name}"')
            
            # Criar usuários padrão se não existirem
            usuarios_padrao = {
                'admin': {
                    'username': 'admin',
                    'first_name': 'Administrador',
                    'last_name': 'Sistema',
                    'email': 'admin@cbmepi.gov.br',
                    'is_superuser': True,
                    'is_staff': True,
                    'is_active': True,
                    'groups': ['admin']
                },
                'superusuario': {
                    'username': 'superusuario',
                    'first_name': 'Super',
                    'last_name': 'Usuário',
                    'email': 'super@cbmepi.gov.br',
                    'is_superuser': True,
                    'is_staff': True,
                    'is_active': True,
                    'groups': ['superusuario']
                }
            }
            
            for codigo, dados in usuarios_padrao.items():
                user, created = User.objects.get_or_create(
                    username=dados['username'],
                    defaults={
                        'first_name': dados['first_name'],
                        'last_name': dados['last_name'],
                        'email': dados['email'],
                        'is_superuser': dados['is_superuser'],
                        'is_staff': dados['is_staff'],
                        'is_active': dados['is_active']
                    }
                )
                
                if created:
                    user.set_password('123456')  # Senha padrão
                    user.save()
                    self.stdout.write(f'✓ Usuário "{dados["username"]}" criado com senha: 123456')
                else:
                    self.stdout.write(f'✓ Usuário "{dados["username"]}" já existe')
                
                # Adicionar ao grupo
                grupo = grupos_criados[dados['groups'][0]]
                user.groups.add(grupo)
            
            # Atribuir usuários existentes ao grupo 'usuario' por padrão
            usuarios_sem_grupo = User.objects.filter(groups__isnull=True, is_superuser=False)
            grupo_usuario = grupos_criados['usuario']
            
            for user in usuarios_sem_grupo:
                user.groups.add(grupo_usuario)
            
            if usuarios_sem_grupo.exists():
                self.stdout.write(f'✓ {usuarios_sem_grupo.count()} usuários adicionados ao grupo "Usuário"')
            
            self.stdout.write(
                self.style.SUCCESS(
                    '\n🎉 Configuração de permissões concluída!\n\n'
                    '📋 Resumo dos grupos criados:\n'
                    '• Admin: Acesso total\n'
                    '• Super Usuário: Acesso total\n'
                    '• Membro CPO: Acesso a oficiais e comissões\n'
                    '• Membro CPP: Acesso a praças e comissões\n'
                    '• Comandante Geral: Acesso total exceto usuários e administração\n'
                    '• Subcomandante Geral: Acesso total exceto usuários e administração\n'
                    '• Diretor de Gestão de Pessoas: Acesso total exceto usuários e administração\n'
                    '• Chefe da Seção de Promoções: Acesso total exceto usuários e administração\n'
                    '• Digitador: Acesso total sem exclusão e sem usuários/administração\n'
                    '• Usuário: Acesso a documentos específicos e visualização\n\n'
                    '🔑 Usuários padrão criados:\n'
                    '• admin (senha: 123456)\n'
                    '• superusuario (senha: 123456)\n\n'
                    '⚠️ IMPORTANTE: Altere as senhas dos usuários padrão após o primeiro login!'
                )
            ) 