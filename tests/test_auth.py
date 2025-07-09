import unittest
import sys
import os
import secrets
import string

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja
from helpers import generate_random_email, generate_random_password

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        """Executado antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Dados de teste dinâmicos
        self.admin_email = generate_random_email()
        self.admin_password = generate_random_password()
        self.assistente_email = generate_random_email()
        self.assistente_password = generate_random_password()

        # Criar usuários para teste
        self.admin = Usuario(
            email=self.admin_email,
            nome='Admin Teste',
            tipo='admin'
        )
        self.admin.set_password(self.admin_password)
        
        self.loja = Loja(codigo='BIG001', nome='BigBox Matriz', bandeira='BIG')
        db.session.add(self.loja)
        db.session.commit()
        
        self.assistente = Usuario(
            email=self.assistente_email,
            nome='Assistente Teste',
            tipo='assistente',
            loja_id=self.loja.id
        )
        self.assistente.set_password(self.assistente_password)
        
        db.session.add(self.admin)
        db.session.add(self.assistente)
        db.session.commit()

    def tearDown(self):
        """Executado depois de cada teste"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        """Função auxiliar de login"""
        return self.client.post('/auth/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def test_login_page_loads(self):
        """Teste se a página de login carrega"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_admin_login_success(self):
        """Teste de login bem-sucedido do admin"""
        response = self.client.post('/auth/login', data={
            'email': self.admin_email,
            'password': self.admin_password
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        # Verifica se foi redirecionado para dashboard admin
        self.assertIn(b'Dashboard', response.data)

    def test_assistente_login_success(self):
        """Teste de login bem-sucedido do assistente"""
        response = self.client.post('/auth/login', data={
            'email': self.assistente_email,
            'password': self.assistente_password
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)

    def test_login_invalid_credentials(self):
        """Teste de login com credenciais inválidas"""
        response = self.client.post('/auth/login', data={
            'email': self.admin_email,
            'password': 'wrong_password'
        })
        
        # Deve retornar para página de login com erro
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_logout(self):
        """Teste de logout"""
        # Fazer login primeiro
        self.client.post('/auth/login', data={
            'email': self.admin_email,
            'password': self.admin_password
        })
        
        # Fazer logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sorteios Festival Na Praia', response.data)

    def test_admin_access_control(self):
        """Teste de controle de acesso para admin"""
        # Login como admin
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.admin.id)
            sess['_fresh'] = True
        
        # Deve conseguir acessar zona admin
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_assistente_access_control(self):
        """Testa se o assistente tem acesso ao seu dashboard e é bloqueado do admin."""
        # Faz login como assistente
        self.login(self.assistente.email, self.assistente_password)
        
        # Tenta acessar o dashboard do assistente (a rota correta não tem barra final)
        response = self.client.get('/assistente/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard Assistente', response.data)
        
        # Tenta acessar uma página de admin (deve ser redirecionado)
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirecionamento para login

    def test_unauthorized_access(self):
        """Teste de acesso não autorizado"""
        # Tentar acessar admin sem login
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirecionamento para login

if __name__ == '__main__':
    unittest.main() 