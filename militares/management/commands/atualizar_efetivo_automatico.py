from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .atualizar_efetivo_vagas import Command as AtualizarEfetivoCommand
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Atualiza automaticamente o efetivo nas vagas e envia relatório por email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            action='store_true',
            help='Envia relatório por email',
        )
        parser.add_argument(
            '--recipients',
            nargs='+',
            help='Lista de emails para receber o relatório',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔄 Iniciando atualização automática do efetivo...')
        )
        
        try:
            # Executar a atualização
            atualizar_command = AtualizarEfetivoCommand()
            resultado = atualizar_command.handle(*args, **options)
            
            # Preparar relatório
            relatorio = self._gerar_relatorio(resultado)
            
            # Log do resultado
            logger.info(f"Atualização automática concluída: {relatorio}")
            
            # Enviar email se solicitado
            if options['email'] and options['recipients']:
                self._enviar_email_relatorio(relatorio, options['recipients'])
            
            self.stdout.write(
                self.style.SUCCESS('✅ Atualização automática concluída com sucesso!')
            )
            
        except Exception as e:
            erro_msg = f"Erro na atualização automática: {str(e)}"
            logger.error(erro_msg)
            self.stdout.write(
                self.style.ERROR(f'❌ {erro_msg}')
            )
            
            # Enviar email de erro se configurado
            if options['email'] and options['recipients']:
                self._enviar_email_erro(str(e), options['recipients'])

    def _gerar_relatorio(self, resultado):
        """Gera um relatório da atualização"""
        data_atual = timezone.now().strftime('%d/%m/%Y %H:%M:%S')
        
        relatorio = f"""
============================================================
📊 RELATÓRIO DE ATUALIZAÇÃO AUTOMÁTICA DO EFETIVO
============================================================
📅 Data/Hora: {data_atual}
👥 Militares processados: {resultado.get('militares_processados', 0)}
🆕 Vagas criadas: {resultado.get('vagas_criadas', 0)}
🔄 Vagas atualizadas: {resultado.get('vagas_atualizadas', 0)}
📈 Previsões atualizadas: {resultado.get('previsoes_atualizadas', 0)}

📋 EFETIVO POR POSTO/QUADRO:
----------------------------------------
"""
        
        for posto_quadro, info in resultado.get('efetivo_por_posto_quadro', {}).items():
            relatorio += f"  {posto_quadro}: {info['efetivo_atual']} militares\n"
        
        return relatorio

    def _enviar_email_relatorio(self, relatorio, recipients):
        """Envia relatório por email"""
        try:
            subject = f'Relatório de Atualização do Efetivo - {timezone.now().strftime("%d/%m/%Y")}'
            
            send_mail(
                subject=subject,
                message=relatorio,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'📧 Relatório enviado para: {", ".join(recipients)}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao enviar email: {str(e)}')
            )

    def _enviar_email_erro(self, erro, recipients):
        """Envia email de erro"""
        try:
            subject = f'ERRO na Atualização do Efetivo - {timezone.now().strftime("%d/%m/%Y")}'
            message = f"""
============================================================
❌ ERRO NA ATUALIZAÇÃO AUTOMÁTICA DO EFETIVO
============================================================
📅 Data/Hora: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
❌ Erro: {erro}

Este é um email automático do sistema SysProm - CBMEPI.
Por favor, verifique o sistema e corrija o problema.
"""
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao enviar email de erro: {str(e)}')
            ) 