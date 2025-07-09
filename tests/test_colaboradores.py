import unittest
import sys
import os
from io import BytesIO
from openpyxl import Workbook

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja, Colaborador
from helpers import generate_random_email, generate_random_password

class ColaboradoresTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # Lojas
        self.loja1 = Loja(codigo='BIG01', nome='BigBox Asa Sul', bandeira='BIG')
        self.loja2 = Loja(codigo='ULTRA02', nome='UltraBox Lago Norte', bandeira='ULTRA')
        db.session.add_all([self.loja1, self.loja2])
        db.session.commit()

        # Usuários
        self.admin_password = generate_random_password()
        self.admin = Usuario(email=generate_random_email(), nome='Admin Colab', tipo='admin')
        self.admin.set_password(self.admin_password)
        
        self.assistente_password = generate_random_password()
        self.assistente = Usuario(email=generate_random_email(), nome='Assistente Colab', tipo='assistente', loja_id=self.loja1.id)
        self.assistente.set_password(self.assistente_password)
        db.session.add_all([self.admin, self.assistente])
        db.session.commit()

        # Colaboradores
        self.colaborador1 = Colaborador(matricula='123', nome='Colaborador Loja 1', setor='Padaria', loja_id=self.loja1.id)
        self.colaborador2 = Colaborador(matricula='456', nome='Colaborador Loja 2', setor='Açougue', loja_id=self.loja2.id)
        db.session.add_all([self.colaborador1, self.colaborador2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/auth/login', data={'email': email, 'password': password})

    def test_admin_lista_colaboradores(self):
        self.login(self.admin.email, self.admin_password)
        # Testar sem a barra final, deixando o Flask redirecionar se necessário
        response = self.client.get('/admin/colaboradores')
        self.assertIn(response.status_code, [200, 308]) # Aceita OK ou Redirect

        # Segue o redirecionamento se houver
        if response.status_code == 308:
            response = self.client.get(response.location)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Colaborador Loja 1', response.data)

    def test_assistente_lista_colaboradores(self):
        self.login(self.assistente.email, self.assistente_password)
        # Testar sem a barra final
        response = self.client.get('/assistente/colaboradores')
        self.assertIn(response.status_code, [200, 308]) # Aceita OK ou Redirect

        if response.status_code == 308:
            response = self.client.get(response.location)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Colaborador Loja 1', response.data)
        self.assertNotIn(b'Colaborador Loja 2', response.data)

    def test_admin_cria_colaborador(self):
        self.login(self.admin.email, self.admin_password)
        response = self.client.post('/admin/colaboradores/adicionar', data={
            'matricula': '789', 'nome': 'Novo Colab Admin', 'setor': 'RH', 'loja_id': self.loja2.id, 'apto': True
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Novo Colab Admin', response.data)

    def test_assistente_cria_colaborador(self):
        self.login(self.assistente.email, self.assistente_password)
        response = self.client.post('/assistente/colaboradores/novo', data={
            'matricula': '101', 'nome': 'Novo Colab Assistente', 'setor': 'Caixa', 'apto': True
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Novo Colab Assistente', response.data)

    def test_admin_edita_colaborador(self):
        self.login(self.admin.email, self.admin_password)
        response = self.client.post(f'/admin/colaboradores/{self.colaborador1.id}/editar', data={
            'matricula': '123', 'nome': 'Editado Admin', 'setor': 'Gerencia', 'loja_id': self.loja1.id, 'apto': False
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Editado Admin', response.data)

    def test_assistente_edita_seu_colaborador(self):
        self.login(self.assistente.email, self.assistente_password)
        response = self.client.post(f'/assistente/colaboradores/{self.colaborador1.id}/editar', data={
            'matricula': '123', 'nome': 'Editado Assistente', 'setor': 'Tesouraria', 'apto': False
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Editado Assistente', response.data)

    def test_admin_toggle_colaborador(self):
        self.login(self.admin.email, self.admin_password)
        self.assertTrue(self.colaborador1.apto)
        response = self.client.post(f'/admin/colaboradores/{self.colaborador1.id}/toggle', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Colaborador.query.get(self.colaborador1.id).apto)

    def test_assistente_toggle_colaborador(self):
        self.login(self.assistente.email, self.assistente_password)
        self.assertTrue(self.colaborador1.apto)
        response = self.client.get(f'/assistente/colaboradores/{self.colaborador1.id}/toggle', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Colaborador.query.get(self.colaborador1.id).apto)

    def test_upload_planilha_admin_sucesso(self):
        self.login(self.admin.email, self.admin_password)
        output = BytesIO()
        workbook = Workbook()
        sheet = workbook.active
        # Usar o "Formato 2" que o log indicou ser o padrão (6 colunas)
        sheet.append(['Filial', 'Unidade', 'Bandeira', 'Matrícula', 'Nome do Colaborador', 'Setor'])
        sheet.append(['1', self.loja1.codigo, 'BIG', '99901', 'Colaborador Upload Formato 2', 'Frios'])
        workbook.save(output)
        output.seek(0)
        
        response = self.client.post('/admin/colaboradores/upload', data={
            'arquivo': (output, 'teste_upload.xlsx')
        }, content_type='multipart/form-data', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        # Verificar se a mensagem de sucesso contém o número correto de novos colaboradores
        self.assertIn(b'Novos colaboradores: 1', response.data)

if __name__ == '__main__':
    unittest.main() 