from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import IntegerField, DateField, SelectField, SubmitField, BooleanField, StringField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length
from datetime import date

class UploadColaboradoresForm(FlaskForm):
    """Formulário para upload de planilha de colaboradores"""
    arquivo = FileField('Arquivo Excel', validators=[
        FileRequired(message='Selecione um arquivo'),
        FileAllowed(['xlsx', 'xls'], 'Apenas arquivos Excel (.xlsx ou .xls)')
    ])
    substituir_todos = BooleanField('Substituir TODOS os colaboradores', default=True)
    submit = SubmitField('Enviar')

class ColaboradorForm(FlaskForm):
    """Formulário para criar/editar colaborador"""
    matricula = StringField('Matrícula', validators=[
        DataRequired(message='Matrícula é obrigatória'),
        Length(min=1, max=20, message='Matrícula deve ter entre 1 e 20 caracteres')
    ])
    nome = StringField('Nome Completo', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(min=2, max=100, message='Nome deve ter entre 2 e 100 caracteres')
    ])
    setor = StringField('Setor', validators=[
        DataRequired(message='Setor é obrigatório'),
        Length(min=2, max=50, message='Setor deve ter entre 2 e 50 caracteres')
    ])
    apto = BooleanField('Apto para sorteios', default=True)
    submit = SubmitField('Salvar')

class SorteioColaboradorForm(FlaskForm):
    """Formulário para sortear colaboradores"""
    premio_id = SelectField('Prêmio', coerce=int, validators=[
        DataRequired(message='Selecione um prêmio')
    ])
    quantidade_ingressos = IntegerField('Quantidade de Ingressos', validators=[
        DataRequired(message='Informe a quantidade'),
        NumberRange(min=1, max=50, message='Quantidade deve ser entre 1 e 50')
    ], default=2)
    confirmar_lista = BooleanField('Confirmo que a lista de colaboradores está correta', validators=[
        DataRequired(message='Você deve confirmar que a lista está correta')
    ])
    submit = SubmitField('Realizar Sorteio') 