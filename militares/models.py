import os
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field
from django.db.models import Q, Count, Sum, Avg, Min, Max
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date, datetime, timedelta
import qrcode
from io import BytesIO
from django.core.files import File
from django.db import connection


class CargoComissao(models.Model):
    """Cargos disponíveis para membros da comissão"""
    nome = models.CharField(max_length=100, verbose_name="Nome do Cargo")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código", help_text="Código único para identificação (ex: COMANDANTE_GERAL)")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        verbose_name = "Cargo da Comissão"
        verbose_name_plural = "Cargos da Comissão"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        # Se não foi definida ordem, usar o próximo número disponível
        if not self.ordem:
            ultimo_cargo = CargoComissao.objects.order_by('-ordem').first()
            self.ordem = (ultimo_cargo.ordem + 1) if ultimo_cargo else 1
        super().save(*args, **kwargs)


def documento_upload_path(instance, filename):
    """Define o caminho de upload para documentos"""
    return f'documentos/{instance.militar.matricula}/{instance.tipo}/{filename}'


# Opções para campos de escolha - definidas no nível do módulo
SEXO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Feminino'),
]

POSTO_GRADUACAO_CHOICES = [
    # Oficiais
    ('CB', 'Coronel'),
    ('TC', 'Tenente Coronel'),
    ('MJ', 'Major'),
    ('CP', 'Capitão'),
    ('1T', '1º Tenente'),
    ('2T', '2º Tenente'),
    ('AS', 'Aspirante a Oficial'),
    ('AA', 'Aluno de Adaptação'),
    ('NVRR', 'Navegador'),
    # Praças
    ('ST', 'Subtenente'),
    ('1S', '1º Sargento'),
    ('2S', '2º Sargento'),
    ('3S', '3º Sargento'),
    ('CAB', 'Cabo'),
    ('SD', 'Soldado'),
]

SITUACAO_CHOICES = [
    ('AT', 'Ativo'),
    ('IN', 'Inativo'),
    ('TR', 'Transferido'),
    ('AP', 'Aposentado'),
    ('EX', 'Exonerado'),
]

QUADRO_CHOICES = [
    ('COMB', 'Combatente'),
    ('SAUDE', 'Saúde'),
    ('ENG', 'Engenheiro'),
    ('COMP', 'Complementar'),
            ('NVRR', 'NVRR'),
    ('PRACAS', 'Praças'),
]


