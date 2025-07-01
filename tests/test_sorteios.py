import unittest
import sys
import os
from datetime import datetime, date

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja, Colaborador, Premio, SorteioSemanal, SorteioColaborador

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
        self.admin = Usuario(
            email='admin@bigbox.com',
            nome='Admin Teste',
            tipo='admin'
        )
        self.admin.set_password('admin123')
        db.session.add(self.admin)
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
        
        # Criar prêmios
        self.premio_big = Premio(
            nome='Show VIP Big',
            descricao='Show exclusivo BigBox',
            data_evento=date(2025, 12, 31),
            tipo='show',
            loja_id=self.loja_big.id,
            criado_por=self.admin.id
        )
        self.premio_ultra = Premio(
            nome='Day Use Ultra',
            descricao='Day use exclusivo UltraBox',
            data_evento=date(2025, 12, 31),
            tipo='day_use',
            loja_id=self.loja_ultra.id,
            criado_por=self.admin.id
        )
        db.session.add(self.premio_big)
        db.session.add(self.premio_ultra)
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

    def test_sorteio_semanal_lojas(self):
        """Teste do sorteio semanal de lojas"""
        self.login_admin()
        
        # Fazer sorteio semanal
        response = self.client.post('/admin/sortear', data={
            'semana_inicio': '2025-01-01'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se o sorteio foi registrado
        sorteio = SorteioSemanal.query.filter_by(semana_inicio=date(2025, 1, 1)).first()
        self.assertIsNotNone(sorteio)
        self.assertIn(sorteio.loja_big_id, [self.loja_big.id])
        self.assertIn(sorteio.loja_ultra_id, [self.loja_ultra.id])

    def test_atribuir_premio_colaborador(self):
        """Teste de atribuição de prêmio a colaborador"""
        self.login_admin()
        
        # Primeiro fazer sorteio semanal
        sorteio_semanal = SorteioSemanal(
            semana_inicio=date(2025, 1, 1),
            loja_big_id=self.loja_big.id,
            loja_ultra_id=self.loja_ultra.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_semanal)
        db.session.commit()
        
        # Atribuir prêmio
        response = self.client.post('/admin/premios/atribuir', data={
            'premio_id': self.premio_big.id,
            'colaborador_id': self.colaboradores_big[0].id,
            'sorteio_semanal_id': sorteio_semanal.id
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi atribuído
        sorteio_colab = SorteioColaborador.query.filter_by(
            premio_id=self.premio_big.id,
            colaborador_id=self.colaboradores_big[0].id
        ).first()
        self.assertIsNotNone(sorteio_colab)

    def test_colaborador_apto_para_sorteio(self):
        """Teste se apenas colaboradores aptos participam do sorteio"""
        self.login_admin()
        
        # Inativar alguns colaboradores
        self.colaboradores_big[0].apto = False
        self.colaboradores_big[1].apto = False
        db.session.commit()
        
        # Fazer sorteio semanal
        sorteio_semanal = SorteioSemanal(
            semana_inicio=date(2025, 1, 1),
            loja_big_id=self.loja_big.id,
            loja_ultra_id=self.loja_ultra.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_semanal)
        db.session.commit()
        
        # Simular sorteio de colaboradores (apenas os aptos devem participar)
        colaboradores_aptos = Colaborador.query.filter_by(
            loja_id=self.loja_big.id, 
            apto=True
        ).all()
        
        self.assertEqual(len(colaboradores_aptos), 3)  # 5 - 2 inativos = 3

    def test_historico_sorteios(self):
        """Teste do histórico de sorteios"""
        self.login_admin()
        
        # Criar dados de histórico
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
        
        # Verificar histórico
        response = self.client.get('/historico')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Show VIP Big', response.data)
        self.assertIn(b'Colaborador Big 0', response.data)

    def test_prevent_duplicate_weekly_draw(self):
        """Teste para prevenir sorteio duplicado na mesma semana"""
        self.login_admin()
        
        # Primeiro sorteio
        sorteio1 = SorteioSemanal(
            semana_inicio=date(2025, 1, 1),
            loja_big_id=self.loja_big.id,
            loja_ultra_id=self.loja_ultra.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio1)
        db.session.commit()
        
        # Tentar segundo sorteio na mesma semana
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
        
        # Fazer sorteio semanal
        sorteio_semanal = SorteioSemanal(
            semana_inicio=date(2025, 1, 1),
            loja_big_id=self.loja_big.id,
            loja_ultra_id=self.loja_ultra.id,
            sorteado_por=self.admin.id
        )
        db.session.add(sorteio_semanal)
        db.session.commit()
        
        # Criar sorteio de colaborador com snapshot
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
        
        # Verificar se snapshot foi salvo
        sorteio_salvo = SorteioColaborador.query.first()
        self.assertIsNotNone(sorteio_salvo.colaboradores_snapshot)
        self.assertIn('matricula', sorteio_salvo.colaboradores_snapshot)

if __name__ == '__main__':
    unittest.main() 