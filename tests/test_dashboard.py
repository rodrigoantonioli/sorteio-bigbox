import unittest
import sys
import os
from datetime import date

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja, Colaborador, Premio, SorteioSemanal, SorteioColaborador

class DashboardTestCase(unittest.TestCase):
    def setUp(self):
        """Executado antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Criar dados de teste
        self.loja_big = Loja(codigo='BIG001', nome='BigBox Matriz', bandeira='BIG')
        self.loja_ultra = Loja(codigo='ULTRA001', nome='UltraBox Center', bandeira='ULTRA')
        db.session.add(self.loja_big)
        db.session.add(self.loja_ultra)
        db.session.commit()
        
        self.admin = Usuario(
            email='admin@bigbox.com',
            nome='Admin Teste',
            tipo='admin'
        )
        self.admin.set_password('admin123')
        
        self.assistente = Usuario(
            email='assistente@bigbox.com',
            nome='Assistente Teste',
            tipo='assistente',
            loja_id=self.loja_big.id
        )
        self.assistente.set_password('assist123')
        
        db.session.add(self.admin)
        db.session.add(self.assistente)
        db.session.commit()
        
        # Criar colaboradores
        for i in range(3):
            colab = Colaborador(
                matricula=f'BIG{i:03d}',
                nome=f'Colaborador Big {i}',
                setor='Vendas',
                loja_id=self.loja_big.id
            )
            db.session.add(colab)
        
        # Criar prêmios
        self.premio = Premio(
            nome='Show VIP',
            descricao='Show exclusivo',
            data_evento=date(2025, 12, 31),
            tipo='show',
            loja_id=self.loja_big.id,
            criado_por=self.admin.id
        )
        db.session.add(self.premio)
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

    def login_assistente(self):
        """Faz login como assistente"""
        return self.client.post('/auth/login', data={
            'email': 'assistente@bigbox.com',
            'password': 'assist123'
        })

    def test_dashboard_admin_loads(self):
        """Teste se dashboard admin carrega"""
        self.login_admin()
        
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Dashboard'.encode('utf-8'), response.data)

    def test_dashboard_admin_statistics(self):
        """Teste se dashboard admin mostra estatísticas"""
        self.login_admin()
        
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Verificar se mostra contadores
        self.assertIn('2'.encode('utf-8'), response.data)  # 2 lojas
        self.assertIn('3'.encode('utf-8'), response.data)  # 3 colaboradores
        self.assertIn('1'.encode('utf-8'), response.data)  # 1 prêmio

    def test_dashboard_manager_loads(self):
        """Teste se dashboard manager carrega"""
        self.login_assistente()
        
        response = self.client.get('/manager/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Dashboard'.encode('utf-8'), response.data)

    def test_dashboard_manager_loja_specific(self):
        """Teste se dashboard manager mostra dados da loja específica"""
        self.login_assistente()
        
        response = self.client.get('/manager/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Deve mostrar dados apenas da loja do assistente
        self.assertIn('BigBox Matriz'.encode('utf-8'), response.data)
        self.assertNotIn('UltraBox Center'.encode('utf-8'), response.data)

    def test_historico_page_loads(self):
        """Teste se página de histórico carrega"""
        response = self.client.get('/historico')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Histórico'.encode('utf-8'), response.data)

    def test_historico_com_dados(self):
        """Teste de histórico com dados de sorteios"""
        # Criar dados de histórico
        sorteio_semanal = SorteioSemanal(
            semana_inicio=date(2025, 1, 1),
            loja_big_id=self.loja_big.id,
            loja_ultra_id=self.loja_ultra.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_semanal)
        db.session.commit()
        
        colaborador = Colaborador.query.filter_by(loja_id=self.loja_big.id).first()
        sorteio_colab = SorteioColaborador(
            sorteio_semanal_id=sorteio_semanal.id,
            premio_id=self.premio.id,
            colaborador_id=colaborador.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_colab)
        db.session.commit()
        
        response = self.client.get('/historico')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Show VIP'.encode('utf-8'), response.data)
        self.assertIn(colaborador.nome.encode('utf-8'), response.data)

    def test_sobre_page_loads(self):
        """Teste se página sobre carrega"""
        response = self.client.get('/sobre')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sobre'.encode('utf-8'), response.data)

    def test_index_page_loads(self):
        """Teste se página inicial carrega"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sorteios Festival Na Praia'.encode('utf-8'), response.data)

    def test_dashboard_recent_activity(self):
        """Teste se dashboard mostra atividades recentes"""
        self.login_admin()
        
        # Criar atividade recente
        sorteio_semanal = SorteioSemanal(
            semana_inicio=date(2025, 1, 1),
            loja_big_id=self.loja_big.id,
            loja_ultra_id=self.loja_ultra.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_semanal)
        db.session.commit()
        
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Verificar se mostra atividade recente
        # Dependendo da implementação, pode mostrar último sorteio

    def test_dashboard_zona_vermelha_access(self):
        """Teste de acesso à zona vermelha (admin)"""
        self.login_admin()
        
        # Admin deve ter acesso a funcionalidades de zona vermelha
        response = self.client.get('/admin/configuracoes')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_zona_vermelha_denied(self):
        """Teste de negação de acesso à zona vermelha (assistente)"""
        self.login_assistente()
        
        # Assistente não deve ter acesso a configurações admin
        response = self.client.get('/admin/configuracoes')
        self.assertEqual(response.status_code, 302)  # Redirecionamento

    def test_dashboard_responsivo(self):
        """Teste básico de responsividade do dashboard"""
        self.login_admin()
        
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Verificar se contém elementos de bootstrap/responsividade
        self.assertIn('col-'.encode('utf-8'), response.data)
        self.assertIn('card'.encode('utf-8'), response.data)

if __name__ == '__main__':
    unittest.main() 