class Militar(models.Model):
    # Campos básicos
    numeracao_antiguidade = models.PositiveIntegerField(null=True, blank=True, verbose_name="Numeração de Antiguidade (Manual)")
    matricula = models.CharField(max_length=20, unique=True, verbose_name="Matrícula")
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    nome_guerra = models.CharField(max_length=100, verbose_name="Nome de Guerra")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    rg = models.CharField(max_length=20, verbose_name="RG")
    orgao_expedidor = models.CharField(max_length=20, verbose_name="Órgão Expedidor")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo")
    
    # Informações militares
    quadro = models.CharField(max_length=10, choices=QUADRO_CHOICES, default='COMB', verbose_name="Quadro")
    posto_graduacao = models.CharField(max_length=4, choices=POSTO_GRADUACAO_CHOICES, verbose_name="Posto/Graduação")
    data_ingresso = models.DateField(verbose_name="Data de Ingresso")
    data_promocao_atual = models.DateField(verbose_name="Data da Promoção Atual")
    situacao = models.CharField(max_length=2, choices=SITUACAO_CHOICES, default='AT', verbose_name="Situação")
    
    # Informações de contato
    email = models.EmailField(verbose_name="E-mail")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    celular = models.CharField(max_length=20, verbose_name="Celular")
    
    foto = models.ImageField(upload_to='fotos_militares/', blank=True, null=True, verbose_name="Foto do Militar")
    
    # Campos de controle
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Novos campos para controle de requisitos e inspeção de saúde
    curso_formacao_oficial = models.BooleanField(default=False, verbose_name="Possui Curso de Formação de Oficial Bombeiro Militar (CFO)")
    curso_aperfeicoamento_oficial = models.BooleanField(default=False, verbose_name="Possui Curso de Aperfeiçoamento de Oficial Bombeiro Militar")
    curso_cho = models.BooleanField(default=False, verbose_name="Possui Curso de Habilitação de Oficiais (CHO)")
    nota_cho = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Nota do CHO", help_text="Nota obtida no Curso de Habilitação de Oficiais (CHO)")
    curso_superior = models.BooleanField(default=False, verbose_name="Possui Curso Superior")
    pos_graduacao = models.BooleanField(default=False, verbose_name="Possui Pós-Graduação")
    curso_csbm = models.BooleanField(default=False, verbose_name="Possui Curso Superior de Bombeiro Militar (CSBM)")
    curso_adaptacao_oficial = models.BooleanField(default=False, verbose_name="Possui Curso de Adaptação de Oficiais (CADOF)")
    
    # Campos para cursos de praças
    curso_cfsd = models.BooleanField(default=False, verbose_name="Possui Curso de Formação de Soldados (CFSD)")
    curso_formacao_pracas = models.BooleanField(default=False, verbose_name="Possui Curso de Formação de Praças")
    curso_chc = models.BooleanField(default=False, verbose_name="Possui Curso de Habilitação de Cabos (CHC) ou equivalente")
    nota_chc = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Nota do CHC", help_text="Nota obtida no Curso de Habilitação de Cabos (CHC)")
    curso_chsgt = models.BooleanField(default=False, verbose_name="Possui Curso de Habilitação de Sargentos (CHSGT) ou equivalente")
    nota_chsgt = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Nota do CHSGT", help_text="Nota obtida no Curso de Habilitação de Sargentos (CHSGT)")
    curso_cas = models.BooleanField(default=False, verbose_name="Possui Curso de Aperfeiçoamento de Sargentos (CAS)")
    
    apto_inspecao_saude = models.BooleanField(default=True, verbose_name="Apto em Inspeção de Saúde")
    data_inspecao_saude = models.DateField(null=True, blank=True, verbose_name="Data da Inspeção de Saúde")
    data_validade_inspecao_saude = models.DateField(null=True, blank=True, verbose_name="Validade da Inspeção de Saúde")
    
    # Campo para salvar a numeração de antiguidade anterior quando inativado
    numeracao_antiguidade_anterior = models.PositiveIntegerField(null=True, blank=True, verbose_name="Numeração de Antiguidade Anterior", help_text="Numeração de antiguidade que o militar tinha antes de ser inativado")
    
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='militar', verbose_name='Usuário vinculado')
    
    class Meta:
        verbose_name = "Militar"
        verbose_name_plural = "Militares"
        ordering = ['posto_graduacao', 'nome_completo']
    
    def __str__(self):
        return f"{self.get_posto_graduacao_display()} {self.nome_completo} - {self.matricula}"
    
    def idade(self):
        """Calcula a idade do militar"""
        hoje = timezone.now().date()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )
    
    def tempo_servico(self):
        """Calcula o tempo de serviço do militar"""
        hoje = timezone.now().date()
        return hoje.year - self.data_ingresso.year - (
            (hoje.month, hoje.day) < (self.data_ingresso.month, self.data_ingresso.day)
        )
    
    def tempo_posto_atual(self):
        """Calcula o tempo no posto/graduação atual"""
        hoje = timezone.now().date()
        tempo = hoje.year - self.data_promocao_atual.year - (
            (hoje.month, hoje.day) < (self.data_promocao_atual.month, self.data_promocao_atual.day)
        )
        # Garantir que o tempo não seja negativo (caso a data de promoção seja no futuro)
        return max(0, tempo)
    
    def intersticio_minimo(self):
        """Retorna o interstício mínimo para o posto atual baseado na configuração"""
        try:
            intersticio = Intersticio.objects.get(
                posto=self.posto_graduacao, 
                quadro=self.quadro, 
                ativo=True
            )
            return intersticio.tempo_total_meses()
        except Intersticio.DoesNotExist:
            # Fallback para valores padrão se não houver configuração
            intersticios_padrao = {
                'AS': 6,  # 6 meses como Aspirante para 2º Tenente
                'AA': 6,  # 6 meses como Aluno de Adaptação para 2º Tenente
                '2T': 36,  # 3 anos como 2º Tenente para 1º Tenente
                '1T': 48,  # 4 anos como 1º Tenente para Capitão
                'CP': 48,  # 4 anos como Capitão para Major
                'MJ': 48,  # 4 anos como Major para Tenente-Coronel
                'TC': 36,  # 3 anos como Tenente-Coronel para Coronel
            }
            return intersticios_padrao.get(self.posto_graduacao, 0)
    
    def intersticio_formatado(self):
        """Retorna o interstício mínimo formatado para exibição"""
        try:
            intersticio = Intersticio.objects.get(
                posto=self.posto_graduacao, 
                quadro=self.quadro, 
                ativo=True
            )
            return intersticio.tempo_formatado()
        except Intersticio.DoesNotExist:
            meses = self.intersticio_minimo()
            if meses == 0:
                return "Não configurado"
            anos = meses // 12
            meses_resto = meses % 12
            if anos == 0:
                return f"{meses_resto} mês(es)"
            elif meses_resto == 0:
                return f"{anos} ano(s)"
            else:
                return f"{anos} ano(s) e {meses_resto} mês(es)"
    
    def tempo_restante_intersticio(self):
        """Calcula quanto tempo falta para completar o interstício"""
        tempo_atual = self.tempo_posto_atual() * 12  # Converter anos para meses
        intersticio_min = self.intersticio_minimo()
        
        if intersticio_min == 0:
            return 0
        
        tempo_restante = intersticio_min - tempo_atual
        return max(0, tempo_restante)
    
    def apto_intersticio(self):
        """Verifica se o militar está apto quanto ao interstício"""
        return self.tempo_restante_intersticio() == 0
    
    def apto_intersticio_ate_data(self, data_promocao):
        """Verifica se o militar completará o interstício mínimo até uma data específica"""
        from datetime import datetime
        # Garantir que data_promocao é um objeto date
        if isinstance(data_promocao, str):
            data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
        elif isinstance(data_promocao, datetime):
            data_promocao = data_promocao.date()
        # Calcular tempo no posto até a data da promoção
        tempo_no_posto_ate_data = (data_promocao - self.data_promocao_atual).days / 365.25
        # Obter interstício mínimo em anos
        intersticio_minimo_meses = self.intersticio_minimo()
        intersticio_minimo_anos = intersticio_minimo_meses / 12
        return tempo_no_posto_ate_data >= intersticio_minimo_anos
    
    def get_numeracao_antiguidade_display(self):
        """Retorna a numeração de antiguidade formatada"""
        if self.numeracao_antiguidade is None:
            return "Não informada"
        return f"{self.numeracao_antiguidade}º"
    
    def validar_numeracao_antiguidade(self):
        """Valida se a numeração de antiguidade está correta para o posto/quadro"""
        if not self.numeracao_antiguidade:
            return True, "Numeração não informada"
        
        # Permitir valores repetidos para manipulação manual
        # Apenas validar se é um número positivo
        if self.numeracao_antiguidade <= 0:
            return False, "A numeração de antiguidade deve ser um número positivo"
        
        return True, "Numeração válida"
    
    def reordenar_numeracoes_apos_alteracao(self, numeracao_anterior=None):
        """
        Após alteração manual da numeração de antiguidade, empurra os demais militares
        para frente ou para trás conforme necessário, mantendo a ordem correta.
        """
        if numeracao_anterior is None or numeracao_anterior == self.numeracao_antiguidade:
            return
        
        numeracao_nova = self.numeracao_antiguidade
        
        # Buscar todos os militares do mesmo posto e quadro (exceto este)
        militares_mesmo_posto = Militar.objects.filter(
            situacao='AT',
            posto_graduacao=self.posto_graduacao,
            quadro=self.quadro
        ).exclude(pk=self.pk)
        
        print(f"[DEBUG] Reordenando: {numeracao_anterior} -> {numeracao_nova}")
        
        if numeracao_nova < numeracao_anterior:
            # Militar "subiu" na antiguidade (ex: 3º -> 1º)
            # Empurrar todos os militares da nova posição até a anterior (+1)
            # CORREÇÃO: Incluir a posição anterior na reordenação
            militares_para_empurrar = militares_mesmo_posto.filter(
                numeracao_antiguidade__gte=numeracao_nova,
                numeracao_antiguidade__lte=numeracao_anterior
            ).exclude(pk=self.pk).order_by('-numeracao_antiguidade')
            
            for militar in militares_para_empurrar:
                militar.numeracao_antiguidade += 1
                militar.save(update_fields=['numeracao_antiguidade'])
                print(f"[DEBUG] Empurrado: {militar.nome_completo} {militar.numeracao_antiguidade-1} -> {militar.numeracao_antiguidade}")
                
        elif numeracao_nova > numeracao_anterior:
            # Militar "desceu" na antiguidade (ex: 1º -> 3º)
            # Empurrar todos os militares da anterior até a nova (-1)
            militares_para_empurrar = militares_mesmo_posto.filter(
                numeracao_antiguidade__gt=numeracao_anterior,
                numeracao_antiguidade__lte=numeracao_nova
            ).exclude(pk=self.pk).order_by('numeracao_antiguidade')
            
            for militar in militares_para_empurrar:
                militar.numeracao_antiguidade -= 1
                militar.save(update_fields=['numeracao_antiguidade'])
                print(f"[DEBUG] Empurrado: {militar.nome_completo} {militar.numeracao_antiguidade+1} -> {militar.numeracao_antiguidade}")
        
        # Atualizar o próprio objeto em memória
        self.refresh_from_db()

    def atribuir_numeracao_por_promocao(self, posto_anterior=None, quadro_anterior=None):
        """
        Atribui numeração de antiguidade quando um militar é promovido
        O militar promovido se torna o último (maior número) da nova graduação
        Considera todos do mesmo posto, independente do quadro
        """
        # Buscar a maior numeração existente para o novo posto (independente do quadro)
        qs = Militar.objects.filter(
            situacao='AT',
            posto_graduacao=self.posto_graduacao
        ).exclude(pk=self.pk)
        
        max_numeracao = qs.aggregate(models.Max('numeracao_antiguidade'))['numeracao_antiguidade__max']
        nova_numeracao = (max_numeracao or 0) + 1
        self.numeracao_antiguidade = nova_numeracao
        self.save(update_fields=['numeracao_antiguidade'])

        return nova_numeracao

    def reordenar_posto_anterior_apos_promocao(self, posto_anterior, quadro_anterior):
        """
        Reordena os militares do posto anterior após uma promoção
        Quando alguém é promovido, os demais "sobem" uma posição:
        - Quem era 2º vira 1º
        - Quem era 3º vira 2º
        - E assim por diante
        """
        if not posto_anterior or posto_anterior == self.posto_graduacao:
            return
        
        # Buscar todos os militares do posto anterior (exceto o promovido), independente do quadro
        # Ordenar por numeração atual para manter a ordem correta
        militares_posto_anterior = Militar.objects.filter(
            situacao='AT',
            posto_graduacao=posto_anterior
        ).exclude(pk=self.pk).order_by('numeracao_antiguidade')
        
        if not militares_posto_anterior.exists():
            return
        
        # Reordenar: cada militar "sobe" uma posição
        militares_para_atualizar = []
        for i, militar in enumerate(militares_posto_anterior, 1):
            if militar.numeracao_antiguidade != i:
                militar.numeracao_antiguidade = i
                militares_para_atualizar.append(militar)
        
        # Salvar todas as alterações em lote
        if militares_para_atualizar:
            Militar.objects.bulk_update(militares_para_atualizar, ['numeracao_antiguidade'])
        
        return len(militares_para_atualizar)
    
    def proxima_promocao(self):
        """Calcula qual será a próxima promoção baseado no posto atual"""
        proximas_promocoes = {
            'AS': '2T',    # Aspirante → 2º Tenente
            'AA': '2T',    # Aluno de Adaptação → 2º Tenente
            '2T': '1T',    # 2º Tenente → 1º Tenente
            '1T': 'CP',    # 1º Tenente → Capitão
            'CP': 'MJ',    # Capitão → Major
            'MJ': 'TC',    # Major → Tenente-Coronel
            'TC': 'CB',    # Tenente-Coronel → Coronel
            'ST': '2T',    # Subtenente → 2º Tenente (para quadros sem Aspirante)
        }
        
        # Regra especial: Subtenente do quadro Combatente promove para Aspirante
        if self.posto_graduacao == 'ST' and self.quadro == 'COMB':
            return 'AS'
        
        return proximas_promocoes.get(self.posto_graduacao, None)
    
    def apto_promocao_antiguidade(self):
        """Verifica se está apto para promoção por antiguidade conforme Art. 13 para todos os quadros e Subtenente"""
        if self.situacao != 'AT':
            return False
        
        # Verificar inspeção de saúde
        hoje = timezone.now().date()
        if not self.apto_inspecao_saude or (self.data_validade_inspecao_saude and self.data_validade_inspecao_saude < hoje):
            return False
        
        # Verificar interstício
        if not self.apto_intersticio():
            return False
        
        # Regras para Subtenente
        if self.posto_graduacao == 'ST':
            # CHO obrigatório para Subtenente do quadro complementar promovendo a 2º Tenente
            if self.quadro == 'COMP' and self.proxima_promocao() == '2T':
                if not getattr(self, 'curso_cho', False):
                    return False
        
        # Regras específicas por quadro
        if self.quadro == 'COMB':
            # Quadro Combatente - CFH obrigatório para todos os postos
            if not getattr(self, 'curso_formacao_oficial', False):
                return False
            elif self.posto_graduacao == 'CP':
                # Capitão precisa ter ambos os cursos
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False
            elif self.posto_graduacao == 'MJ':
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False
            elif self.posto_graduacao in ['TC', 'CB']:
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False
                if not getattr(self, 'curso_csbm', False):
                    return False
        
        elif self.quadro == 'SAUDE':
            # Quadro de Saúde - CFH obrigatório para todos os postos
            if not getattr(self, 'curso_formacao_oficial', False):
                return False
            elif self.posto_graduacao == 'CP':
                # Capitão precisa ter ambos os cursos
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False
            elif self.posto_graduacao == 'MJ':
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False
            elif self.posto_graduacao in ['TC', 'CB']:
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False
                if not getattr(self, 'curso_csbm', False):
                    return False
        
        elif self.quadro == 'ENG':
            # Quadro de Engenheiros - CADOF obrigatório para Aluno de Adaptação, CFO para outros postos
            if self.posto_graduacao == 'AA':
                if not getattr(self, 'curso_adaptacao_oficial', False):
                    return False
            else:
                if not getattr(self, 'curso_formacao_oficial', False):
                    return False
            if self.posto_graduacao == 'CP':
                # Capitão precisa ter ambos os cursos
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False
            elif self.posto_graduacao == 'MJ':
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False
            elif self.posto_graduacao in ['TC', 'CB']:
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False
                if not getattr(self, 'curso_csbm', False):
                    return False
        
        elif self.quadro == 'COMP':
            # Quadro Complementar - Regras específicas
            if self.posto_graduacao in ['ST', '2T', '1T']:
                # CHO obrigatório para Subtenente, 2º Tenente e 1º Tenente
                if not getattr(self, 'curso_cho', False):
                    return False
            elif self.posto_graduacao == 'CP':
                # Capitão do Complementar precisa de CHO e curso superior
                if not getattr(self, 'curso_cho', False):
                    return False
                if not self.curso_superior:
                    return False
            elif self.posto_graduacao == 'MJ':
                # Major do Complementar precisa de CHO, curso superior e pós-graduação
                if not getattr(self, 'curso_cho', False):
                    return False
                if not self.curso_superior:
                    return False
                if not self.pos_graduacao:
                    return False
            elif self.posto_graduacao == 'TC':
                # Tenente-Coronel do Complementar precisa de CHO, curso superior, pós-graduação e CSBM
                if not getattr(self, 'curso_cho', False):
                    return False
                if not self.curso_superior:
                    return False
                if not self.pos_graduacao:
                    return False
                if not getattr(self, 'curso_csbm', False):
                    return False
            elif self.posto_graduacao == 'CB':
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False
                if not getattr(self, 'curso_csbm', False):
                    return False
        
        return True

    def inspecao_saude_vencida(self):
        """Verifica se a inspeção de saúde está vencida"""
        if not self.apto_inspecao_saude:
            return True
        
        if self.data_validade_inspecao_saude:
            hoje = timezone.now().date()
            return self.data_validade_inspecao_saude < hoje
        
        return False

    def cursos_inerentes_quadro(self):
        """Retorna os cursos que são inerentes ao quadro do militar"""
        cursos_inerentes = {
            'COMB': {
                'cursos_cfo': 1,  # CFO obrigatório para Combatente
                'cursos_cao': 1,  # CAO obrigatório para Combatente
            },
            'SAUDE': {
                'cursos_cfo': 1,  # CFO obrigatório para Saúde
                'cursos_cao': 1,  # CAO obrigatório para Saúde
            },
            'ENG': {
                'cursos_cfo': 1,  # CFO obrigatório para Engenheiro
                'cursos_cao': 1,  # CAO obrigatório para Engenheiro
            },
            'COMP': {
                'curso_cho': 1,  # CHO obrigatório para Complementar
            },
            'PRACAS': {
                'cursos_cfsd': 1,  # CFSD obrigatório para Praças
                'cursos_chc': 1,   # CHC obrigatório para Praças
                'cursos_chsgt': 1, # CHSGT obrigatório para Praças
                'cursos_cas': 1,   # CAS obrigatório para Praças
            }
        }
        
        return cursos_inerentes.get(self.quadro, {})

    def marcar_cursos_inerentes_ficha(self, ficha_conceito):
        """Marca automaticamente os cursos inerentes ao quadro na ficha de conceito"""
        cursos_inerentes = self.cursos_inerentes_quadro()
        
        for campo_curso, quantidade in cursos_inerentes.items():
            if hasattr(ficha_conceito, campo_curso):
                setattr(ficha_conceito, campo_curso, quantidade)
        
        return ficha_conceito
    
    def clean(self):
        """Validação personalizada incluindo numeração de antiguidade"""
        from django.core.exceptions import ValidationError
        
        # Validações existentes
        super().clean()
        
        # Validar numeração de antiguidade (apenas se for informada)
        if self.numeracao_antiguidade:
            valido, mensagem = self.validar_numeracao_antiguidade()
            if not valido:
                raise ValidationError({'numeracao_antiguidade': mensagem})
        if self.posto_graduacao == 'ST' and self.quadro == 'COMB':
            raise ValidationError("Não existe Subtenente no quadro Combatente.")

    def get_promocao_anterior(self):
        """Retorna a promoção anterior do militar (última promoção antes da atual)"""
        try:
            # Buscar a promoção mais recente que não seja a atual
            promocao_anterior = self.promocao_set.filter(
                data_promocao__lt=self.data_promocao_atual
            ).order_by('-data_promocao').first()
            return promocao_anterior
        except:
            return None
    
    def get_data_promocao_anterior(self):
        """Retorna a data da promoção anterior"""
        promocao_anterior = self.get_promocao_anterior()
        if promocao_anterior:
            return promocao_anterior.data_promocao
        return None
    
    def get_antiguidade_promocao_anterior(self):
        """Retorna a antiguidade baseada na promoção anterior (data mais antiga = mais antigo)"""
        data_promocao_anterior = self.get_data_promocao_anterior()
        if data_promocao_anterior:
            return data_promocao_anterior
        return None
    
    @classmethod
    def reordenar_por_antiguidade_promocao(cls, militares_queryset):
        """
        Reordena militares do mesmo posto/graduação por:
        1. Data da promoção atual (mais antiga primeiro)
        2. Antiguidade da promoção anterior (mais antiga primeiro)
        """
        if not militares_queryset:
            return []
        
        # Agrupar por posto/graduação
        militares_por_posto = {}
        for militar in militares_queryset:
            posto = militar.posto_graduacao
            if posto not in militares_por_posto:
                militares_por_posto[posto] = []
            militares_por_posto[posto].append(militar)
        
        # Reordenar cada grupo
        militares_ordenados = []
        for posto, militares in militares_por_posto.items():
            # Ordenar por data da promoção atual (mais antiga primeiro)
            militares_ordenados_posto = sorted(
                militares,
                key=lambda m: (m.data_promocao_atual, m.get_antiguidade_promocao_anterior() or m.data_promocao_atual)
            )
            militares_ordenados.extend(militares_ordenados_posto)
        
        return militares_ordenados
    
    @classmethod
    def reordenar_numeracoes_por_antiguidade_promocao(cls, posto_graduacao=None, quadro=None):
        """
        Reordena automaticamente as numerações de antiguidade baseada na data da promoção atual
        e antiguidade da promoção anterior para militares do mesmo posto/graduação.
        A numeração é atribuída separadamente para cada posto (cada posto começa do 1º).
        O NVRR é tratado como um grupo isolado.
        """
        # Filtrar militares
        filtros = {'situacao': 'AT'}
        if posto_graduacao:
            filtros['posto_graduacao'] = posto_graduacao
        if quadro:
            filtros['quadro'] = quadro
        
        militares = cls.objects.filter(**filtros)
        
        # Agrupar por posto/graduação
        militares_por_posto = {}
        for militar in militares:
            posto = militar.posto_graduacao
            if posto not in militares_por_posto:
                militares_por_posto[posto] = []
            militares_por_posto[posto].append(militar)
        
        total_reordenados = 0
        
        # Reordenar cada posto separadamente
        for posto, militares_posto in militares_por_posto.items():
            # Ordenar apenas por data da promoção atual (mais antiga primeiro)
            militares_ordenados_posto = sorted(
                militares_posto,
                key=lambda m: m.data_promocao_atual
            )
            
            # Atribuir numerações sequenciais para este posto (começando do 1º)
            for i, militar in enumerate(militares_ordenados_posto, 1):
                militar.numeracao_antiguidade = i
                militar.save(update_fields=['numeracao_antiguidade'])
                total_reordenados += 1
        
        return total_reordenados
    
    @classmethod
    def reordenar_nvrr_separadamente(cls):
        """
        Reordena apenas os militares do NVRR como um grupo isolado
        """
        militares_nvrr = cls.objects.filter(
            posto_graduacao='NVRR',
            situacao='AT'
        ).order_by('data_promocao_atual')
        
        total_reordenados = 0
        
        # Atribuir numerações sequenciais para o NVRR (começando do 1º)
        for i, militar in enumerate(militares_nvrr, 1):
            militar.numeracao_antiguidade = i
            militar.save(update_fields=['numeracao_antiguidade'])
            total_reordenados += 1
        
        return total_reordenados
    
    def get_info_antiguidade_promocao(self):
        """Retorna informações formatadas sobre a antiguidade baseada na promoção"""
        data_promocao_atual = self.data_promocao_atual
        data_promocao_anterior = self.get_data_promocao_anterior()
        
        info = {
            'data_promocao_atual': data_promocao_atual,
            'data_promocao_anterior': data_promocao_anterior,
            'tempo_posto_atual': self.tempo_posto_atual(),
        }
        
        if data_promocao_anterior:
            # Calcular tempo desde a promoção anterior
            from datetime import date
            hoje = date.today()
            anos_anterior = hoje.year - data_promocao_anterior.year
            if (hoje.month, hoje.day) < (data_promocao_anterior.month, data_promocao_anterior.day):
                anos_anterior -= 1
            info['tempo_desde_promocao_anterior'] = anos_anterior
        
        return info

    def is_oficial(self):
        """Retorna True se o militar for oficial, False se for praça."""
        return self.posto_graduacao in [
            'CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA'
        ]
    
    def is_nvrr(self):
        """Retorna True se o militar for do NVRR"""
        return self.quadro == 'NVRR'

    def save(self, *args, **kwargs):
        # Detectar alteração do campo curso_cho, situação, posto e quadro
        curso_cho_antigo = None
        situacao_anterior = None
        posto_anterior = None
        quadro_anterior = None
        numeracao_anterior = None
        if self.pk:
            antigo = Militar.objects.filter(pk=self.pk).first()
            if antigo:
                curso_cho_antigo = antigo.curso_cho
                situacao_anterior = antigo.situacao
                posto_anterior = antigo.posto_graduacao
                quadro_anterior = antigo.quadro
                numeracao_anterior = antigo.numeracao_antiguidade
        
        # Deslocamento automático quando numeração de antiguidade é alterada manualmente
        # REMOVIDO: conflito com reordenação do admin
        # if self.pk and numeracao_anterior is not None and self.numeracao_antiguidade != numeracao_anterior:
        #     print(f"[DEBUG] Numeração alterada de {numeracao_anterior} para {self.numeracao_antiguidade}")
        #     self._deslocar_antiguidade_manual(numeracao_anterior, self.numeracao_antiguidade)
        
        super().save(*args, **kwargs)

        # Reordenação automática quando militar é inativado
        if (situacao_anterior and situacao_anterior == 'AT' and 
            self.situacao in ['IN', 'TR', 'AP', 'EX']):
            # Salvar numeração anterior antes de inativar
            if numeracao_anterior:
                self.numeracao_antiguidade_anterior = numeracao_anterior
                self.numeracao_antiguidade = None
                super().save(update_fields=['numeracao_antiguidade_anterior', 'numeracao_antiguidade'])
            # Militar foi inativado, reordenar antiguidade
            self.reordenar_apos_inativacao()
            # Atualizar vaga correspondente
            self._atualizar_vaga_apos_inativacao()
        
        # Reativação automática quando militar é reativado
        elif (situacao_anterior and situacao_anterior in ['IN', 'TR', 'AP', 'EX'] and 
              self.situacao == 'AT'):
            print(f"[DEBUG] Militar {self.nome_completo} sendo reativado")
            print(f"[DEBUG] Numeração anterior salva: {self.numeracao_antiguidade_anterior}")
            
            if self.numeracao_antiguidade_anterior:
                militares_ativos = Militar.objects.filter(
                    posto_graduacao=self.posto_graduacao,
                    quadro=self.quadro,
                    situacao='AT'
                ).exclude(pk=self.pk)
                print(f"[DEBUG] Militares ativos no mesmo posto/quadro: {militares_ativos.count()}")
                print(f"[DEBUG] Posição {self.numeracao_antiguidade_anterior} ocupada: {militares_ativos.filter(numeracao_antiguidade=self.numeracao_antiguidade_anterior).exists()}")
                
                if not militares_ativos.filter(numeracao_antiguidade=self.numeracao_antiguidade_anterior).exists():
                    print(f"[DEBUG] Restaurando antiguidade {self.numeracao_antiguidade_anterior}")
                    self.numeracao_antiguidade = self.numeracao_antiguidade_anterior
                    self.numeracao_antiguidade_anterior = None
                    super().save(update_fields=['numeracao_antiguidade', 'numeracao_antiguidade_anterior'])
                else:
                    print(f"[DEBUG] Posição ocupada, deslocando demais e inserindo reativado na posição correta")
                    # Deslocar todos os militares daquela posição em diante (+1)
                    militares_para_deslocar = militares_ativos.filter(numeracao_antiguidade__gte=self.numeracao_antiguidade_anterior).order_by('-numeracao_antiguidade')
                    for militar in militares_para_deslocar:
                        militar.numeracao_antiguidade += 1
                    Militar.objects.bulk_update(militares_para_deslocar, ['numeracao_antiguidade'])
                    # Agora inserir o reativado na posição correta
                    self.numeracao_antiguidade = self.numeracao_antiguidade_anterior
                    self.numeracao_antiguidade_anterior = None
                    super().save(update_fields=['numeracao_antiguidade', 'numeracao_antiguidade_anterior'])
            else:
                print(f"[DEBUG] Sem numeração anterior, reordenando todos")
                self.reordenar_apos_reativacao()
            self._atualizar_vaga_apos_reativacao()

        # MUDANÇA AUTOMÁTICA DE QUADRO: Quando militar é promovido de ST para 2T
        if (self.pk and posto_anterior == 'ST' and self.posto_graduacao == '2T' and 
            quadro_anterior == 'PRACAS'):
            # Militar foi promovido de Subtenente para 2º Tenente
            print(f"[DEBUG] Militar {self.nome_completo} promovido de ST para 2T - mudando quadro de PRACAS para COMP")
            self.quadro = 'COMP'  # Complementar para 2º Tenente
            
            # CONVERSÃO AUTOMÁTICA DE FICHA: Converter ficha de praças para oficiais
            ficha_oficiais, mensagem_conversao = self.converter_ficha_pracas_para_oficiais(
                motivo_conversao=f"Promoção automática de ST para 2T: {posto_anterior} -> {self.posto_graduacao}"
            )
            if ficha_oficiais:
                print(f"[DEBUG] Ficha convertida automaticamente para {self.nome_completo}: {mensagem_conversao}")
            else:
                print(f"[DEBUG] Conversão de ficha não realizada para {self.nome_completo}: {mensagem_conversao}")
            
            # Não chamar super().save() aqui para evitar recursão

        # CONVERSÃO AUTOMÁTICA DE FICHA: Quando militar muda do quadro de praças para oficiais
        if (self.pk and quadro_anterior == 'PRACAS' and 
            self.quadro in ['COMB', 'SAUDE', 'ENG', 'COMP'] and
            self.posto_graduacao in ['2T', '1T', 'CP', 'MJ', 'TC', 'CB']):
            # Militar mudou de praças para oficiais
            ficha_oficiais, mensagem_conversao = self.converter_ficha_pracas_para_oficiais(
                motivo_conversao=f"Mudança automática de quadro: {quadro_anterior} -> {self.quadro}"
            )
            if ficha_oficiais:
                print(f"[DEBUG] Ficha convertida automaticamente para {self.nome_completo}: {mensagem_conversao}")
            else:
                print(f"[DEBUG] Conversão de ficha não realizada para {self.nome_completo}: {mensagem_conversao}")

        # Recalcular efetivo atual de Vaga e PrevisaoVaga para posto/quadro anterior e atual
        def recalcular_vagas(posto, quadro):
            mapeamento_postos = {
                'CB': 'CB', 'TC': 'TC', 'MJ': 'MJ', 'CP': 'CP', '1T': '1T', '2T': '2T',
                'ST': 'ST', '1S': '1S', '2S': '2S', '3S': '3S', 'CAB': 'CAB', 'SD': 'SD',
            }
            posto_vaga = mapeamento_postos.get(posto)
            if not posto_vaga:
                return
            try:
                vaga = Vaga.objects.get(posto=posto_vaga, quadro=quadro)
                vaga.efetivo_atual = Militar.objects.filter(
                    posto_graduacao=posto_vaga,
                    quadro=quadro,
                    situacao='AT'
                ).count()
                vaga.save(update_fields=['efetivo_atual'])
            except Vaga.DoesNotExist:
                pass
            try:
                from militares.models import PrevisaoVaga
                previsao = PrevisaoVaga.objects.get(posto=posto_vaga, quadro=quadro, ativo=True)
                previsao.efetivo_atual = Militar.objects.filter(
                    posto_graduacao=posto_vaga,
                    quadro=quadro,
                    situacao='AT'
                ).count()
                previsao.vagas_disponiveis = previsao.calcular_vagas_disponiveis()
                previsao.save(update_fields=['efetivo_atual', 'vagas_disponiveis'])
            except Exception:
                pass
        # Recalcular para o posto/quadro anterior se mudou
        if self.pk and (posto_anterior != self.posto_graduacao or quadro_anterior != self.quadro or situacao_anterior != self.situacao):
            if posto_anterior and quadro_anterior:
                recalcular_vagas(posto_anterior, quadro_anterior)
        # Sempre recalcular para o posto/quadro atual
        recalcular_vagas(self.posto_graduacao, self.quadro)

    def reordenar_apos_inativacao(self):
        """
        Reordena as numerações de antiguidade após a inativação de um militar
        Quando um militar é inativado, os demais "sobem" uma posição:
        - Quem era 4º vira 3º
        - Quem era 5º vira 4º
        - E assim por diante
        """
        if self.situacao not in ['IN', 'TR', 'AP', 'EX']:
            return 0  # Não é inativo
        
        # Buscar todos os militares ativos do mesmo posto e quadro (exceto este)
        militares_mesmo_posto = Militar.objects.filter(
            situacao='AT',
            posto_graduacao=self.posto_graduacao,
            quadro=self.quadro
        ).exclude(pk=self.pk).order_by('numeracao_antiguidade')
        
        if not militares_mesmo_posto.exists():
            return 0  # Não há outros militares para reordenar
        
        # Reordenar: cada militar "sobe" uma posição
        militares_para_atualizar = []
        for i, militar in enumerate(militares_mesmo_posto, 1):
            if militar.numeracao_antiguidade != i:
                militar.numeracao_antiguidade = i
                militares_para_atualizar.append(militar)
        
        # Salvar todas as alterações em lote
        if militares_para_atualizar:
            Militar.objects.bulk_update(militares_para_atualizar, ['numeracao_antiguidade'])
        
        return len(militares_para_atualizar)

    def _atualizar_vaga_apos_inativacao(self):
        """
        Atualiza a vaga correspondente quando um militar é inativado
        Abre automaticamente uma vaga para o posto/quadro do militar inativado
        """
        try:
            # Mapear postos para compatibilidade com modelo Vaga
            mapeamento_postos = {
                'CB': 'CB',    # Coronel
                'TC': 'TC',    # Tenente-Coronel
                'MJ': 'MJ',    # Major
                'CP': 'CP',    # Capitão
                '1T': '1T',    # 1º Tenente
                '2T': '2T',    # 2º Tenente
                'ST': 'ST',    # Subtenente
                '1S': '1S',    # 1º Sargento
                '2S': '2S',    # 2º Sargento
                '3S': '3S',    # 3º Sargento
                'CAB': 'CAB',  # Cabo
                'SD': 'SD',    # Soldado
            }
            
            posto_vaga = mapeamento_postos.get(self.posto_graduacao)
            if not posto_vaga:
                return
            
            # Buscar vaga correspondente
            try:
                vaga = Vaga.objects.get(posto=posto_vaga, quadro=self.quadro)
                # Recalcular efetivo atual (contar militares ativos)
                vaga.efetivo_atual = Militar.objects.filter(
                    posto_graduacao=posto_vaga,
                    quadro=self.quadro,
                    situacao='AT'
                ).count()
                vaga.save(update_fields=['efetivo_atual'])
            except Vaga.DoesNotExist:
                # Se não existe vaga, criar uma nova
                Vaga.objects.create(
                    posto=posto_vaga,
                    quadro=self.quadro,
                    efetivo_atual=0,
                    efetivo_maximo=10  # Valor padrão
                )

            # Atualizar também a PrevisaoVaga correspondente
            from militares.models import PrevisaoVaga
            try:
                previsao = PrevisaoVaga.objects.get(posto=posto_vaga, quadro=self.quadro, ativo=True)
                # Recalcular efetivo atual (contar militares ativos)
                previsao.efetivo_atual = Militar.objects.filter(
                    posto_graduacao=posto_vaga,
                    quadro=self.quadro,
                    situacao='AT'
                ).count()
                previsao.vagas_disponiveis = previsao.calcular_vagas_disponiveis()
                previsao.save(update_fields=['efetivo_atual', 'vagas_disponiveis'])
            except PrevisaoVaga.DoesNotExist:
                pass
        except Exception as e:
            # Log do erro mas não interromper o processo
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao atualizar vaga após inativação do militar {self.pk}: {str(e)}")

    @classmethod
    def reordenar_todos_apos_inativacao(cls, posto_graduacao=None, quadro=None):
        """
        Reordena automaticamente todas as numerações de antiguidade após inativações
        Útil para corrigir numerações que podem ter ficado inconsistentes
        """
        # Filtrar militares
        filtros = {'situacao': 'AT'}
        if posto_graduacao:
            filtros['posto_graduacao'] = posto_graduacao
        if quadro:
            filtros['quadro'] = quadro
        
        militares = cls.objects.filter(**filtros)
        
        # Agrupar por posto/graduação e quadro
        militares_por_grupo = {}
        for militar in militares:
            chave = (militar.posto_graduacao, militar.quadro)
            if chave not in militares_por_grupo:
                militares_por_grupo[chave] = []
            militares_por_grupo[chave].append(militar)
        
        total_reordenados = 0
        
        # Reordenar cada grupo separadamente
        for (posto, quadro), militares_grupo in militares_por_grupo.items():
            # Ordenar por data da promoção atual (mais antiga primeiro)
            militares_ordenados = sorted(
                militares_grupo,
                key=lambda m: m.data_promocao_atual
            )
            
            # Atribuir numerações sequenciais (começando do 1º)
            for i, militar in enumerate(militares_ordenados, 1):
                if militar.numeracao_antiguidade != i:
                    militar.numeracao_antiguidade = i
                    militar.save(update_fields=['numeracao_antiguidade'])
                    total_reordenados += 1
        
        return total_reordenados

    def delete(self, *args, **kwargs):
        # Salvar posto, quadro e situação antes de excluir
        posto_anterior = self.posto_graduacao
        quadro_anterior = self.quadro
        situacao_anterior = self.situacao
        super().delete(*args, **kwargs)
        # Após exclusão, recalcular efetivo e vagas para o posto/quadro anterior
        try:
            from militares.models import PrevisaoVaga, Vaga
            # Atualizar PrevisaoVaga
            previsao = PrevisaoVaga.objects.filter(posto=posto_anterior, quadro=quadro_anterior, ativo=True).first()
            if previsao:
                efetivo_atual = Militar.objects.filter(posto_graduacao=posto_anterior, quadro=quadro_anterior, situacao='AT').count()
                previsao.efetivo_atual = efetivo_atual
                previsao.save()
            # Atualizar Vaga
            vaga = Vaga.objects.filter(posto=posto_anterior, quadro=quadro_anterior).first()
            if vaga:
                efetivo_atual = Militar.objects.filter(posto_graduacao=posto_anterior, quadro=quadro_anterior, situacao='AT').count()
                vaga.efetivo_atual = efetivo_atual
                vaga.save()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao atualizar vagas após exclusão de militar: {e}")

    def reordenar_apos_reativacao(self):
        """
        Reordena as numerações de antiguidade após a reativação de um militar
        Quando um militar é reativado, pode ser necessário reordenar todos
        """
        if self.situacao != 'AT':
            return 0  # Não é ativo
        
        # Buscar todos os militares ativos do mesmo posto e quadro (incluindo este)
        militares_mesmo_posto = Militar.objects.filter(
            situacao='AT',
            posto_graduacao=self.posto_graduacao,
            quadro=self.quadro
        ).order_by('data_promocao_atual')
        
        if not militares_mesmo_posto.exists():
            return 0  # Não há militares para reordenar
        
        # Reordenar: atribuir numerações sequenciais baseadas na data de promoção
        militares_para_atualizar = []
        for i, militar in enumerate(militares_mesmo_posto, 1):
            if militar.numeracao_antiguidade != i:
                militar.numeracao_antiguidade = i
                militares_para_atualizar.append(militar)
        
        # Salvar todas as alterações em lote
        if militares_para_atualizar:
            Militar.objects.bulk_update(militares_para_atualizar, ['numeracao_antiguidade'])
        
        return len(militares_para_atualizar)

    def _atualizar_vaga_apos_reativacao(self):
        """
        Atualiza a vaga correspondente quando um militar é reativado
        """
        try:
            # Mapear postos para compatibilidade com modelo Vaga
            mapeamento_postos = {
                'CB': 'CB',    # Coronel
                'TC': 'TC',    # Tenente-Coronel
                'MJ': 'MJ',    # Major
                'CP': 'CP',    # Capitão
                '1T': '1T',    # 1º Tenente
                '2T': '2T',    # 2º Tenente
                'ST': 'ST',    # Subtenente
                '1S': '1S',    # 1º Sargento
                '2S': '2S',    # 2º Sargento
                '3S': '3S',    # 3º Sargento
                'CAB': 'CAB',  # Cabo
                'SD': 'SD',    # Soldado
            }
            
            posto_vaga = mapeamento_postos.get(self.posto_graduacao)
            if not posto_vaga:
                return
            
            # Buscar vaga correspondente
            try:
                vaga = Vaga.objects.get(posto=posto_vaga, quadro=self.quadro)
                # Recalcular efetivo atual (contar militares ativos)
                vaga.efetivo_atual = Militar.objects.filter(
                    posto_graduacao=posto_vaga,
                    quadro=self.quadro,
                    situacao='AT'
                ).count()
                vaga.save(update_fields=['efetivo_atual'])
            except Vaga.DoesNotExist:
                pass

            # Atualizar também a PrevisaoVaga correspondente
            from militares.models import PrevisaoVaga
            try:
                previsao = PrevisaoVaga.objects.get(posto=posto_vaga, quadro=self.quadro, ativo=True)
                # Recalcular efetivo atual (contar militares ativos)
                previsao.efetivo_atual = Militar.objects.filter(
                    posto_graduacao=posto_vaga,
                    quadro=self.quadro,
                    situacao='AT'
                ).count()
                previsao.vagas_disponiveis = previsao.calcular_vagas_disponiveis()
                previsao.save(update_fields=['efetivo_atual', 'vagas_disponiveis'])
            except PrevisaoVaga.DoesNotExist:
                pass
        except Exception as e:
            # Log do erro mas não interromper o processo
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao atualizar vaga após reativação do militar {self.pk}: {str(e)}")

    def _deslocar_antiguidade_manual(self, numeracao_anterior, numeracao_nova):
        """
        Desloca automaticamente os militares quando a numeração de antiguidade é alterada manualmente
        Exemplo: se militar era 5º e vira 3º, os que eram 3º e 4º viram 4º e 5º
        """
        try:
            # Buscar militares do mesmo posto/quadro (exceto este)
            militares_mesmo_posto = Militar.objects.filter(
                posto_graduacao=self.posto_graduacao,
                quadro=self.quadro,
                situacao='AT'
            ).exclude(pk=self.pk)
            
            print(f"[DEBUG] Deslocando antiguidade: {numeracao_anterior} -> {numeracao_nova}")
            
            if numeracao_nova < numeracao_anterior:
                # Militar "subiu" na antiguidade (ex: 5º -> 1º)
                # Deslocar todos os militares da nova posição até a anterior (+1)
                militares_para_deslocar = militares_mesmo_posto.filter(
                    numeracao_antiguidade__gte=numeracao_nova,
                    numeracao_antiguidade__lte=numeracao_anterior
                ).exclude(pk=self.pk).order_by('-numeracao_antiguidade')
                
                for militar in militares_para_deslocar:
                    militar.numeracao_antiguidade += 1
                
                if militares_para_deslocar:
                    Militar.objects.bulk_update(militares_para_deslocar, ['numeracao_antiguidade'])
                    print(f"[DEBUG] {militares_para_deslocar.count()} militares deslocados para frente")
                    
            elif numeracao_nova > numeracao_anterior:
                # Militar "desceu" na antiguidade (ex: 3º -> 5º)
                # Deslocar todos os militares da anterior até a nova (-1)
                militares_para_deslocar = militares_mesmo_posto.filter(
                    numeracao_antiguidade__gt=numeracao_anterior,
                    numeracao_antiguidade__lte=numeracao_nova
                ).exclude(pk=self.pk).order_by('numeracao_antiguidade')
                
                for militar in militares_para_deslocar:
                    militar.numeracao_antiguidade -= 1
                
                if militares_para_deslocar:
                    Militar.objects.bulk_update(militares_para_deslocar, ['numeracao_antiguidade'])
                    print(f"[DEBUG] {militares_para_deslocar.count()} militares deslocados para trás")
            
            # Se a nova posição já estava ocupada, reordenar todos
            if militares_mesmo_posto.filter(numeracao_antiguidade=numeracao_nova).exists():
                print(f"[DEBUG] Posição {numeracao_nova} já ocupada, reordenando todos")
                self.reordenar_apos_reativacao()
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao deslocar antiguidade manual do militar {self.pk}: {str(e)}")

    def converter_ficha_pracas_para_oficiais(self, motivo_conversao="Mudança de quadro"):
        """
        Converte automaticamente a ficha de conceito de praças para oficiais
        quando um militar muda do quadro de praças para oficiais
        """
        from militares.models import FichaConceitoPracas, FichaConceitoOficiais
        
        # Verificar se existe ficha de praças
        ficha_pracas = self.fichaconceitopracas_set.first()
        if not ficha_pracas:
            return None, "Nenhuma ficha de conceito de praças encontrada"
        
        # Verificar se já existe ficha de oficiais
        if self.fichaconceitooficiais_set.exists():
            return None, "Militar já possui ficha de conceito de oficiais"
        
        try:
            # Criar nova ficha de oficiais com os dados da ficha de praças
            ficha_oficiais = FichaConceitoOficiais.objects.create(
                militar=self,
                # Campos comuns entre praças e oficiais
                tempo_posto=ficha_pracas.tempo_posto,
                cursos_especializacao=ficha_pracas.cursos_especializacao,
                cursos_cfsd=ficha_pracas.cursos_cfsd,
                cursos_chc=ficha_pracas.cursos_chc,
                cursos_chsgt=ficha_pracas.cursos_chsgt,
                cursos_cas=ficha_pracas.cursos_cas,
                cursos_cho=ficha_pracas.cursos_cho,
                cursos_civis_superior=ficha_pracas.cursos_civis_superior,
                cursos_civis_especializacao=ficha_pracas.cursos_civis_especializacao,
                cursos_civis_mestrado=ficha_pracas.cursos_civis_mestrado,
                cursos_civis_doutorado=ficha_pracas.cursos_civis_doutorado,
                medalha_federal=ficha_pracas.medalha_federal,
                medalha_estadual=ficha_pracas.medalha_estadual,
                medalha_cbmepi=ficha_pracas.medalha_cbmepi,
                elogio_individual=ficha_pracas.elogio_individual,
                elogio_coletivo=ficha_pracas.elogio_coletivo,
                punicao_repreensao=ficha_pracas.punicao_repreensao,
                punicao_detencao=ficha_pracas.punicao_detencao,
                punicao_prisao=ficha_pracas.punicao_prisao,
                falta_aproveitamento=ficha_pracas.falta_aproveitamento,
                observacoes=f"Ficha convertida automaticamente: {motivo_conversao}. Original: {ficha_pracas.id}"
            )
            
            # ATUALIZAR DADOS ATUAIS DO MILITAR NA FICHA
            # Marcar cursos inerentes ao novo quadro
            self.marcar_cursos_inerentes_ficha(ficha_oficiais)
            
            # ATUALIZAR TEMPO NO POSTO COM DADOS ATUAIS
            ficha_oficiais.tempo_posto = self.tempo_posto_atual()
            
            # ATUALIZAR CURSOS BASEADO NOS DADOS ATUAIS DO MILITAR
            if self.curso_cho:
                ficha_oficiais.cursos_cho = 1
            if self.curso_cfsd:
                ficha_oficiais.cursos_cfsd = 1
            if self.curso_chc:
                ficha_oficiais.cursos_chc = 1
            if self.curso_chsgt:
                ficha_oficiais.cursos_chsgt = 1
            if self.curso_cas:
                ficha_oficiais.cursos_cas = 1
            if self.curso_superior:
                ficha_oficiais.cursos_civis_superior = 1
            if self.pos_graduacao:
                ficha_oficiais.cursos_civis_especializacao = 1
            
            # Recalcular pontos da ficha
            ficha_oficiais.calcular_pontos()
            
            # Atualizar data de registro da ficha para a data da promoção
            ficha_oficiais.data_registro = self.data_promocao_atual
            ficha_oficiais.save()
            
            # Remover a ficha de praças antiga APÓS salvar a nova
            ficha_pracas.delete()
            
            # ATUALIZAR TEMPO NO POSTO COM DADOS ATUAIS
            ficha_oficiais.tempo_posto = self.tempo_posto_atual()
            
            # ATUALIZAR CURSOS BASEADO NOS DADOS ATUAIS DO MILITAR
            if self.curso_cho:
                ficha_oficiais.cursos_cho = 1
            if self.curso_cfsd:
                ficha_oficiais.cursos_cfsd = 1
            if self.curso_chc:
                ficha_oficiais.cursos_chc = 1
            if self.curso_chsgt:
                ficha_oficiais.cursos_chsgt = 1
            if self.curso_cas:
                ficha_oficiais.cursos_cas = 1
            if self.curso_superior:
                ficha_oficiais.cursos_civis_superior = 1
            if self.pos_graduacao:
                ficha_oficiais.cursos_civis_especializacao = 1
            
            # Recalcular pontos da ficha
            ficha_oficiais.calcular_pontos()
            
            # Atualizar data de registro da ficha para a data da promoção
            ficha_oficiais.data_registro = self.data_promocao_atual
            ficha_oficiais.save()
            
            return ficha_oficiais, f"Ficha convertida com sucesso de praças para oficiais. ID: {ficha_oficiais.id}"
            
        except Exception as e:
            return None, f"Erro ao converter ficha: {str(e)}"


