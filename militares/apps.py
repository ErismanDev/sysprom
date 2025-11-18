from django.apps import AppConfig


class MilitaresConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "militares"
    
    def ready(self):
        import militares.signals
        
        # Iniciar tarefa automática de atualização de situações
        # Apenas se não estiver em modo de migração ou shell
        import sys
        if 'migrate' not in sys.argv and 'makemigrations' not in sys.argv and 'shell' not in sys.argv:
            try:
                from militares.tarefas_automaticas import iniciar_tarefa_automatica
                iniciar_tarefa_automatica()
            except Exception as e:
                # Em caso de erro, apenas logar, não interromper o servidor
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Não foi possível iniciar tarefa automática: {e}')