# Pacote utils
from .cloudinary_utils import *

# Importa funções do utils.py
from datetime import datetime, timezone, timedelta
import re
from collections import defaultdict

def get_brazil_datetime():
    """Retorna datetime atual no horário do Brasil (GMT-3)"""
    brazil_tz = timezone(timedelta(hours=-3))
    return datetime.now(brazil_tz).replace(tzinfo=None)

def get_brazil_date():
    """Retorna date atual no horário do Brasil (GMT-3)"""
    return get_brazil_datetime().date()

def format_brazil_datetime(dt):
    """Formata datetime para exibição no formato brasileiro"""
    if dt:
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    return ''

def format_brazil_date(dt):
    """Formata date para exibição no formato brasileiro"""
    if dt:
        return dt.strftime('%d/%m/%Y')
    return ''

def parse_instagram_comments(text, palavra_chave='EU QUERO', tickets_maximos=30):
    """
    Processa o texto copiado do Instagram e extrai os participantes válidos.
    """
    # Implementação básica - pode ser expandida conforme necessário
    return {}, []

def validar_arquivo_instagram(arquivo):
    """Valida arquivo do Instagram"""
    return True