class Intersticio(models.Model):
    """Configuração de interstício mínimo por posto"""
    posto = models.CharField(max_length=4, choices=POSTO_GRADUACAO_CHOICES, verbose_name="Posto")
    quadro = models.CharField(max_length=10, choices=QUADRO_CHOICES, verbose_name="Quadro")
    tempo_minimo_anos = models.PositiveIntegerField(verbose_name="Tempo Mínimo (anos)")
    tempo_minimo_meses = models.PositiveIntegerField(default=0, verbose_name="Tempo Mínimo (meses)")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Interstício"
        verbose_name_plural = "Interstícios"
        unique_together = ['posto', 'quadro']
        ordering = ['quadro', 'posto']
    
    def __str__(self):
        return f"{self.get_posto_display()} - {self.get_quadro_display()} ({self.tempo_minimo_anos}a {self.tempo_minimo_meses}m)"
    
    def tempo_total_meses(self):
        """Retorna o tempo total em meses"""
        return (self.tempo_minimo_anos * 12) + self.tempo_minimo_meses
    
    def tempo_formatado(self):
        """Retorna o tempo formatado para exibição"""
        if self.tempo_minimo_meses == 0:
            return f"{self.tempo_minimo_anos} ano(s)"
        elif self.tempo_minimo_anos == 0:
            return f"{self.tempo_minimo_meses} mês(es)"
        else:
            return f"{self.tempo_minimo_anos} ano(s) e {self.tempo_minimo_meses} mês(es)"
    
    def get_pontuacao_ficha_conceito(self):
        """Calcula a pontuação total da ficha de conceito consolidada"""
        fichas_oficiais = list(self.fichaconceitooficiais_set.all())
        fichas_pracas = list(self.fichaconceitopracas_set.all())
        todas_fichas = fichas_oficiais + fichas_pracas
        return sum(ficha.calcular_pontos() for ficha in todas_fichas)
    
    def apto_quadro_acesso_simples(self):
        """Versão simplificada para verificar se o militar está apto para quadro de acesso"""
        # Verificar se está ativo
        if self.situacao != 'AT':
            return False, "Militar não está em situação ativa"
        
        # Verificar se a inspeção de saúde está vencida (versão simplificada)
        if not self.apto_inspecao_saude:
            return False, "Militar não está apto em inspeção de saúde"
        
        if self.data_validade_inspecao_saude:
            from django.utils import timezone
            hoje = timezone.now().date()
            if self.data_validade_inspecao_saude < hoje:
                return False, "Inspeção de saúde vencida"
        
        # Verificar tempo mínimo no posto (versão simplificada)
        try:
            tempo_posto = self.tempo_posto_atual()
            intersticio_min = self.intersticio_minimo()
            if tempo_posto < intersticio_min:
                return False, f"Tempo no posto insuficiente ({tempo_posto} anos, mínimo {intersticio_min} anos)"
        except:
            return False, "Erro ao calcular tempo no posto"
        
        # Verificar cursos básicos por quadro
        if self.quadro == 'COMB':
            if not self.curso_formacao_oficial:
                return False, "Falta Curso de Formação de Oficial Bombeiro Militar (CFO)"
        elif self.quadro == 'ENG':
            if not self.curso_formacao_oficial:
                return False, "Falta Curso de Formação de Oficial Bombeiro Militar (CFO)"
        elif self.quadro == 'SAUDE':
            if not self.curso_formacao_oficial:
                return False, "Falta Curso de Formação de Oficial Bombeiro Militar (CFO)"
        elif self.quadro == 'COMP':
            if self.posto_graduacao in ['ST', '2T', '1T', 'CP']:
                if not self.curso_cho:
                    return False, "Falta Curso de Habilitação de Oficiais (CHO)"
        
        # Regras específicas para praças
        elif self.posto_graduacao in ['SD', 'CAB', '3S', '2S', '1S', 'ST']:
            # Verificar cursos específicos para praças
            if self.posto_graduacao == 'SD':
                if not self.curso_cfsd:
                    return False, "Falta Curso de Formação de Soldados (CFSD)"
            elif self.posto_graduacao == 'CAB':
                if not self.curso_chc:
                    return False, "Falta Curso de Habilitação de Cabos (CHC)"
            elif self.posto_graduacao in ['3S', '2S', '1S']:
                if not self.curso_chsgt:
                    return False, "Falta Curso de Habilitação de Sargentos (CHSGT)"
            elif self.posto_graduacao == 'ST':
                if not self.curso_cas:
                    return False, "Falta Curso de Aperfeiçoamento de Sargentos (CAS)"
        
        return True, "Apto para quadro de acesso"
    
    def apto_quadro_acesso(self):
        """Verifica se o militar está apto para entrar em quadro de acesso"""
        # Usar a versão simplificada para evitar problemas de carregamento
        return self.apto_quadro_acesso_simples()
    
    def requisitos_ingresso_quadro(self):
        """Retorna os requisitos de ingresso no quadro atual"""
        requisitos = {
            'COMB': {
                'titulo': 'Quadro de Combatente',
                'requisitos': [
                    'Ser oficial do quadro de combatente',
                    'Ter aproveitamento em curso de formação de oficial',
                    'Estar em situação regular',
                    'Não ter punições disciplinares graves',
                    'Inspeção de saúde válida',
                    'Tempo mínimo no posto conforme legislação'
                ]
            },
            'SAUDE': {
                'titulo': 'Quadro de Saúde',
                'requisitos': [
                    'Ser oficial médico, enfermeiro ou farmacêutico',
                    'Ter diploma de curso superior na área',
                    'Estar registrado no conselho profissional',
                    'Ter aproveitamento em curso de formação de oficial',
                    'Estar em situação regular',
                    'Inspeção de saúde válida',
                    'Tempo mínimo no posto conforme legislação'
                ]
            },
            'ENG': {
                'titulo': 'Quadro de Engenheiro',
                'requisitos': [
                    'Ser oficial engenheiro',
                    'Ter diploma de engenharia',
                    'Estar registrado no CREA',
                    'Ter aproveitamento em curso de formação de oficial',
                    'Estar em situação regular',
                    'Inspeção de saúde válida',
                    'Tempo mínimo no posto conforme legislação'
                ]
            },
            'COMP': {
                'titulo': 'Quadro Complementar',
                'requisitos': [
                    'Ser oficial de área específica',
                    'Ter formação superior na área',
                    'Ter aproveitamento em curso de formação de oficial',
                    'Estar em situação regular',
                    'Inspeção de saúde válida',
                    'Tempo mínimo no posto conforme legislação'
                ]
            }
        }
        return requisitos.get(self.quadro, {})

    def get_proxima_promocao_display(self):
        """Retorna o nome da próxima promoção"""
        proxima = self.proxima_promocao()
        if proxima:
            for codigo, nome in self.POSTO_GRADUACAO_CHOICES:
                if codigo == proxima:
                    return nome
        return "Não aplicável"
    
    def requisitos_proxima_promocao(self):
        """Retorna os requisitos específicos para a próxima promoção"""
        proxima = self.proxima_promocao()
        if not proxima:
            return []
        
        requisitos = []
        
        # Regras para Quadro Complementar
        if self.quadro == 'COMP':
            if self.posto_graduacao in ['ST', '2T', '1T']:
                requisitos.append('Curso de Habilitação de Oficiais (CHO)')
            elif self.posto_graduacao == 'CP':
                requisitos.append('Curso de Habilitação de Oficiais (CHO)')
                requisitos.append('Curso Superior')
            elif self.posto_graduacao == 'MJ':
                requisitos.append('Curso de Habilitação de Oficiais (CHO)')
                requisitos.append('Curso Superior')
        
        # Regras para Oficiais (todos os quadros)
        elif self.posto_graduacao in ['AS', '2T', '1T']:
            requisitos.append('Curso de Formação de Oficial Bombeiro Militar')
        elif self.posto_graduacao == 'CP':
            if self.quadro == 'COMP':
                requisitos.append('Curso Superior')
            else:
                requisitos.append('Curso de Formação de Oficial Bombeiro Militar')
                requisitos.append('Curso de Aperfeiçoamento de Oficial Bombeiro Militar')
        elif self.posto_graduacao == 'MJ':
            requisitos.append('Curso de Aperfeiçoamento de Oficial Bombeiro Militar')
        elif self.posto_graduacao in ['TC', 'CB']:
            requisitos.append('Curso de Aperfeiçoamento de Oficial Bombeiro Militar')
            requisitos.append('Curso Superior de Bombeiro Militar (CSBM)')
        
        return requisitos

    def validar_requisitos_promocao(self, posto_destino):
        """Valida requisitos específicos para promoção a um posto de destino"""
        if self.situacao != 'AT':
            return False, "Militar não está em situação ativa"
        
        # Verificar inspeção de saúde
        if self.inspecao_saude_vencida():
            return False, "Inspeção de saúde vencida"
        
        # Verificar tempo mínimo no posto
        tempo_posto = self.tempo_posto_atual()
        intersticio_min = self.intersticio_minimo()
        if tempo_posto < intersticio_min:
            return False, f"Tempo no posto insuficiente ({tempo_posto} anos, mínimo {intersticio_min} anos)"
        
        # Regras específicas para Quadro Complementar
        if self.quadro == 'COMP':
            if self.posto_graduacao in ['ST', '2T', '1T']:
                if not getattr(self, 'curso_cho', False):
                    return False, "Falta Curso de Habilitação de Oficiais (CHO)"
            elif self.posto_graduacao == 'CP':
                if not getattr(self, 'curso_cho', False):
                    return False, "Falta Curso de Habilitação de Oficiais (CHO)"
                if not self.curso_superior:
                    return False, "Falta Curso Superior"
            elif self.posto_graduacao == 'MJ':
                if not getattr(self, 'curso_cho', False):
                    return False, "Falta Curso de Habilitação de Oficiais (CHO)"
                if not self.curso_superior:
                    return False, "Falta Curso Superior"
        
        # Regras para Oficiais (todos os quadros)
        elif self.quadro in ['COMB', 'SAUDE', 'ENG']:
            if posto_destino in ['2T', '1T']:
                if not getattr(self, 'curso_formacao_oficial', False):
                    return False, "Falta Curso de Formação de Oficial Bombeiro Militar"
            elif posto_destino == 'CP':
                if not getattr(self, 'curso_formacao_oficial', False):
                    return False, "Falta Curso de Formação de Oficial Bombeiro Militar"
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False, "Falta Curso de Aperfeiçoamento de Oficial Bombeiro Militar"
            elif posto_destino == 'MJ':
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False, "Falta Curso de Aperfeiçoamento de Oficial Bombeiro Militar"
            elif posto_destino in ['TC', 'CB']:
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False, "Falta Curso de Aperfeiçoamento de Oficial Bombeiro Militar"
                if not getattr(self, 'curso_csbm', False):
                    return False, "Falta Curso Superior de Bombeiro Militar (CSBM)"
        
        # Regras específicas para Quadro Complementar
        elif self.quadro == 'COMP':
            if posto_destino in ['2T', '1T']:
                if not getattr(self, 'curso_formacao_oficial', False):
                    return False, "Falta Curso de Formação de Oficial Bombeiro Militar"
            elif posto_destino == 'CP':
                if not self.curso_superior:
                    return False, "Falta Curso Superior"
            elif posto_destino == 'MJ':
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False, "Falta Curso de Aperfeiçoamento de Oficial Bombeiro Militar"
            elif posto_destino in ['TC', 'CB']:
                if not getattr(self, 'curso_aperfeicoamento_oficial', False):
                    return False, "Falta Curso de Aperfeiçoamento de Oficial Bombeiro Militar"
                if not getattr(self, 'curso_csbm', False):
                    return False, "Falta Curso Superior de Bombeiro Militar (CSBM)"
        
        return True, "Apto para promoção"

    def clean(self):
        super().clean()
        # Limites de posto por quadro
        limites = {
            'COMP': ['ST', '2T', '1T', 'CP', 'MJ', 'TC'],
            'COMB': ['2T', '1T', 'AS', 'CP', 'MJ', 'TC'],
            'ENG':  ['AA', '2T', '1T', 'CP', 'MJ', 'TC'],
            'SAUDE': ['AA', '2T', '1T', 'CP', 'MJ', 'TC'],
        }
        postos_permitidos = limites.get(self.quadro, [])
        if self.posto_graduacao not in postos_permitidos:
            raise ValidationError(f"O quadro {self.get_quadro_display()} só permite até o posto: {postos_permitidos[-1]}.")


class Documento(models.Model):
    """Modelo para upload de documentos da ficha de conceito"""
    
    TIPO_CHOICES = [
        ('DIPLOMA', 'Diploma'),
        ('CERTIFICADO', 'Certificado'),
        ('DECRETO', 'Decreto'),
        ('PORTARIA', 'Portaria'),
        ('ORDEM_SERVICO', 'Ordem de Serviço'),
        ('ELOGIO', 'Elogio'),
        ('PUNICAO', 'Punição'),
        ('OUTROS', 'Outros'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente de Conferência'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
        ('ARQUIVADO', 'Arquivado'),
        ('ASSINADO', 'Assinado'),
    ]
    
    militar = models.ForeignKey(Militar, on_delete=models.CASCADE, verbose_name="Militar")
    ficha_conceito_oficiais = models.ForeignKey('FichaConceitoOficiais', on_delete=models.CASCADE, verbose_name="Ficha de Conceito - Oficiais", null=True, blank=True)
    ficha_conceito_pracas = models.ForeignKey('FichaConceitoPracas', on_delete=models.CASCADE, verbose_name="Ficha de Conceito - Praças", null=True, blank=True)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, verbose_name="Tipo de Documento")
    titulo = models.CharField(max_length=200, verbose_name="Título do Documento")
    arquivo = models.FileField(upload_to=documento_upload_path, verbose_name="Arquivo")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data do Upload")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    conferido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Conferido por")
    data_conferencia = models.DateTimeField(null=True, blank=True, verbose_name="Data da Conferência")
    assinado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Assinado por", related_name="documentos_assinados")
    data_assinatura = models.DateTimeField(null=True, blank=True, verbose_name="Data da Assinatura")
    observacoes_assinatura = models.TextField(blank=True, null=True, verbose_name="Observações da Assinatura")
    funcao_assinatura = models.CharField(max_length=200, blank=True, null=True, verbose_name="Função para Assinatura")
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-data_upload']
    
    def __str__(self):
        return f"{self.militar.nome_completo} - {self.titulo}"
    
    def filename(self):
        return os.path.basename(self.arquivo.name)


class FichaConceitoOficiais(models.Model):
    """Ficha de Conceito para OFICIAIS conforme tabela oficial do CBMEPI"""
    militar = models.ForeignKey(Militar, on_delete=models.CASCADE, verbose_name="Militar")

    # Pontos positivos
    tempo_posto = models.PositiveIntegerField(default=0, verbose_name="Tempo no Posto (anos)")
    cursos_especializacao = models.PositiveIntegerField(default=0, verbose_name="Especialização (militar)")
    cursos_csbm = models.PositiveIntegerField(default=0, verbose_name="CSBM")
    cursos_cfsd = models.PositiveIntegerField(default=0, verbose_name="CFSD")
    cursos_chc = models.PositiveIntegerField(default=0, verbose_name="CHC ou adaptação a Cb")
    cursos_chsgt = models.PositiveIntegerField(default=0, verbose_name="CHSGT ou adaptação a Sgt")
    cursos_cas = models.PositiveIntegerField(default=0, verbose_name="CAS")
    cursos_cho = models.PositiveIntegerField(default=0, verbose_name="CHO")
    cursos_cfo = models.PositiveIntegerField(default=0, verbose_name="CFO")
    cursos_cao = models.PositiveIntegerField(default=0, verbose_name="CÃO")
    cursos_instrutor_csbm = models.PositiveIntegerField(default=0, verbose_name="CSBM (Instrutor)")
    cursos_civis_superior = models.PositiveIntegerField(default=0, verbose_name="Superior (civil)")
    cursos_civis_especializacao = models.PositiveIntegerField(default=0, verbose_name="Especialização (civil)")
    cursos_civis_mestrado = models.PositiveIntegerField(default=0, verbose_name="Mestrado (civil)")
    cursos_civis_doutorado = models.PositiveIntegerField(default=0, verbose_name="Doutorado (civil)")
    medalha_federal = models.PositiveIntegerField(default=0, verbose_name="Medalha Federal")
    medalha_estadual = models.PositiveIntegerField(default=0, verbose_name="Medalha Estadual")
    medalha_cbmepi = models.PositiveIntegerField(default=0, verbose_name="Medalha CBMEPI")
    elogio_individual = models.PositiveIntegerField(default=0, verbose_name="Elogio Individual")
    elogio_coletivo = models.PositiveIntegerField(default=0, verbose_name="Elogio Coletivo")

    # Pontos negativos
    punicao_repreensao = models.PositiveIntegerField(default=0, verbose_name="Repreensão")
    punicao_detencao = models.PositiveIntegerField(default=0, verbose_name="Detenção")
    punicao_prisao = models.PositiveIntegerField(default=0, verbose_name="Prisão")
    falta_aproveitamento = models.PositiveIntegerField(default=0, verbose_name="Falta de Aproveitamento em Cursos Militares")

    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data do Registro")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    pontos = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Total de Pontos Calculado")
    
    class Meta:
        verbose_name = "Ficha de Conceito - Oficiais"
        verbose_name_plural = "Fichas de Conceito - Oficiais"
        unique_together = ("militar",)
        ordering = ["militar"]
    
    def __str__(self):
        return f"Ficha de Conceito - {self.militar.nome_completo} (Oficiais)"
    
    def calcular_pontos(self):
        # Valores de pontuação para OFICIAIS
        valores = {
            # Tempo de Serviço no Posto Atual
            'tempo_posto': 1.0,
            
            # Conclusão de Cursos Militares
            'cursos_especializacao': 2.5,
            'cursos_csbm': 4.0,
            
            # Instrutor em Cursos Militares
            'cursos_cfsd': 0.5,
            'cursos_chc': 0.75,
            'cursos_chsgt': 1.0,
            'cursos_cas': 1.25,
            'cursos_cho': 1.5,
            'cursos_cfo': 1.75,
            'cursos_cao': 3.0,
            'cursos_instrutor_csbm': 2.5,
            
            # Conclusão em Cursos Civis (sem limite)
            'cursos_civis_superior': 1.5,
            'cursos_civis_especializacao': 2.0,
            'cursos_civis_mestrado': 3.0,
            'cursos_civis_doutorado': 4.0,
            
            # Medalhas e Condecorações
            'medalha_federal': 0.5,
            'medalha_estadual': 0.25,
            'medalha_cbmepi': 0.25,
            
            # Elogios
            'elogio_individual': 0.25,
            'elogio_coletivo': 0.125,
            
            # Punições (negativas)
            'punicao_repreensao': -0.25,
            'punicao_detencao': -0.5,
            'punicao_prisao': -1.0,
            'falta_aproveitamento': -0.5,
        }
        
        # Limites para OFICIAIS
        limites = {
            'tempo_posto': 5.0,
            'cursos_militares': 5.0,
            'instrutor_cursos': 10.0,
            'medalhas': 1.0,
            'elogios': 0.25,
            'punicoes': -2.0,
        }
        
        pontos = 0.0
        
        # 1. Tempo no Posto (máximo 5 pontos)
        pontos_tempo = self.tempo_posto * valores['tempo_posto']
        pontos += min(pontos_tempo, limites['tempo_posto'])
        
        # 2. Conclusão de Cursos Militares (máximo 5 pontos)
        pontos_cursos_militares = (
            self.cursos_especializacao * valores['cursos_especializacao'] +
            self.cursos_csbm * valores['cursos_csbm']
        )
        pontos += min(pontos_cursos_militares, limites['cursos_militares'])
        
        # 3. Instrutor em Cursos Militares (máximo 10 pontos)
        pontos_instrutor = (
            self.cursos_cfsd * valores['cursos_cfsd'] +
            self.cursos_chc * valores['cursos_chc'] +
            self.cursos_chsgt * valores['cursos_chsgt'] +
            self.cursos_cas * valores['cursos_cas'] +
            self.cursos_cho * valores['cursos_cho'] +
            self.cursos_cfo * valores['cursos_cfo'] +
            self.cursos_cao * valores['cursos_cao'] +
            self.cursos_instrutor_csbm * valores['cursos_instrutor_csbm']
        )
        pontos += min(pontos_instrutor, limites['instrutor_cursos'])
        
        # 4. Conclusão em Cursos Civis (sem limite)
        pontos_cursos_civis = (
            self.cursos_civis_superior * valores['cursos_civis_superior'] +
            self.cursos_civis_especializacao * valores['cursos_civis_especializacao'] +
            self.cursos_civis_mestrado * valores['cursos_civis_mestrado'] +
            self.cursos_civis_doutorado * valores['cursos_civis_doutorado']
        )
        pontos += pontos_cursos_civis
        
        # 5. Medalhas e Condecorações (máximo 1 ponto)
        pontos_medalhas = (
            self.medalha_federal * valores['medalha_federal'] +
            self.medalha_estadual * valores['medalha_estadual'] +
            self.medalha_cbmepi * valores['medalha_cbmepi']
        )
        pontos += min(pontos_medalhas, limites['medalhas'])
        
        # 6. Elogios (máximo 0,25 pontos)
        pontos_elogios = (
            self.elogio_individual * valores['elogio_individual'] +
            self.elogio_coletivo * valores['elogio_coletivo']
        )
        pontos += min(pontos_elogios, limites['elogios'])
        
        # 7. Punições (máximo -2,0 pontos)
        pontos_punicoes = (
            self.punicao_repreensao * valores['punicao_repreensao'] +
            self.punicao_detencao * valores['punicao_detencao'] +
            self.punicao_prisao * valores['punicao_prisao'] +
            self.falta_aproveitamento * valores['falta_aproveitamento']
        )
        pontos += max(pontos_punicoes, limites['punicoes'])
        
        return round(pontos, 2)
    
    def save(self, *args, **kwargs):
        # Preenche automaticamente o tempo no posto sempre
        self.tempo_posto = self.militar.tempo_posto_atual()
        self.pontos = self.calcular_pontos()  # Garante que o campo pontos está sempre atualizado
        super().save(*args, **kwargs)


