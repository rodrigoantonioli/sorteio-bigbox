from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import IntegerField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from datetime import date

class UploadColaboradoresForm(FlaskForm):
    """Formulário para upload de planilha de colaboradores"""
    file = FileField('Arquivo Excel', validators=[
        FileRequired(message='Selecione um arquivo'),
        FileAllowed(['xlsx', 'xls'], 'Apenas arquivos Excel (.xlsx ou .xls)')
    ])
    submit = SubmitField('Enviar')

class SorteioColaboradorForm(FlaskForm):
    """Formulário para sortear colaboradores"""
    quantidade_ingressos = IntegerField('Quantidade de Ingressos', validators=[
        DataRequired(message='Informe a quantidade'),
        NumberRange(min=1, max=50, message='Quantidade deve ser entre 1 e 50')
    ], default=2)
    
    tipo_ingresso = SelectField('Tipo de Ingresso', choices=[
        ('show', 'Show'),
        ('day_use', 'Day Use')
    ], validators=[DataRequired()])
    
    dia_evento = DateField('Data do Evento', validators=[
        DataRequired(message='Selecione a data do evento')
    ], default=date.today)
    
    submit = SubmitField('Realizar Sorteio') 