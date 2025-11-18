#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comando para atualizar as funções dos militares:
- Remove a função básica "Serviço Operacional" quando o militar tem funções específicas
- Mantém apenas as funções específicas para cada militar
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from militares.models import UsuarioFuncaoMilitar, FuncaoMilitar
from django.db import transaction

class Command(BaseCommand):
    help = 'Atualiza as funções dos militares removendo a função básica quando há funções específicas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a execução sem fazer alterações no banco de dados.',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostra informações detalhadas sobre cada usuário processado.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write("=== ATUALIZAÇÃO DAS FUNÇÕES DOS MILITARES ===\n")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 MODO SIMULAÇÃO - Nenhuma alteração será feita\n"))
        
        # Buscar função básica "Serviço Operacional"
        try:
            funcao_basica = FuncaoMilitar.objects.get(nome="Serviço Operacional")
        except FuncaoMilitar.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Função 'Serviço Operacional' não encontrada!"))
            return
        
        # Buscar usuários com múltiplas funções
        usuarios_com_multiplas_funcoes = []
        usuarios_apenas_basica = []
        
        for user in User.objects.all():
            funcoes = UsuarioFuncaoMilitar.objects.filter(usuario=user)
            funcoes_basicas = funcoes.filter(funcao_militar=funcao_basica)
            funcoes_especificas = funcoes.exclude(funcao_militar=funcao_basica)
            
            if funcoes.count() > 1 and funcoes_basicas.exists() and funcoes_especificas.exists():
                usuarios_com_multiplas_funcoes.append({
                    'user': user,
                    'funcoes_basicas': funcoes_basicas,
                    'funcoes_especificas': funcoes_especificas
                })
            elif funcoes.count() == 1 and funcoes_basicas.exists():
                usuarios_apenas_basica.append(user)
        
        self.stdout.write(f"📊 ESTATÍSTICAS:")
        self.stdout.write(f"  • Usuários com múltiplas funções (básica + específicas): {len(usuarios_com_multiplas_funcoes)}")
        self.stdout.write(f"  • Usuários apenas com função básica: {len(usuarios_apenas_basica)}")
        self.stdout.write(f"  • Total de usuários: {User.objects.count()}\n")
        
        if not usuarios_com_multiplas_funcoes:
            self.stdout.write(self.style.SUCCESS("✅ Nenhum usuário com múltiplas funções encontrado!"))
            return
        
        # Mostrar usuários que serão processados
        self.stdout.write("👥 USUÁRIOS QUE SERÃO PROCESSADOS:")
        for i, item in enumerate(usuarios_com_multiplas_funcoes[:10], 1):  # Mostrar apenas os primeiros 10
            user = item['user']
            funcoes_especificas = [f.funcao_militar.nome for f in item['funcoes_especificas']]
            self.stdout.write(f"  {i}. {user.username}: {funcoes_especificas}")
        
        if len(usuarios_com_multiplas_funcoes) > 10:
            self.stdout.write(f"  ... e mais {len(usuarios_com_multiplas_funcoes) - 10} usuários")
        
        self.stdout.write("")
        
        # Processar usuários
        if not dry_run:
            with transaction.atomic():
                processados = 0
                for item in usuarios_com_multiplas_funcoes:
                    user = item['user']
                    funcoes_basicas = item['funcoes_basicas']
                    funcoes_especificas = item['funcoes_especificas']
                    
                    # Remover função básica
                    funcoes_removidas = funcoes_basicas.count()
                    funcoes_basicas.delete()
                    
                    if verbose:
                        funcoes_especificas_nomes = [f.funcao_militar.nome for f in funcoes_especificas]
                        self.stdout.write(f"  ✓ {user.username}: Removida função básica, mantidas: {funcoes_especificas_nomes}")
                    
                    processados += 1
                
                self.stdout.write(f"\n✅ PROCESSAMENTO CONCLUÍDO!")
                self.stdout.write(f"  • Usuários processados: {processados}")
                self.stdout.write(f"  • Funções básicas removidas: {sum(item['funcoes_basicas'].count() for item in usuarios_com_multiplas_funcoes)}")
        else:
            self.stdout.write(f"\n🔍 SIMULAÇÃO - Seriam processados {len(usuarios_com_multiplas_funcoes)} usuários")
            total_funcoes_remover = sum(item['funcoes_basicas'].count() for item in usuarios_com_multiplas_funcoes)
            self.stdout.write(f"🔍 SIMULAÇÃO - Seriam removidas {total_funcoes_remover} funções básicas")
        
        # Verificação final
        self.stdout.write(f"\n📊 VERIFICAÇÃO FINAL:")
        usuarios_apenas_basica_final = User.objects.filter(funcoes_militares__funcao_militar=funcao_basica).distinct().count()
        usuarios_com_especificas = User.objects.exclude(funcoes_militares__funcao_militar=funcao_basica).distinct().count()
        
        self.stdout.write(f"  • Usuários apenas com função básica: {usuarios_apenas_basica_final}")
        self.stdout.write(f"  • Usuários com funções específicas: {usuarios_com_especificas}")
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS("\n🎉 Atualização concluída com sucesso!"))
        else:
            self.stdout.write(self.style.WARNING("\n🔍 Simulação concluída. Use sem --dry-run para executar as alterações."))
