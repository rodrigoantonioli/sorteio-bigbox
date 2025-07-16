import os
from datetime import timedelta
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

# Define o caminho do banco dentro da pasta instance
instance_folder = os.path.join(basedir, 'instance')
db_path = os.path.join(instance_folder, 'sorteio.db')

# Cria a pasta 'instance' na raiz do projeto se ela não existir
if not os.path.exists(instance_folder):
    os.makedirs(instance_folder)

class Config:
    """Configurações base da aplicação"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLAlchemy - Configuração melhorada para PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Corrige URL do PostgreSQL para SQLAlchemy (Render pode usar postgres://)
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback para SQLite em desenvolvimento
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Upload de arquivos
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB máximo
    UPLOAD_FOLDER = '/app/uploads'
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
    
    # Configurações de Admin
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'default-dev-password'

class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # HTTPS apenas
    # Remove SQLALCHEMY_ECHO em produção
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """Configurações de teste"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Usa banco de dados em memória
    WTF_CSRF_ENABLED = False # Desabilita CSRF para testes de formulário

# Seleção de configuração baseada no ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Retorna a configuração apropriada baseada no FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default']) 