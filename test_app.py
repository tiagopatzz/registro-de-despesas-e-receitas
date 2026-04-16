import unittest
from app import app

class FinancasTestCase(unittest.TestCase):
    # Essa função roda antes de CADA teste para preparar o ambiente
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    # --- TESTES DE CONFIGURAÇÃO DO SISTEMA (1 a 4) ---
    def test_01_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    def test_02_secret_key_exists(self):
        self.assertIsNotNone(app.secret_key)

    def test_03_mail_server_config(self):
        self.assertEqual(app.config['MAIL_SERVER'], 'smtp.gmail.com')

    def test_04_mail_port_config(self):
        # Aceita tanto porta TLS quanto SSL
        self.assertIn(app.config['MAIL_PORT'], [587, 465])


    # --- TESTES DE CARREGAMENTO DE PÁGINAS GET (5 a 7) ---
    def test_05_login_page_loads(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Acesso', response.data) # Verifica se a palavra 'Acesso' está no HTML

    def test_06_cadastro_page_loads(self):
        response = self.client.get('/cadastro')
        self.assertEqual(response.status_code, 200)

    def test_07_404_error_page(self):
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 404)


    # --- TESTES DE PROTEÇÃO DE ROTAS (8 a 15) ---
    # Garante que um usuário anônimo seja bloqueado (Erro 302 - Redirect para Login)
    def test_08_index_requires_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_09_perfil_requires_login(self):
        response = self.client.get('/perfil')
        self.assertEqual(response.status_code, 302)

    def test_10_exportar_pdf_requires_login(self):
        response = self.client.get('/exportar_pdf')
        self.assertEqual(response.status_code, 302)

    def test_11_delete_requires_login(self):
        response = self.client.get('/delete/1')
        self.assertEqual(response.status_code, 302)

    def test_12_index_post_requires_login(self):
        response = self.client.post('/', data={'descricao': 'Teste Hack'})
        self.assertEqual(response.status_code, 302)

    def test_13_perfil_post_requires_login(self):
        response = self.client.post('/perfil', data={'nome': 'Hack'})
        self.assertEqual(response.status_code, 302)

    def test_14_filtro_data_requires_login(self):
        response = self.client.get('/?data_inicio=2026-01-01')
        self.assertEqual(response.status_code, 302)

    def test_15_filtro_status_requires_login(self):
        response = self.client.get('/?status=PAGO')
        self.assertEqual(response.status_code, 302)


    # --- TESTES DE AUTENTICAÇÃO E LÓGICA (16 a 20) ---
    def test_16_login_invalido(self):
        # Tenta logar com dados falsos e segue o redirecionamento
        response = self.client.post('/login', data=dict(login="fake_user", senha="123"), follow_redirects=True)
        # A mensagem de flash deve aparecer na tela
        self.assertIn(b'incorretos', response.data)

    def test_17_logout_redirects(self):
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)

    def test_18_mail_username_config_exists(self):
        self.assertIsNotNone(app.config.get('MAIL_USERNAME'))

    def test_19_mail_tls_ssl_config_exists(self):
        # Verifica se pelo menos um dos protocolos de segurança de email está ativo
        seguranca_ativa = app.config.get('MAIL_USE_TLS') or app.config.get('MAIL_USE_SSL')
        self.assertTrue(seguranca_ativa)

    def test_20_cadastro_method_not_allowed(self):
        # Tenta acessar rota de cadastro com PUT (deve dar erro 405 Method Not Allowed)
        response = self.client.put('/cadastro')
        self.assertEqual(response.status_code, 405)

if __name__ == '__main__':
    unittest.main()
