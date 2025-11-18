#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from militares.models import FuncaoMilitar, PermissaoFuncao

class Command(BaseCommand):
    help = 'Configura todas as permissões para o Administrador do Sistema'

    def handle(self, *args, **options):
        self.stdout.write("=== CONFIGURANDO PERMISSÕES DO ADMINISTRADOR DO SISTEMA ===\n")
        
        # Buscar função do administrador
        admin = FuncaoMilitar.objects.filter(nome='Administrador do Sistema').first()
        
        if not admin:
            self.stdout.write(self.style.ERROR('❌ Função "Administrador do Sistema" não encontrada!'))
            return
        
        self.stdout.write(f"✅ Função encontrada: {admin.nome} (ID: {admin.id})")
        
        # Remover permissões existentes (se houver)
        perms_existentes = PermissaoFuncao.objects.filter(funcao_militar=admin)
        if perms_existentes.exists():
            count_removidas = perms_existentes.count()
            perms_existentes.delete()
            self.stdout.write(f"🗑️  Removidas {count_removidas} permissões existentes")
        
        # Definir todas as permissões que o administrador deve ter
        modulos = [
            'MILITARES', 'FICHAS_CONCEITO', 'QUADROS_ACESSO', 'PROMOCOES', 
            'VAGAS', 'COMISSAO', 'DOCUMENTOS', 'USUARIOS', 'RELATORIOS', 
            'CONFIGURACOES', 'ALMANAQUES', 'CALENDARIOS', 'NOTIFICACOES',
            'MODELOS_ATA', 'CARGOS_COMISSAO', 'QUADROS_FIXACAO', 'ASSINATURAS',
            'ESTATISTICAS', 'EXPORTACAO', 'IMPORTACAO', 'BACKUP', 'AUDITORIA',
            'DASHBOARD', 'BUSCA', 'AJAX', 'API', 'SESSAO', 'FUNCAO', 'PERFIL', 'SISTEMA'
        ]
        
        acessos = [
            'VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 
            'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR',
            'REORDENAR_ANTIGUIDADE'
        ]
        
        # Criar todas as permissões
        permissoes_criadas = 0
        for modulo in modulos:
            for acesso in acessos:
                permissao, created = PermissaoFuncao.objects.get_or_create(
                    funcao_militar=admin,
                    modulo=modulo,
                    acesso=acesso,
                    defaults={'ativo': True}
                )
                if created:
                    permissoes_criadas += 1
                else:
                    # Ativar se já existia mas estava inativa
                    if not permissao.ativo:
                        permissao.ativo = True
                        permissao.save()
                        permissoes_criadas += 1
        
        self.stdout.write(f"\n📊 Resultado:")
        self.stdout.write(f"  ✅ Módulos configurados: {len(modulos)}")
        self.stdout.write(f"  ✅ Tipos de acesso por módulo: {len(acessos)}")
        self.stdout.write(f"  ✅ Total de permissões criadas/ativadas: {permissoes_criadas}")
        self.stdout.write(f"  ✅ Total esperado: {len(modulos) * len(acessos)}")
        
        # Verificação final
        perms_finais = PermissaoFuncao.objects.filter(funcao_militar=admin, ativo=True)
        self.stdout.write(f"\n🔍 Verificação final:")
        self.stdout.write(f"  📋 Total de permissões ativas: {perms_finais.count()}")
        
        if perms_finais.count() == len(modulos) * len(acessos):
            self.stdout.write(self.style.SUCCESS("🎉 SUCESSO! Todas as permissões foram configuradas corretamente!"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  ATENÇÃO! Nem todas as permissões foram criadas."))
        
        # Mostrar resumo por módulo
        self.stdout.write(f"\n📋 Resumo por módulo:")
        modulos_com_perms = {}
        for p in perms_finais:
            if p.modulo not in modulos_com_perms:
                modulos_com_perms[p.modulo] = []
            modulos_com_perms[p.modulo].append(p.acesso)
        
        for modulo in sorted(modulos_com_perms.keys()):
            acessos_modulo = sorted(modulos_com_perms[modulo])
            self.stdout.write(f"  {modulo}: {len(acessos_modulo)} permissões - {', '.join(acessos_modulo)}")
        
        self.stdout.write(f"\n✅ Configuração concluída!")
