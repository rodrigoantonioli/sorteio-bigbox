import cloudinary
import cloudinary.uploader
import cloudinary.utils
import cloudinary.api
from flask import current_app
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
import re

def init_cloudinary():
    """Inicializa o Cloudinary com a URL do ambiente"""
    cloudinary.config(
        cloudinary_url=current_app.config['CLOUDINARY_URL']
    )

def upload_image(file, folder='premios', premio_nome=None):
    """
    Faz upload de uma imagem para o Cloudinary com nome padronizado
    
    Args:
        file: Arquivo de imagem (werkzeug.FileStorage)
        folder: Pasta no Cloudinary (default: 'premios')
        premio_nome: Nome do prêmio para padronização do nome da imagem
    
    Returns:
        dict: Dados do upload incluindo public_id e secure_url
    """
    try:
        # Gera nome padronizado: premio_YYYYMMDD_HHMMSS
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if premio_nome:
            # Limpa o nome do prêmio para usar no filename
            nome_limpo = re.sub(r'[^a-zA-Z0-9_-]', '_', premio_nome.lower())
            nome_limpo = re.sub(r'_+', '_', nome_limpo)  # Remove underscores duplicados
            nome_limpo = nome_limpo.strip('_')  # Remove underscores das extremidades
            public_id = f"premio_{nome_limpo}_{timestamp}"
        else:
            public_id = f"premio_{timestamp}"
        
        # Faz o upload
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            public_id=public_id,
            resource_type="image",
            transformation=[
                {'width': 800, 'height': 600, 'crop': 'limit'},
                {'quality': 'auto'},
                {'format': 'jpg'}
            ]
        )
        
        return {
            'success': True,
            'public_id': result['public_id'],
            'secure_url': result['secure_url'],
            'url': result['url']
        }
        
    except Exception as e:
        current_app.logger.error(f"Erro no upload para Cloudinary: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def delete_image(public_id):
    """
    Remove uma imagem do Cloudinary
    
    Args:
        public_id: ID público da imagem no Cloudinary
    
    Returns:
        dict: Resultado da operação
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return {
            'success': True,
            'result': result
        }
    except Exception as e:
        current_app.logger.error(f"Erro ao deletar imagem do Cloudinary: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def get_image_url(public_id, transformation=None):
    """
    Gera URL da imagem com transformações opcionais
    
    Args:
        public_id: ID público da imagem
        transformation: Lista de transformações (opcional)
    
    Returns:
        str: URL da imagem
    """
    try:
        if transformation:
            return cloudinary.utils.cloudinary_url(public_id, transformation=transformation)[0]
        else:
            return cloudinary.utils.cloudinary_url(public_id)[0]
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar URL da imagem: {str(e)}")
        return None

def is_valid_image(file):
    """
    Verifica se o arquivo é uma imagem válida
    
    Args:
        file: Arquivo para verificação
    
    Returns:
        bool: True se for uma imagem válida
    """
    if not file or not file.filename:
        return False
    
    # Extensões permitidas
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    
    # Verifica extensão
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    return file_extension in allowed_extensions

def extract_public_id_from_url(cloudinary_url):
    """
    Extrai o public_id de uma URL do Cloudinary
    
    Args:
        cloudinary_url: URL completa da imagem no Cloudinary
    
    Returns:
        str: public_id da imagem ou None se não for uma URL válida
    """
    try:
        if not cloudinary_url or 'cloudinary' not in cloudinary_url:
            return None
            
        # Padrão para extrair public_id de URL do Cloudinary
        # Exemplo: https://res.cloudinary.com/dmsl8huhv/image/upload/v1234567890/premios/premio_nome_20240101_120000.jpg
        pattern = r'/(?:v\d+/)?([^/]+/[^.]+)'
        match = re.search(pattern, cloudinary_url)
        
        if match:
            return match.group(1)  # Retorna folder/public_id
        
        return None
        
    except Exception as e:
        current_app.logger.error(f"Erro ao extrair public_id da URL: {str(e)}")
        return None

def cleanup_unused_images():
    """
    Remove imagens não utilizadas do Cloudinary
    Esta função deve ser executada periodicamente
    
    Returns:
        dict: Resultado da operação de limpeza
    """
    try:
        from app.models import Premio
        
        # Busca todas as imagens no banco
        premios_com_imagem = Premio.query.filter(
            Premio.imagem.isnot(None),
            Premio.imagem.contains('cloudinary')
        ).all()
        
        # Extrai public_ids das imagens em uso
        public_ids_em_uso = set()
        for premio in premios_com_imagem:
            public_id = extract_public_id_from_url(premio.imagem)
            if public_id:
                public_ids_em_uso.add(public_id)
        
        # Lista todas as imagens na pasta premios do Cloudinary
        result = cloudinary.api.resources(
            type='upload',
            prefix='premios/',
            max_results=500
        )
        
        # Identifica imagens não utilizadas
        imagens_para_deletar = []
        for resource in result.get('resources', []):
            if resource['public_id'] not in public_ids_em_uso:
                imagens_para_deletar.append(resource['public_id'])
        
        # Remove imagens não utilizadas
        deleted_count = 0
        for public_id in imagens_para_deletar:
            delete_result = delete_image(public_id)
            if delete_result['success']:
                deleted_count += 1
                current_app.logger.info(f"Imagem removida: {public_id}")
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'total_checked': len(result.get('resources', [])),
            'in_use_count': len(public_ids_em_uso)
        }
        
    except Exception as e:
        current_app.logger.error(f"Erro na limpeza de imagens: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }