import unittest
import sys
import os
from datetime import datetime, date
import pytest
from flask import url_for
from flask.testing import FlaskClient

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja, Colaborador, Premio, SorteioSemanal, SorteioColaborador
from helpers import generate_random_email, generate_random_password

class SorteiosTestCase(unittest.TestCase):
    def setUp(self):
        """Executado antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Criar lojas
        self.loja_big = Loja(codigo='BIG001', nome='BigBox Matriz', bandeira='BIG')
        self.loja_ultra = Loja(codigo='ULTRA001', nome='UltraBox Center', bandeira='ULTRA')
        db.session.add(self.loja_big)
        db.session.add(self.loja_ultra)
        db.session.commit()
        
        # Criar admin
        self.admin_email = generate_random_email()
        self.admin_password = generate_random_password()
        self.admin = Usuario(
            email=self.admin_email,
            nome='Admin Teste',
            tipo='admin'
        )
        self.admin.set_password(self.admin_password)
        db.session.add(self.admin)
        db.session.commit()

        # Criar assistente para a loja BigBox
        self.assistente_email = generate_random_email()
        self.assistente_password = generate_random_password()
        self.assistente = Usuario(
            email=self.assistente_email,
            nome='Assistente Teste',
            tipo='assistente',
            loja_id=self.loja_big.id
        )
        self.assistente.set_password(self.assistente_password)
        db.session.add(self.assistente)
        db.session.commit()
        
        # Criar colaboradores
        self.colaboradores_big = []
        for i in range(5):
            colab = Colaborador(
                matricula=f'BIG{i:03d}',
                nome=f'Colaborador Big {i}',
                setor='Vendas',
                loja_id=self.loja_big.id
            )
            self.colaboradores_big.append(colab)
            db.session.add(colab)
        
        self.colaboradores_ultra = []
        for i in range(5):
            colab = Colaborador(
                matricula=f'ULTRA{i:03d}',
                nome=f'Colaborador Ultra {i}',
                setor='Vendas',
                loja_id=self.loja_ultra.id
            )
            self.colaboradores_ultra.append(colab)
            db.session.add(colab)
        
        db.session.commit()
        
        # Criar prêmios para outros testes
        self.premio_big = Premio(
            nome='Show VIP Big',
            descricao='Show exclusivo BigBox',
            data_evento=date(2025, 12, 31),
            tipo='show',
            loja_id=self.loja_big.id,
            criado_por=self.admin.id
        )
        db.session.add(self.premio_big)
        db.session.commit()

        # Criar prêmio genérico (sem loja) para o teste de fluxo
        self.premio_generico = Premio(
            nome='Prêmio Genérico Teste',
            descricao='Prêmio para ser atribuído',
            data_evento=date(2025, 12, 31),
            tipo='show',
            criado_por=self.admin.id
        )
        db.session.add(self.premio_generico)
        db.session.commit()

    def tearDown(self):
        """Executado depois de cada teste"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_admin(self):
        """Faz login como admin"""
        return self.client.post('/auth/login', data={
            'email': self.admin_email,
            'password': self.admin_password
        })

    def login_assistente(self):
        """Faz login como assistente"""
        return self.client.post('/auth/login', data={
            'email': self.assistente_email,
            'password': self.assistente_password
        })

    def test_sorteio_semanal_lojas(self):
        """Teste do sorteio semanal de lojas"""
        self.login_admin()
        
        response = self.client.post('/admin/sortear', data={
            'semana_inicio': '2025-01-01'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        sorteio = SorteioSemanal.query.filter_by(semana_inicio=date(2025, 1, 1)).first()
        self.assertIsNotNone(sorteio)
        self.assertIn(sorteio.loja_big_id, [self.loja_big.id])
        self.assertIn(sorteio.loja_ultra_id, [self.loja_ultra.id])

    def test_fluxo_atribuicao_e_sorteio_colaborador(self):
        """
        Testa o fluxo completo:
        1. Admin atribui um prêmio a uma loja.
        2. Assistente da loja sorteia um colaborador.
        """
        # --- ETAPA 1: Admin atribui o prêmio ---
        self.login_admin()
        
        sorteio_semanal = SorteioSemanal(
            semana_inicio=date(2025, 1, 1),
            loja_big_id=self.loja_big.id,
            loja_ultra_id=self.loja_ultra.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_semanal)
        db.session.commit()
        
        response_atribuir = self.client.post(f'/admin/premios/{self.premio_generico.id}/atribuir', data={
            'loja_id': self.loja_big.id
        }, follow_redirects=True)
        self.assertEqual(response_atribuir.status_code, 200)
        
        premio_atualizado = Premio.query.get(self.premio_generico.id)
        self.assertEqual(premio_atualizado.loja_id, self.loja_big.id)
        
        self.client.get('/auth/logout')

        # --- ETAPA 2: Assistente sorteia o colaborador ---
        self.login_assistente()
        
        # Assistente da loja BigBox realiza o sorteio do colaborador
        response_sorteio = self.client.post('/assistente/sortear', data={
            'premio_id': self.premio_generico.id,
            'confirmar_lista': True
        }, follow_redirects=True)
        self.assertEqual(response_sorteio.status_code, 200)
        
        # --- ETAPA 3: Verificação ---
        sorteio_colab = SorteioColaborador.query.filter_by(premio_id=self.premio_generico.id).first()
        self.assertIsNotNone(sorteio_colab)

        ids_colaboradores_loja = [c.id for c in self.colaboradores_big]
        self.assertIn(sorteio_colab.colaborador_id, ids_colaboradores_loja)

    def test_colaborador_apto_para_sorteio(self):
        """Teste se apenas colaboradores aptos participam do sorteio"""
        self.login_admin()
        
        self.colaboradores_big[0].apto = False
        self.colaboradores_big[1].apto = False
        db.session.commit()
        
        sorteio_semanal = SorteioSemanal(
            semana_inicio=date(2025, 1, 1),
            loja_big_id=self.loja_big.id,
            loja_ultra_id=self.loja_ultra.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_semanal)
        db.session.commit()
        
        colaboradores_aptos = Colaborador.query.filter_by(
            loja_id=self.loja_big.id, 
            apto=True
        ).all()
        
        self.assertEqual(len(colaboradores_aptos), 3)

    def test_historico_sorteios(self):
        """Teste do histórico de sorteios"""
        self.login_admin()
        
        sorteio_semanal = SorteioSemanal(
            semana_inicio=date(2025, 1, 1),
            loja_big_id=self.loja_big.id,
            loja_ultra_id=self.loja_ultra.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_semanal)
        db.session.commit()
        
        sorteio_colab = SorteioColaborador(
            sorteio_semanal_id=sorteio_semanal.id,
            premio_id=self.premio_big.id,
            colaborador_id=self.colaboradores_big[0].id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_colab)
        db.session.commit()
        
        response = self.client.get('/admin/sorteios')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Show VIP Big', response.data)
        self.assertIn(b'Colaborador Big 0', response.data)

    def test_prevent_duplicate_weekly_draw(self):
        """Teste para prevenir sorteio duplicado na mesma semana"""
        self.login_admin()
        
        sorteio1 = SorteioSemanal(
            semana_inicio=date(2025, 1, 1),
            loja_big_id=self.loja_big.id,
            loja_ultra_id=self.loja_ultra.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio1)
        db.session.commit()
        
        with self.assertRaises(Exception):
            sorteio2 = SorteioSemanal(
                semana_inicio=date(2025, 1, 1),
                loja_big_id=self.loja_big.id,
                loja_ultra_id=self.loja_ultra.id,
                sorteado_por=self.admin.id
            )
            db.session.add(sorteio2)
            db.session.commit()

    def test_snapshot_colaboradores(self):
        """Teste do snapshot de colaboradores no sorteio"""
        self.login_admin()
        
        sorteio_semanal = SorteioSemanal(
            semana_inicio=date(2025, 1, 1),
            loja_big_id=self.loja_big.id,
            loja_ultra_id=self.loja_ultra.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_semanal)
        db.session.commit()
        
        colaboradores_snapshot = [
            {'matricula': c.matricula, 'nome': c.nome, 'setor': c.setor}
            for c in self.colaboradores_big if c.apto
        ]
        
        sorteio_colab = SorteioColaborador(
            sorteio_semanal_id=sorteio_semanal.id,
            premio_id=self.premio_big.id,
            colaborador_id=self.colaboradores_big[0].id,
            sorteado_por=self.admin.id,
            colaboradores_snapshot=str(colaboradores_snapshot)
        )
        db.session.add(sorteio_colab)
        db.session.commit()
        
        sorteio_salvo = SorteioColaborador.query.get(sorteio_colab.id)
        self.assertIsNotNone(sorteio_salvo.colaboradores_snapshot)

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_instagram_sorteio_layout(client: FlaskClient):
    # Simula acesso à página de participantes de um sorteio Instagram
    response = client.get('/admin/instagram/1/participantes')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # Verifica se a ficha do sorteio está presente
    assert 'class="ficha-content' in html
    # Verifica se a coluna dos ganhadores está presente
    assert 'class="ganhadores-header' in html
    # Verifica se o título do sorteio aparece
    assert 'Sorteio Instagram' in html or 'Sorteio' in html
    # Verifica se o alerta de sucesso pode ser renderizado
    assert 'alerta-sucesso-topo' in html or 'alert alert-success' in html
    # Verifica se a lista de ganhadores pode ser exibida
    assert 'listaGanhadores' in html

if __name__ == '__main__':
    unittest.main() 