class FichaConceitoPracas(models.Model):
    """Ficha de Conceito para PRACAS conforme tabela oficial do CBMEPI"""
    militar = models.ForeignKey(Militar, on_delete=models.CASCADE, verbose_name="Militar")

    # Pontos positivos
    tempo_posto = models.PositiveIntegerField(default=0, verbose_name="Tempo no Posto (anos)")
    cursos_especializacao = models.PositiveIntegerField(default=0, verbose_name="Especialização (militar)")
    cursos_cfsd = models.PositiveIntegerField(default=0, verbose_name="CFSD")
    cursos_chc = models.PositiveIntegerField(default=0, verbose_name="CHC ou adaptação a Cb")
    cursos_chsgt = models.PositiveIntegerField(default=0, verbose_name="CHSGT ou adaptação a Sgt")
    cursos_cas = models.PositiveIntegerField(default=0, verbose_name="CAS")
    cursos_cho = models.PositiveIntegerField(default=0, verbose_name="CHO")
    cursos_civis_tecnico = models.PositiveIntegerField(default=0, verbose_name="Técnico (civil) - carga horária > 1000h")
    cursos_civis_superior = models.PositiveIntegerField(default=0, verbose_name="Superior (civil)")
    cursos_civis_especializacao = models.PositiveIntegerField(default=0, verbose_name="Especialização (civil)")
    cursos_civis_mestrado = models.PositiveIntegerField(default=0, verbose_name="Mestrado (civil)")
    cursos_civis_doutorado = models.PositiveIntegerField(default=0, verbose_name="Doutorado (civil)")
    medalha_federal = models.PositiveIntegerField(default=0, verbose_name="Medalha Federal")
    medalha_estadual = models.PositiveIntegerField(default=0, verbose_name="Medalha Estadual")
    medalha_cbmepi = models.PositiveIntegerField(default=0, verbose_name="Medalha CBMEPI")
    elogio_individual = models.PositiveIntegerField(default=0, verbose_name="Elogio Individual")
    elogio_coletivo = models.PositiveIntegerField(default=0, verbose_name="Elogio Coletivo")

    # Pontos negativos
    punicao_repreensao = models.PositiveIntegerField(default=0, verbose_name="Repreensão")
    punicao_detencao = models.PositiveIntegerField(default=0, verbose_name="Detenção")
    punicao_prisao = models.PositiveIntegerField(default=0, verbose_name="Prisão")
    falta_aproveitamento = models.PositiveIntegerField(default=0, verbose_name="Falta de Aproveitamento em Cursos Militares")

    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data do Registro")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    pontos = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Total de Pontos Calculado")
    
    class Meta:
        verbose_name = "Ficha de Conceito - Praças"
        verbose_name_plural = "Fichas de Conceito - Praças"
        unique_together = ("militar",)
        ordering = ["militar"]
    
    def __str__(self):
        return f"Ficha de Conceito - {self.militar.nome_completo} (Praças)"
    
    def calcular_pontos(self):
        # Valores de pontuação para PRACAS conforme especificação fornecida
        valores = {
            # 1. Tempo de Serviço no Quadro - Na Graduação atual: 1,00 ponto por ano
            'tempo_posto': 1.0,
            
            # 2. Conclusão de Cursos Militares (máximo 4 pontos)
            'cursos_especializacao': 2.0,
            
            # 3. Monitor em cursos militares: (máximo 5 pontos)
            'cursos_cfsd': 0.50,      # CFSD
            'cursos_chc': 0.75,       # CHC ou adaptação a Cabos
            'cursos_chsgt': 1.00,     # CHSGT ou adaptação a Sargentos
            'cursos_cas': 1.25,       # CAS
            'cursos_cho': 1.50,       # CHO
            
            # 4. Conclusão em cursos civis
            'cursos_civis_tecnico': 1.75,    # Técnico com carga horária superior a 1000h
            'cursos_civis_superior': 3.00,   # Superior
            'cursos_civis_especializacao': 4.00,  # Especialização
            'cursos_civis_mestrado': 9.00,   # Mestrado
            'cursos_civis_doutorado': 15.00, # Doutorado
            
            # 5. Medalhas e Condecorações (máximo 1,0 ponto)
            'medalha_federal': 0.50,  # Federal
            'medalha_estadual': 0.30, # Estadual
            'medalha_cbmepi': 0.20,   # CBMEPI
            
            # 6. Elogios (máximo 0,25 ponto)
            'elogio_individual': 0.15, # Individual
            'elogio_coletivo': 0.10,  # Coletivo
            
            # Pontos Negativos
            'punicao_repreensao': -1.0,      # Repreensão
            'punicao_detencao': -2.00,       # Detenção
            'punicao_prisao': -5.00,         # Prisão
            'falta_aproveitamento': -10.00,  # Falta de Aproveitamento em Cursos Militares
        }
        
        # Limites para PRACAS
        limites = {
            'cursos_militares': 4.0,      # Máximo 4 pontos
            'monitor_cursos': 5.0,         # Máximo 5 pontos
            'medalhas': 1.0,              # Máximo 1,0 ponto
            'elogios': 0.25,              # Máximo 0,25 ponto
        }
        
        pontos = 0.0
        
        # 1. Tempo de Serviço no Quadro - Na Graduação atual: 1,00 ponto por ano
        pontos_tempo = self.tempo_posto * valores['tempo_posto']
        pontos += pontos_tempo  # Sem limite máximo
        
        # 2. Conclusão de Cursos Militares (máximo 4 pontos)
        pontos_cursos_militares = (
            self.cursos_especializacao * valores['cursos_especializacao']
        )
        pontos += min(pontos_cursos_militares, limites['cursos_militares'])
        
        # 3. Monitor em cursos militares: (máximo 5 pontos)
        pontos_monitor = (
            self.cursos_cfsd * valores['cursos_cfsd'] +
            self.cursos_chc * valores['cursos_chc'] +
            self.cursos_chsgt * valores['cursos_chsgt'] +
            self.cursos_cas * valores['cursos_cas'] +
            self.cursos_cho * valores['cursos_cho']
        )
        pontos += min(pontos_monitor, limites['monitor_cursos'])
        
        # 4. Conclusão em cursos civis (sem limite)
        pontos_cursos_civis = (
            self.cursos_civis_tecnico * valores['cursos_civis_tecnico'] +
            self.cursos_civis_superior * valores['cursos_civis_superior'] +
            self.cursos_civis_especializacao * valores['cursos_civis_especializacao'] +
            self.cursos_civis_mestrado * valores['cursos_civis_mestrado'] +
            self.cursos_civis_doutorado * valores['cursos_civis_doutorado']
        )
        pontos += pontos_cursos_civis
        
        # 5. Medalhas e Condecorações (máximo 1,0 ponto)
        pontos_medalhas = (
            self.medalha_federal * valores['medalha_federal'] +
            self.medalha_estadual * valores['medalha_estadual'] +
            self.medalha_cbmepi * valores['medalha_cbmepi']
        )
        pontos += min(pontos_medalhas, limites['medalhas'])
        
        # 6. Elogios (máximo 0,25 ponto)
        pontos_elogios = (
            self.elogio_individual * valores['elogio_individual'] +
            self.elogio_coletivo * valores['elogio_coletivo']
        )
        pontos += min(pontos_elogios, limites['elogios'])
        
        # 7. Pontos Negativos (sem limite mínimo)
        pontos_negativos = (
            self.punicao_repreensao * valores['punicao_repreensao'] +
            self.punicao_detencao * valores['punicao_detencao'] +
            self.punicao_prisao * valores['punicao_prisao'] +
            self.falta_aproveitamento * valores['falta_aproveitamento']
        )
        pontos += pontos_negativos
        
        return round(pontos, 2)
    
    def save(self, *args, **kwargs):
        # Preenche automaticamente o tempo no posto sempre
        self.tempo_posto = self.militar.tempo_posto_atual()
        self.pontos = self.calcular_pontos()  # Garante que o campo pontos está sempre atualizado
        super().save(*args, **kwargs)


