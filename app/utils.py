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
    
    Args:
        text: Texto completo copiado do post do Instagram
        palavra_chave: Palavra-chave que deve estar presente no comentário
        tickets_maximos: Número máximo de tickets por participante
        
    Returns:
        dict: Dicionário com username como chave e dados do participante como valor
    """
    participantes = defaultdict(lambda: {'comentarios_validos': 0, 'tickets': 0})
    
    # Padrão para identificar comentários
    # Formato: "Foto do perfil de username\nusername\n \nTEMPO\nCOMENTÁRIO"
    pattern = r'Foto do perfil de ([^\n]+)\n\1\n[^\n]*\n[^\n]+\n([^\n]+(?:\n(?!Foto do perfil de)[^\n]+)*)'
    
    # Normalizar a palavra-chave para comparação case-insensitive
    palavra_chave_lower = palavra_chave.lower().strip()
    
    # Encontrar todos os comentários
    matches = re.findall(pattern, text, re.MULTILINE)
    
    for username, comentario in matches:
        username = username.strip()
        comentario = comentario.strip()
        
        # Verificar se o comentário contém a palavra-chave (case-insensitive)
        comentario_lower = comentario.lower()
        
        # Verificar correspondência exata ou variações comuns
        valido = False
        
        # Verificar correspondência exata
        if palavra_chave_lower in comentario_lower:
            valido = True
        else:
            # Verificar variações comuns (remover pontuação, espaços extras, etc.)
            comentario_limpo = re.sub(r'[^\w\s]', '', comentario_lower)
            palavra_chave_limpa = re.sub(r'[^\w\s]', '', palavra_chave_lower)
            
            # Verificar se as palavras da palavra-chave estão presentes
            palavras_chave = palavra_chave_limpa.split()
            if all(palavra in comentario_limpo for palavra in palavras_chave):
                valido = True
        
        if valido:
            participantes[username]['comentarios_validos'] += 1
            # Limitar tickets ao máximo configurado
            participantes[username]['tickets'] = min(
                participantes[username]['comentarios_validos'],
                tickets_maximos
            )
    
    return dict(participantes)

def validar_arquivo_instagram(file):
    """
    Valida se o arquivo enviado é um arquivo de texto válido.
    
    Args:
        file: Arquivo enviado pelo formulário
        
    Returns:
        tuple: (bool, str) - (válido, mensagem de erro se houver)
    """
    if not file:
        return False, "Nenhum arquivo foi enviado"
    
    # Verificar extensão
    filename = file.filename
    if not filename.endswith('.txt'):
        return False, "O arquivo deve ser um arquivo .txt"
    
    # Verificar tamanho (máximo 10MB)
    file.seek(0, 2)  # Ir para o final do arquivo
    size = file.tell()
    file.seek(0)  # Voltar para o início
    
    if size > 10 * 1024 * 1024:  # 10MB
        return False, "O arquivo é muito grande (máximo 10MB)"
    
    if size == 0:
        return False, "O arquivo está vazio"
    
    return True, None 