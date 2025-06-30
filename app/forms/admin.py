from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional
from datetime import date

class SorteioSemanalForm(FlaskForm):
    """Formulário para sorteio semanal"""
    semana_inicio = DateField('Data de Início da Semana', 
                            validators=[DataRequired(message='Data é obrigatória')],
                            default=date.today)
    submit = SubmitField('Realizar Sorteio')

class UsuarioForm(FlaskForm):
    """Formulário para criar/editar usuário gerente"""
    nome = StringField('Nome Completo', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(min=3, max=100, message='Nome deve ter entre 3 e 100 caracteres')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email é obrigatório'),
        Email(message='Email inválido'),
        Length(max=100)
    ])
    password = PasswordField('Senha', validators=[
        Optional(),  # Opcional para edição
        Length(min=6, message='Senha deve ter no mínimo 6 caracteres')
    ])
    loja_id = SelectField('Loja', coerce=int, validators=[
        DataRequired(message='Selecione uma loja')
    ])
    submit = SubmitField('Salvar') 