class QuadroAcesso(models.Model):
    """Quadro de Acesso para Promoções conforme Lei 5.461/2005"""
    
    TIPO_CHOICES = [
        ('ANTIGUIDADE', 'Quadro de Acesso por Antiguidade'),
        ('MERECIMENTO', 'Quadro de Acesso por Merecimento'),
    ]
    
    POSTO_CHOICES = [
        ('AS', 'Aspirante a Oficial'),
        ('AA', 'Aluno de Adaptação'),
        ('2T', '2º Tenente'),
        ('1T', '1º Tenente'),
        ('CP', 'Capitão'),
        ('MJ', 'Major'),
        ('TC', 'Tenente-Coronel'),
        ('CB', 'Coronel'),
        ('ST', 'Subtenente'),
        ('1S', '1º Sargento'),
        ('2S', '2º Sargento'),
        ('3S', '3º Sargento'),
        ('CAB', 'Cabo'),
        ('SD', 'Soldado'),
    ]
    
    QUADRO_CHOICES = [
        ('COMB', 'Combatente'),
        ('SAUDE', 'Saúde'),
        ('ENG', 'Engenheiro'),
        ('COMP', 'Complementar'),
        ('NVRR', 'NVRR'),
        ('PRACAS', 'Praças'),
    ]
    
    STATUS_CHOICES = [
        ('ELABORADO', 'Elaborado'),
        ('NAO_ELABORADO', 'Não Elaborado'),
        ('EM_ELABORACAO', 'Em Elaboração'),
        ('HOMOLOGADO', 'Homologado'),
        ('ASSINADO', 'Assinado'),
    ]
    
    MOTIVO_NAO_ELABORACAO_CHOICES = [
        ('SEM_VAGA', 'Inexistência de vaga'),
        ('SEM_REQUISITOS', 'Não há militar que satisfaça os requisitos essenciais'),
        ('SEM_EFETIVO', 'Sem efetivo suficiente'),
        ('OUTROS', 'Outros motivos'),
    ]
    
    numero = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Numeração do Quadro",
        help_text="Numeração automática e única, ex: QAA-OF-2025/07/18 ou QAA-OF-2025/07/18 - A 01"
    )
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, verbose_name="Tipo")
    categoria = models.CharField(
        max_length=10, 
        choices=[
            ('OFICIAIS', 'Oficiais'),
            ('PRACAS', 'Praças')
        ],
        default='OFICIAIS',
        verbose_name="Categoria"
    )
    data_promocao = models.DateField(verbose_name="Data da Promoção")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='EM_ELABORACAO', verbose_name="Status")

    motivo_nao_elaboracao = models.CharField(max_length=20, choices=MOTIVO_NAO_ELABORACAO_CHOICES, blank=True, null=True, verbose_name="Motivo da Não Elaboração")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    data_homologacao = models.DateField(null=True, blank=True, verbose_name="Data de Homologação")
    homologado_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Homologado por", related_name="quadros_homologados")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Quadro de Acesso"
        verbose_name_plural = "Quadros de Acesso"
        # Constraint apenas para quadros automáticos (não manuais)
        # Quadros manuais podem ser repetidos quantas vezes quiser
        ordering = ['-data_promocao', 'tipo']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - Quadro Completo - {self.data_promocao}"
    
    def save(self, *args, **kwargs):
        if not self.numero:
            ano = self.data_promocao.year
            mes = self.data_promocao.month
            dia = self.data_promocao.day
            tipo_prefixo = 'OF' if self.categoria == 'OFICIAIS' else 'PR'

            # Determinar critério para base_numero e busca
            criterio = self.tipo

            # Prefixo do quadro
            if criterio == 'ANTIGUIDADE':
                quadro_prefixo = 'QAA'
            elif criterio == 'MERECIMENTO':
                quadro_prefixo = 'QAM'
            else:
                quadro_prefixo = 'QAA'

            base_numero = f"{quadro_prefixo}-{tipo_prefixo}-{ano:04d}/{mes:02d}/{dia:02d}"

            # Buscar todos os quadros com a mesma data, categoria e critério
            quadros_existentes = QuadroAcesso.objects.filter(
                data_promocao=self.data_promocao,
                categoria=self.categoria,
                tipo=self.tipo
            ).exclude(pk=self.pk).order_by('data_criacao')

            if quadros_existentes.exists():
                # Já existe um quadro principal, este será um aditamento
                ultimo_aditamento = quadros_existentes.filter(
                    numero__contains='-A'
                ).order_by('numero').last()
                
                if ultimo_aditamento:
                    # Extrair o número do último aditamento
                    numero_ultimo = ultimo_aditamento.numero
                    if '-A' in numero_ultimo:
                        try:
                            num_aditamento = int(numero_ultimo.split('-A')[-1])
                            novo_numero = f"{base_numero}-A{num_aditamento + 1:02d}"
                        except ValueError:
                            novo_numero = f"{base_numero}-A01"
                    else:
                        novo_numero = f"{base_numero}-A01"
                else:
                    # Primeiro aditamento
                    novo_numero = f"{base_numero}-A01"
            else:
                # Primeiro quadro (principal)
                novo_numero = f"{base_numero}-01"

            self.numero = novo_numero

        super().save(*args, **kwargs)
    
    def get_geracao_display(self):
        """Retorna a geração em formato legível (01, 02, 03... ou 1º Aditamento, etc.)"""
        if not self.numero:
            return "N/A"
        
        # Se não tem " A " no número, é o quadro principal - extrai o número sequencial
        if ' A ' not in self.numero:
            try:
                # Extrai o número sequencial do final (ex: QAA-OF-2025/07/18 - 01)
                seq_part = self.numero.split(' - ')[1]
                seq_num = int(seq_part)
                return f"{seq_num:02d}"
            except (ValueError, IndexError):
                return "Quadro Principal"
        
        # Extrai o número do aditamento
        try:
            aditamento_part = self.numero.split(' A ')[1]
            aditamento_num = int(aditamento_part)
            
            # Mapeia números para nomes
            aditamentos = {
                1: "1º Aditamento",
                2: "2º Aditamento", 
                3: "3º Aditamento",
                4: "4º Aditamento",
                5: "5º Aditamento",
                6: "6º Aditamento",
                7: "7º Aditamento",
                8: "8º Aditamento",
                9: "9º Aditamento",
                10: "10º Aditamento",
                11: "11º Aditamento",
                12: "12º Aditamento",
                13: "13º Aditamento",
                14: "14º Aditamento",
                15: "15º Aditamento",
                16: "16º Aditamento",
                17: "17º Aditamento",
                18: "18º Aditamento",
                19: "19º Aditamento",
                20: "20º Aditamento"
            }
            
            return aditamentos.get(aditamento_num, f"{aditamento_num}º Aditamento")
        except (ValueError, IndexError):
            return "N/A"
    
    def clean(self):
        """Validação customizada - permite aditamentos através da numeração automática"""
        super().clean()
        
        # Removida a validação que bloqueava quadros para a mesma data/tipo
        # Agora o sistema de numeração automática gerencia os aditamentos
        # O método save() já gera números únicos para cada quadro (principal ou aditamento)
    
    def get_titulo_completo(self):
        """Retorna o título completo do quadro"""
        # Usar sempre o tipo do quadro (ANTIGUIDADE ou MERECIMENTO)
        tipo_display = self.get_tipo_display()
        
        # Verificar se é um aditamento
        if self.numero and ' A ' in self.numero:
            # É um aditamento - incluir a informação do aditamento
            geracao_display = self.get_geracao_display()
            return f"{tipo_display} - {geracao_display} - {self.data_promocao.strftime('%d/%m/%Y')}"
        else:
            # É um quadro principal
            return f"{tipo_display} - Quadro Completo - {self.data_promocao.strftime('%d/%m/%Y')}"
    
    def get_motivo_display_completo(self):
        """Retorna o motivo completo da não elaboração"""
        if self.status == 'NAO_ELABORADO' and self.motivo_nao_elaboracao:
            motivos = {
                'SEM_VAGA': 'inexistência de vaga, nos termos do art. 4, § 1º da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022',
                'SEM_REQUISITOS': 'não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do art. 12 da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022',
                'SEM_EFETIVO': 'não haver efetivo suficiente para elaboração do quadro',
                'OUTROS': self.observacoes or 'motivos diversos'
            }
            return motivos.get(self.motivo_nao_elaboracao, '')
        return ''
    
    def total_militares(self):
        """Retorna o total de militares no quadro"""
        return self.itemquadroacesso_set.count()
    
    def militares_aptos(self):
        """Retorna militares aptos para o quadro completo com validações específicas"""
        # Usar sempre o tipo do quadro (ANTIGUIDADE ou MERECIMENTO)
        criterio = self.tipo
        
        # Buscar militares candidatos baseado no tipo e categoria
        if self.categoria == 'OFICIAIS':
            if criterio == 'MERECIMENTO':
                # Para merecimento, apenas oficiais a partir de Capitão (sem exigir ficha de conceito)
                militares_candidatos = Militar.objects.filter(
                    situacao='AT',
                    quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP'],
                    posto_graduacao__in=['CP', 'MJ', 'TC']  # Removido 'CB'
                )
            else:
                # Para antiguidade, todos os oficiais EXCETO Tenente-Coronel (que só pode ser promovido por merecimento)
                militares_candidatos = Militar.objects.filter(
                    situacao='AT',
                    quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP']
                ).exclude(posto_graduacao='TC')
                
                # Para quadros de oficiais, incluir também subtenentes do quadro PRACAS (transição ST->2T)
                # Isso permite que subtenentes do quadro PRACAS sejam considerados para promoção a 2º Tenente do COMP
                subtenentes_pracas = Militar.objects.filter(
                    situacao='AT',
                    quadro='PRACAS',
                    posto_graduacao='ST'
                )
                # Converter para lista para evitar problemas com UNION e ORDER BY
                militares_candidatos = list(militares_candidatos) + list(subtenentes_pracas)
        elif self.categoria == 'PRACAS':
            if criterio == 'MERECIMENTO':
                # Para merecimento, apenas praças a partir de 2º Sargento (excluindo Subtenente) - sem exigir ficha de conceito
                militares_candidatos = Militar.objects.filter(
                    situacao='AT',
                    quadro='PRACAS',
                    posto_graduacao__in=['2S', '1S']
                )
            else:
                # Para antiguidade, todas as praças EXCETO Subtenente
                militares_candidatos = Militar.objects.filter(
                    situacao='AT',
                    quadro='PRACAS'
                ).exclude(posto_graduacao='ST')
        else:
            militares_candidatos = Militar.objects.none()
        
        # Aplicar validações rigorosas
        militares_aptos = []
        for militar in militares_candidatos:
            # Excluir coronéis (CB) pois não têm próximo posto para promoção
            if militar.posto_graduacao == 'CB':
                continue
            apto, motivo = self.validar_requisitos_quadro_acesso(militar)
            if apto:
                militares_aptos.append(militar)
        
        return militares_aptos
    
    def militares_inaptos_com_motivo(self):
        """Retorna militares inaptos com seus respectivos motivos"""
        # Filtrar militares por categoria do quadro (OFICIAIS ou PRACAS)
        if self.categoria == 'OFICIAIS':
            # Para quadros de oficiais, buscar apenas oficiais
            militares_candidatos = Militar.objects.filter(
                situacao='AT',
                quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP']
            )
        elif self.categoria == 'PRACAS':
            # Para quadros de praças, buscar apenas praças
            militares_candidatos = Militar.objects.filter(
                situacao='AT',
                quadro='PRACAS'
            )
        else:
            # Caso não tenha categoria definida, buscar todos os ativos
            militares_candidatos = Militar.objects.filter(situacao='AT')
        
        militares_inaptos = []
        for militar in militares_candidatos:
            apto, motivo = self.validar_requisitos_quadro_acesso(militar)
            if not apto:
                militares_inaptos.append({
                    'militar': militar,
                    'motivo': motivo
                })
        
        return militares_inaptos
    
    def validar_requisitos_quadro_acesso(self, militar, data_promocao=None):
        """Valida se o militar atende aos requisitos para ingressar no quadro de acesso"""
        if not data_promocao:
            data_promocao = self.data_promocao
        
        # Determinar o critério de ordenação (agora só existe self.tipo)
        criterio = self.tipo
        
        # 1. Verificar interstício mínimo até a data da promoção
        if not self._validar_intersticio_minimo(militar, data_promocao):
            return False, "Militar não completou o interstício mínimo até a data da promoção"
        
        # 2. Verificar inspeção de saúde em dia até a data da geração do quadro
        if not self._validar_inspecao_saude(militar):
            return False, "Militar não possui inspeção de saúde em dia"
        
        # 3. Verificar cursos inerentes ao posto atual para o posto subsequente
        if not self._validar_cursos_inerentes(militar):
            return False, "Militar não possui os cursos inerentes necessários para o posto subsequente"
        
        return True, "Militar apto para o quadro de acesso"
    
    def _validar_intersticio_minimo(self, militar, data_promocao):
        """Valida se o militar completou o interstício mínimo até a data da promoção"""
        # Calcular tempo no posto até a data da promoção
        data_promocao_atual = militar.data_promocao_atual
        if not data_promocao_atual:
            return False
        
        # Calcular anos e meses entre a promoção atual e a data da promoção
        anos = data_promocao.year - data_promocao_atual.year
        meses = data_promocao.month - data_promocao_atual.month
        
        if meses < 0:
            anos -= 1
            meses += 12
        
        tempo_total_meses = anos * 12 + meses
        
        # Obter interstício mínimo configurado
        try:
            intersticio = Intersticio.objects.get(
                posto=militar.posto_graduacao,
                quadro=militar.quadro,
                ativo=True
            )
            intersticio_minimo = intersticio.tempo_total_meses()
        except Intersticio.DoesNotExist:
            # Fallback para valores padrão
            intersticios_padrao = {
                'AS': 6, '2T': 36, '1T': 48, 'CP': 48, 'MJ': 48, 'TC': 36, 'ST': 36
            }
            intersticio_minimo = intersticios_padrao.get(militar.posto_graduacao, 0)
        
        return tempo_total_meses >= intersticio_minimo
    
    def _validar_inspecao_saude(self, militar):
        """Valida se o militar possui inspeção de saúde em dia"""
        if not militar.apto_inspecao_saude:
            return False
        
        # Verificar se tem data de validade e se está em dia
        if militar.data_validade_inspecao_saude:
            hoje = timezone.now().date()
            return militar.data_validade_inspecao_saude >= hoje
        
        # Se não tem data de validade, verificar se tem data da inspeção
        if militar.data_inspecao_saude:
            # Considerar válida por 2 anos se não há data de validade específica
            hoje = timezone.now().date()
            validade_estimada = militar.data_inspecao_saude + timezone.timedelta(days=730)  # 2 anos
            return validade_estimada >= hoje
        
        return False
    
    def _validar_cursos_inerentes(self, militar):
        """
        Valida se o militar possui os cursos inerentes necessários para o posto subsequente,
        considerando todos os quadros e postos (inclusive praças, se aplicável).
        O militar só será considerado apto se possuir todos os cursos obrigatórios para a transição.
        """
        proximo_posto = self._obter_proximo_posto(militar.posto_graduacao)
        if not proximo_posto:
            return True  # Não há promoção possível, não exige cursos

        # Dicionário de cursos obrigatórios por quadro e transição de posto
        cursos_obrigatorios = {
            'COMB': {
                'ST':   ['curso_cho'],
                '2T':  ['curso_formacao_oficial'],
                '1T':  ['curso_formacao_oficial'],
                'CP':  ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial'],
                'MJ':  ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial'],
                'TC':  ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial', 'curso_csbm'],
            },
            'SAUDE': {
                '2T':  ['curso_formacao_oficial'],
                '1T':  ['curso_formacao_oficial'],
                'CP':  ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial'],
                'MJ':  ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial'],
                'TC':  ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial', 'curso_csbm'],
            },
            'ENG': {
                'AS':  ['curso_adaptacao_oficial'],
                '2T':  ['curso_formacao_oficial'],
                '1T':  ['curso_formacao_oficial'],
                'CP':  ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial'],
                'MJ':  ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial'],
                'TC':  ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial', 'curso_csbm'],
            },
            'COMP': {
                'ST':  ['curso_cho'],
                '2T':  ['curso_cho'],
                '1T':  ['curso_cho'],
                'CP':  ['curso_cho', 'curso_superior'],
                'MJ':  ['curso_cho', 'curso_superior', 'pos_graduacao'],
                'TC':  ['curso_cho', 'curso_superior', 'pos_graduacao', 'curso_csbm'],
            },
            # Requisitos específicos para promoção por antiguidade de praças:
            'PRACAS': {
                'SD':  ['curso_cfsd'],  # Soldado precisa de CFSD OU Curso de Formação de Praças para promoção a Cabo
                'CAB':  ['curso_cfsd', 'curso_chc'],  # Cabo precisa de CFSD + CHC para promoção a 3º Sargento
                '3S':  ['curso_cfsd', 'curso_chc', 'curso_chsgt'],  # 3º Sargento precisa de CFSD + CHC + CHSGT para promoção a 2º Sargento
                '2S':  ['curso_cfsd', 'curso_chc', 'curso_chsgt', 'curso_cas'],  # 2º Sargento precisa de todos os cursos para promoção a 1º Sargento
                '1S':  ['curso_cfsd', 'curso_chc', 'curso_chsgt', 'curso_cas'],  # 1º Sargento precisa de todos os cursos para promoção a Subtenente
                'ST':  ['curso_cho'],  # Subtenente precisa de CHO para promoção a 2º Tenente
            },
        }

        quadro = militar.quadro if militar.quadro in cursos_obrigatorios else 'PRACAS'
        cursos_necessarios = cursos_obrigatorios.get(quadro, {}).get(militar.posto_graduacao, [])

        if not cursos_necessarios:
            return True  # Não há cursos obrigatórios definidos para esta transição

        # Regras específicas para promoção por antiguidade de praças
        if quadro == 'PRACAS':
            # Soldado → Cabo: precisa de CFSD OU Curso de Formação de Praças
            if militar.posto_graduacao == 'SD':
                return militar.curso_cfsd or militar.curso_formacao_pracas
            
            # Cabo → 3º Sargento: precisa de CFSD + CHC
            elif militar.posto_graduacao == 'CAB':
                return militar.curso_cfsd and militar.curso_chc
            
            # 3º Sargento → 2º Sargento: precisa de CFSD + CHC + CHSGT
            elif militar.posto_graduacao == '3S':
                return militar.curso_cfsd and militar.curso_chc and militar.curso_chsgt
            
            # 2º Sargento → 1º Sargento: precisa de CFSD + CHC + CHSGT + CAS
            elif militar.posto_graduacao == '2S':
                return (militar.curso_cfsd and militar.curso_chc and 
                       militar.curso_chsgt and militar.curso_cas)
            
            # 1º Sargento → Subtenente: precisa de CFSD + CHC + CHSGT + CAS
            elif militar.posto_graduacao == '1S':
                return (militar.curso_cfsd and militar.curso_chc and 
                       militar.curso_chsgt and militar.curso_cas)
            
            # Subtenente → 2º Tenente: precisa de CHO
            elif militar.posto_graduacao == 'ST':
                return militar.curso_cho
        
        # Para outros quadros, verificar se possui todos os cursos necessários
        for curso in cursos_necessarios:
            if not getattr(militar, curso, False):
                return False
        return True
    
    def _obter_proximo_posto(self, posto_atual):
        """Retorna o próximo posto na hierarquia"""
        proximas_promocoes = {
            'AS': '2T', '2T': '1T', '1T': 'CP', 'CP': 'MJ', 'MJ': 'TC', 'TC': 'CB',
            'ST': '2T', 'SD': 'CAB', 'CAB': '3S', '3S': '2S', '2S': '1S', '1S': 'ST'
        }
        return proximas_promocoes.get(posto_atual)
    
    def determinar_tipo_quadro_por_transicao(self, posto_origem, posto_destino):
        """
        Determina o tipo de quadro baseado na transição de posto
        Regras:
        - Até 1º Tenente em todos os quadros: SÓ por antiguidade
        - De Capitão para frente: ambas as situações (antiguidade E merecimento), exceto Coronel que é só por merecimento
        - Para praças: SD→CAB, CAB→3S, 3S→2S por antiguidade; 2S→1S, 1S→ST por AMBOS os critérios
        """
        transicao = f"{posto_origem}→{posto_destino}"
        
        # Transições só por antiguidade (até 1º Tenente)
        transicoes_antiguidade = ['AS→2T', 'CADOF→2T', 'ST→2T', '2T→1T', '1T→CP']
        
        # Transições só por merecimento
        transicoes_merecimento = ['TC→CB']  # Tenente-Coronel → Coronel (só merecimento)
        
        # Transições que permitem ambos os critérios (de Capitão para frente, exceto Coronel)
        transicoes_ambos = ['CP→MJ', 'MJ→TC']  # Capitão → Major, Major → Tenente-Coronel
        
        # Transições de praças por antiguidade
        transicoes_pracas_antiguidade = ['SD→CAB', 'CAB→3S', '3S→2S']
        
        # Transições de praças que permitem ambos os critérios
        transicoes_pracas_ambos = ['2S→1S', '1S→ST']
        
        if transicao in transicoes_pracas_antiguidade:
            return 'ANTIGUIDADE'  # Promoções de praças por antiguidade
        elif transicao in transicoes_pracas_ambos:
            return 'AMBOS'  # Promoções de praças por ambos os critérios
        elif transicao in transicoes_antiguidade:
            return 'ANTIGUIDADE'
        elif transicao in transicoes_merecimento:
            return 'MERECIMENTO'
        elif transicao in transicoes_ambos:
            # Para estas transições, o tipo será determinado pelo tipo do quadro criado
            # Se o quadro for de antiguidade, usa antiguidade; se for de merecimento, usa merecimento
            return 'AMBOS'  # Indica que ambos os critérios são permitidos
        else:
            # Para outras transições, manter compatibilidade
            return 'ANTIGUIDADE'  # padrão
    
    def pode_ser_elaborado(self):
        """Verifica se o quadro pode ser elaborado"""
        if self.status == 'NAO_ELABORADO':
            return False
        
        militares_aptos = self.militares_aptos()
        return militares_aptos.exists()
    
    def gerar_quadro_automatico(self):
        """Gera o quadro de acesso completo automaticamente incluindo todos os postos e quadros"""
        return self.gerar_quadro_completo()
    
    def _ordenar_por_antiguidade(self, militares_aptos):
        """Ordena militares por antiguidade dentro de cada posto/graduação"""
        from itertools import groupby
        
        # Definir ordem dos postos (do mais graduado ao menos graduado)
        ordem_postos = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        
        militares_ordenados = []
        
        # Agrupar militares por posto/graduação
        for militar in militares_aptos:
            # Usar data da última promoção como critério principal
            data_promocao = militar.data_promocao_atual
            if not data_promocao:
                data_promocao = militar.data_ingresso  # Fallback para data de ingresso
            
            # Numeração de antiguidade como critério de desempate
            numeracao = militar.numeracao_antiguidade or 999999
            
            # Para cabos com CHSGT, usar nota do curso como critério principal
            nota_chsgt = None
            if militar.posto_graduacao == 'CAB' and militar.curso_chsgt:
                nota_chsgt = militar.nota_chsgt or 0
            
            # Para soldados com CHC, usar nota do curso como critério principal
            nota_chc = None
            if militar.posto_graduacao == 'SD' and militar.curso_chc:
                nota_chc = militar.nota_chc or 0
            
            militares_ordenados.append({
                'militar': militar,
                'data_promocao': data_promocao,
                'numeracao_antiguidade': numeracao,
                'data_ingresso': militar.data_ingresso,
                'quadro': militar.quadro,
                'posto': militar.posto_graduacao,
                'nota_chsgt': nota_chsgt,
                'nota_chc': nota_chc
            })
        
        # Ordenar por posto (mais graduado primeiro) e depois por antiguidade dentro de cada posto
        # Para cabos, ordenar por nota do CHSGT (maior nota primeiro) e depois por antiguidade
        # Para soldados, ordenar por nota do CHC (maior nota primeiro) e depois por antiguidade
        militares_ordenados.sort(key=lambda x: (
            ordem_postos.index(x['posto']) if x['posto'] in ordem_postos else 999,
            # Para cabos com CHSGT, ordenar por nota (maior primeiro) e depois por antiguidade
            # Para soldados com CHC, ordenar por nota (maior primeiro) e depois por antiguidade
            -(x['nota_chsgt'] or 0) if x['posto'] == 'CAB' and x['nota_chsgt'] is not None else (
                -(x['nota_chc'] or 0) if x['posto'] == 'SD' and x['nota_chc'] is not None else 0
            ),
            x['data_promocao'],
            x['numeracao_antiguidade']
        ))
        
        return militares_ordenados
    
    def _ordenar_por_merecimento(self, militares_aptos):
        """Ordena militares por merecimento (pontuação da ficha de conceito)"""
        militares_ordenados = []
        for militar in militares_aptos:
            ficha = militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
            pontuacao = ficha.pontos if ficha else 0
            militares_ordenados.append({
                'militar': militar,
                'pontuacao': pontuacao,
                'data_promocao': militar.data_promocao_atual,
                'data_ingresso': militar.data_ingresso
            })
        
        # Ordenar por pontuação (decrescente - maior pontuação primeiro) e depois por data de promoção (crescente) como desempate
        militares_ordenados.sort(key=lambda x: (-x['pontuacao'], x['data_promocao']))
        return militares_ordenados
    
    def get_criterio_ordenacao(self):
        """Retorna o critério de ordenação do quadro"""
        if self.tipo == 'ANTIGUIDADE':
            return "Posto/Graduação → Data da Última Promoção → Numeração de Antiguidade (dentro de cada posto). Para Cabos com CHSGT: Nota do CHSGT (maior nota primeiro) → Antiguidade. Para Soldados com CHC: Nota do CHC (maior nota primeiro) → Antiguidade."
        elif self.tipo == 'MERECIMENTO':
            return "Posto/Graduação → Pontuação da Ficha de Conceito (maior pontuação primeiro, dentro de cada posto)"
        else:
            return "Ordem de inclusão (posição definida pelo usuário)"
    
    def adicionar_militar_manual(self, militar, posicao=None, pontuacao=0, motivo_insercao='AUTOMATICO', 
                                observacoes_insercao=None, documento_referencia=None, data_documento=None):
        """Adiciona um militar manualmente ao quadro, garantindo que não será listado em quadros de oficiais e praças ao mesmo tempo."""
        if self.status == 'HOMOLOGADO':
            raise ValueError("Quadros homologados não podem ser editados")

        # Verificar se o militar já está neste quadro
        if self.itemquadroacesso_set.filter(militar=militar).exists():
            raise ValueError(f"O militar {militar.nome_completo} já está no quadro")

        # Para inserções manuais, permitir qualquer militar por motivos especiais
        # Apenas verificar se está ativo
        if militar.situacao != 'AT':
            raise ValueError(f"Apenas militares em situação ativa podem ser adicionados ao quadro. ({militar.nome_completo})")
        
        print(f"DEBUG: Validando militar {militar.nome_completo} ({militar.posto_graduacao}) para quadro {self.categoria}")

        # Determinar se é inserção manual ou automática
        inserido_manualmente = motivo_insercao != 'AUTOMATICO'

        # Determinar posição e pontuação baseado no tipo do quadro
        if self.tipo == 'ANTIGUIDADE':
            pontuacao = militar.numeracao_antiguidade or 999999
            posicao = None  # Será calculada automaticamente
        elif self.tipo == 'MERECIMENTO':
            ficha = militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
            if ficha:
                pontuacao = float(ficha.pontos)
            else:
                pontuacao = 0
            posicao = None  # Será calculada automaticamente
        else:
            # Para outros tipos, usar posição automática
            if posicao is None:
                ultima_posicao = self.itemquadroacesso_set.aggregate(
                    models.Max('posicao')
                )['posicao__max'] or 0
                posicao = ultima_posicao + 1

        # Criar o item do quadro com os novos campos
        item = ItemQuadroAcesso(
            quadro_acesso=self,
            militar=militar,
            posicao=posicao or 1,
            pontuacao=pontuacao,
            inserido_manualmente=inserido_manualmente,
            motivo_insercao=motivo_insercao,
            observacoes_insercao=observacoes_insercao,
            documento_referencia=documento_referencia,
            data_documento=data_documento
        )
        item.full_clean()  # Chama clean() e validações do modelo
        item.save()
        
        print(f"DEBUG: Item criado para {militar.nome_completo} - posição {item.posicao}, pontuação {item.pontuacao}, manual: {inserido_manualmente}")

        # Se for ordenação automática, reordenar
        if self.tipo in ['ANTIGUIDADE', 'MERECIMENTO']:
            self._reordenar_por_criterio()

        # Atualizar status do quadro
        if self.status == 'EM_ELABORACAO':
            self.status = 'ELABORADO'
            self.save()

        return True
    
    def _reordenar_por_criterio(self):
        """Reordena os militares do quadro baseado no tipo escolhido"""
        itens = list(self.itemquadroacesso_set.all())
        
        if self.tipo == 'ANTIGUIDADE':
            # Ordenar por numeração de antiguidade (menor = primeiro)
            itens.sort(key=lambda x: x.militar.numeracao_antiguidade or 999999)
        elif self.tipo == 'MERECIMENTO':
            # Ordenar por pontuação da ficha de conceito (maior = primeiro)
            itens.sort(key=lambda x: float(x.pontuacao), reverse=True)
        
        # Atualizar posições
        for i, item in enumerate(itens, 1):
            item.posicao = i
            item.save()
    
    def remover_militar_manual(self, militar):
        """Remove um militar do quadro"""
        print(f"DEBUG: Iniciando remoção do militar {militar.nome_completo}")
        
        if self.status == 'HOMOLOGADO':
            raise ValueError("Quadros homologados não podem ser editados")
        
        item = self.itemquadroacesso_set.filter(militar=militar).first()
        if not item:
            raise ValueError(f"O militar {militar.nome_completo} não está no quadro")
        
        print(f"DEBUG: Item encontrado - posição {item.posicao}, militar {item.militar.nome_completo}")
        
        item.delete()
        print(f"DEBUG: Item deletado com sucesso")
        
        # Reordenar posições se necessário
        self._reordenar_posicoes()
        print(f"DEBUG: Posições reordenadas")
        
        return True
    
    def _reordenar_posicoes(self):
        """Reordena as posições dos militares no quadro"""
        itens = self.itemquadroacesso_set.all().order_by('posicao')
        for i, item in enumerate(itens, 1):
            if item.posicao != i:
                item.posicao = i
                item.save()
    
    def proxima_promocao_display(self):
        """Retorna o próximo posto para promoção"""
        proximas_promocoes = {
            'AS': '2º Tenente',
            '2T': '1º Tenente',
            '1T': 'Capitão',
            'CP': 'Major',
            'MJ': 'Tenente-Coronel',
            'TC': 'Coronel',
            'ST': '2º Tenente',
        }
        return proximas_promocoes.get(self.posto, 'Não definido')
    
    def get_quadro_formatado(self):
        """Retorna o quadro formatado para exibição"""
        if self.status == 'NAO_ELABORADO':
            return {
                'status': 'Não Elaborado',
                'motivo': self.get_motivo_display_completo(),
                'itens': []
            }
        
        itens = self.itemquadroacesso_set.all().order_by('posicao')
        return {
            'status': 'Elaborado',
            'criterio': self.get_criterio_ordenacao(),
            'total_militares': itens.count(),
            'itens': itens
        }
    
    def gerar_quadro_completo(self):
        """Gera um quadro completo incluindo todos os postos e quadros com as novas regras de transição"""
        if self.status == 'NAO_ELABORADO':
            return False, "Quadro não pode ser elaborado"
        
        # Limpar itens existentes antes de gerar novos
        self.itemquadroacesso_set.all().delete()
        
        try:
            # Usar o método padronizado para buscar militares aptos
            militares_aptos = self.militares_aptos()
            militares_inaptos = self.militares_inaptos_com_motivo()
            
            # Converter para o formato esperado pelo resto do método
            todos_militares_aptos = []
            todos_militares_inaptos = []
            
            # Processar militares aptos
            for militar in militares_aptos:
                proximo_posto = self._obter_proximo_posto(militar.posto_graduacao)
                tipo_transicao = self.determinar_tipo_quadro_por_transicao(militar.posto_graduacao, proximo_posto) if proximo_posto else None
                
                todos_militares_aptos.append({
                    'militar': militar,
                    'quadro': militar.quadro,
                    'posto': militar.posto_graduacao,
                    'proximo_posto': proximo_posto,
                    'tipo_transicao': tipo_transicao,
                    'motivo': 'Apto'
                })
            
            # Processar militares inaptos
            for item in militares_inaptos:
                militar = item['militar']
                proximo_posto = self._obter_proximo_posto(militar.posto_graduacao)
                
                todos_militares_inaptos.append({
                    'militar': militar,
                    'quadro': militar.quadro,
                    'posto': militar.posto_graduacao,
                    'motivo': item['motivo']
                })
            
            # Verificar se há militares aptos
            if not todos_militares_aptos:
                self.status = 'NAO_ELABORADO'
                self.motivo_nao_elaboracao = 'SEM_REQUISITOS'
                motivos_detalhados = []
                for item in todos_militares_inaptos:
                    motivos_detalhados.append(f"{item['militar'].nome_completo} ({item['quadro']}-{item['posto']}): {item['motivo']}")
                self.observacoes = "Militares inaptos:\n" + "\n".join(motivos_detalhados[:20])
                if len(motivos_detalhados) > 20:
                    self.observacoes += f"\n... e mais {len(motivos_detalhados) - 20} militares"
                self.save()
                return False, f"Não há militares aptos para o quadro. {len(todos_militares_inaptos)} militares inaptos encontrados."
            
            # REESCRITA DA PARTE DE MERECIMENTO
            if self.tipo == 'MERECIMENTO':
                # Usar o método específico para ordenação por merecimento
                militares_ordenados = self._ordenar_por_merecimento_completo(todos_militares_aptos)
                
                # Criar itens do quadro com numeração independente por grupo (quadro + posto)
                grupos = {}
                for item in militares_ordenados:
                    militar = item['militar']
                    # Se for subtenente do quadro PRACAS, incluir no grupo COMP-ST
                    if militar.quadro == 'PRACAS' and militar.posto_graduacao == 'ST':
                        chave = 'COMP-ST'
                    else:
                        chave = f"{militar.quadro}-{militar.posto_graduacao}"
                    if chave not in grupos:
                        grupos[chave] = []
                    grupos[chave].append(item)
                
                # Criar itens do quadro com numeração independente por grupo
                for chave, grupo in grupos.items():
                    # Filtrar apenas subtenentes do quadro PRACAS para a transição ST->2T do COMP
                    if chave == 'COMP-ST':
                        grupo = [item for item in grupo if item['militar'].quadro == 'PRACAS']
                    for posicao, item in enumerate(grupo, 1):
                        # Para quadros de merecimento, salvar a pontuação da ficha de conceito
                        if self.tipo == 'MERECIMENTO':
                            pontuacao_salvar = item.get('pontuacao_ficha', 0.0)
                        else:
                            pontuacao_salvar = item.get('pontuacao_ficha', item.get('pontuacao'))
                        
                        ItemQuadroAcesso.objects.create(
                            quadro_acesso=self,
                            militar=item['militar'],
                            posicao=posicao,
                            pontuacao=pontuacao_salvar
                        )
            else:
                # Para antiguidade: usar o método específico para ordenação por antiguidade
                militares_ordenados = self._ordenar_por_antiguidade_completo(todos_militares_aptos)
                
                # Criar itens do quadro com numeração independente por grupo (quadro + posto)
                grupos = {}
                for item in militares_ordenados:
                    militar = item['militar']
                    # Se for subtenente do quadro PRACAS, incluir no grupo COMP-ST
                    if militar.quadro == 'PRACAS' and militar.posto_graduacao == 'ST':
                        chave = 'COMP-ST'
                    else:
                        chave = f"{militar.quadro}-{militar.posto_graduacao}"
                    if chave not in grupos:
                        grupos[chave] = []
                    grupos[chave].append(item)
                
                # Criar itens do quadro com numeração independente por grupo
                for chave, grupo in grupos.items():
                    # Filtrar apenas subtenentes do quadro PRACAS para a transição ST->2T do COMP
                    if chave == 'COMP-ST':
                        grupo = [item for item in grupo if item['militar'].quadro == 'PRACAS']
                    for posicao, item in enumerate(grupo, 1):
                        # Para quadros de antiguidade, salvar a numeração de antiguidade ou data de promoção
                        if item['militar'].numeracao_antiguidade is not None:
                            pontuacao_salvar = item['militar'].numeracao_antiguidade
                        else:
                            pontuacao_salvar = item['militar'].data_promocao_atual.toordinal() if item['militar'].data_promocao_atual else 999999
                        
                        ItemQuadroAcesso.objects.create(
                            quadro_acesso=self,
                            militar=item['militar'],
                            posicao=posicao,
                            pontuacao=pontuacao_salvar
                        )
            
            # Atualizar status do quadro
            self.status = 'ELABORADO'
            self.observacoes = f"Quadro {self.get_tipo_display()} elaborado com {len(todos_militares_aptos)} militares aptos. {len(todos_militares_inaptos)} militares inaptos."
            self.save()
            
            return True, f"Quadro {self.get_tipo_display()} elaborado com {len(todos_militares_aptos)} militares aptos. {len(todos_militares_inaptos)} militares inaptos."
        
        except Exception as e:
            # Em caso de erro, marcar como não elaborado
            self.status = 'NAO_ELABORADO'
            self.motivo_nao_elaboracao = 'OUTROS'
            self.observacoes = f"Erro na elaboração: {str(e)}"
            self.save()
            return False, f"Erro na elaboração do quadro: {str(e)}"
    
    def _ordenar_por_antiguidade_completo(self, militares_aptos):
        """Ordena militares por antiguidade considerando todos os quadros e postos"""
        from itertools import groupby
        
        # Definir ordem dos quadros (do mais graduado ao menos graduado)
        ordem_quadros = ['COMB', 'SAUDE', 'ENG', 'COMP', 'PRACAS']
        
        # Definir ordem dos postos (do mais graduado ao menos graduado)
        ordem_postos = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        
        militares_ordenados = []
        for item in militares_aptos:
            militar = item['militar']
            # Usar data da última promoção como critério principal
            data_promocao = militar.data_promocao_atual
            if not data_promocao:
                data_promocao = militar.data_ingresso  # Fallback para data de ingresso
            
            # Numeração de antiguidade como critério de desempate
            numeracao = militar.numeracao_antiguidade or 999999
            
            # Para subtenentes, usar nota do CHO como critério de ordenação
            nota_cho = militar.nota_cho if militar.posto_graduacao == 'ST' and militar.nota_cho else 0.0
            
            # Para cabos com CHSGT, usar nota do curso como critério de ordenação
            nota_chsgt = None
            if militar.posto_graduacao == 'CAB' and militar.curso_chsgt:
                nota_chsgt = militar.nota_chsgt or 0
            
            # Para soldados com CHC, usar nota do curso como critério de ordenação
            nota_chc = None
            if militar.posto_graduacao == 'SD' and militar.curso_chc:
                nota_chc = militar.nota_chc or 0
            
            militares_ordenados.append({
                'militar': militar,
                'data_promocao': data_promocao,
                'numeracao_antiguidade': numeracao,
                'data_ingresso': militar.data_ingresso,
                'quadro': militar.quadro,
                'posto': militar.posto_graduacao,
                'nota_cho': nota_cho,
                'nota_chsgt': nota_chsgt,
                'nota_chc': nota_chc
            })
        
        # Ordenar por quadro, depois por posto, e finalmente por antiguidade dentro de cada posto
        # Para subtenentes, ordenar pela nota do CHO (maior nota primeiro)
        # Para cabos com CHSGT, ordenar pela nota do CHSGT (maior nota primeiro)
        # Para soldados com CHC, ordenar pela nota do CHC (maior nota primeiro)
        militares_ordenados.sort(key=lambda x: (
            ordem_quadros.index(x['quadro']) if x['quadro'] in ordem_quadros else 999,
            ordem_postos.index(x['posto']) if x['posto'] in ordem_postos else 999,
            # Para subtenentes, usar nota do CHO (maior primeiro)
            # Para cabos com CHSGT, usar nota do CHSGT (maior primeiro)
            # Para soldados com CHC, usar nota do CHC (maior primeiro)
            # Para outros, usar data de promoção
            -x['nota_cho'] if x['posto'] == 'ST' else (
                -x['nota_chsgt'] if x['posto'] == 'CAB' and x['nota_chsgt'] is not None else (
                    -x['nota_chc'] if x['posto'] == 'SD' and x['nota_chc'] is not None else x['data_promocao']
                )
            ),
            # Usar numeração de antiguidade como desempate
            x['numeracao_antiguidade']
        ))
        
        return militares_ordenados
    
    def _ordenar_por_merecimento_completo(self, militares_aptos):
        """Ordena militares por merecimento considerando todos os quadros e postos"""
        # Definir ordem dos quadros (incluindo praças)
        ordem_quadros = ['COMB', 'SAUDE', 'ENG', 'COMP', 'PRACAS']
        
        # Definir ordem dos postos (hierarquia correta: mais alto para mais baixo)
        # CORRIGIDO: removido CB duplicado e adicionado postos que faltavam
        ordem_postos = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        
        militares_ordenados = []
        for item in militares_aptos:
            militar = item['militar']
            ficha = militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
            if ficha:
                # Calcular pontuação de ordenação: quadro + posto + pontuação da ficha
                indice_quadro = ordem_quadros.index(militar.quadro) if militar.quadro in ordem_quadros else 999
                indice_posto = ordem_postos.index(militar.posto_graduacao) if militar.posto_graduacao in ordem_postos else 999
                
                # Pontuação composta: (quadro * 1000000) + (posto * 100000) + pontuação da ficha
                # Para merecimento: manter hierarquia (quadro + posto) mas ordenar por pontuação da ficha (maior primeiro)
                pontos_ficha = float(ficha.pontos) if ficha.pontos is not None else 0.0
                
                # Para subtenentes, considerar também a nota do CHO na pontuação
                if militar.posto_graduacao == 'ST' and militar.nota_cho:
                    # Adicionar a nota do CHO à pontuação da ficha (maior nota = maior pontuação)
                    pontos_ficha += float(militar.nota_cho) * 10  # Multiplicar por 10 para dar peso à nota do CHO
                
                # CORRIGIDO: Inverter a pontuação da ficha para que maior pontuação = menor valor = primeiro
                # Usar 100000 - pontos_ficha para que maior pontuação da ficha apareça primeiro
                pontuacao_ordenacao = (indice_quadro * 1000000) + (indice_posto * 100000) + (100000 - pontos_ficha)
                
                militares_ordenados.append({
                    'militar': militar,
                    'pontuacao': pontuacao_ordenacao,
                    'pontuacao_ficha': pontos_ficha,
                    'data_promocao': militar.data_promocao_atual,
                    'data_ingresso': militar.data_ingresso,
                    'quadro': militar.quadro,
                    'posto': militar.posto_graduacao
                })
            else:
                # Se não tem ficha, usar pontuação mínima
                indice_quadro = ordem_quadros.index(militar.quadro) if militar.quadro in ordem_quadros else 999
                indice_posto = ordem_postos.index(militar.posto_graduacao) if militar.posto_graduacao in ordem_postos else 999
                pontuacao_ordenacao = (indice_quadro * 1000000) + (indice_posto * 100000) + 100000
                
                militares_ordenados.append({
                    'militar': militar,
                    'pontuacao': pontuacao_ordenacao,
                    'pontuacao_ficha': 0.0,
                    'data_promocao': militar.data_promocao_atual,
                    'data_ingresso': militar.data_ingresso,
                    'quadro': militar.quadro,
                    'posto': militar.posto_graduacao
                })
        
        # Ordenar por pontuação composta (menor = primeiro)
        # Isso garante: 1º quadro, 2º posto, 3º maior pontuação da ficha
        militares_ordenados.sort(key=lambda x: x['pontuacao'])
        return militares_ordenados


