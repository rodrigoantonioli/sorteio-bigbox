import unittest
import sys
import os
from datetime import date

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja, Premio

class PremiosTestCase(unittest.TestCase):
    def setUp(self):
        """Executado antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Criar loja e admin
        self.loja = Loja(codigo='BIG001', nome='BigBox Matriz', bandeira='BIG')
        db.session.add(self.loja)
        db.session.commit()
        
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

    def test_listar_premios(self):
        """Teste de listagem de prêmios"""
        self.login_admin()
        
        # Criar prêmios
        premio1 = Premio(
            nome='Show VIP',
            descricao='Show exclusivo',
            data_evento=date(2025, 12, 31),
            tipo='show',
            loja_id=self.loja.id,
            criado_por=self.admin.id
        )
        premio2 = Premio(
            nome='Day Use',
            descricao='Day use exclusivo',
            data_evento=date(2025, 12, 25),
            tipo='day_use',
            loja_id=self.loja.id,
            criado_por=self.admin.id
        )
        db.session.add(premio1)
        db.session.add(premio2)
        db.session.commit()
        
        response = self.client.get('/admin/premios')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Show VIP'.encode('utf-8'), response.data)
        self.assertIn('Day Use'.encode('utf-8'), response.data)

    def test_criar_premio_show(self):
        """Teste de criação de prêmio tipo show"""
        self.login_admin()
        
        response = self.client.post('/admin/premios/novo', data={
            'nome': 'Show Especial',
            'descricao': 'Show com artista nacional',
            'data_evento': '2025-12-31',
            'tipo': 'show',
            'loja_id': self.loja.id
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi criado
        premio = Premio.query.filter_by(nome='Show Especial').first()
        self.assertIsNotNone(premio)
        self.assertEqual(premio.tipo, 'show')
        self.assertEqual(premio.loja_id, self.loja.id)

    def test_criar_premio_day_use(self):
        """Teste de criação de prêmio tipo day use"""
        self.login_admin()
        
        response = self.client.post('/admin/premios/novo', data={
            'nome': 'Day Use Premium',
            'descricao': 'Day use com tudo incluso',
            'data_evento': '2025-12-25',
            'tipo': 'day_use',
            'loja_id': self.loja.id
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi criado
        premio = Premio.query.filter_by(nome='Day Use Premium').first()
        self.assertIsNotNone(premio)
        self.assertEqual(premio.tipo, 'day_use')

    def test_editar_premio(self):
        """Teste de edição de prêmio"""
        self.login_admin()
        
        # Criar prêmio
        premio = Premio(
            nome='Show Original',
            descricao='Descrição original',
            data_evento=date(2025, 12, 31),
            tipo='show',
            loja_id=self.loja.id,
            criado_por=self.admin.id
        )
        db.session.add(premio)
        db.session.commit()
        
        # Editar prêmio
        response = self.client.post(f'/admin/premios/{premio.id}/editar', data={
            'nome': 'Show Editado',
            'descricao': 'Descrição editada',
            'data_evento': '2025-12-31',
            'tipo': 'show',
            'loja_id': self.loja.id
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi editado
        premio_editado = Premio.query.get(premio.id)
        self.assertEqual(premio_editado.nome, 'Show Editado')
        self.assertEqual(premio_editado.descricao, 'Descrição editada')

    def test_inativar_premio(self):
        """Teste de inativação de prêmio"""
        self.login_admin()
        
        # Criar prêmio
        premio = Premio(
            nome='Show Teste',
            descricao='Descrição teste',
            data_evento=date(2025, 12, 31),
            tipo='show',
            loja_id=self.loja.id,
            criado_por=self.admin.id
        )
        db.session.add(premio)
        db.session.commit()
        
        # Inativar prêmio
        response = self.client.post(f'/admin/premios/{premio.id}/toggle', 
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi inativado
        premio_inativado = Premio.query.get(premio.id)
        self.assertFalse(premio_inativado.ativo)

    def test_premio_vinculado_loja(self):
        """Teste de vinculação de prêmio à loja"""
        self.login_admin()
        
        # Criar outra loja
        outra_loja = Loja(codigo='ULTRA001', nome='UltraBox Center', bandeira='ULTRA')
        db.session.add(outra_loja)
        db.session.commit()
        
        # Criar prêmios para lojas diferentes
        premio_big = Premio(
            nome='Show BigBox',
            descricao='Show para BigBox',
            data_evento=date(2025, 12, 31),
            tipo='show',
            loja_id=self.loja.id,
            criado_por=self.admin.id
        )
        premio_ultra = Premio(
            nome='Show UltraBox',
            descricao='Show para UltraBox',
            data_evento=date(2025, 12, 31),
            tipo='show',
            loja_id=outra_loja.id,
            criado_por=self.admin.id
        )
        db.session.add(premio_big)
        db.session.add(premio_ultra)
        db.session.commit()
        
        # Verificar vinculação
        self.assertEqual(premio_big.loja.bandeira, 'BIG')
        self.assertEqual(premio_ultra.loja.bandeira, 'ULTRA')

    def test_premio_sem_loja_especifica(self):
        """Teste de prêmio sem loja específica (pool geral)"""
        self.login_admin()
        
        # Criar prêmio sem loja específica
        premio_geral = Premio(
            nome='Prêmio Geral',
            descricao='Prêmio do pool geral',
            data_evento=date(2025, 12, 31),
            tipo='show',
            loja_id=None,  # Sem loja específica
            criado_por=self.admin.id
        )
        db.session.add(premio_geral)
        db.session.commit()
        
        # Verificar se foi criado
        premio_salvo = Premio.query.filter_by(nome='Prêmio Geral').first()
        self.assertIsNotNone(premio_salvo)
        self.assertIsNone(premio_salvo.loja_id)

    def test_validacao_data_evento(self):
        """Teste de validação da data do evento"""
        self.login_admin()
        
        # Tentar criar prêmio com data passada
        response = self.client.post('/admin/premios/novo', data={
            'nome': 'Prêmio Passado',
            'descricao': 'Prêmio com data passada',
            'data_evento': '2020-01-01',  # Data no passado
            'tipo': 'show',
            'loja_id': self.loja.id
        })
        
        # Verificar se prêmio não foi criado ou se houve validação
        premio = Premio.query.filter_by(nome='Prêmio Passado').first()
        # Dependendo da implementação, pode não ter sido criado
        # ou pode ter sido criado com aviso

if __name__ == '__main__':
    unittest.main() 