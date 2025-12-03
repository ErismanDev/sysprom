from django.test import SimpleTestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages


class LoginEnsinoViewTests(SimpleTestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('militares:ensino_login')

    def test_get_login_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_missing_tipo_usuario(self):
        response = self.client.post(self.url, {
            'identificador': 'x',
            'senha': 'y',
            'nao_sou_robo': 'on',
        })
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Por favor, selecione o tipo de usuário.', messages)

    def test_post_missing_captcha(self):
        response = self.client.post(self.url, {
            'tipo_usuario': 'aluno',
            'identificador': 'x',
            'senha': 'y',
        })
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Você deve confirmar que não é um robô para continuar.', messages)

    def test_post_missing_fields(self):
        response = self.client.post(self.url, {
            'tipo_usuario': 'aluno',
            'nao_sou_robo': 'on',
        })
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Por favor, preencha todos os campos.', messages)

    def test_post_tipo_invalido(self):
        response = self.client.post(self.url, {
            'tipo_usuario': 'foo',
            'identificador': 'x',
            'senha': 'y',
            'nao_sou_robo': 'on',
        })
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Tipo de usuário inválido.', messages)