class ItemQuadroAcesso(models.Model):
    """Itens do Quadro de Acesso - posição de cada militar"""
    
    MOTIVO_INSERCAO_CHOICES = [
        ('AUTOMATICO', 'Inserção Automática'),
        ('MANDADO_JUDICIAL', 'Mandado Judicial'),
        ('DECISAO_ADMINISTRATIVA', 'Decisão Administrativa'),
        ('RECURSO_ADMINISTRATIVO', 'Recurso Administrativo'),
        ('ACORDO_JUDICIAL', 'Acordo Judicial'),
        ('SENTENCA_JUDICIAL', 'Sentença Judicial'),
        ('OUTROS', 'Outros Motivos'),
    ]
    
    quadro_acesso = models.ForeignKey(QuadroAcesso, on_delete=models.CASCADE, verbose_name="Quadro de Acesso")
    militar = models.ForeignKey(Militar, on_delete=models.CASCADE, verbose_name="Militar")
    posicao = models.IntegerField(verbose_name="Posição")
    pontuacao = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Pontuação")
    data_inclusao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Inclusão")
    
    # Novos campos para controle de inserções manuais
    inserido_manualmente = models.BooleanField(default=False, verbose_name="Inserido Manualmente")
    motivo_insercao = models.CharField(
        max_length=25, 
        choices=MOTIVO_INSERCAO_CHOICES, 
        default='AUTOMATICO',
        verbose_name="Motivo da Inserção"
    )
    observacoes_insercao = models.TextField(blank=True, null=True, verbose_name="Observações da Inserção")
    documento_referencia = models.CharField(max_length=200, blank=True, null=True, verbose_name="Documento de Referência")
    data_documento = models.DateField(null=True, blank=True, verbose_name="Data do Documento")
    
    class Meta:
        verbose_name = "Item do Quadro de Acesso"
        verbose_name_plural = "Itens do Quadro de Acesso"
        unique_together = ['quadro_acesso', 'militar']
        ordering = ['quadro_acesso', 'posicao']
    
    def __str__(self):
        return f"{self.militar.nome_completo} - {self.posicao}ª posição"
    
    def clean(self):
        """Validação personalizada para impedir inclusão de militares inaptos"""
        from django.core.exceptions import ValidationError
        
        if self.militar and self.quadro_acesso:
            # 1. Validações básicas (sempre aplicadas)
            if self.militar.situacao != 'AT':
                raise ValidationError("Militar não está em situação ativa")
            
            # 2. Aplicar validações rigorosas para todos os quadros
            # Para quadros automáticos, aplicar todas as validações rigorosas
                if not self.militar.apto_inspecao_saude:
                    raise ValidationError("Militar não está apto em inspeção de saúde")
                
                # Verificar se a inspeção de saúde está vencida
                if self.militar.data_validade_inspecao_saude:
                    from django.utils import timezone
                    hoje = timezone.now().date()
                    if self.militar.data_validade_inspecao_saude < hoje:
                        raise ValidationError("Inspeção de saúde vencida")
                
                # Verificar se o militar tem os cursos obrigatórios
                if not self.militar.cursos_inerentes_quadro():
                    raise ValidationError("Militar não possui os cursos obrigatórios para o quadro")
                
                # Verificar interstício
                if not self.militar.apto_intersticio_ate_data(self.quadro_acesso.data_promocao):
                    raise ValidationError(f"Militar não completará o interstício mínimo até {self.quadro_acesso.data_promocao}")
                
                # Aplicar validações específicas do quadro
                apto, motivo = self.quadro_acesso.validar_requisitos_quadro_acesso(self.militar)
                if not apto:
                    raise ValidationError(f"Militar não atende aos requisitos: {motivo}")
        
        super().clean()
    
    def save(self, *args, **kwargs):
        """Sobrescrever save para aplicar validações"""
        self.clean()
        super().save(*args, **kwargs)


class Promocao(models.Model):
    """Registro de Promoções realizadas"""
    
    CRITERIO_CHOICES = [
        ('ANTIGUIDADE', 'Antiguidade'),
        ('MERECIMENTO', 'Merecimento'),
        ('POST_MORTEM', 'Post Mortem'),
        ('RESSARCIMENTO', 'Ressarcimento de Preterição'),
    ]
    
    militar = models.ForeignKey(Militar, on_delete=models.CASCADE, verbose_name="Militar")
    posto_anterior = models.CharField(max_length=4, choices=POSTO_GRADUACAO_CHOICES, verbose_name="Posto Anterior")
    posto_novo = models.CharField(max_length=4, choices=POSTO_GRADUACAO_CHOICES, verbose_name="Novo Posto")
    criterio = models.CharField(max_length=15, choices=CRITERIO_CHOICES, verbose_name="Critério")
    data_promocao = models.DateField(verbose_name="Data da Promoção")
    data_publicacao = models.DateField(verbose_name="Data da Publicação")
    numero_ato = models.CharField(max_length=50, verbose_name="Número do Ato")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data do Registro")
    
    class Meta:
        verbose_name = "Promoção"
        verbose_name_plural = "Promoções"
        ordering = ['-data_promocao']
    
    def __str__(self):
        return f"{self.militar.nome_completo} - {self.get_posto_anterior_display()} → {self.get_posto_novo_display()}"


class Vaga(models.Model):
    """Controle de Vagas para Promoções"""
    
    POSTO_CHOICES = [
        ('2T', '2º Tenente'),
        ('1T', '1º Tenente'),
        ('CP', 'Capitão'),
        ('MJ', 'Major'),
        ('TC', 'Tenente-Coronel'),
        ('CB', 'Coronel'),
    ]
    
    QUADRO_CHOICES = [
        ('COMB', 'Combatente'),
        ('SAUDE', 'Saúde'),
        ('ENG', 'Engenheiro'),
        ('COMP', 'Complementar'),
    ]
    
    posto = models.CharField(max_length=4, choices=POSTO_CHOICES, verbose_name="Posto")
    quadro = models.CharField(max_length=5, choices=QUADRO_CHOICES, verbose_name="Quadro")
    efetivo_atual = models.IntegerField(default=0, verbose_name="Efetivo Atual")
    efetivo_maximo = models.IntegerField(verbose_name="Efetivo Máximo")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Vaga"
        verbose_name_plural = "Vagas"
        unique_together = ['posto', 'quadro']
        ordering = ['posto', 'quadro']
    
    def __str__(self):
        return f"{self.get_posto_display()} - {self.get_quadro_display()}"
    
    @property
    def vagas_disponiveis(self):
        """Calcula vagas disponíveis"""
        return max(0, self.efetivo_maximo - self.efetivo_atual)
    
    @property
    def percentual_ocupacao(self):
        """Calcula percentual de ocupação"""
        if self.efetivo_maximo > 0:
            return (self.efetivo_atual / self.efetivo_maximo) * 100
        return 0


class Curso(models.Model):
    """Cadastro de Cursos Militares e Civis"""
    
    TIPO_CHOICES = [
        ('MILITAR', 'Militar'),
        ('CIVIL', 'Civil'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name="Nome do Curso")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo")
    pontuacao = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Pontuação")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ['tipo', 'nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class MedalhaCondecoracao(models.Model):
    """Cadastro de Medalhas e Condecorações"""
    
    TIPO_CHOICES = [
        ('FEDERAL', 'Governo Federal'),
        ('ESTADUAL', 'Governo Estadual'),
        ('CBMEPI', 'CBMEPI'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name="Nome")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo")
    pontuacao = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Pontuação")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Medalha/Condecoração"
        verbose_name_plural = "Medalhas e Condecorações"
        ordering = ['tipo', 'nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

        return f"{self.nome} ({self.get_tipo_display()})"


class PrevisaoVaga(models.Model):
    """Configuração de previsão de vagas por posto e quadro"""
    posto = models.CharField(max_length=4, choices=POSTO_GRADUACAO_CHOICES, verbose_name="Posto")
    quadro = models.CharField(max_length=10, choices=QUADRO_CHOICES, verbose_name="Quadro")
    efetivo_atual = models.PositiveIntegerField(default=0, verbose_name="Efetivo Atual")
    efetivo_previsto = models.PositiveIntegerField(default=0, verbose_name="Efetivo Previsto")
    vagas_disponiveis = models.PositiveIntegerField(default=0, verbose_name="Vagas Disponíveis")
    vagas_fixadas = models.PositiveIntegerField(default=0, verbose_name="Vagas Fixadas", help_text="Vagas fixadas manualmente para este posto/quadro")
    observacoes_vagas_fixadas = models.TextField(blank=True, null=True, verbose_name="Observações das Vagas Fixadas")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Previsão de Vaga"
        verbose_name_plural = "Previsões de Vagas"
        unique_together = ['posto', 'quadro']
        ordering = ['quadro', 'posto']
    
    def __str__(self):
        return f"{self.get_posto_display()} - {self.get_quadro_display()} ({self.efetivo_atual}/{self.efetivo_previsto})"
    
    def calcular_vagas_disponiveis(self):
        """Calcula vagas disponíveis baseado no efetivo atual e previsto"""
        return max(0, self.efetivo_previsto - self.efetivo_atual)
    
    def save(self, *args, **kwargs):
        """Sobrescreve o save para calcular vagas disponíveis automaticamente"""
        self.vagas_disponiveis = self.calcular_vagas_disponiveis()
        super().save(*args, **kwargs)
    
    def get_status_display(self):
        """Retorna o status da previsão de vagas"""
        if self.vagas_disponiveis > 0:
            return "Disponível"
        elif self.efetivo_atual == self.efetivo_previsto:
            return "Completo"
        else:
            return "Excedido"


class AssinaturaQuadroAcesso(models.Model):
    """Assinaturas de um quadro de acesso - permite múltiplas assinaturas"""
    
    quadro_acesso = models.ForeignKey(QuadroAcesso, on_delete=models.CASCADE, verbose_name="Quadro de Acesso", related_name="assinaturas")
    assinado_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Assinado por")
    data_assinatura = models.DateTimeField(auto_now_add=True, verbose_name="Data da Assinatura")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações da Assinatura")
    tipo_assinatura = models.CharField(
        max_length=20,
        choices=[
            ('ELABORACAO', 'Elaboração'),
            ('REVISAO', 'Revisão'),
            ('APROVACAO', 'Aprovação'),
            ('HOMOLOGACAO', 'Homologação'),
            ('OUTROS', 'Outros'),
        ],
        default='APROVACAO',
        verbose_name="Tipo de Assinatura"
    )
    funcao_assinatura = models.CharField(
        blank=True,
        help_text="Função/cargo do usuário no momento da assinatura",
        max_length=100,
        null=True,
        verbose_name="Função no momento da assinatura",
    )
    
    class Meta:
        verbose_name = "Assinatura do Quadro de Acesso"
        verbose_name_plural = "Assinaturas do Quadro de Acesso"
        ordering = ['-data_assinatura']
        unique_together = ['quadro_acesso', 'assinado_por', 'tipo_assinatura']
    
    def __str__(self):
        return f"{self.quadro_acesso} - {self.assinado_por.get_full_name()} - {self.get_tipo_assinatura_display()}"
    
    def verificar_permissao_assinatura(self, usuario):
        """Verifica se o usuário tem permissão para assinar este quadro"""
        # Verificar se o usuário é membro da comissão correta
        if self.quadro_acesso.tipo in ['ANTIGUIDADE', 'MERECIMENTO']:
            # Para quadros de oficiais, verificar se é membro da CPO
            comissao_cpo = ComissaoPromocao.get_comissao_ativa_por_tipo('CPO')
            if comissao_cpo and comissao_cpo.pode_assinar_documento_oficial(usuario):
                return True
        else:
            # Para quadros de praças, verificar se é membro da CPP
            comissao_cpp = ComissaoPromocao.get_comissao_ativa_por_tipo('CPP')
            if comissao_cpp and comissao_cpp.pode_assinar_documento_praca(usuario):
                return True
        
        return False


class ComissaoPromocao(models.Model):
    """Comissão de Promoções (Oficiais e Praças) conforme Lei 5.461/2005"""
    
    TIPO_CHOICES = [
        ('CPO', 'Comissão de Promoções de Oficiais'),
        ('CPP', 'Comissão de Promoções de Praças'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVA', 'Ativa'),
        ('INATIVA', 'Inativa'),
        ('SUSPENSA', 'Suspensa'),
    ]
    
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES, verbose_name="Tipo de Comissão")
    nome = models.CharField(max_length=200, verbose_name="Nome da Comissão")
    data_criacao = models.DateField(verbose_name="Data de Criação")
    data_termino = models.DateField(null=True, blank=True, verbose_name="Data de Término")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ATIVA', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Comissão de Promoções"
        verbose_name_plural = "Comissões de Promoções"
        ordering = ['tipo', '-data_criacao']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nome} ({self.get_status_display()})"
    
    @property
    def presidente(self):
        """Retorna o presidente da comissão (Comandante-Geral)"""
        return self.membros.filter(tipo='PRESIDENTE').first()
    
    @property
    def membros_natos(self):
        """Retorna os membros natos da comissão"""
        return self.membros.filter(tipo='NATO')
    
    @property
    def membros_efetivos(self):
        """Retorna os membros efetivos da comissão"""
        return self.membros.filter(tipo='EFETIVO')
    
    @property
    def total_membros(self):
        """Retorna o total de membros da comissão"""
        return self.membros.count()
    
    def esta_ativa(self):
        """Verifica se a comissão está ativa"""
        return self.status == 'ATIVA' and (not self.data_termino or self.data_termino >= date.today())
    
    def pode_assinar_documento_oficial(self, usuario):
        """Verifica se o usuário pode assinar documentos de oficiais"""
        if self.tipo != 'CPO':
            return False
        return self.membros.filter(usuario=usuario, ativo=True).exists()
    
    def pode_assinar_documento_praca(self, usuario):
        """Verifica se o usuário pode assinar documentos de praças"""
        if self.tipo != 'CPP':
            return False
        return self.membros.filter(usuario=usuario, ativo=True).exists()
    
    def eh_presidente(self, usuario):
        """Verifica se o usuário é presidente desta comissão"""
        # Primeiro, verificar se o usuário tem função de presidente
        from .models import UsuarioFuncao
        from django.utils import timezone
        
        # Verificar se o usuário tem função ativa de presidente
        funcoes_presidente = UsuarioFuncao.objects.filter(
            usuario=usuario,
            cargo_funcao__nome__icontains='presidente',
            status='ATIVO',
            data_inicio__lte=timezone.now().date(),
            data_fim__isnull=True
        ).exists()
        
        if funcoes_presidente:
            return True
            
        # Fallback: verificar pelo tipo de membro da comissão
        presidente = self.presidente
        if presidente and presidente.usuario == usuario and presidente.esta_ativo():
            return True
        return False
    
    def eh_presidente_por_funcao(self, usuario, funcao):
        """Verifica se o usuário é presidente desta comissão baseado em uma função específica"""
        # Verificar se a função é de presidente
        if not funcao or not funcao.cargo_funcao.nome.lower().find('presidente') >= 0:
            return False
        
        # Verificar se a função é ativa
        if not funcao.esta_ativo():
            return False
        
        # Verificar se a função corresponde ao tipo de comissão
        if self.tipo == 'CPO' and 'cpo' in funcao.cargo_funcao.nome.lower():
            return True
        elif self.tipo == 'CPP' and 'cpp' in funcao.cargo_funcao.nome.lower():
            return True
        
        return False
    
    @classmethod
    def get_comissao_ativa_por_tipo(cls, tipo):
        """Retorna a comissão ativa de um determinado tipo"""
        return cls.objects.filter(tipo=tipo, status='ATIVA').first()





class MembroComissao(models.Model):
    """Membros da Comissão de Promoções (Oficiais e Praças)"""
    
    TIPO_CHOICES = [
        ('PRESIDENTE', 'Presidente da Comissão'),
        ('EFETIVO', 'Membro Efetivo'),
        ('NATO', 'Membro Nato'),
        ('SECRETARIO', 'Secretário'),
    ]
    
    # CARGO_CHOICES removido
    
    comissao = models.ForeignKey(ComissaoPromocao, on_delete=models.CASCADE, related_name='membros', verbose_name="Comissão")
    militar = models.ForeignKey(Militar, on_delete=models.CASCADE, verbose_name="Militar")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário do Sistema", null=True, blank=True)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, verbose_name="Tipo de Membro")
    cargo = models.ForeignKey('CargoFuncao', on_delete=models.PROTECT, verbose_name="Função/Cargo do Usuário")
    data_nomeacao = models.DateField(verbose_name="Data de Nomeação")
    data_termino = models.DateField(null=True, blank=True, verbose_name="Data de Término")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Membro da Comissão"
        verbose_name_plural = "Membros da Comissão"
        unique_together = ['comissao', 'militar', 'tipo']
        ordering = ['tipo', 'militar__nome_completo']
    
    def __str__(self):
        return f"{self.militar.nome_completo} - {self.get_tipo_display()} ({self.cargo.nome})"
    
    def esta_ativo(self):
        """Verifica se o membro está ativo"""
        return self.ativo and (not self.data_termino or self.data_termino >= date.today())
    
    def pode_assinar_documento(self, tipo_documento):
        """Verifica se o membro pode assinar um tipo específico de documento"""
        if not self.esta_ativo() or not self.usuario:
            return False
        
        if tipo_documento == 'OFICIAL':
            return self.comissao.tipo == 'CPO'
        elif tipo_documento == 'PRACA':
            return self.comissao.tipo == 'CPP'
        
        return False


class SessaoComissao(models.Model):
    """Sessões da Comissão de Promoções de Oficiais"""
    
    TIPO_CHOICES = [
        ('ORDINARIA', 'Ordinária'),
        ('EXTRAORDINARIA', 'Extraordinária'),
        ('ESPECIAL', 'Especial'),
    ]
    
    STATUS_CHOICES = [
        ('AGENDADA', 'Agendada'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
        ('SUSPENSA', 'Suspensa'),
    ]
    
    comissao = models.ForeignKey(ComissaoPromocao, on_delete=models.CASCADE, related_name='sessoes', verbose_name="Comissão")
    numero = models.PositiveIntegerField(verbose_name="Número da Sessão")
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, verbose_name="Tipo de Sessão")
    data_sessao = models.DateField(verbose_name="Data da Sessão")
    hora_inicio = models.TimeField(verbose_name="Hora de Início")
    hora_fim = models.TimeField(null=True, blank=True, verbose_name="Hora de Término")
    local = models.CharField(max_length=200, verbose_name="Local")
    pauta = models.TextField(verbose_name="Pauta")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='AGENDADA', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Sessão da Comissão"
        verbose_name_plural = "Sessões da Comissão"
        unique_together = ['comissao', 'numero']
        ordering = ['-data_sessao', '-numero']
    
    def __str__(self):
        return f"Sessão {self.numero} - {self.comissao.nome} ({self.data_sessao.strftime('%d/%m/%Y')})"
    
    @property
    def presentes(self):
        """Retorna os membros presentes na sessão"""
        return self.presencas.filter(presente=True)
    
    @property
    def ausentes(self):
        """Retorna os membros ausentes na sessão"""
        return self.presencas.filter(presente=False)
    
    @property
    def total_presentes(self):
        """Retorna o total de membros presentes"""
        return self.presentes.count()
    
    @property
    def quorum_atingido(self):
        """Verifica se foi atingido o quorum (maioria dos membros)"""
        total_membros = self.comissao.total_membros
        return self.total_presentes > (total_membros / 2)
    
    @property
    def todos_presentes_votaram_exceto_presidente(self):
        """Verifica se todos os presentes (exceto o presidente) votaram em todas as deliberações"""
        if not self.deliberacoes.exists():
            return False
        
        # Membros presentes exceto o presidente
        membros_presentes_exceto_presidente = [
            p.membro for p in self.presencas.filter(presente=True) 
            if p.membro.cargo != 'PRESIDENTE'
        ]
        
        if not membros_presentes_exceto_presidente:
            return True  # Se não há membros presentes exceto presidente, considera como votado
        
        # Verificar se todos votaram em todas as deliberações
        for deliberacao in self.deliberacoes.all():
            votos_por_deliberacao = deliberacao.votos.filter(
                membro__in=membros_presentes_exceto_presidente
            ).count()
            if votos_por_deliberacao < len(membros_presentes_exceto_presidente):
                return False
        
        return True



class PresencaSessao(models.Model):
    """Controle de presença dos membros nas sessões"""
    
    sessao = models.ForeignKey(SessaoComissao, on_delete=models.CASCADE, related_name='presencas', verbose_name="Sessão")
    membro = models.ForeignKey(MembroComissao, on_delete=models.CASCADE, verbose_name="Membro")
    presente = models.BooleanField(default=False, verbose_name="Presente")
    justificativa = models.TextField(blank=True, null=True, verbose_name="Justificativa da Ausência")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Presença na Sessão"
        verbose_name_plural = "Presenças na Sessão"
        unique_together = ['sessao', 'membro']
        ordering = ['sessao', 'membro__militar__nome_completo']
    
    def __str__(self):
        status = "Presente" if self.presente else "Ausente"
        return f"{self.membro.militar.nome_completo} - {status}"


class DeliberacaoComissao(models.Model):
    """Deliberações da Comissão de Promoções de Oficiais"""
    
    TIPO_CHOICES = [
        ('APROVACAO', 'Aprovação'),
        ('REPROVACAO', 'Reprovação'),
        ('SUSPENSAO', 'Suspensão'),
        ('ENCAMINHAMENTO', 'Encaminhamento'),
        ('OUTROS', 'Outros'),
    ]
    
    sessao = models.ForeignKey(SessaoComissao, on_delete=models.CASCADE, related_name='deliberacoes', verbose_name="Sessão")
    numero = models.PositiveIntegerField(verbose_name="Número da Deliberação")
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, verbose_name="Tipo de Deliberação")
    assunto = models.CharField(max_length=200, verbose_name="Assunto")
    descricao = models.TextField(verbose_name="Descrição")
    resultado = models.TextField(verbose_name="Resultado/Deliberação")
    votos_favor = models.PositiveIntegerField(default=0, verbose_name="Votos Favoráveis")
    votos_contra = models.PositiveIntegerField(default=0, verbose_name="Votos Contrários")
    votos_abstencao = models.PositiveIntegerField(default=0, verbose_name="Abstenções")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Deliberação da Comissão"
        verbose_name_plural = "Deliberações da Comissão"
        unique_together = ['sessao', 'numero']
        ordering = ['sessao', 'numero']
    
    def __str__(self):
        return f"Deliberação {self.numero} - {self.assunto}"
    
    @property
    def total_votos(self):
        """Retorna o total de votos"""
        return self.votos_favor + self.votos_contra + self.votos_abstencao
    
    @property
    def aprovada(self):
        """Verifica se a deliberação foi aprovada"""
        return self.votos_favor > self.votos_contra


class VotoDeliberacao(models.Model):
    """Votos individuais dos membros nas deliberações"""
    
    VOTO_CHOICES = [
        ('FAVOR', 'Favorável'),
        ('CONTRA', 'Contrário'),
        ('ABSTENCAO', 'Abstenção'),
    ]
    
    deliberacao = models.ForeignKey(DeliberacaoComissao, on_delete=models.CASCADE, related_name='votos', verbose_name="Deliberação")
    membro = models.ForeignKey(MembroComissao, on_delete=models.CASCADE, verbose_name="Membro")
    voto = models.CharField(max_length=10, choices=VOTO_CHOICES, verbose_name="Voto")
    justificativa = models.TextField(blank=True, null=True, verbose_name="Justificativa")
    voto_proferido = models.TextField(blank=True, null=True, verbose_name="Voto Proferido", help_text="Texto do voto proferido pelo membro")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    assinado = models.BooleanField(default=False, verbose_name="Assinado Eletronicamente")
    data_assinatura = models.DateTimeField(null=True, blank=True, verbose_name="Data da Assinatura Eletrônica")
    
    # Campos para assinatura eletrônica
    funcao_assinatura = models.CharField(max_length=200, blank=True, null=True, verbose_name="Função para Assinatura")
    tipo_assinatura = models.CharField(
        max_length=15,
        choices=[
            ('VOTO', 'Voto'),
            ('APROVACAO', 'Aprovação'),
            ('REVISAO', 'Revisão'),
            ('OUTROS', 'Outros'),
        ],
        default='VOTO',
        verbose_name="Tipo de Assinatura"
    )
    observacoes_assinatura = models.TextField(blank=True, null=True, verbose_name="Observações da Assinatura")
    
    class Meta:
        verbose_name = "Voto na Deliberação"
        verbose_name_plural = "Votos na Deliberação"
        unique_together = ['deliberacao', 'membro']
        ordering = ['deliberacao', 'membro__militar__nome_completo']
    
    def __str__(self):
        return f"{self.membro.militar.nome_completo} - {self.get_voto_display()}"


def documento_sessao_upload_path(instance, filename):
    """Define o caminho de upload para documentos da sessão"""
    return f'documentos/sessoes/{instance.sessao.comissao.tipo}/{instance.sessao.comissao.pk}/sessao_{instance.sessao.numero}/{filename}'


class DocumentoSessao(models.Model):
    """Documentos anexados às sessões da comissão"""
    
    TIPO_CHOICES = [
        ('PAUTA', 'Pauta da Sessão'),
        ('ATA', 'Ata da Sessão'),
        ('MEMORANDO', 'Memorando'),
        ('OFICIO', 'Ofício'),
        ('REQUERIMENTO', 'Requerimento'),
        ('MANDADO_JUDICIAL', 'Mandado Judicial'),
        ('DESPACHO', 'Despacho'),
        ('PARECER', 'Parecer'),
        ('DECISAO', 'Decisão'),
        ('SENTENCA', 'Sentença'),
        ('NOTIFICACAO', 'Notificação'),
        ('INTIMACAO', 'Intimação'),
        ('CERTIDAO', 'Certidão'),
        ('PROCURACAO', 'Procuração'),
        ('CONTRATO', 'Contrato'),
        ('PORTARIA', 'Portaria'),
        ('DECRETO', 'Decreto'),
        ('RELATORIO', 'Relatório'),
        ('QUADRO_ACESSO', 'Quadro de Acesso'),
        ('FICHA_CONCEITO', 'Ficha de Conceito'),
        ('OUTROS', 'Outros'),
    ]
    
    sessao = models.ForeignKey(SessaoComissao, on_delete=models.CASCADE, related_name='documentos', verbose_name="Sessão")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Documento")
    titulo = models.CharField(max_length=200, verbose_name="Título do Documento")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    arquivo = models.FileField(upload_to=documento_sessao_upload_path, verbose_name="Arquivo")
    upload_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Upload por")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data do Upload")
    deliberacao_gerada = models.ForeignKey(DeliberacaoComissao, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Deliberação Gerada")
    
    class Meta:
        verbose_name = "Documento da Sessão"
        verbose_name_plural = "Documentos da Sessão"
        ordering = ['-data_upload']
    
    def __str__(self):
        return f"{self.titulo} - {self.sessao}"
    
    def filename(self):
        """Retorna apenas o nome do arquivo"""
        return os.path.basename(self.arquivo.name)
    
    def extension(self):
        """Retorna a extensão do arquivo"""
        return os.path.splitext(self.arquivo.name)[1].lower()
    
    def is_pdf(self):
        """Verifica se é um arquivo PDF"""
        return self.extension() == '.pdf'
    
    def is_image(self):
        """Verifica se é uma imagem"""
        return self.extension() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    
    def can_preview(self):
        """Verifica se o arquivo pode ser visualizado no navegador"""
        return self.is_pdf() or self.is_image()


class JustificativaEncerramento(models.Model):
    """Justificativas para encerramento de sessão quando membros não votaram"""
    
    sessao = models.ForeignKey(SessaoComissao, on_delete=models.CASCADE, related_name='justificativas_encerramento', verbose_name="Sessão")
    membro = models.ForeignKey(MembroComissao, on_delete=models.CASCADE, verbose_name="Membro")
    justificativa = models.TextField(verbose_name="Justificativa")
    registrado_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Registrado por")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data do Registro")
    
    class Meta:
        verbose_name = "Justificativa de Encerramento"
        verbose_name_plural = "Justificativas de Encerramento"
        unique_together = ['sessao', 'membro']
        ordering = ['-data_registro']
    
    def __str__(self):
        return f"Justificativa de {self.membro.militar.nome_completo} - Sessão {self.sessao.numero}"


