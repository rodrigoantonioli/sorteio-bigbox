import unittest
import sys
import os
from datetime import datetime, date

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.extensions import db
from app.models import Usuario, Loja, Colaborador, Premio, SorteioSemanal, SorteioColaborador
from helpers import generate_random_password

class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        """Executado antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Executado depois de cada teste"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_usuario_model(self):
        """Teste do modelo Usuario"""
        password = generate_random_password()
        usuario = Usuario(
            email='test@example.com',
            nome='Test User',
            tipo='admin'
        )
        usuario.set_password(password)
        db.session.add(usuario)
        db.session.commit()
        
        usuario_salvo = Usuario.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(usuario_salvo)
        self.assertTrue(usuario_salvo.check_password(password))
        self.assertFalse(usuario_salvo.check_password(generate_random_password()))

    def test_loja_model(self):
        """Teste do modelo Loja"""
        # Criar loja
        loja = Loja(
            codigo='BIG001',
            nome='BigBox Matriz',
            bandeira='BIG'
        )
        
        db.session.add(loja)
        db.session.commit()
        
        # Verificar se foi salva
        loja_salva = Loja.query.filter_by(codigo='BIG001').first()
        self.assertIsNotNone(loja_salva)
        self.assertEqual(loja_salva.nome, 'BigBox Matriz')
        self.assertEqual(loja_salva.bandeira, 'BIG')

    def test_colaborador_model(self):
        """Teste do modelo Colaborador"""
        # Criar loja primeiro
        loja = Loja(codigo='BIG001', nome='BigBox Matriz', bandeira='BIG')
        db.session.add(loja)
        db.session.commit()
        
        # Criar colaborador
        colaborador = Colaborador(
            matricula='12345',
            nome='João Silva',
            setor='Vendas',
            loja_id=loja.id
        )
        
        db.session.add(colaborador)
        db.session.commit()
        
        # Verificar se foi salvo
        colaborador_salvo = Colaborador.query.filter_by(matricula='12345').first()
        self.assertIsNotNone(colaborador_salvo)
        self.assertEqual(colaborador_salvo.nome, 'João Silva')
        self.assertEqual(colaborador_salvo.loja.codigo, 'BIG001')

    def test_premio_model(self):
        """Teste do modelo Premio"""
        # Criar usuário e loja primeiro
        usuario = Usuario(email='admin@bigbox.com', nome='Admin', tipo='admin')
        usuario.set_password('senha123')
        loja = Loja(codigo='BIG001', nome='BigBox Matriz', bandeira='BIG')
        
        db.session.add(usuario)
        db.session.add(loja)
        db.session.commit()
        
        # Criar prêmio
        premio = Premio(
            nome='Show VIP',
            descricao='Show com artista famoso',
            data_evento=date(2025, 12, 31),
            tipo='show',
            loja_id=loja.id,
            criado_por=usuario.id
        )
        
        db.session.add(premio)
        db.session.commit()
        
        # Verificar se foi salvo
        premio_salvo = Premio.query.filter_by(nome='Show VIP').first()
        self.assertIsNotNone(premio_salvo)
        self.assertEqual(premio_salvo.tipo, 'show')
        self.assertEqual(premio_salvo.loja.codigo, 'BIG001')

    def test_constraint_matricula_loja(self):
        """Teste da constraint única para matrícula por loja"""
        # Criar loja
        loja = Loja(codigo='BIG001', nome='BigBox Matriz', bandeira='BIG')
        db.session.add(loja)
        db.session.commit()
        
        # Criar primeiro colaborador
        colaborador1 = Colaborador(
            matricula='12345',
            nome='João Silva',
            setor='Vendas',
            loja_id=loja.id
        )
        db.session.add(colaborador1)
        db.session.commit()
        
        # Tentar criar segundo colaborador com mesma matrícula na mesma loja
        colaborador2 = Colaborador(
            matricula='12345',
            nome='Maria Santos',
            setor='Caixa',
            loja_id=loja.id
        )
        db.session.add(colaborador2)
        
        # Deve dar erro de constraint
        with self.assertRaises(Exception):
            db.session.commit()

if __name__ == '__main__':
    unittest.main() 