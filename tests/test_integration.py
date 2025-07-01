import unittest
import sys
import os
from datetime import date

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja, Colaborador, Premio, SorteioSemanal, SorteioColaborador

class IntegrationTestCase(unittest.TestCase):
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

    def create_full_test_environment(self):
        """Cria ambiente completo para testes"""
        # Criar lojas
        loja_big = Loja(codigo='BIG001', nome='BigBox Matriz', bandeira='BIG')
        loja_ultra = Loja(codigo='ULTRA001', nome='UltraBox Center', bandeira='ULTRA')
        db.session.add(loja_big)
        db.session.add(loja_ultra)
        db.session.commit()
        
        # Criar admin
        admin = Usuario(
            email='admin@bigbox.com',
            nome='Admin Sistema',
            tipo='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        # Criar assistentes
        assistente_big = Usuario(
            email='assistente.big@bigbox.com',
            nome='Assistente BigBox',
            tipo='assistente',
            loja_id=loja_big.id
        )
        assistente_big.set_password('assist123')
        
        assistente_ultra = Usuario(
            email='assistente.ultra@bigbox.com',
            nome='Assistente UltraBox',
            tipo='assistente',
            loja_id=loja_ultra.id
        )
        assistente_ultra.set_password('assist123')
        
        db.session.add(assistente_big)
        db.session.add(assistente_ultra)
        db.session.commit()
        
        # Criar colaboradores
        for i in range(5):
            colab_big = Colaborador(
                matricula=f'BIG{i:03d}',
                nome=f'Colaborador Big {i}',
                setor='Vendas',
                loja_id=loja_big.id
            )
            colab_ultra = Colaborador(
                matricula=f'ULTRA{i:03d}',
                nome=f'Colaborador Ultra {i}',
                setor='Vendas',
                loja_id=loja_ultra.id
            )
            db.session.add(colab_big)
            db.session.add(colab_ultra)
        
        db.session.commit()
        
        # Criar prêmios
        premio_big = Premio(
            nome='Show VIP BigBox',
            descricao='Show exclusivo BigBox',
            data_evento=date(2025, 12, 31),
            tipo='show',
            loja_id=loja_big.id,
            criado_por=admin.id
        )
        premio_ultra = Premio(
            nome='Day Use UltraBox',
            descricao='Day use exclusivo UltraBox',
            data_evento=date(2025, 12, 25),
            tipo='day_use',
            loja_id=loja_ultra.id,
            criado_por=admin.id
        )
        db.session.add(premio_big)
        db.session.add(premio_ultra)
        db.session.commit()
        
        return {
            'admin': admin,
            'assistente_big': assistente_big,
            'assistente_ultra': assistente_ultra,
            'loja_big': loja_big,
            'loja_ultra': loja_ultra,
            'premio_big': premio_big,
            'premio_ultra': premio_ultra
        }

    def test_fluxo_completo_sorteio_semanal(self):
        """Teste do fluxo completo de sorteio semanal"""
        data = self.create_full_test_environment()
        
        # 1. Admin faz login
        login_response = self.client.post('/auth/login', data={
            'email': 'admin@bigbox.com',
            'password': 'admin123'
        })
        self.assertEqual(login_response.status_code, 302)  # Redirecionamento
        
        # 2. Acessa dashboard admin
        dashboard_response = self.client.get('/admin/dashboard')
        self.assertEqual(dashboard_response.status_code, 200)
        
        # 3. Faz sorteio semanal
        sorteio_response = self.client.post('/admin/sortear', data={
            'semana_inicio': '2025-01-01'
        }, follow_redirects=True)
        self.assertEqual(sorteio_response.status_code, 200)
        
        # 4. Verifica se sorteio foi registrado
        sorteio = SorteioSemanal.query.filter_by(semana_inicio=date(2025, 1, 1)).first()
        self.assertIsNotNone(sorteio)
        
        # 5. Atribui prêmio a colaborador
        colaborador = Colaborador.query.filter_by(loja_id=data['loja_big'].id).first()
        atribuir_response = self.client.post('/admin/premios/atribuir', data={
            'premio_id': data['premio_big'].id,
            'colaborador_id': colaborador.id,
            'sorteio_semanal_id': sorteio.id
        }, follow_redirects=True)
        self.assertEqual(atribuir_response.status_code, 200)
        
        # 6. Verifica se atribuição foi registrada
        sorteio_colab = SorteioColaborador.query.filter_by(
            premio_id=data['premio_big'].id,
            colaborador_id=colaborador.id
        ).first()
        self.assertIsNotNone(sorteio_colab)
        
        # 7. Verifica histórico
        historico_response = self.client.get('/historico')
        self.assertEqual(historico_response.status_code, 200)
        self.assertIn(data['premio_big'].nome.encode('utf-8'), historico_response.data)

    def test_fluxo_assistente_gerencia_colaboradores(self):
        """Teste do fluxo de assistente gerenciando colaboradores"""
        data = self.create_full_test_environment()
        
        # 1. Assistente faz login
        login_response = self.client.post('/auth/login', data={
            'email': 'assistente.big@bigbox.com',
            'password': 'assist123'
        })
        self.assertEqual(login_response.status_code, 302)
        
        # 2. Acessa dashboard manager
        dashboard_response = self.client.get('/manager/dashboard')
        self.assertEqual(dashboard_response.status_code, 200)
        
        # 3. Lista colaboradores da sua loja
        colaboradores_response = self.client.get('/manager/colaboradores')
        self.assertEqual(colaboradores_response.status_code, 200)
        
        # 4. Adiciona novo colaborador
        novo_colab_response = self.client.post('/manager/colaboradores/novo', data={
            'matricula': 'BIG999',
            'nome': 'Novo Colaborador',
            'setor': 'Caixa'
        }, follow_redirects=True)
        self.assertEqual(novo_colab_response.status_code, 200)
        
        # 5. Verifica se colaborador foi criado
        novo_colab = Colaborador.query.filter_by(
            matricula='BIG999',
            loja_id=data['loja_big'].id
        ).first()
        self.assertIsNotNone(novo_colab)
        self.assertEqual(novo_colab.nome, 'Novo Colaborador')

    def test_fluxo_controle_acesso_completo(self):
        """Teste completo de controle de acesso"""
        data = self.create_full_test_environment()
        
        # 1. Verificar acesso sem login
        response_admin = self.client.get('/admin/dashboard')
        self.assertEqual(response_admin.status_code, 302)  # Redirecionamento para login
        
        response_manager = self.client.get('/manager/dashboard')
        self.assertEqual(response_manager.status_code, 302)  # Redirecionamento para login
        
        # 2. Login como assistente
        self.client.post('/auth/login', data={
            'email': 'assistente.big@bigbox.com',
            'password': 'assist123'
        })
        
        # 3. Verificar acesso do assistente
        response_manager_ok = self.client.get('/manager/dashboard')
        self.assertEqual(response_manager_ok.status_code, 200)
        
        response_admin_denied = self.client.get('/admin/dashboard')
        self.assertEqual(response_admin_denied.status_code, 302)  # Deve ser negado
        
        # 4. Logout
        self.client.get('/auth/logout')
        
        # 5. Login como admin
        self.client.post('/auth/login', data={
            'email': 'admin@bigbox.com',
            'password': 'admin123'
        })
        
        # 6. Verificar acesso do admin
        response_admin_ok = self.client.get('/admin/dashboard')
        self.assertEqual(response_admin_ok.status_code, 200)
        
        response_manager_ok = self.client.get('/manager/dashboard')
        self.assertEqual(response_manager_ok.status_code, 200)  # Admin pode acessar tudo

    def test_fluxo_gestao_premios_completo(self):
        """Teste completo de gestão de prêmios"""
        data = self.create_full_test_environment()
        
        # 1. Admin faz login
        self.client.post('/auth/login', data={
            'email': 'admin@bigbox.com',
            'password': 'admin123'
        })
        
        # 2. Lista prêmios existentes
        premios_response = self.client.get('/admin/premios')
        self.assertEqual(premios_response.status_code, 200)
        
        # 3. Cria novo prêmio
        novo_premio_response = self.client.post('/admin/premios/novo', data={
            'nome': 'Prêmio Teste Integração',
            'descricao': 'Prêmio criado no teste de integração',
            'data_evento': '2025-12-31',
            'tipo': 'show',
            'loja_id': data['loja_big'].id
        }, follow_redirects=True)
        self.assertEqual(novo_premio_response.status_code, 200)
        
        # 4. Verifica se prêmio foi criado
        premio_criado = Premio.query.filter_by(nome='Prêmio Teste Integração').first()
        self.assertIsNotNone(premio_criado)
        
        # 5. Edita prêmio
        editar_response = self.client.post(f'/admin/premios/{premio_criado.id}/editar', data={
            'nome': 'Prêmio Teste Editado',
            'descricao': 'Descrição editada',
            'data_evento': '2025-12-31',
            'tipo': 'show',
            'loja_id': data['loja_big'].id
        }, follow_redirects=True)
        self.assertEqual(editar_response.status_code, 200)
        
        # 6. Verifica se foi editado
        premio_editado = Premio.query.get(premio_criado.id)
        self.assertEqual(premio_editado.nome, 'Prêmio Teste Editado')

    def test_fluxo_auditoria_historico(self):
        """Teste do fluxo de auditoria e histórico"""
        data = self.create_full_test_environment()
        
        # 1. Admin faz login
        self.client.post('/auth/login', data={
            'email': 'admin@bigbox.com',
            'password': 'admin123'
        })
        
        # 2. Realizar várias operações para gerar histórico
        
        # Sorteio semanal
        sorteio_response = self.client.post('/admin/sortear', data={
            'semana_inicio': '2025-01-01'
        }, follow_redirects=True)
        
        sorteio = SorteioSemanal.query.filter_by(semana_inicio=date(2025, 1, 1)).first()
        
        # Atribuir múltiplos prêmios
        colaboradores = Colaborador.query.filter_by(loja_id=data['loja_big'].id).limit(2).all()
        
        for i, colaborador in enumerate(colaboradores):
            premio = data['premio_big'] if i == 0 else data['premio_ultra']
            atribuir_response = self.client.post('/admin/premios/atribuir', data={
                'premio_id': premio.id,
                'colaborador_id': colaborador.id,
                'sorteio_semanal_id': sorteio.id
            }, follow_redirects=True)
            self.assertEqual(atribuir_response.status_code, 200)
        
        # 3. Verificar histórico completo
        historico_response = self.client.get('/historico')
        self.assertEqual(historico_response.status_code, 200)
        
        # Verificar se todas as operações estão no histórico
        self.assertIn(data['premio_big'].nome.encode('utf-8'), historico_response.data)
        self.assertIn(colaboradores[0].nome.encode('utf-8'), historico_response.data)
        
        # 4. Verificar integridade dos dados
        total_sorteios = SorteioColaborador.query.count()
        self.assertEqual(total_sorteios, 2)
        
        # 5. Verificar snapshots de colaboradores
        sorteios_com_snapshot = SorteioColaborador.query.filter(
            SorteioColaborador.colaboradores_snapshot.isnot(None)
        ).all()
        # Dependendo da implementação, pode ter snapshots

if __name__ == '__main__':
    unittest.main() 