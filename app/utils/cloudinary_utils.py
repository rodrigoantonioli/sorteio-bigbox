import cloudinary
import cloudinary.uploader
import cloudinary.utils
from flask import current_app
import os
import uuid
from werkzeug.utils import secure_filename

def init_cloudinary():
    """Inicializa o Cloudinary com a URL do ambiente"""
    cloudinary.config(
        cloudinary_url=current_app.config['CLOUDINARY_URL']
    )

def upload_image(file, folder='premios'):
    """
    Faz upload de uma imagem para o Cloudinary
    
    Args:
        file: Arquivo de imagem (werkzeug.FileStorage)
        folder: Pasta no Cloudinary (default: 'premios')
    
    Returns:
        dict: Dados do upload incluindo public_id e secure_url
    """
    try:
        # Gera um nome único para o arquivo
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Faz o upload
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            public_id=unique_filename,
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