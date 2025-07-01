import unittest
import sys
import os
import tempfile
import openpyxl
from werkzeug.datastructures import FileStorage

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja, Colaborador

class ColaboradoresTestCase(unittest.TestCase):
    def setUp(self):
        """Executado antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Criar loja e usuários para testes
        self.loja = Loja(codigo='BIG001', nome='BigBox Matriz', bandeira='BIG')
        db.session.add(self.loja)
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
            loja_id=self.loja.id
        )
        self.assistente.set_password('assist123')
        
        db.session.add(self.admin)
        db.session.add(self.assistente)
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

    def test_listar_colaboradores_admin(self):
        """Teste de listagem de colaboradores (admin vê todos)"""
        self.login_admin()
        
        # Criar colaboradores
        colab1 = Colaborador(matricula='12345', nome='João Silva', 
                           setor='Vendas', loja_id=self.loja.id)
        colab2 = Colaborador(matricula='67890', nome='Maria Santos', 
                           setor='Caixa', loja_id=self.loja.id)
        db.session.add(colab1)
        db.session.add(colab2)
        db.session.commit()
        
        response = self.client.get('/admin/colaboradores')
        self.assertEqual(response.status_code, 200)
        self.assertIn('João Silva'.encode('utf-8'), response.data)
        self.assertIn('Maria Santos'.encode('utf-8'), response.data)

    def test_listar_colaboradores_assistente(self):
        """Teste de listagem de colaboradores (assistente vê só da sua loja)"""
        self.login_assistente()
        
        # Criar colaborador na loja do assistente
        colab1 = Colaborador(matricula='12345', nome='João Silva', 
                           setor='Vendas', loja_id=self.loja.id)
        
        # Criar outra loja e colaborador
        outra_loja = Loja(codigo='BIG002', nome='BigBox Filial', bandeira='BIG')
        db.session.add(outra_loja)
        db.session.commit()
        
        colab2 = Colaborador(matricula='67890', nome='Maria Santos', 
                           setor='Caixa', loja_id=outra_loja.id)
        
        db.session.add(colab1)
        db.session.add(colab2)
        db.session.commit()
        
        response = self.client.get('/manager/colaboradores')
        self.assertEqual(response.status_code, 200)
        self.assertIn('João Silva'.encode('utf-8'), response.data)
        self.assertNotIn('Maria Santos'.encode('utf-8'), response.data)  # Não deve ver da outra loja

    def test_criar_colaborador(self):
        """Teste de criação de colaborador"""
        self.login_admin()
        
        response = self.client.post('/admin/colaboradores/adicionar', data={
            'matricula': '12345',
            'nome': 'João Silva',
            'setor': 'Vendas',
            'loja_id': self.loja.id
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi criado
        colab = Colaborador.query.filter_by(matricula='12345').first()
        self.assertIsNotNone(colab)
        self.assertEqual(colab.nome, 'João Silva')
        self.assertEqual(colab.loja_id, self.loja.id)

    def test_editar_colaborador(self):
        """Teste de edição de colaborador"""
        self.login_admin()
        
        # Criar colaborador
        colab = Colaborador(matricula='12345', nome='João Original', 
                          setor='Vendas', loja_id=self.loja.id)
        db.session.add(colab)
        db.session.commit()
        
        # Editar colaborador
        response = self.client.post(f'/admin/colaboradores/{colab.id}/editar', data={
            'matricula': '12345',
            'nome': 'João Editado',
            'setor': 'Gerencia',
            'loja_id': self.loja.id
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi editado
        colab_editado = Colaborador.query.get(colab.id)
        self.assertEqual(colab_editado.nome, 'João Editado')
        self.assertEqual(colab_editado.setor, 'Gerencia')

    def test_inativar_colaborador(self):
        """Teste de inativação de colaborador"""
        self.login_admin()
        
        # Criar colaborador
        colab = Colaborador(matricula='12345', nome='João Silva', 
                          setor='Vendas', loja_id=self.loja.id)
        db.session.add(colab)
        db.session.commit()
        
        # Inativar colaborador
        response = self.client.post(f'/admin/colaboradores/{colab.id}/toggle', 
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi inativado (toggle muda o status)
        colab_inativado = Colaborador.query.get(colab.id)
        self.assertFalse(colab_inativado.apto)

    def create_test_excel_file(self):
        """Cria arquivo Excel de teste para upload"""
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        
        # Criar workbook e worksheet
        wb = openpyxl.Workbook()
        ws = wb.active
        
        # Cabeçalhos
        ws['A1'] = 'MATRICULA'
        ws['B1'] = 'NOME'
        ws['C1'] = 'SETOR'
        
        # Dados de teste
        ws['A2'] = '12345'
        ws['B2'] = 'João Silva'
        ws['C2'] = 'Vendas'
        
        ws['A3'] = '67890'
        ws['B3'] = 'Maria Santos'
        ws['C3'] = 'Caixa'
        
        wb.save(temp_file.name)
        temp_file.close()
        
        return temp_file.name

    def test_upload_colaboradores(self):
        """Teste de upload de colaboradores via Excel"""
        self.login_assistente()
        
        # Criar arquivo Excel de teste
        excel_file = self.create_test_excel_file()
        
        try:
            with open(excel_file, 'rb') as f:
                data = {
                    'arquivo': (f, 'colaboradores.xlsx')
                }
                response = self.client.post('/manager/colaboradores/upload', 
                                          data=data, 
                                          content_type='multipart/form-data',
                                          follow_redirects=True)
                
                self.assertEqual(response.status_code, 200)
                
                # Verificar se colaboradores foram criados
                colaboradores = Colaborador.query.filter_by(loja_id=self.loja.id).all()
                self.assertEqual(len(colaboradores), 2)
                
                nomes = [c.nome for c in colaboradores]
                self.assertIn('João Silva', nomes)
                self.assertIn('Maria Santos', nomes)
        finally:
            # Limpar arquivo temporário
            os.unlink(excel_file)

if __name__ == '__main__':
    unittest.main() 