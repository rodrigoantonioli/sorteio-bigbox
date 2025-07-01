from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField, IntegerField, TextAreaField
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
    loja_id = SelectField('Loja', coerce=int, validators=[Optional()])
    password = StringField('Senha', validators=[
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
    loja_id = SelectField('Loja Ganhadora', coerce=int, validators=[Optional()])
    submit = SubmitField('Salvar') 