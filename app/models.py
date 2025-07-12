from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.utils import get_brazil_datetime
import os

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'admin' ou 'assistente'
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

class Loja(db.Model):
    __tablename__ = 'lojas'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    bandeira = db.Column(db.String(10), nullable=False)  # 'BIG' ou 'ULTRA'
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Colaborador(db.Model):
    __tablename__ = 'colaboradores'
    
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(20), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(50), nullable=False)
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)
    apto = db.Column(db.Boolean, default=True)
    ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Constraint para evitar matrícula duplicada na mesma loja
    __table_args__ = (db.UniqueConstraint('matricula', 'loja_id', name='_matricula_loja_uc'),)

class Premio(db.Model):
    __tablename__ = 'premios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    data_evento = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'show' ou 'day_use'
    imagem = db.Column(db.String(255), nullable=True)  # Nome do arquivo de imagem
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=True)  # Vinculação com loja ganhadora
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    criado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    def get_imagem_url(self):
        """Retorna a URL da imagem do prêmio ou imagem padrão"""
        if self.imagem and os.path.exists(f'app/static/images/premios/{self.imagem}'):
            return f'/static/images/premios/{self.imagem}'
        else:
            # Retorna imagem padrão baseada no tipo
            if self.tipo == 'show':
                return '/static/images/premios/default_show.jpg'
            else:  # day_use
                return '/static/images/premios/default_day_use.jpg'

class SorteioSemanal(db.Model):
    __tablename__ = 'sorteios_semanais'
    
    id = db.Column(db.Integer, primary_key=True)
    semana_inicio = db.Column(db.Date, unique=True, nullable=False)
    loja_big_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)
    loja_ultra_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)
    data_sorteio = db.Column(db.DateTime, default=get_brazil_datetime)
    sorteado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class SorteioColaborador(db.Model):
    __tablename__ = 'sorteios_colaboradores'
    
    id = db.Column(db.Integer, primary_key=True)
    sorteio_semanal_id = db.Column(db.Integer, db.ForeignKey('sorteios_semanais.id'), nullable=False)
    premio_id = db.Column(db.Integer, db.ForeignKey('premios.id'), nullable=False)
    colaborador_id = db.Column(db.Integer, db.ForeignKey('colaboradores.id'), nullable=False)
    data_sorteio = db.Column(db.DateTime, default=get_brazil_datetime)
    sorteado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    lista_confirmada = db.Column(db.Boolean, default=False)
    colaboradores_snapshot = db.Column(db.Text)

# Relacionamentos usando db.relationship
Usuario.loja = db.relationship('Loja', backref='usuarios')
Colaborador.loja = db.relationship('Loja', backref='colaboradores')
Premio.criador = db.relationship('Usuario', backref='premios_criados')
Premio.loja = db.relationship('Loja', backref='premios_disponiveis')

SorteioSemanal.loja_big = db.relationship('Loja', foreign_keys=[SorteioSemanal.loja_big_id])
SorteioSemanal.loja_ultra = db.relationship('Loja', foreign_keys=[SorteioSemanal.loja_ultra_id])
SorteioSemanal.sorteador = db.relationship('Usuario', foreign_keys=[SorteioSemanal.sorteado_por])

SorteioColaborador.sorteio_semanal = db.relationship('SorteioSemanal')
SorteioColaborador.premio = db.relationship('Premio')
SorteioColaborador.colaborador = db.relationship('Colaborador')
SorteioColaborador.sorteador = db.relationship('Usuario', foreign_keys=[SorteioColaborador.sorteado_por]) 

class SorteioInstagram(db.Model):
    __tablename__ = 'sorteios_instagram'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    palavra_chave = db.Column(db.String(100), nullable=False, default='EU QUERO')
    tickets_maximos = db.Column(db.Integer, nullable=False, default=30)
    quantidade_vencedores = db.Column(db.Integer, nullable=False, default=1, server_default='1')
    texto_original = db.Column(db.Text, nullable=False)  # Texto completo do post
    data_criacao = db.Column(db.DateTime, default=get_brazil_datetime)
    data_sorteio = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='processando')  # processando, pronto, sorteado
    criado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relacionamentos
    criador = db.relationship('Usuario', backref='sorteios_instagram_criados')
    participantes = db.relationship('ParticipanteInstagram', backref='sorteio', cascade='all, delete-orphan')

class ParticipanteInstagram(db.Model):
    __tablename__ = 'participantes_instagram'
    
    id = db.Column(db.Integer, primary_key=True)
    sorteio_id = db.Column(db.Integer, db.ForeignKey('sorteios_instagram.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    comentarios_validos = db.Column(db.Integer, default=0)
    tickets = db.Column(db.Integer, default=0)  # Limitado ao máximo configurado
    vencedor = db.Column(db.Boolean, default=False)
    
    # Constraint para evitar username duplicado no mesmo sorteio
    __table_args__ = (db.UniqueConstraint('username', 'sorteio_id', name='_username_sorteio_uc'),)

class ConfiguracaoInstagram(db.Model):
    __tablename__ = 'configuracao_instagram'
    
    id = db.Column(db.Integer, primary_key=True)
    palavra_chave_padrao = db.Column(db.String(100), nullable=False, default='EU QUERO')
    tickets_maximos_padrao = db.Column(db.Integer, nullable=False, default=30)
    atualizado_em = db.Column(db.DateTime, default=get_brazil_datetime)
    atualizado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id')) 