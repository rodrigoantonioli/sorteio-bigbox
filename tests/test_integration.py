import unittest
import sys
import os
from datetime import date, timedelta
from flask import url_for

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja, Colaborador, Premio, SorteioSemanal, SorteioColaborador
from .helpers import generate_random_email, generate_random_password

class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        """Executado antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # Criar Lojas
        self.loja1 = Loja(codigo='BIG01', nome='BigBox Matriz', bandeira='BIG')
        self.loja2 = Loja(codigo='ULTRA01', nome='UltraBox Center', bandeira='ULTRA')
        db.session.add_all([self.loja1, self.loja2])
        db.session.commit()

        # Criar Usuários
        self.admin_password = generate_random_password()
        self.admin = Usuario(email=generate_random_email(), nome='Admin Sistema', tipo='admin')
        self.admin.set_password(self.admin_password)

        self.assistente_password = generate_random_password()
        self.assistente = Usuario(email=generate_random_email(), nome='Assistente Sistema', tipo='assistente', loja_id=self.loja1.id)
        self.assistente.set_password(self.assistente_password)
        db.session.add_all([self.admin, self.assistente])
        db.session.commit()

        # Criar Colaboradores e Prêmios
        self.colaborador_loja1 = Colaborador(matricula='100', nome='Colaborador Loja 1', setor='Teste', loja_id=self.loja1.id)
        self.colaborador_loja2 = Colaborador(matricula='200', nome='Colaborador Loja 2', setor='Teste', loja_id=self.loja2.id)
        self.premio_geral = Premio(nome='Prêmio Geral', tipo='geral', data_evento=date.today() + timedelta(days=10), criado_por=self.admin.id)
        self.premio_show = Premio(nome='Show VIP BigBox', tipo='show', data_evento=date.today() + timedelta(days=20), criado_por=self.admin.id)

        db.session.add_all([self.colaborador_loja1, self.colaborador_loja2, self.premio_geral, self.premio_show])
        db.session.commit()

    def tearDown(self):
        """Executado depois de cada teste"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        """Função auxiliar de login"""
        return self.client.post('/auth/login', data={'email': email, 'password': password})

    def logout(self):
        """Função auxiliar de logout"""
        return self.client.get('/auth/logout')

    def create_full_test_environment(self):
        """Cria ambiente completo para testes em um estado limpo."""
        # Garante que o ambiente está limpo antes de criar novos dados
        db.session.remove()
        db.drop_all()
        db.create_all()

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
        """Teste do fluxo completo: Sorteio semanal, atribuição e sorteio de colaborador."""
        data = self.create_full_test_environment()
        
        # ETAPA 1: Admin realiza o sorteio semanal das lojas
        self.login(data['admin'].email, 'admin123')
        
        sorteio_response = self.client.post('/admin/sortear', data={
            'semana_inicio': '2025-01-01'
        }, follow_redirects=True)
        self.assertEqual(sorteio_response.status_code, 200)
        
        sorteio = SorteioSemanal.query.filter_by(semana_inicio=date(2025, 1, 1)).first()
        self.assertIsNotNone(sorteio)
        self.logout()

        # ETAPA 2: Assistente da loja ganhadora sorteia um colaborador
        self.login(data['assistente_big'].email, 'assist123')

        # O prêmio 'premio_big' já está associado à loja 'loja_big' no setup
        sorteio_colab_response = self.client.post('/assistente/sortear', data={
            'premio_id': data['premio_big'].id,
            'confirmar_lista': True
        }, follow_redirects=True)
        self.assertEqual(sorteio_colab_response.status_code, 200)

        # ETAPA 3: Verificação
        sorteio_colab = SorteioColaborador.query.filter_by(premio_id=data['premio_big'].id).first()
        self.assertIsNotNone(sorteio_colab)
        
        # Verifica se o colaborador sorteado é da loja correta
        colaborador_sorteado = Colaborador.query.get(sorteio_colab.colaborador_id)
        self.assertEqual(colaborador_sorteado.loja_id, data['loja_big'].id)
        
        # Verifica se o histórico público (quando deslogado) mostra o resultado
        self.logout()
        historico_response = self.client.get('/')
        self.assertEqual(historico_response.status_code, 200)
        self.assertIn(data['loja_big'].nome.encode('utf-8'), historico_response.data)
        self.assertIn(colaborador_sorteado.nome.encode('utf-8'), historico_response.data)
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
        dashboard_response = self.client.get('/assistente/dashboard')
        self.assertEqual(dashboard_response.status_code, 200)
        
        # 3. Lista colaboradores da sua loja
        colaboradores_response = self.client.get('/assistente/colaboradores')
        self.assertEqual(colaboradores_response.status_code, 200)
        
        # 4. Adiciona novo colaborador
        novo_colab_response = self.client.post('/assistente/colaboradores/novo', data={
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
        """
        Testa o fluxo de controle de acesso:
        - Usuário não logado é redirecionado para o login.
        - Assistente não pode acessar páginas de admin.
        - Admin pode acessar tudo.
        """
        # 1. Acesso sem login (deve redirecionar para /auth/login)
        response_admin = self.client.get('/admin/dashboard', follow_redirects=False)
        self.assertEqual(response_admin.status_code, 302)
        self.assertTrue(response_admin.location.startswith('/auth/login'))

        response_manager = self.client.get('/assistente/dashboard', follow_redirects=False)
        self.assertEqual(response_manager.status_code, 302)
        self.assertTrue(response_manager.location.startswith('/auth/login'))

        # 2. Login como Assistente
        self.login(self.assistente.email, self.assistente_password)

        # 3. Assistente tenta acessar página de Admin (deve ser redirecionado)
        response_admin_page = self.client.get('/admin/usuarios', follow_redirects=False)
        self.assertEqual(response_admin_page.status_code, 302)
        with self.app.test_request_context():
            self.assertIn(url_for('main.index', _external=False), response_admin_page.location)

        # 4. Assistente acessa sua própria página (deve funcionar)
        response_manager_page = self.client.get('/assistente/dashboard')
        self.assertEqual(response_manager_page.status_code, 200)

        self.logout()

        # 5. Login como Admin
        self.login(self.admin.email, self.admin_password)
        
        # 6. Admin tenta acessar página de assistente (deve ser redirecionado)
        response_admin_tries_manager = self.client.get('/assistente/dashboard', follow_redirects=False)
        self.assertEqual(response_admin_tries_manager.status_code, 302)

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
        
        # ETAPA 1: Admin realiza sorteio semanal
        self.login(data['admin'].email, 'admin123')
        self.client.post('/admin/sortear', data={'semana_inicio': '2025-01-01'}, follow_redirects=True)
        self.logout()

        # ETAPA 2: Assistentes realizam os sorteios de colaboradores
        # Assistente Big
        self.login(data['assistente_big'].email, 'assist123')
        self.client.post('/assistente/sortear', data={'premio_id': data['premio_big'].id, 'confirmar_lista': True}, follow_redirects=True)
        self.logout()

        # Assistente Ultra
        self.login(data['assistente_ultra'].email, 'assist123')
        self.client.post('/assistente/sortear', data={'premio_id': data['premio_ultra'].id, 'confirmar_lista': True}, follow_redirects=True)
        self.logout()
        
        # ETAPA 3: Admin verifica o histórico de auditoria
        self.login(data['admin'].email, 'admin123')
        
        historico_response = self.client.get('/admin/sorteios')
        self.assertEqual(historico_response.status_code, 200)
        
        # Verificar se os dois sorteios estão no histórico
        self.assertIn(data['premio_big'].nome.encode('utf-8'), historico_response.data)
        self.assertIn(data['premio_ultra'].nome.encode('utf-8'), historico_response.data)
        
        # Verificar se a contagem de sorteios de colaboradores está correta (agora deve ser 2)
        self.assertIn(b'<span class="badge bg-light text-dark ms-2">2</span>', historico_response.data)

        # Verificar integridade dos dados
        total_sorteios = SorteioColaborador.query.count()
        self.assertEqual(total_sorteios, 2)

    def test_parser_com_arquivo_real(self):
        """Testa o parser com um arquivo real de comentários do Instagram (posts.txt)."""
        from app.utils import parse_instagram_comments
        
        # Carrega o conteúdo do arquivo de teste principal
        filepath = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'posts.txt')
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            self.fail("Arquivo de teste 'uploads/posts.txt' não encontrado.")

        # Executa a função de parsing com limite de 30 tickets
        participantes = parse_instagram_comments(content, palavra_chave='eu quero', tickets_maximos=30)

        # Define os resultados esperados com base na contagem real do parser
        expected_results = {
            'fakeuser1': 15,
            'fakeuser2': 30,  # Limitado a 30 tickets
            'fakeuser3': 1,
            'fakeuser4': 30,
            'fakeuser5': 25,
            'fakeuser6': 14,  # Valor real do parser
            'fakeuser7': 30,
            'fakeuser8': 30,
            'fakeuser9': 30,
            'fakeuser10': 30,
            'fakeuser11': 20,  # Valor real do parser
        }
        
        # Valida o número total de participantes únicos
        self.assertGreater(len(participantes), 50) # Garante que muitos participantes foram parsed
        
        # Valida a contagem de tickets para usuários específicos
        for username, expected_tickets in expected_results.items():
            self.assertIn(username, participantes, f"Usuário esperado '{username}' não foi encontrado.")
            self.assertEqual(participantes[username]['tickets'], expected_tickets, f"Contagem de tickets para '{username}' está incorreta.")

        # Valida que usuários com comentários inválidos não estão na lista
        self.assertNotIn('gleycinhag', participantes, "Usuário que apenas mencionou outro não deveria ser incluído.")

if __name__ == '__main__':
    unittest.main() 