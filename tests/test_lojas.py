import unittest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja
from helpers import generate_random_email, generate_random_password

class LojasTestCase(unittest.TestCase):
    def setUp(self):
        """Executado antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Admin
        self.admin_email = generate_random_email()
        self.admin_password = generate_random_password()
        self.admin = Usuario(email=self.admin_email, nome='Admin Lojas', tipo='admin')
        self.admin.set_password(self.admin_password)
        db.session.add(self.admin)
        db.session.commit()

    def tearDown(self):
        """Executado depois de cada teste"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        """Faz login como admin"""
        return self.client.post('/auth/login', data={
            'email': self.admin_email,
            'password': self.admin_password
        }, follow_redirects=True)

    def test_listar_lojas(self):
        """Teste de listagem de lojas"""
        self.login()
        
        # Criar algumas lojas
        loja1 = Loja(codigo='BIG001', nome='BigBox Matriz', bandeira='BIG')
        loja2 = Loja(codigo='ULTRA001', nome='UltraBox Center', bandeira='ULTRA')
        db.session.add(loja1)
        db.session.add(loja2)
        db.session.commit()
        
        response = self.client.get('/admin/lojas')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BigBox Matriz', response.data)
        self.assertIn(b'UltraBox Center', response.data)

    def test_criar_loja(self):
        """Teste de criação de loja"""
        self.login()
        
        response = self.client.post('/admin/lojas/adicionar', data={
            'codigo': 'BIG001',
            'nome': 'BigBox Teste',
            'bandeira': 'BIG'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi criada no banco
        loja = Loja.query.filter_by(codigo='BIG001').first()
        self.assertIsNotNone(loja)
        self.assertEqual(loja.nome, 'BigBox Teste')
        self.assertEqual(loja.bandeira, 'BIG')

    def test_editar_loja(self):
        """Teste de edição de loja"""
        self.login()
        
        # Criar loja
        loja = Loja(codigo='EDIT01', nome='Loja Original', bandeira='BIG')
        db.session.add(loja)
        db.session.commit()
        
        # Editar loja
        response = self.client.post(f'/admin/lojas/{loja.id}/editar', data={
            'codigo': 'EDIT01',
            'nome': 'Loja Editada',
            'bandeira': 'BIG'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi editada
        loja_editada = Loja.query.get(loja.id)
        self.assertEqual(loja_editada.nome, 'Loja Editada')

    def test_inativar_loja(self):
        """Teste de inativação de loja"""
        self.login()
        
        # Criar loja
        loja = Loja(codigo='INATIV01', nome='Loja Ativa', bandeira='ULTRA')
        db.session.add(loja)
        db.session.commit()
        
        # Inativar loja
        response = self.client.post(f'/admin/lojas/{loja.id}/toggle', 
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi inativada
        loja_inativada = Loja.query.get(loja.id)
        self.assertFalse(loja_inativada.ativo)

    def test_loja_codigo_unico(self):
        """Teste de código de loja único"""
        self.login()
        
        # Criar primeira loja
        self.client.post('/admin/lojas/adicionar', data={
            'codigo': 'UNICO01',
            'nome': 'Loja Um',
            'bandeira': 'BIG'
        }, follow_redirects=True)
        
        # Tentar criar segunda loja com mesmo código
        self.client.post('/admin/lojas/adicionar', data={
            'codigo': 'UNICO01',
            'nome': 'Loja Dois',
            'bandeira': 'BIG'
        }, follow_redirects=True)
        
        # Deve haver apenas uma loja com esse código
        lojas = Loja.query.filter_by(codigo='UNICO01').all()
        self.assertEqual(len(lojas), 1)

if __name__ == '__main__':
    unittest.main() 