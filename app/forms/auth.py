from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    """Formulário de login"""
    email = StringField('Email', validators=[
        DataRequired(message='Email é obrigatório'),
        Email(message='Email inválido')
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='Senha é obrigatória'),
        Length(min=6, message='Senha deve ter no mínimo 6 caracteres')
    ])
    remember_me = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar') 