class AtaSessao(models.Model):
    """Ata editada da sessão da comissão"""
    
    sessao = models.OneToOneField(SessaoComissao, on_delete=models.CASCADE, related_name='ata_editada', verbose_name="Sessão")
    conteudo = CKEditor5Field('Conteúdo da Ata', blank=True, null=True, config_name='ata_config')
    editado_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Editado por")
    data_edicao = models.DateTimeField(auto_now=True, verbose_name="Data da Edição")
    versao = models.PositiveIntegerField(default=1, verbose_name="Versão")
    status = models.CharField(
        max_length=20,
        choices=[
            ('RASCUNHO', 'Rascunho'),
            ('PARA_ASSINATURA', 'Para Assinatura'),
            ('ASSINADA', 'Assinada'),
            ('FINALIZADA', 'Finalizada')
        ],
        default='RASCUNHO',
        verbose_name="Status"
    )
    data_finalizacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Finalização")
    
    class Meta:
        verbose_name = "Ata da Sessão"
        verbose_name_plural = "Atas das Sessões"
        ordering = ['-data_edicao']
    
    def __str__(self):
        return f"Ata da Sessão {self.sessao.numero} - Versão {self.versao}"
    
    def save(self, *args, **kwargs):
        if self.pk:
            # Verificar se houve modificação real no conteúdo
            try:
                # Buscar a versão anterior no banco
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT conteudo FROM militares_atasessao WHERE id = %s",
                        [self.pk]
                    )
                    resultado = cursor.fetchone()
                    if resultado:
                        conteudo_anterior = resultado[0]
                        # Se o conteúdo não mudou, não atualizar a data
                        if conteudo_anterior == self.conteudo:
                            # Usar update_fields para evitar atualizar data_edicao
                            kwargs['update_fields'] = ['versao', 'editado_por', 'status', 'data_finalizacao']
                            # Não incrementar versão se não houve mudança real
                            if not kwargs.get('force_update_data', False):
                                kwargs['update_fields'] = [f for f in kwargs['update_fields'] if f != 'versao']
                        else:
                            # Se houve mudança real, incrementar versão
                            self.versao += 1
                    else:
                        # Se não encontrou registro anterior, incrementar versão
                        self.versao += 1
            except Exception:
                # Em caso de erro, incrementar versão por segurança
                self.versao += 1
        else:
            # Nova ata, versão 1
            self.versao = 1
        
        super().save(*args, **kwargs)
    
    def total_assinaturas(self):
        """Retorna o total de assinaturas na ata"""
        return self.assinaturas.count()
    
    def assinaturas_pendentes(self):
        """Retorna as assinaturas pendentes"""
        membros_presentes = self.sessao.presencas.filter(presente=True)
        assinaturas_existentes = self.assinaturas.values_list('membro_id', flat=True)
        return membros_presentes.exclude(id__in=assinaturas_existentes)
    
    def pode_ser_finalizada(self):
        """Verifica se a ata pode ser finalizada (todos os presentes assinaram)"""
        return self.total_assinaturas() >= self.sessao.total_presentes


class AssinaturaAta(models.Model):
    """Assinaturas dos membros na ata da sessão"""
    
    TIPO_ASSINATURA_CHOICES = [
        ('ELABORACAO', 'Elaboração'),
        ('REVISAO', 'Revisão'),
        ('APROVACAO', 'Aprovação'),
        ('HOMOLOGACAO', 'Homologação'),
        ('OUTROS', 'Outros'),
    ]
    
    ata = models.ForeignKey(AtaSessao, on_delete=models.CASCADE, related_name='assinaturas', verbose_name="Ata")
    membro = models.ForeignKey(MembroComissao, on_delete=models.CASCADE, verbose_name="Membro")
    assinado_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Assinado por")
    data_assinatura = models.DateTimeField(auto_now_add=True, verbose_name="Data da Assinatura")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Campos para assinatura eletrônica
    hash_documento = models.CharField(max_length=255, blank=True, null=True, verbose_name="Hash do Documento")
    timestamp = models.CharField(max_length=100, blank=True, null=True, verbose_name="Timestamp da Assinatura")
    assinatura_digital = models.TextField(blank=True, null=True, verbose_name="Assinatura Digital")
    certificado = models.CharField(max_length=100, blank=True, null=True, verbose_name="Certificado Digital")
    ip_assinatura = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP da Assinatura")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    
    # Campos para função e tipo de assinatura
    funcao_assinatura = models.CharField(max_length=200, blank=True, null=True, verbose_name="Função para Assinatura")
    tipo_assinatura = models.CharField(
        max_length=15, 
        choices=TIPO_ASSINATURA_CHOICES, 
        default='APROVACAO',
        verbose_name="Tipo de Assinatura"
    )
    
    class Meta:
        verbose_name = "Assinatura da Ata"
        verbose_name_plural = "Assinaturas da Ata"
        unique_together = ['ata', 'membro']
        ordering = ['data_assinatura']
    
    def __str__(self):
        return f"Assinatura de {self.membro.militar.nome_completo} - Ata {self.ata.sessao.numero}"
    
    @property
    def assinatura_eletronica(self):
        """Verifica se é uma assinatura eletrônica"""
        return bool(self.hash_documento and self.assinatura_digital)


