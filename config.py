import os
from datetime import timedelta
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Configurações base da aplicação"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sorteio.db'
    # Corrige URL do PostgreSQL para SQLAlchemy (Render usa postgres://)
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload de arquivos
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB máximo
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # Paginação
    ITEMS_PER_PAGE = 20
    
    # Admin padrão
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@bigbox.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'BigBox2025!')

class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # HTTPS apenas

# Seleção de configuração baseada no ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Retorna a configuração apropriada baseada no FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default']) 