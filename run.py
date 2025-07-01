from flask import Flask
from config import get_config, db_path
from app.extensions import db, login_manager, migrate, mail
import os
import openpyxl
from app.models import Usuario, Loja

def create_app(config_name='default'):
    """Factory pattern para criar a aplicação Flask"""
    app = Flask(__name__,
                template_folder='app/templates',
                static_folder='app/static')
    
    # Configuração
    from config import config
    app.config.from_object(config[config_name])
    
    # Cria a pasta instance se não existir
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Cria a pasta de uploads se não existir
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    
    # Configurações do Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Registra blueprints
    from app.routes import main_bp, auth_bp, admin_bp, manager_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(manager_bp, url_prefix='/gerente')
    
    # Comando CLI para inicializar o banco
    @app.cli.command()
    def init_db():
        """Inicializa o banco de dados"""
        db.create_all()
        print("✓ Tabelas do banco de dados criadas.")
        
        # Cria admin se não existir
        admin_email = app.config.get('ADMIN_EMAIL')
        admin_password = app.config.get('ADMIN_PASSWORD')
        
        if not admin_email or not admin_password:
            print("❌ ADMIN_EMAIL e ADMIN_PASSWORD devem estar definidos no .env")
            return
            
        if not Usuario.query.filter_by(email=admin_email).first():
            admin = Usuario(
                email=admin_email,
                nome='Administrador',
                tipo='admin'
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            print(f"✓ Usuário admin criado: {admin_email}")
        else:
            print(f"✓ Usuário admin já existe: {admin_email}")

        # Popula lojas do Excel
        excel_path = os.path.join(os.path.dirname(__file__), 'inputs', 'TABELA LOJAS.xlsx')
        if not os.path.exists(excel_path):
            print(f"❌ Arquivo não encontrado: {excel_path}")
            return
            
        try:
            workbook = openpyxl.load_workbook(excel_path)
            sheet = workbook.active
            lojas_criadas = 0
            lojas_existentes = 0
            
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row or len(row) < 4 or row[3] is None:
                    break
                    
                codigo = str(row[2]).strip()
                bandeira = str(row[3]).strip().upper()
                
                if bandeira not in ['BIG', 'ULTRA']:
                    break

                if not Loja.query.filter_by(codigo=codigo).first():
                    nome = codigo.split(' - ', 1)[1] if ' - ' in codigo else codigo
                    loja = Loja(codigo=codigo, nome=nome, bandeira=bandeira)
                    db.session.add(loja)
                    lojas_criadas += 1
                else:
                    lojas_existentes += 1
                    
            db.session.commit()
            print(f"✓ Lojas criadas: {lojas_criadas}")
            print(f"✓ Lojas já existentes: {lojas_existentes}")
            
        except Exception as e:
            print(f"❌ Erro ao carregar lojas: {e}")
            db.session.rollback()
            return

        print("✅ Inicialização do banco de dados concluída com sucesso!")

    return app

# Cria a aplicação
app = create_app(os.getenv('FLASK_ENV') or 'default')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 