class ModeloAta(models.Model):
    """Modelos/templates de atas que podem ser salvos e reutilizados"""
    
    TIPO_COMISSAO_CHOICES = [
        ('CPO', 'Comissão de Promoções de Oficiais'),
        ('CPP', 'Comissão de Promoções de Praças'),
        ('GERAL', 'Geral (Ambos os tipos)'),
    ]
    
    TIPO_SESSAO_CHOICES = [
        ('ORDINARIA', 'Ordinária'),
        ('EXTRAORDINARIA', 'Extraordinária'),
        ('ESPECIAL', 'Especial'),
        ('GERAL', 'Geral (Todos os tipos)'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name="Nome do Modelo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    tipo_comissao = models.CharField(max_length=10, choices=TIPO_COMISSAO_CHOICES, default='GERAL', verbose_name="Tipo de Comissão")
    tipo_sessao = models.CharField(max_length=15, choices=TIPO_SESSAO_CHOICES, default='GERAL', verbose_name="Tipo de Sessão")
    conteudo = CKEditor5Field('Conteúdo do Modelo', help_text="Use variáveis como {{sessao.numero}}, {{sessao.data_sessao}}, {{sessao.local}}, etc.", config_name='modelo_ata_config')
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    padrao = models.BooleanField(default=False, verbose_name="Modelo Padrão", help_text="Se marcado, será usado como modelo padrão para novas atas")
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Criado por")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Modelo de Ata"
        verbose_name_plural = "Modelos de Ata"
        ordering = ['-padrao', 'nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_comissao_display()})"
    
    def aplicar_variaveis(self, sessao):
        """Aplica as variáveis do modelo com os dados da sessão"""
        from django.template import Template, Context
        
        # Criar contexto com dados da sessão
        context = Context({
            'sessao': sessao,
            'comissao': sessao.comissao,
        })
        
        # Renderizar template
        template = Template(self.conteudo)
        return template.render(context)
    
    def pode_ser_usado_para(self, sessao):
        """Verifica se o modelo pode ser usado para uma determinada sessão"""
        if not self.ativo:
            return False
        
        # Verificar tipo de comissão
        if self.tipo_comissao != 'GERAL' and self.tipo_comissao != sessao.comissao.tipo:
            return False
        
        # Verificar tipo de sessão
        if self.tipo_sessao != 'GERAL' and self.tipo_sessao != sessao.tipo:
            return False
        
        return True
    
    def save(self, *args, **kwargs):
        # Se este modelo está sendo marcado como padrão, desmarcar outros do mesmo tipo
        if self.padrao:
            ModeloAta.objects.filter(
                tipo_comissao=self.tipo_comissao,
                tipo_sessao=self.tipo_sessao,
                padrao=True
            ).exclude(pk=self.pk).update(padrao=False)
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_modelo_padrao(cls, sessao):
        """Retorna o modelo padrão para uma sessão específica"""
        return cls.objects.filter(
            padrao=True,
            ativo=True
        ).filter(
            models.Q(tipo_comissao='GERAL') | models.Q(tipo_comissao=sessao.comissao.tipo)
        ).filter(
            models.Q(tipo_sessao='GERAL') | models.Q(tipo_sessao=sessao.tipo)
        ).first()
    
    @classmethod
    def get_modelos_disponiveis(cls, sessao):
        """Retorna todos os modelos disponíveis para uma sessão específica"""
        return cls.objects.filter(
            ativo=True
        ).filter(
            models.Q(tipo_comissao='GERAL') | models.Q(tipo_comissao=sessao.comissao.tipo)
        ).filter(
            models.Q(tipo_sessao='GERAL') | models.Q(tipo_sessao=sessao.tipo)
        ).order_by('-padrao', 'nome')


class NotificacaoSessao(models.Model):
    """Notificações de sessões para usuários"""
    
    TIPO_CHOICES = [
        ('SESSAO_PENDENTE', 'Sessão Pendente'),
        ('VOTACAO_PENDENTE', 'Votação Pendente'),
        ('SESSAO_AGENDADA', 'Sessão Agendada'),
        ('SESSAO_HOJE', 'Sessão Hoje'),
        ('DELIBERACAO_PENDENTE', 'Deliberação Pendente'),
        ('ATA_PENDENTE', 'Ata Pendente'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes_sessao', verbose_name="Usuário")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Notificação")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensagem = models.TextField(verbose_name="Mensagem")
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='MEDIA', verbose_name="Prioridade")
    lida = models.BooleanField(default=False, verbose_name="Lida")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_leitura = models.DateTimeField(null=True, blank=True, verbose_name="Data de Leitura")
    
    # Referências opcionais para sessões, deliberações, etc.
    sessao = models.ForeignKey(SessaoComissao, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Sessão")
    deliberacao = models.ForeignKey(DeliberacaoComissao, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Deliberação")
    comissao = models.ForeignKey(ComissaoPromocao, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Comissão")
    
    class Meta:
        verbose_name = "Notificação de Sessão"
        verbose_name_plural = "Notificações de Sessão"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['usuario', 'lida']),
            models.Index(fields=['tipo', 'data_criacao']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
    
    def marcar_como_lida(self):
        """Marca a notificação como lida"""
        if not self.lida:
            self.lida = True
            self.data_leitura = timezone.now()
            self.save(update_fields=['lida', 'data_leitura'])
    
    @classmethod
    def criar_notificacao_sessao_pendente(cls, usuario, sessao):
        """Cria notificação para sessão pendente"""
        if not cls.objects.filter(
            usuario=usuario,
            tipo='SESSAO_PENDENTE',
            sessao=sessao,
            lida=False
        ).exists():
            return cls.objects.create(
                usuario=usuario,
                tipo='SESSAO_PENDENTE',
                titulo=f"Sessão {sessao.numero} Pendente",
                mensagem=f"A sessão {sessao.numero} da {sessao.comissao.nome} está pendente de votação.",
                prioridade='ALTA',
                sessao=sessao,
                comissao=sessao.comissao
            )
        return None
    
    @classmethod
    def criar_notificacao_votacao_pendente(cls, usuario, deliberacao):
        """Cria notificação para votação pendente"""
        if not cls.objects.filter(
            usuario=usuario,
            tipo='VOTACAO_PENDENTE',
            deliberacao=deliberacao,
            lida=False
        ).exists():
            return cls.objects.create(
                usuario=usuario,
                tipo='VOTACAO_PENDENTE',
                titulo=f"Votação Pendente - Deliberação {deliberacao.numero}",
                mensagem=f"A deliberação '{deliberacao.assunto}' da sessão {deliberacao.sessao.numero} aguarda sua votação.",
                prioridade='URGENTE',
                deliberacao=deliberacao,
                sessao=deliberacao.sessao,
                comissao=deliberacao.sessao.comissao
            )
        return None
    
    @classmethod
    def criar_notificacao_sessao_hoje(cls, usuario, sessao):
        """Cria notificação para sessão hoje"""
        if not cls.objects.filter(
            usuario=usuario,
            tipo='SESSAO_HOJE',
            sessao=sessao,
            lida=False
        ).exists():
            return cls.objects.create(
                usuario=usuario,
                tipo='SESSAO_HOJE',
                titulo=f"Sessão {sessao.numero} Hoje",
                mensagem=f"A sessão {sessao.numero} da {sessao.comissao.nome} está agendada para hoje às {sessao.hora_inicio.strftime('%H:%M')}.",
                prioridade='URGENTE',
                sessao=sessao,
                comissao=sessao.comissao
            )
        return None
    
    @classmethod
    def limpar_notificacoes_antigas(cls, dias=30):
        """Remove notificações antigas"""
        from datetime import timedelta
        data_limite = timezone.now() - timedelta(days=dias)
        cls.objects.filter(
            data_criacao__lt=data_limite,
            lida=True
        ).delete()


class VagaManual(models.Model):
    """Vagas manuais que podem surgir - inserção manual"""
    
    POSTO_CHOICES = [
        ('2T', '2º Tenente'),
        ('1T', '1º Tenente'),
        ('CP', 'Capitão'),
        ('MJ', 'Major'),
        ('TC', 'Tenente-Coronel'),
        ('CB', 'Coronel'),
    ]
    
    QUADRO_CHOICES = [
        ('COMB', 'Combatente'),
        ('SAUDE', 'Saúde'),
        ('ENG', 'Engenheiro'),
        ('COMP', 'Complementar'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADA', 'Aprovada'),
        ('REJEITADA', 'Rejeitada'),
        ('IMPLEMENTADA', 'Implementada'),
    ]
    
    posto = models.CharField(max_length=4, choices=POSTO_CHOICES, verbose_name="Posto")
    quadro = models.CharField(max_length=5, choices=QUADRO_CHOICES, verbose_name="Quadro")
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade de Vagas")
    justificativa = models.TextField(verbose_name="Justificativa")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status")
    data_solicitacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Solicitação")
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name="Data da Aprovação")
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Aprovado por")
    data_implementacao = models.DateTimeField(null=True, blank=True, verbose_name="Data da Implementação")
    
    class Meta:
        verbose_name = "Vaga Manual"
        verbose_name_plural = "Vagas Manuais"
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"{self.get_posto_display()} - {self.get_quadro_display()} ({self.quantidade} vaga{'s' if self.quantidade > 1 else ''})"
    
    def get_quadro_completo_display(self):
        """Retorna o nome completo do quadro"""
        quadro_nomes = {
            'COMB': 'Quadro de Oficiais Bombeiros Militares Combatentes - QOBM/Comb.',
            'SAUDE': 'Quadro de Oficiais Bombeiros Militares de Saúde - QOBM/Saúde',
            'ENG': 'Quadro de Oficiais Bombeiros Militares Engenheiros - QOBM/Eng.',
            'COMP': 'Quadro de Oficiais Bombeiros Militares Complementar - QOBM/Comp.',
        }
        return quadro_nomes.get(self.quadro, self.get_quadro_display())


class QuadroFixacaoVagas(models.Model):
    """Quadro de Fixação de Vagas para Oficiais"""
    
    TIPO_CHOICES = [
        ('OFICIAIS', 'Oficiais'),
        ('PRACAS', 'Praças'),
    ]
    
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('EM_ELABORACAO', 'Em Elaboração'),
        ('FINALIZADO', 'Finalizado'),
        ('APROVADO', 'Aprovado'),
        ('HOMOLOGADO', 'Homologado'),
    ]

    numero = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Numeração do Quadro",
        help_text="Numeração automática e única, ex: QFV-OF-2025/07/18 ou QFV-OF-2025/07/18 - A 01"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título do Quadro")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='OFICIAIS', verbose_name="Tipo")
    data_criacao = models.DateField(auto_now_add=True, verbose_name="Data de Criação")
    data_promocao = models.DateField(verbose_name="Data da Promoção")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='RASCUNHO', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações Gerais")
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Criado por")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Quadro de Fixação de Vagas"
        verbose_name_plural = "Quadros de Fixação de Vagas"
        ordering = ['-data_promocao', '-data_criacao']
        # Remover qualquer unique_together por data_promocao

    def __str__(self):
        return f"{self.numero} - {self.titulo} - {self.get_tipo_display()} - {self.data_promocao.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        if not self.numero:
            # Gera a numeração: QFV-TIPO-AAAA/MM/DD - 01 ou QFV-TIPO-AAAA/MM/DD - 01 A XX
            ano = self.data_promocao.year
            mes = self.data_promocao.month
            dia = self.data_promocao.day
            
            # Define o prefixo baseado no tipo
            tipo_prefixo = 'OF' if self.tipo == 'OFICIAIS' else 'PR'
            base_numero = f"QFV-{tipo_prefixo}-{ano:04d}/{mes:02d}/{dia:02d}"
            
            # Verifica se já existe um quadro para a mesma data
            quadros_existentes = QuadroFixacaoVagas.objects.filter(
                data_promocao=self.data_promocao,
                tipo=self.tipo
            ).exclude(pk=self.pk if self.pk else None)
            
            if quadros_existentes.exists():
                # Se já existe, verifica se é o primeiro aditamento ou subsequente
                primeiro_quadro = quadros_existentes.filter(
                    numero__startswith=base_numero
                ).exclude(
                    numero__contains=' A '
                ).first()
                
                if primeiro_quadro:
                    # Já existe o quadro principal, este será um aditamento
                    max_aditamento = 0
                    for quadro in quadros_existentes:
                        if ' A ' in quadro.numero:
                            try:
                                # Extrai o número do aditamento (ex: "01 A 02" -> 2)
                                aditamento_part = quadro.numero.split(' A ')[1]
                                aditamento_num = int(aditamento_part)
                                max_aditamento = max(max_aditamento, aditamento_num)
                            except (ValueError, IndexError):
                                pass
                    self.numero = f"{base_numero} - 01 A {max_aditamento + 1:02d}"
                else:
                    # Não existe quadro principal, este será o primeiro
                    self.numero = f"{base_numero} - 01"
            else:
                # Primeiro quadro para esta data
                self.numero = f"{base_numero} - 01"
        super().save(*args, **kwargs)

    def get_geracao_display(self):
        """Retorna a geração em formato legível (01, 02, 03... ou 1º Aditamento, etc.)"""
        if not self.numero:
            return "N/A"
        
        # Se não tem " A " no número, é o quadro principal - extrai o número sequencial
        if ' A ' not in self.numero:
            try:
                # Extrai o número sequencial do final (ex: QFV-OF-2025/07/18 - 01)
                seq_part = self.numero.split(' - ')[1]
                seq_num = int(seq_part)
                return f"{seq_num:02d}"
            except (ValueError, IndexError):
                return "Quadro Principal"
        
        # Extrai o número do aditamento
        try:
            aditamento_part = self.numero.split(' A ')[1]
            aditamento_num = int(aditamento_part)
            
            # Mapeia números para nomes
            aditamentos = {
                1: "1º Aditamento",
                2: "2º Aditamento", 
                3: "3º Aditamento",
                4: "4º Aditamento",
                5: "5º Aditamento",
                6: "6º Aditamento",
                7: "7º Aditamento",
                8: "8º Aditamento",
                9: "9º Aditamento",
                10: "10º Aditamento",
                11: "11º Aditamento",
                12: "12º Aditamento",
                13: "13º Aditamento",
                14: "14º Aditamento",
                15: "15º Aditamento",
                16: "16º Aditamento",
                17: "17º Aditamento",
                18: "18º Aditamento",
                19: "19º Aditamento",
                20: "20º Aditamento"
            }
            
            return aditamentos.get(aditamento_num, f"{aditamento_num}º Aditamento")
        except (ValueError, IndexError):
            return "N/A"


class ItemQuadroFixacaoVagas(models.Model):
    """Itens do Quadro de Fixação de Vagas"""
    
    quadro = models.ForeignKey(QuadroFixacaoVagas, on_delete=models.CASCADE, related_name='itens', verbose_name="Quadro")
    previsao_vaga = models.ForeignKey(PrevisaoVaga, on_delete=models.CASCADE, verbose_name="Previsão de Vaga")
    vagas_fixadas = models.PositiveIntegerField(default=0, verbose_name="Vagas Fixadas")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Item do Quadro de Fixação de Vagas"
        verbose_name_plural = "Itens do Quadro de Fixação de Vagas"
        unique_together = ['quadro', 'previsao_vaga']
        ordering = ['previsao_vaga__quadro', 'previsao_vaga__posto']
    
    def __str__(self):
        return f"{self.previsao_vaga.get_quadro_display()} - {self.previsao_vaga.get_posto_display()} - {self.vagas_fixadas} vagas"
    
    @property
    def vagas_disponiveis(self):
        """Retorna as vagas disponíveis da previsão"""
        return self.previsao_vaga.vagas_disponiveis
    
    @property
    def efetivo_atual(self):
        """Retorna o efetivo atual da previsão"""
        return self.previsao_vaga.efetivo_atual
    
    @property
    def efetivo_previsto(self):
        """Retorna o efetivo previsto da previsão"""
        return self.previsao_vaga.efetivo_previsto
    
    @property
    def claro(self):
        """Retorna as vagas claras (disponíveis) da previsão"""
        return self.previsao_vaga.vagas_disponiveis
    
    @property
    def quadro_display(self):
        """Retorna o display do quadro da previsão"""
        return self.previsao_vaga.get_quadro_display()
    
    @property
    def posto_display(self):
        """Retorna o display do posto da previsão"""
        return self.previsao_vaga.get_posto_display()

    @property
    def efetivo_atual_real(self):
        if self.previsao_vaga.posto == 'ST' and self.previsao_vaga.quadro == 'PRACAS':
            return Militar.objects.filter(
                posto_graduacao='ST',
                quadro='COMP',
                situacao='AT'
            ).count()
        else:
            return Militar.objects.filter(
                posto_graduacao=self.previsao_vaga.posto,
                quadro=self.previsao_vaga.quadro,
                situacao='AT'
            ).count()
    
    def save(self, *args, **kwargs):
        """Sobrescreve o save para garantir que vagas fixadas sejam sempre iguais às vagas disponíveis"""
        # Sempre sincronizar vagas fixadas com vagas disponíveis
        self.vagas_fixadas = self.previsao_vaga.vagas_disponiveis
        super().save(*args, **kwargs)


class AssinaturaQuadroFixacaoVagas(models.Model):
    """Assinaturas de um quadro de fixação de vagas - permite múltiplas assinaturas"""
    
    TIPO_ASSINATURA_CHOICES = [
        ('APROVACAO', 'Aprovação'),
        ('HOMOLOGACAO', 'Homologação'),
        ('REVISAO', 'Revisão'),
        ('CONFERENCIA', 'Conferência'),
        ('ELETRONICA', 'Eletrônica'),
    ]
    
    quadro_fixacao_vagas = models.ForeignKey(QuadroFixacaoVagas, on_delete=models.CASCADE, verbose_name="Quadro de Fixação de Vagas", related_name="assinaturas")
    assinado_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Assinado por")
    data_assinatura = models.DateTimeField(auto_now_add=True, verbose_name="Data da Assinatura")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações da Assinatura")
    tipo_assinatura = models.CharField(
        max_length=15, 
        choices=TIPO_ASSINATURA_CHOICES, 
        default='APROVACAO',
        verbose_name="Tipo de Assinatura"
    )
    funcao_assinatura = models.CharField(
        blank=True,
        help_text="Função/cargo do usuário no momento da assinatura",
        max_length=100,
        null=True,
        verbose_name="Função no momento da assinatura",
    )
    
    class Meta:
        verbose_name = "Assinatura do Quadro de Fixação de Vagas"
        verbose_name_plural = "Assinaturas do Quadro de Fixação de Vagas"
        ordering = ['-data_assinatura']
        unique_together = ['quadro_fixacao_vagas', 'assinado_por', 'tipo_assinatura']
    
    def __str__(self):
        return f"{self.quadro_fixacao_vagas.titulo} - {self.assinado_por.get_full_name()} - {self.get_tipo_assinatura_display()}"
    
    def verificar_permissao_assinatura(self, usuario):
        """Verifica se o usuário tem permissão para assinar este tipo de documento"""
        # Para quadros de oficiais, verificar se é membro da CPO
        if self.quadro_fixacao_vagas.tipo == 'OFICIAIS':
            comissao_cpo = ComissaoPromocao.get_comissao_ativa_por_tipo('CPO')
            if not comissao_cpo or not comissao_cpo.pode_assinar_documento_oficial(usuario):
                return False
        # Para quadros de praças, verificar se é membro da CPP
        elif self.quadro_fixacao_vagas.tipo == 'PRACAS':
            comissao_cpp = ComissaoPromocao.get_comissao_ativa_por_tipo('CPP')
            if not comissao_cpp or not comissao_cpp.pode_assinar_documento_praca(usuario):
                return False
        return True

@receiver(post_save, sender=Militar)
def criar_usuario_para_militar(sender, instance, created, **kwargs):
    """Cria usuário automaticamente para militar quando criado"""
    if created and not instance.user:
        try:
            # Criar usuário com username baseado na matrícula
            username = f"militar_{instance.matricula}"
            email = instance.email if instance.email else f"{username}@cbmepi.pi.gov.br"
            
            # Verificar se já existe usuário com este username
            if User.objects.filter(username=username).exists():
                username = f"{username}_{instance.pk}"
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=instance.nome_completo.split()[0] if instance.nome_completo else '',
                last_name=' '.join(instance.nome_completo.split()[1:]) if instance.nome_completo and len(instance.nome_completo.split()) > 1 else '',
                password=instance.cpf.replace('.', '').replace('-', '').replace('/', '')  # CPF como senha inicial
            )
            
            instance.user = user
            instance.save(update_fields=['user'])
            
        except Exception as e:
            print(f"Erro ao criar usuário para militar {instance.matricula}: {e}")


@receiver(post_save, sender=Militar)
def atualizar_fichas_conceito_militar(sender, instance, **kwargs):
    """Atualiza fichas de conceito quando militar é salvo"""
    try:
        # Atualizar ficha de conceito de oficiais se existir
        ficha_oficiais = instance.fichaconceitooficiais_set.first()
        if ficha_oficiais:
            ficha_oficiais.save()
        
        # Atualizar ficha de conceito de praças se existir
        ficha_pracas = instance.fichaconceitopracas_set.first()
        if ficha_pracas:
            ficha_pracas.save()
            
    except Exception as e:
        print(f"Erro ao atualizar fichas de conceito para militar {instance.matricula}: {e}")


class CargoFuncao(models.Model):
    """Cargos/Funções possíveis para usuários do sistema (ex: Presidente, Membro Nato, etc)"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Cargo/Função")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        verbose_name = "Cargo/Função do Sistema"
        verbose_name_plural = "Cargos/Funções do Sistema"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class UsuarioFuncao(models.Model):
    """Funções/cargos atribuídos diretamente aos usuários do sistema"""
    
    TIPO_FUNCAO_CHOICES = [
        ('ADMINISTRATIVO', 'Administrativo'),
        ('OPERACIONAL', 'Operacional'),
        ('COMISSAO', 'Membro de Comissão'),
        ('GESTAO', 'Gestão'),
        ('SUPORTE', 'Suporte Técnico'),
        ('OUTROS', 'Outros'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo'),
        ('SUSPENSO', 'Suspenso'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='funcoes', verbose_name="Usuário")
    cargo_funcao = models.ForeignKey(CargoFuncao, on_delete=models.CASCADE, verbose_name="Cargo/Função")
    tipo_funcao = models.CharField(max_length=20, choices=TIPO_FUNCAO_CHOICES, verbose_name="Tipo de Função")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ATIVO', verbose_name="Status")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Término")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Função do Usuário"
        verbose_name_plural = "Funções dos Usuários"
        ordering = ['usuario__first_name', 'data_inicio']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.cargo_funcao.nome}"
    
    def esta_ativo(self):
        """Verifica se a função está ativa"""
        hoje = date.today()
        return (
            self.status == 'ATIVO' and 
            self.data_inicio <= hoje and 
            (not self.data_fim or self.data_fim >= hoje)
        )
    
    @property
    def duracao_dias(self):
        """Retorna a duração em dias da função"""
        if self.data_fim:
            return (self.data_fim - self.data_inicio).days
        return (date.today() - self.data_inicio).days
    
    def pode_ser_editada_por(self, usuario):
        """Verifica se um usuário pode editar esta função"""
        return usuario.is_staff or usuario == self.usuario


class PermissaoFuncao(models.Model):
    """Permissões específicas para cada cargo/função"""
    
    MODULOS_CHOICES = [
        ('MILITARES', 'Gestão de Militares'),
        ('FICHAS_CONCEITO', 'Fichas de Conceito'),
        ('QUADROS_ACESSO', 'Quadros de Acesso'),
        ('PROMOCOES', 'Promoções'),
        ('VAGAS', 'Gestão de Vagas'),
        ('COMISSAO', 'Comissão de Promoções'),
        ('DOCUMENTOS', 'Documentos'),
        ('USUARIOS', 'Gestão de Usuários'),
        ('RELATORIOS', 'Relatórios'),
        ('CONFIGURACOES', 'Configurações do Sistema'),
    ]
    
    ACESSOS_CHOICES = [
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
    
    cargo_funcao = models.ForeignKey(CargoFuncao, on_delete=models.CASCADE, related_name='permissoes', verbose_name="Cargo/Função", null=True, blank=True)
    modulo = models.CharField(max_length=20, choices=MODULOS_CHOICES, verbose_name="Módulo")
    acesso = models.CharField(max_length=20, choices=ACESSOS_CHOICES, verbose_name="Tipo de Acesso")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Permissão de Função"
        verbose_name_plural = "Permissões de Funções"
        unique_together = ['cargo_funcao', 'modulo', 'acesso']
        ordering = ['cargo_funcao__nome', 'modulo', 'acesso']
    
    def __str__(self):
        if self.cargo_funcao:
            return f"{self.cargo_funcao.nome} - {self.get_modulo_display()} - {self.get_acesso_display()}"
        else:
            return f"Genérica - {self.get_modulo_display()} - {self.get_acesso_display()}"


class PerfilAcesso(models.Model):
    """Perfis de acesso predefinidos para facilitar a configuração"""
    
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Perfil")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    permissoes = models.ManyToManyField(PermissaoFuncao, blank=True, verbose_name="Permissões")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Perfil de Acesso"
        verbose_name_plural = "Perfis de Acesso"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def aplicar_perfil(self, cargo_funcao):
        """Aplica as permissões do perfil a um cargo/função"""
        # Remove permissões existentes
        PermissaoFuncao.objects.filter(cargo_funcao=cargo_funcao).delete()
        
        # Adiciona as permissões do perfil
        for permissao in self.permissoes.all():
            PermissaoFuncao.objects.create(
                cargo_funcao=cargo_funcao,
                modulo=permissao.modulo,
                acesso=permissao.acesso,
                observacoes=f"Aplicado do perfil: {self.nome}"
            )


class CalendarioPromocao(models.Model):
    """Modelo para gerenciar calendários de promoções"""
    ANO_CHOICES = [(str(year), str(year)) for year in range(2020, 2031)]
    SEMESTRE_CHOICES = [
        ('1', '1º Semestre'),
        ('2', '2º Semestre'),
    ]
    TIPO_CHOICES = [
        ('OFICIAIS', 'Oficiais'),
        ('PRACAS', 'Praças'),
    ]
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('EM_ELABORACAO', 'Em Elaboração'),
        ('APROVADO', 'Aprovado'),
        ('HOMOLOGADO', 'Homologado'),
    ]

    numero = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Numeração do Calendário",
        help_text="Numeração automática e única, ex: CAL-OF-2025/1 ou CAL-OF-2025/1-A01"
    )
    ano = models.CharField(max_length=4, choices=ANO_CHOICES, verbose_name="Ano")
    semestre = models.CharField(max_length=1, choices=SEMESTRE_CHOICES, verbose_name="Semestre")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='OFICIAIS', verbose_name="Tipo")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='RASCUNHO', verbose_name="Status")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Aprovação")
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Aprovado por", related_name="calendarios_aprovados")
    data_homologacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Homologação")
    homologado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Homologado por", related_name="calendarios_homologados")

    class Meta:
        verbose_name = "Calendário de Promoção"
        verbose_name_plural = "Calendários de Promoção"
        ordering = ['-ano', '-semestre', 'tipo', '-data_criacao']

    def __str__(self):
        if self.numero:
            return f"Calendário {self.numero} - {self.get_tipo_display()} - {self.get_semestre_display()} {self.ano}"
        return f"Calendário {self.get_tipo_display()} - {self.get_semestre_display()} {self.ano}"

    @property
    def periodo_completo(self):
        return f"{self.get_tipo_display()} - {self.get_semestre_display()} {self.ano}"

    def save(self, *args, **kwargs):
        if not self.numero:
            # Gerar numeração automática
            tipo_prefixo = 'OF' if self.tipo == 'OFICIAIS' else 'PR'
            base_numero = f"CAL-{tipo_prefixo}-{self.ano}/{self.semestre}"
            
            # Buscar calendários existentes com a mesma base
            calendarios_existentes = CalendarioPromocao.objects.filter(
                numero__startswith=base_numero
            ).exclude(pk=self.pk).order_by('numero')
            
            if calendarios_existentes.exists():
                # Já existe um calendário principal, este será um aditamento
                ultimo_aditamento = calendarios_existentes.filter(
                    numero__contains='-A'
                ).order_by('numero').last()
                
                if ultimo_aditamento:
                    # Extrair o número do último aditamento
                    numero_ultimo = ultimo_aditamento.numero
                    if '-A' in numero_ultimo:
                        try:
                            num_aditamento = int(numero_ultimo.split('-A')[-1])
                            self.numero = f"{base_numero}-A{num_aditamento + 1:02d}"
                        except ValueError:
                            self.numero = f"{base_numero}-A01"
                    else:
                        self.numero = f"{base_numero}-A01"
                else:
                    self.numero = f"{base_numero}-A01"
            else:
                # Primeiro calendário para este período
                self.numero = base_numero
        
        super().save(*args, **kwargs)

    def pode_ser_excluido(self):
        """Verifica se o calendário pode ser excluído"""
        return self.status in ['RASCUNHO', 'EM_ELABORACAO']

    def pode_ser_editado(self):
        """Verifica se o calendário pode ser editado"""
        return self.status in ['RASCUNHO', 'EM_ELABORACAO']

    def aprovar(self, usuario):
        """Aprova o calendário"""
        if self.status in ['RASCUNHO', 'EM_ELABORACAO']:
            self.status = 'APROVADO'
            self.data_aprovacao = timezone.now()
            self.aprovado_por = usuario
            self.save()

    def homologar(self, usuario):
        """Homologa o calendário"""
        if self.status == 'APROVADO':
            self.status = 'HOMOLOGADO'
            self.data_homologacao = timezone.now()
            self.homologado_por = usuario
            self.save()

    def is_aditamento(self):
        """Verifica se é um aditamento"""
        return '-A' in self.numero if self.numero else False

    def get_calendario_principal(self):
        """Retorna o calendário principal (sem aditamento)"""
        if self.is_aditamento():
            base_numero = self.numero.split('-A')[0]
            return CalendarioPromocao.objects.filter(numero=base_numero).first()
        return self

    def get_aditamentos(self):
        """Retorna os aditamentos deste calendário"""
        if not self.is_aditamento():
            base_numero = self.numero
            return CalendarioPromocao.objects.filter(
                numero__startswith=f"{base_numero}-A"
            ).order_by('numero')
        return CalendarioPromocao.objects.none()
    
    def get_titulo_completo(self):
        """Retorna o título completo do calendário"""
        if self.numero and ' A ' in self.numero:
            # É um aditamento
            return f"Calendário {self.numero} - {self.get_tipo_display()} - {self.get_semestre_display()} {self.ano} (Aditamento)"
        else:
            # É um calendário principal
            return f"Calendário {self.numero} - {self.get_tipo_display()} - {self.get_semestre_display()} {self.ano}"


class AssinaturaCalendarioPromocao(models.Model):
    """Modelo para assinaturas eletrônicas de calendários de promoção"""
    TIPO_ASSINATURA_CHOICES = [
        ('ELABORACAO', 'Elaboração'),
        ('REVISAO', 'Revisão'),
        ('APROVACAO', 'Aprovação'),
        ('HOMOLOGACAO', 'Homologação'),
        ('OUTROS', 'Outros'),
    ]
    
    calendario = models.ForeignKey(
        CalendarioPromocao, 
        on_delete=models.CASCADE, 
        related_name='assinaturas',
        verbose_name="Calendário"
    )
    tipo_assinatura = models.CharField(
        max_length=20, 
        choices=TIPO_ASSINATURA_CHOICES,
        verbose_name="Tipo de Assinatura"
    )
    assinado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Assinado por"
    )
    data_assinatura = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Assinatura"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações"
    )
    funcao_assinatura = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Função para Assinatura"
    )
    hash_assinatura = models.CharField(
        max_length=255,
        verbose_name="Hash da Assinatura"
    )
    codigo_verificacao = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código de Verificação"
    )
    
    class Meta:
        verbose_name = "Assinatura de Calendário de Promoção"
        verbose_name_plural = "Assinaturas de Calendários de Promoção"
        ordering = ['-data_assinatura']
    
    def __str__(self):
        return f"Assinatura {self.get_tipo_assinatura_display()} - {self.calendario.numero} - {self.assinado_por.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.codigo_verificacao:
            # Gerar código de verificação único
            import uuid
            self.codigo_verificacao = f"CP-{uuid.uuid4().hex[:8].upper()}"
        
        if not self.hash_assinatura:
            # Gerar hash da assinatura
            import hashlib
            dados = f"{self.calendario.numero}{self.tipo_assinatura}{self.assinado_por.username}{self.data_assinatura}"
            self.hash_assinatura = hashlib.sha256(dados.encode()).hexdigest()
        
        super().save(*args, **kwargs)


class ItemCalendarioPromocao(models.Model):
    """Itens/atividades do calendário de promoções"""
    TIPO_ATIVIDADE_CHOICES = [
        ('FIXACAO_VAGAS', 'Fixação de vagas (DGP/CBMEPI)'),
        ('ENCAMINHAMENTO_FICHAS', 'Atualização das fichas de conceito e assentamentos'),
        ('INSPECAO_SAUDE', 'Inspeção de Saúde'),
        ('PUBLICACAO_INSPECAO', 'Publicação da Inspeção de Saúde'),
        ('PRAZO_RECURSO_INSPECAO', 'Prazo para interposição de recurso da Inspeção de Saúde'),
        ('ANALISE_RECURSO_INSPECAO', 'Prazo para análise de interposição de recurso da Inspeção de Saúde'),
        ('INSPECAO_RECURSOS', 'Prazo para Inspeção de Saúde de recursos deferidos'),
        ('PUBLICACAO_RECURSOS', 'Publicação da Inspeção de Saúde de recursos deferidos'),
        ('ANALISE_QUADRO', 'Análise e aprovação do Quadro de Acesso'),
        ('PUBLICACAO_QUADRO', 'Publicação do Quadro de Acesso'),
        ('PRAZO_RECURSO_QUADRO', 'Prazo para interposição de recurso do Quadro de Acesso'),
        ('ANALISE_RECURSO_QUADRO', 'Prazo para análise de interposição de recurso do Quadro de Acesso'),
        ('ANALISE_ALTERACOES', 'Análise e aprovação das alterações do Quadro de Acesso'),
        ('PUBLICACAO_ALTERACOES', 'Publicação das alterações do Quadro de Acesso'),
        ('PROPOSTA_PROMOCAO', 'Encaminhamento da Proposta de Promoção'),
        ('DATA_PROMOCAO', 'Data da Promoção'),
    ]
    
    # Ordem padrão das atividades (1 = primeiro, 2 = segundo, etc.)
    ORDEM_PADRAO = {
        'FIXACAO_VAGAS': 1,
        'ENCAMINHAMENTO_FICHAS': 2,
        'INSPECAO_SAUDE': 3,
        'PUBLICACAO_INSPECAO': 4,
        'PRAZO_RECURSO_INSPECAO': 5,
        'ANALISE_RECURSO_INSPECAO': 6,
        'INSPECAO_RECURSOS': 7,
        'PUBLICACAO_RECURSOS': 8,
        'ANALISE_QUADRO': 9,
        'PUBLICACAO_QUADRO': 10,
        'PRAZO_RECURSO_QUADRO': 11,
        'ANALISE_RECURSO_QUADRO': 12,
        'ANALISE_ALTERACOES': 13,
        'PUBLICACAO_ALTERACOES': 14,
        'PROPOSTA_PROMOCAO': 15,
        'DATA_PROMOCAO': 16,
    }
    
    calendario = models.ForeignKey(
        CalendarioPromocao, 
        on_delete=models.CASCADE, 
        related_name='itens',
        verbose_name="Calendário"
    )
    tipo_atividade = models.CharField(
        max_length=50, 
        choices=TIPO_ATIVIDADE_CHOICES,
        verbose_name="Tipo de Atividade"
    )
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Fim")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    
    class Meta:
        verbose_name = "Item do Calendário de Promoção"
        verbose_name_plural = "Itens do Calendário de Promoção"
        ordering = ['calendario', 'ordem']
        unique_together = ['calendario', 'tipo_atividade']
    
    def __str__(self):
        return f"{self.get_tipo_atividade_display()} - {self.calendario}"
    
    @property
    def periodo_formatado(self):
        if self.data_inicio == self.data_fim:
            return self.data_inicio.strftime('%d/%m/%Y')
        else:
            return f"{self.data_inicio.strftime('%d/%m/%Y')} a {self.data_fim.strftime('%d/%m/%Y')}"
    
    @property
    def status_atual(self):
        hoje = timezone.now().date()
        if hoje < self.data_inicio:
            return 'PENDENTE'
        elif self.data_inicio <= hoje <= self.data_fim:
            return 'EM_ANDAMENTO'
        else:
            return 'CONCLUIDO'

    def save(self, *args, **kwargs):
        # Aplicar ordem automática baseada no tipo de atividade
        if not self.ordem or self.ordem == 0:
            self.ordem = self.ORDEM_PADRAO.get(self.tipo_atividade, 999)
        
        super().save(*args, **kwargs)

    @classmethod
    def reordenar_itens_calendario(cls, calendario):
        """Reordena todos os itens de um calendário baseado na ordem padrão"""
        itens = cls.objects.filter(calendario=calendario).order_by('ordem', 'tipo_atividade')
        
        for i, item in enumerate(itens, 1):
            # Usar a ordem padrão se disponível, senão usar a posição atual
            ordem_padrao = cls.ORDEM_PADRAO.get(item.tipo_atividade, i)
            if item.ordem != ordem_padrao:
                item.ordem = ordem_padrao
                item.save(update_fields=['ordem'])
        
        return itens


class AlmanaqueMilitar(models.Model):
    """Modelo para armazenar almanaques dos militares gerados"""
    
    TIPO_CHOICES = [
        ('OFICIAIS', 'Oficiais'),
        ('PRACAS', 'Praças'),
        ('GERAL', 'Geral'),
    ]
    
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('EM_ELABORACAO', 'Em Elaboração'),
        ('FINALIZADO', 'Finalizado'),
        ('APROVADO', 'Aprovado'),
        ('HOMOLOGADO', 'Homologado'),
    ]
    
    numero = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Numeração do Almanaque",
        help_text="Numeração automática e única, ex: ALM-OF-2025/07/23 ou ALM-PR-2025/07/23"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='GERAL', verbose_name="Tipo")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='RASCUNHO', verbose_name="Status")
    data_geracao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Geração")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    data_ultima_promocao = models.DateField(null=True, blank=True, verbose_name="Data da Última Promoção")
    arquivo_pdf = models.FileField(upload_to='almanaques/', verbose_name="Arquivo PDF", blank=True, null=True)
    total_oficiais = models.IntegerField(default=0, verbose_name="Total de Oficiais")
    total_pracas = models.IntegerField(default=0, verbose_name="Total de Praças")
    total_geral = models.IntegerField(default=0, verbose_name="Total Geral")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    conteudo_html = models.TextField(blank=True, null=True, verbose_name="Conteúdo HTML")
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Criado por", null=True, blank=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Almanaque Militar"
        verbose_name_plural = "Almanaques Militares"
        ordering = ['-data_geracao']
    
    def __str__(self):
        return f"{self.numero} - {self.titulo}"
    
    def save(self, *args, **kwargs):
        if not self.numero:
            # Gerar numeração automática
            from datetime import datetime
            hoje = datetime.now()
            ano = hoje.year
            mes = hoje.month
            dia = hoje.day
            
            # Prefixo baseado no tipo
            if self.tipo == 'OFICIAIS':
                prefixo = 'ALM-OF'
            elif self.tipo == 'PRACAS':
                prefixo = 'ALM-PR'
            else:
                prefixo = 'ALM-GE'
            
            # Buscar último almanaque do mesmo tipo e data
            ultimo_almanaque = AlmanaqueMilitar.objects.filter(
                tipo=self.tipo,
                data_geracao__date=hoje.date()
            ).order_by('-numero').first()
            
            if ultimo_almanaque and ultimo_almanaque.numero:
                # Extrair número sequencial
                try:
                    numero_base = ultimo_almanaque.numero.split('-')[-1]
                    if len(numero_base) > 8:  # Tem sufixo
                        numero_seq = int(numero_base.split('A')[-1])
                        novo_numero_seq = numero_seq + 1
                        self.numero = f"{prefixo}-{ano:04d}/{mes:02d}/{dia:02d}-A{novo_numero_seq:02d}"
                    else:
                        self.numero = f"{prefixo}-{ano:04d}/{mes:02d}/{dia:02d}-A01"
                except:
                    self.numero = f"{prefixo}-{ano:04d}/{mes:02d}/{dia:02d}-A01"
            else:
                self.numero = f"{prefixo}-{ano:04d}/{mes:02d}/{dia:02d}"
        
        super().save(*args, **kwargs)
    
    def get_total_assinaturas(self):
        """Retorna o total de assinaturas do almanaque"""
        return self.assinaturas.count()
    
    def get_assinaturas_ordenadas(self):
        """Retorna as assinaturas ordenadas por data"""
        return self.assinaturas.order_by('data_assinatura')
    
    def pode_ser_editado(self):
        """Verifica se o almanaque pode ser editado"""
        return self.status in ['RASCUNHO', 'EM_ELABORACAO']
    
    def pode_ser_excluido(self):
        """Verifica se o almanaque pode ser excluído"""
        return self.status in ['RASCUNHO']
    
    def pode_ser_assinado(self):
        """Verifica se o almanaque pode ser assinado"""
        return self.status in ['RASCUNHO', 'EM_ELABORACAO', 'FINALIZADO', 'APROVADO']
    
    def get_status_color(self):
        """Retorna a cor do status para exibição"""
        colors = {
            'RASCUNHO': 'secondary',
            'EM_ELABORACAO': 'warning',
            'FINALIZADO': 'info',
            'APROVADO': 'success',
            'HOMOLOGADO': 'primary'
        }
        return colors.get(self.status, 'secondary')


class AssinaturaAlmanaque(models.Model):
    """Modelo para armazenar assinaturas dos almanaques"""
    
    TIPO_ASSINATURA_CHOICES = [
        ('APROVACAO', 'Aprovação'),
        ('HOMOLOGACAO', 'Homologação'),
        ('REVISAO', 'Revisão'),
        ('CONFERENCIA', 'Conferência'),
        ('ELETRONICA', 'Eletrônica'),
    ]
    
    almanaque = models.ForeignKey(
        AlmanaqueMilitar, 
        on_delete=models.CASCADE, 
        verbose_name="Almanaque",
        related_name="assinaturas"
    )
    assinado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Assinado por"
    )
    tipo_assinatura = models.CharField(
        max_length=15, 
        choices=TIPO_ASSINATURA_CHOICES, 
        default='APROVACAO',
        verbose_name="Tipo de Assinatura"
    )
    cargo_funcao = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name="Cargo/Função"
    )
    data_assinatura = models.DateTimeField(auto_now_add=True, verbose_name="Data da Assinatura")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Assinatura de Almanaque"
        verbose_name_plural = "Assinaturas de Almanaques"
        ordering = ['data_assinatura']
        unique_together = ['almanaque', 'assinado_por', 'tipo_assinatura']
    
    def __str__(self):
        return f"Assinatura de {self.assinado_por.get_full_name()} em {self.almanaque.numero}"
    
    def verificar_permissao_assinatura(self, usuario):
        """Verifica se o usuário tem permissão para assinar"""
        # Implementar lógica de permissões específicas
        return usuario.is_authenticated


