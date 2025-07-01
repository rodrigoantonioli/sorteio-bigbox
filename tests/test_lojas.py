import unittest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja

class LojasTestCase(unittest.TestCase):
    def setUp(self):
        """Executado antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Criar admin para testes
        self.admin = Usuario(
            email='admin@bigbox.com',
            nome='Admin Teste',
            tipo='admin'
        )
        self.admin.set_password('admin123')
        db.session.add(self.admin)
        db.session.commit()

    def tearDown(self):
        """Executado depois de cada teste"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_admin(self):
        """Faz login como admin"""
        return self.client.post('/auth/login', data={
            'email': 'admin@bigbox.com',
            'password': 'admin123'
        })

    def test_listar_lojas(self):
        """Teste de listagem de lojas"""
        self.login_admin()
        
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

    def test_criar_loja_big(self):
        """Teste de criação de loja BigBox"""
        self.login_admin()
        
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

    def test_criar_loja_ultra(self):
        """Teste de criação de loja UltraBox"""
        self.login_admin()
        
        response = self.client.post('/admin/lojas/adicionar', data={
            'codigo': 'ULTRA001',
            'nome': 'UltraBox Teste',
            'bandeira': 'ULTRA'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi criada no banco
        loja = Loja.query.filter_by(codigo='ULTRA001').first()
        self.assertIsNotNone(loja)
        self.assertEqual(loja.nome, 'UltraBox Teste')
        self.assertEqual(loja.bandeira, 'ULTRA')

    def test_editar_loja(self):
        """Teste de edição de loja"""
        self.login_admin()
        
        # Criar loja
        loja = Loja(codigo='BIG001', nome='BigBox Original', bandeira='BIG')
        db.session.add(loja)
        db.session.commit()
        
        # Editar loja
        response = self.client.post(f'/admin/lojas/{loja.id}/editar', data={
            'codigo': 'BIG001',
            'nome': 'BigBox Editada',
            'bandeira': 'BIG'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi editada
        loja_editada = Loja.query.get(loja.id)
        self.assertEqual(loja_editada.nome, 'BigBox Editada')

    def test_inativar_loja(self):
        """Teste de inativação de loja"""
        self.login_admin()
        
        # Criar loja
        loja = Loja(codigo='BIG001', nome='BigBox Teste', bandeira='BIG')
        db.session.add(loja)
        db.session.commit()
        
        # Inativar loja
        response = self.client.post(f'/admin/lojas/{loja.id}/toggle', 
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi inativada
        loja_inativada = Loja.query.get(loja.id)
        self.assertFalse(loja_inativada.ativo)

    def test_codigo_loja_unico(self):
        """Teste de unicidade do código da loja"""
        self.login_admin()
        
        # Criar primeira loja
        response1 = self.client.post('/admin/lojas/adicionar', data={
            'codigo': 'BIG001',
            'nome': 'BigBox Primeira',
            'bandeira': 'BIG'
        })
        
        # Tentar criar segunda loja com mesmo código
        response2 = self.client.post('/admin/lojas/adicionar', data={
            'codigo': 'BIG001',
            'nome': 'BigBox Segunda',
            'bandeira': 'BIG'
        })
        
        # Deve haver apenas uma loja com esse código
        lojas = Loja.query.filter_by(codigo='BIG001').all()
        self.assertEqual(len(lojas), 1)

if __name__ == '__main__':
    unittest.main() 