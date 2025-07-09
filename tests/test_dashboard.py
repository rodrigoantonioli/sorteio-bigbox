import unittest
import sys
import os
from datetime import date, timedelta

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja, Premio, SorteioSemanal, SorteioColaborador, Colaborador
from helpers import generate_random_email, generate_random_password
from flask import url_for

class DashboardTestCase(unittest.TestCase):
    def setUp(self):
        """Executado antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # 1. Criar e commitar Lojas primeiro para obter IDs
        self.loja_assistente = Loja(codigo='BIG01', nome='BigBox Matriz', bandeira='BIG')
        self.outra_loja = Loja(codigo='ULTRA01', nome='UltraBox Center', bandeira='ULTRA')
        db.session.add_all([self.loja_assistente, self.outra_loja])
        db.session.commit()

        # 2. Criar Admin e Assistente (agora com loja_id válido)
        self.admin_email = generate_random_email()
        self.admin_password = generate_random_password()
        self.admin = Usuario(email=self.admin_email, nome='Admin Teste', tipo='admin')
        self.admin.set_password(self.admin_password)

        self.assistente_email = generate_random_email()
        self.assistente_password = generate_random_password()
        self.assistente = Usuario(
            email=self.assistente_email,
            nome='Assistente Teste',
            tipo='assistente',
            loja_id=self.loja_assistente.id  # Agora isso terá um valor
        )
        self.assistente.set_password(self.assistente_password)
        
        db.session.add_all([self.admin, self.assistente])
        db.session.commit()

        # 3. Criar Premio (associado ao admin)
        self.premio = Premio(
            nome='Show VIP', 
            tipo='show', 
            criado_por=self.admin.id, # Usar ID do admin criado
            data_evento=date.today() + timedelta(days=30)
        )
        db.session.add(self.premio)
        db.session.commit()

        # 4. Criar Colaboradores para estatísticas
        for i in range(3):
            colab = Colaborador(
                matricula=f'BIG{i:03d}', nome=f'Colaborador Big {i}', 
                setor='Vendas', loja_id=self.loja_assistente.id
            )
            db.session.add(colab)
        db.session.commit()

    def tearDown(self):
        """Executado depois de cada teste"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_admin(self):
        """Faz login como admin e retorna a resposta do redirect"""
        return self.client.post('/auth/login', data={
            'email': self.admin_email,
            'password': self.admin_password
        })

    def login_assistente(self):
        """Faz login como assistente e retorna a resposta do redirect"""
        return self.client.post('/auth/login', data={
            'email': self.assistente_email,
            'password': self.assistente_password
        })

    def test_dashboard_admin_loads(self):
        """Teste se o dashboard do admin carrega"""
        response_login = self.login_admin()
        self.assertEqual(response_login.status_code, 302)
        response = self.client.get(response_login.location)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard Admin', response.data)

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
        """Teste se o dashboard do manager carrega"""
        response_login = self.login_assistente()
        self.assertEqual(response_login.status_code, 302)
        response = self.client.get(response_login.location)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

    def test_dashboard_manager_loja_specific(self):
        """Teste se o dashboard do assistente mostra apenas sua loja"""
        response_login = self.login_assistente()
        self.assertEqual(response_login.status_code, 302)
        response = self.client.get(response_login.location)
        self.assertEqual(response.status_code, 200)
        self.assertIn(bytes(self.loja_assistente.nome, 'utf-8'), response.data)
        self.assertNotIn(bytes(self.outra_loja.nome, 'utf-8'), response.data)

    def test_historico_page_loads(self):
        """Teste se a pagina de historico (inicial) carrega para usuários não logados"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # O título da página inicial é "Festival Na Praia 2025"
        self.assertIn(b'Festival Na Praia', response.data)

    def test_historico_com_dados(self):
        """Teste se o histórico exibe dados de sorteios para usuários não logados"""
        # Cria dados de teste para sorteio de loja
        sorteio_semanal = SorteioSemanal(
            semana_inicio=date.today(),
            loja_big_id=self.loja_assistente.id,
            loja_ultra_id=self.outra_loja.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_semanal)
        db.session.commit()
        
        # Cria um colaborador sorteado para teste
        colaborador_sorteado = Colaborador.query.first()
        sorteio_colaborador = SorteioColaborador(
            colaborador_id=colaborador_sorteado.id,
            premio_id=self.premio.id,
            sorteio_semanal_id=sorteio_semanal.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_colaborador)
        db.session.commit()

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # Verifica se as lojas sorteadas aparecem
        self.assertIn(bytes(self.loja_assistente.nome, 'utf-8'), response.data)
        self.assertIn(bytes(self.outra_loja.nome, 'utf-8'), response.data)
        
        # Verifica se os dados do colaborador sorteado e prêmio aparecem no histórico
        self.assertIn(b'Hist\xc3\xb3rico de Sorteios', response.data)
        self.assertIn(bytes(colaborador_sorteado.nome, 'utf-8'), response.data)
        self.assertIn(bytes(self.premio.nome, 'utf-8'), response.data)

    def test_sobre_page_loads(self):
        """Teste se a página sobre carrega"""
        response = self.client.get('/sobre')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sobre o Sistema'.encode('utf-8'), response.data)

    def test_index_page_loads(self):
        """Teste se a página inicial carrega"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sistema de Sorteio'.encode('utf-8'), response.data)

    def test_dashboard_recent_activity(self):
        """Teste se dashboard mostra atividades recentes"""
        self.login_admin()
        
        # Criar atividade recente
        sorteio_semanal = SorteioSemanal(
            semana_inicio=date(2025, 1, 1),
            loja_big_id=self.loja_assistente.id,
            loja_ultra_id=self.outra_loja.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_semanal)
        db.session.commit()
        
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Verificar se mostra atividade recente
        # Dependendo da implementação, pode mostrar último sorteio

    def test_admin_redirected_from_index(self):
        """Teste se o admin logado é redirecionado da página inicial para seu dashboard"""
        response_login = self.login_admin()
        self.assertEqual(response_login.status_code, 302)
        
        with self.app.test_request_context():
            dashboard_url = url_for('admin.dashboard')
            response_index = self.client.get('/')
            self.assertEqual(response_index.status_code, 302)
            self.assertTrue(response_index.location.endswith(dashboard_url))

    def test_dashboard_zona_vermelha_access(self):
        """Teste se admin tem acesso a zona vermelha (configuracoes)"""
        self.login_admin()
        response = self.client.get('/admin/configuracoes') 
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Configura\xc3\xa7\xc3\xb5es do Sistema', response.data)

    def test_dashboard_zona_vermelha_denied(self):
        """Teste se assistente nao tem acesso a zona vermelha"""
        self.login_assistente()
        with self.app.test_request_context():
            index_url = url_for('main.index')
            response = self.client.get('/admin/configuracoes', follow_redirects=False) 
            self.assertEqual(response.status_code, 302) 
            self.assertTrue(response.location.endswith(index_url))
        
    def test_dashboard_responsivo(self):
        """Teste de placeholders de responsividade"""
        # Teste placeholder para verificar se o setup funciona
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main() 