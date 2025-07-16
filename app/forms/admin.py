from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField, IntegerField, TextAreaField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
from datetime import date

class SorteioSemanalForm(FlaskForm):
    """Formulário para sortear lojas semanalmente"""
    semana_inicio = DateField('Semana (Terça-feira)', validators=[
        DataRequired(message='Selecione a data da terça-feira')
    ], default=date.today)
    submit = SubmitField('Realizar Sorteio')

class UsuarioForm(FlaskForm):
    """Formulário para criar/editar usuários gerentes"""
    nome = StringField('Nome Completo', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(min=2, max=100, message='Nome deve ter entre 2 e 100 caracteres')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email é obrigatório'),
        Email(message='Email inválido'),
        Length(max=100, message='Email muito longo')
    ])
    loja_id = SelectField('Loja Associada', coerce=int, validators=[
        DataRequired(message='Selecione uma loja para o assistente')
    ])
    password = StringField('Senha', validators=[
        Optional(),
        Length(min=6, max=50, message='Senha deve ter entre 6 e 50 caracteres')
    ])
    submit = SubmitField('Salvar')

class PremioForm(FlaskForm):
    """Formulário para criar/editar prêmios"""
    nome = StringField('Nome do Prêmio', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(min=2, max=100, message='Nome deve ter entre 2 e 100 caracteres')
    ])
    descricao = TextAreaField('Descrição', validators=[
        Length(max=500, message='Descrição muito longa')
    ])
    data_evento = DateField('Data do Evento', validators=[
        DataRequired(message='Data do evento é obrigatória')
    ])
    tipo = SelectField('Tipo', choices=[
        ('show', 'Show'),
        ('day_use', 'Day Use')
    ], validators=[DataRequired(message='Tipo é obrigatório')])
    imagem = FileField('Imagem do Prêmio', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Apenas arquivos JPG, JPEG, PNG, GIF e WEBP são permitidos!')
    ])
    submit = SubmitField('Salvar')

class AtribuirPremioForm(FlaskForm):
    """Formulário para atribuir prêmio a uma loja ganhadora"""
    loja_id = SelectField('Loja Ganhadora', coerce=int, validators=[
        DataRequired(message='Selecione uma loja')
    ])
    submit = SubmitField('Atribuir à Loja')

class LojaForm(FlaskForm):
    """Formulário para criar/editar lojas"""
    codigo = StringField('Código da Loja', validators=[
        DataRequired(message='Código é obrigatório'),
        Length(min=2, max=50, message='Código deve ter entre 2 e 50 caracteres')
    ])
    nome = StringField('Nome da Loja', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(min=2, max=100, message='Nome deve ter entre 2 e 100 caracteres')
    ])
    bandeira = SelectField('Bandeira', choices=[
        ('BIG', 'BIG Box'),
        ('ULTRA', 'UltraBox')
    ], validators=[DataRequired(message='Bandeira é obrigatória')])
    ativo = BooleanField('Loja Ativa', default=True)
    submit = SubmitField('Salvar')

class UploadColaboradoresForm(FlaskForm):
    arquivo = FileField('Arquivo Excel', validators=[DataRequired()])
    submit = SubmitField('Fazer Upload')

class SorteioInstagramForm(FlaskForm):
    """Formulário para criar ou editar um sorteio do Instagram."""
    titulo = StringField('Título do Sorteio', validators=[DataRequired(), Length(max=200)])
    descricao = TextAreaField('Descrição (Opcional)')
    texto_original = TextAreaField('Cole aqui o texto do post do Instagram', validators=[DataRequired()])
    palavra_chave = StringField('Palavra-chave para Comentários', default='EU QUERO', validators=[DataRequired(), Length(max=100)])
    tickets_maximos = IntegerField('Máximo de Tickets por Participante', default=30, validators=[DataRequired(), NumberRange(min=1)])
    quantidade_vencedores = IntegerField('Quantidade de Vencedores', default=1, validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Salvar Sorteio')

class ConfiguracaoInstagramForm(FlaskForm):
    palavra_chave_padrao = StringField('Palavra-chave Padrão', validators=[DataRequired(), Length(max=100)])
    tickets_maximos_padrao = IntegerField('Tickets Máximos Padrão', validators=[DataRequired(), NumberRange(min=1, max=100)])
    submit = SubmitField('Salvar Configurações') 