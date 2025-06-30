from datetime import datetime
from flask_login import UserMixin
from app.extensions import db
import bcrypt

class Usuario(UserMixin, db.Model):
    """Modelo de Usuário (Admin e Gerentes)"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.Enum('admin', 'gerente', name='tipo_usuario'), nullable=False)
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    loja = db.relationship('Loja', backref='gerente', foreign_keys=[loja_id])
    sorteios_realizados = db.relationship('SorteioSemanal', backref='sorteado_por_usuario', 
                                        foreign_keys='SorteioSemanal.sorteado_por')
    
    def set_password(self, password):
        """Criptografa e armazena a senha"""
        self.senha_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return bcrypt.checkpw(password.encode('utf-8'), self.senha_hash.encode('utf-8'))
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

class Loja(db.Model):
    """Modelo de Loja"""
    __tablename__ = 'lojas'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    bandeira = db.Column(db.Enum('BIG', 'ULTRA', name='bandeira_loja'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    colaboradores = db.relationship('Colaborador', backref='loja', lazy='dynamic')
    sorteios_big = db.relationship('SorteioSemanal', foreign_keys='SorteioSemanal.loja_big_id',
                                 backref='loja_big_sorteada')
    sorteios_ultra = db.relationship('SorteioSemanal', foreign_keys='SorteioSemanal.loja_ultra_id',
                                    backref='loja_ultra_sorteada')
    
    def __repr__(self):
        return f'<Loja {self.codigo} - {self.nome}>'

class Colaborador(db.Model):
    """Modelo de Colaborador"""
    __tablename__ = 'colaboradores'
    
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(20), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(50), nullable=False)
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)
    apto = db.Column(db.Boolean, default=True)
    ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    sorteios = db.relationship('SorteioColaborador', backref='colaborador', lazy='dynamic')
    
    # Índice único para matrícula + loja
    __table_args__ = (db.UniqueConstraint('matricula', 'loja_id', name='_matricula_loja_uc'),)
    
    def __repr__(self):
        return f'<Colaborador {self.matricula} - {self.nome}>'

class SorteioSemanal(db.Model):
    """Modelo de Sorteio Semanal (lojas sorteadas)"""
    __tablename__ = 'sorteios_semanais'
    
    id = db.Column(db.Integer, primary_key=True)
    semana_inicio = db.Column(db.Date, nullable=False, unique=True)
    loja_big_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)
    loja_ultra_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)
    data_sorteio = db.Column(db.DateTime, default=datetime.utcnow)
    sorteado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relacionamentos
    sorteios_colaboradores = db.relationship('SorteioColaborador', backref='sorteio_semanal', 
                                           lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SorteioSemanal {self.semana_inicio}>'

class SorteioColaborador(db.Model):
    """Modelo de Sorteio de Colaboradores"""
    __tablename__ = 'sorteios_colaboradores'
    
    id = db.Column(db.Integer, primary_key=True)
    sorteio_semanal_id = db.Column(db.Integer, db.ForeignKey('sorteios_semanais.id'), nullable=False)
    colaborador_id = db.Column(db.Integer, db.ForeignKey('colaboradores.id'), nullable=False)
    tipo_ingresso = db.Column(db.String(50), nullable=False)  # 'show' ou 'day_use'
    dia_evento = db.Column(db.Date, nullable=False)
    data_sorteio = db.Column(db.DateTime, default=datetime.utcnow)
    sorteado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relacionamentos
    usuario_sorteador = db.relationship('Usuario', backref='colaboradores_sorteados', 
                                      foreign_keys=[sorteado_por])
    
    def __repr__(self):
        return f'<SorteioColaborador {self.colaborador_id} - {self.tipo_ingresso}>' 