import unittest
import sys
import os

# Adiciona o diretório raiz ao path para encontrar o módulo 'run'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        """Executado antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        """Executado depois de cada teste"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        """Teste se a aplicação existe"""
        self.assertFalse(self.app is None)

    def test_app_is_testing(self):
        """Teste se a aplicação está no modo de teste"""
        self.assertTrue(self.app.config['TESTING'])
        
    def test_index_page(self):
        """Teste se a página inicial carrega"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sorteios Festival Na Praia', response.data) 