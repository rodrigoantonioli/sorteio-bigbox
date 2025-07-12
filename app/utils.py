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
    A lógica é desenhada para seguir o padrão estrutural do Instagram:
    "Foto do perfil de..." -> username -> timestamp -> comentário.
    """
    participantes = defaultdict(lambda: {'comentarios_validos': 0, 'tickets': 0})
    palavra_chave_lower = palavra_chave.lower().strip()
    
    # Regex para identificar uma linha de tempo (ex: "4 h", "1 d")
    timestamp_re = re.compile(r'^\d+\s+(h|d|min|s)\b.*$')
    
    # Divide o texto em blocos, um para cada post de usuário.
    # Usa "lookahead" para não perder o delimitador na divisão.
    blocos = re.split(r'(?=Foto do perfil de)', text)
    
    for bloco in blocos:
        linhas = [line.strip() for line in bloco.splitlines() if line.strip()]
        
        if not linhas or not linhas[0].startswith("Foto do perfil de"):
            continue
            
        if len(linhas) < 2:
            continue
            
        # O username é extraído da primeira linha.
        username = linhas[0].replace("Foto do perfil de ", "").strip()
        
        # O username se repete na segunda linha, o que confirma a estrutura do bloco.
        if linhas[1] != username:
            continue
        
        # O comentário é a primeira linha "real" após o username e a linha de tempo.
        comentario = ""
        for i in range(2, len(linhas)):
            linha_candidata = linhas[i]
            if not timestamp_re.match(linha_candidata):
                comentario = linha_candidata
                break

        if not comentario:
            continue
            
        # Validação da palavra-chave
        comentario_ascii = comentario.encode('ascii', 'ignore').decode('ascii')
        comentario_limpo = re.sub(r'[^\w\s]', '', comentario_ascii.lower())
        comentario_palavras = set(comentario_limpo.split())

        # Limpa a palavra-chave para comparação
        palavra_chave_limpa = re.sub(r'[^\w\s]', '', palavra_chave_lower)
        palavras_chave_set = set(palavra_chave_limpa.split())
        
        if palavras_chave_set.issubset(comentario_palavras):
            participantes[username]['comentarios_validos'] += 1
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