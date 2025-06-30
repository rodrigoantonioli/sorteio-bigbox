from flask import Flask
from config import get_config
from app.extensions import db, login_manager, migrate, mail
import os

def create_app():
    """Factory pattern para criar a aplicação Flask"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuração
    app.config.from_object(get_config())
    
    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Configurações do Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Cria diretório de uploads se não existir
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Registra blueprints
    from app.routes import main_bp, auth_bp, admin_bp, manager_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(manager_bp, url_prefix='/gerente')
    
    # Cria tabelas e admin padrão
    with app.app_context():
        from app.models import Usuario, Loja
        db.create_all()
        
        # Cria usuário admin padrão se não existir
        admin = Usuario.query.filter_by(email=app.config['ADMIN_EMAIL']).first()
        if not admin:
            admin = Usuario(
                email=app.config['ADMIN_EMAIL'],
                nome='Administrador',
                tipo='admin'
            )
            admin.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()
            print(f"Usuário admin criado: {app.config['ADMIN_EMAIL']}")
    
    return app

# Cria a aplicação
app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 