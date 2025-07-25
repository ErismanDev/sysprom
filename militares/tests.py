from django.test import TestCase
from datetime import date
from militares.models import Militar

class QuadrosCursosTestCase(TestCase):
    def setUp(self):
        # Criar militares de teste para cada quadro
        self.militares_teste = []
        self.militares_teste.append(Militar.objects.create(
            matricula="TESTE_COMB001",
            nome_completo="Militar Combatente Sem Curso",
            nome_guerra="Combatente",
            cpf="900.000.000-01",
            rg="1111111",
            orgao_expedidor="SSP",
            data_nascimento=date(1990, 1, 1),
            sexo="M",
            quadro="COMB",
            posto_graduacao="2T",
            data_ingresso=date(2015, 1, 1),
            data_promocao_atual=date(1980, 1, 1),
            situacao="AT",
            email="combatente@teste.com",
            telefone="(86) 11111-1111",
            celular="(86) 11111-1111",
            apto_inspecao_saude=True,
            data_inspecao_saude=date(2024, 1, 1),
            data_validade_inspecao_saude=date(2025, 12, 31),
            curso_formacao_oficial=False,
            curso_aperfeicoamento_oficial=False,
        ))
        self.militares_teste.append(Militar.objects.create(
            matricula="TESTE_SAUDE001",
            nome_completo="Militar Saúde Sem Curso",
            nome_guerra="Saúde",
            cpf="900.000.000-02",
            rg="2222222",
            orgao_expedidor="SSP",
            data_nascimento=date(1990, 1, 1),
            sexo="M",
            quadro="SAUDE",
            posto_graduacao="2T",
            data_ingresso=date(2015, 1, 1),
            data_promocao_atual=date(1980, 1, 1),
            situacao="AT",
            email="saude@teste.com",
            telefone="(86) 22222-2222",
            celular="(86) 22222-2222",
            apto_inspecao_saude=True,
            data_inspecao_saude=date(2024, 1, 1),
            data_validade_inspecao_saude=date(2025, 12, 31),
            curso_formacao_oficial=False,
            curso_aperfeicoamento_oficial=False,
        ))
        self.militares_teste.append(Militar.objects.create(
            matricula="TESTE_ENG001",
            nome_completo="Militar Engenheiro Sem Curso",
            nome_guerra="Engenheiro",
            cpf="900.000.000-03",
            rg="3333333",
            orgao_expedidor="SSP",
            data_nascimento=date(1990, 1, 1),
            sexo="M",
            quadro="ENG",
            posto_graduacao="2T",
            data_ingresso=date(2015, 1, 1),
            data_promocao_atual=date(1980, 1, 1),
            situacao="AT",
            email="engenheiro@teste.com",
            telefone="(86) 33333-3333",
            celular="(86) 33333-3333",
            apto_inspecao_saude=True,
            data_inspecao_saude=date(2024, 1, 1),
            data_validade_inspecao_saude=date(2025, 12, 31),
            curso_formacao_oficial=False,
            curso_aperfeicoamento_oficial=False,
        ))
        self.militares_teste.append(Militar.objects.create(
            matricula="TESTE_CURSOS001",
            nome_completo="Militar Com Cursos",
            nome_guerra="Cursos",
            cpf="900.000.000-04",
            rg="4444444",
            orgao_expedidor="SSP",
            data_nascimento=date(1990, 1, 1),
            sexo="M",
            quadro="COMB",
            posto_graduacao="2T",
            data_ingresso=date(2015, 1, 1),
            data_promocao_atual=date(1980, 1, 1),
            situacao="AT",
            email="cursos@teste.com",
            telefone="(86) 44444-4444",
            celular="(86) 44444-4444",
            apto_inspecao_saude=True,
            data_inspecao_saude=date(2024, 1, 1),
            data_validade_inspecao_saude=date(2025, 12, 31),
            curso_formacao_oficial=True,
            curso_aperfeicoamento_oficial=False,
        ))

    def test_apto_quadro_acesso(self):
        for militar in self.militares_teste:
            apto_quadro, motivo = militar.apto_quadro_acesso()
            self.assertIsInstance(apto_quadro, bool)
            self.assertIsInstance(motivo, str)

    def test_capitao(self):
        militar_capitao = Militar.objects.create(
            matricula="TESTE_CAP001",
            nome_completo="Capitão Teste",
            nome_guerra="Capitão",
            cpf="900.000.000-05",
            rg="5555555",
            orgao_expedidor="SSP",
            data_nascimento=date(1990, 1, 1),
            sexo="M",
            quadro="COMB",
            posto_graduacao="CP",
            data_ingresso=date(2010, 1, 1),
            data_promocao_atual=date(2018, 1, 1),
            situacao="AT",
            email="capitao@teste.com",
            telefone="(86) 55555-5555",
            celular="(86) 55555-5555",
            apto_inspecao_saude=True,
            data_inspecao_saude=date(2024, 1, 1),
            data_validade_inspecao_saude=date(2025, 12, 31),
            curso_formacao_oficial=True,
            curso_aperfeicoamento_oficial=False,  # Falta este curso
        )
        apto_quadro, motivo = militar_capitao.apto_quadro_acesso()
        self.assertIsInstance(apto_quadro, bool)
        self.assertIsInstance(motivo, str)
