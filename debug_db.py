#!/usr/bin/env python3
"""
Script de debug para testar configuração do banco de dados
"""
import os

def test_database_config():
    """Testa a configuração do banco de dados"""
    print("=== TESTE DE CONFIGURAÇÃO DO BANCO DE DADOS ===\n")
    
    # Define variáveis de ambiente ANTES de importar
    os.environ['FLASK_ENV'] = 'production'
    # URL externa do Render (baseada no padrão database_id.region-postgres.render.com)
    os.environ['DATABASE_URL'] = 'postgresql://sorteio_user:H5J1zDHbUZIRy5IU0G2pLtRYRoB8hWpH@dpg-d1hmdj7fte5s73ae0eag-a.oregon-postgres.render.com/sorteio_bigbox'
    os.environ['ADMIN_EMAIL'] = 'admin@bigbox.com'
    os.environ['ADMIN_PASSWORD'] = 'BigBox2025!'
    
    # Agora importa depois de definir as variáveis
    from run import create_app
    from app.extensions import db
    from app.models import Usuario, Loja
    
    app = create_app('production')
    
    with app.app_context():
        print(f"Environment: {os.environ.get('FLASK_ENV')}")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Admin Email: {app.config.get('ADMIN_EMAIL')}")
        print(f"Admin Password: {'*' * len(app.config.get('ADMIN_PASSWORD', ''))}")
        print()
        
        try:
            # Testa conexão
            print("🔍 Testando conexão com PostgreSQL...")
            with db.engine.connect() as conn:
                result = conn.execute(db.text('SELECT version()'))
                version = result.fetchone()[0]
                print(f"✓ Conectado ao PostgreSQL: {version[:50]}...")
            
            # Testa criação de tabelas
            print("\n🔍 Testando criação de tabelas...")
            db.create_all()
            print("✓ Tabelas criadas com sucesso!")
            
            # Lista tabelas existentes
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✓ Tabelas no banco: {tables}")
            
            # Testa inserção de dados
            print("\n🔍 Testando inserção de dados...")
            
            # Cria admin se não existir
            admin = Usuario.query.filter_by(email='admin@bigbox.com').first()
            if not admin:
                admin = Usuario(
                    email='admin@bigbox.com',
                    nome='Administrador',
                    tipo='admin'
                )
                admin.set_password('BigBox2025!')
                db.session.add(admin)
                db.session.commit()
                print("✓ Admin criado!")
            else:
                print("✓ Admin já existe!")
            
            # Testa carregamento de lojas
            total_lojas_antes = Loja.query.count()
            print(f"✓ Lojas existentes antes: {total_lojas_antes}")
            
            # Carrega lojas do Excel se necessário
            if total_lojas_antes == 0:
                print("🔍 Carregando lojas do Excel...")
                import openpyxl
                excel_path = os.path.join(os.path.dirname(__file__), 'inputs', 'TABELA LOJAS.xlsx')
                
                if os.path.exists(excel_path):
                    workbook = openpyxl.load_workbook(excel_path)
                    sheet = workbook.active
                    lojas_criadas = 0
                    
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
                            
                    workbook.close()
                    db.session.commit()
                    print(f"✓ Lojas criadas: {lojas_criadas}")
            
            # Conta registros finais
            total_usuarios = Usuario.query.count()
            total_lojas = Loja.query.count()
            print(f"✓ Total de usuários: {total_usuarios}")
            print(f"✓ Total de lojas: {total_lojas}")
            
            print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
            print("✅ O banco PostgreSQL está funcionando perfeitamente!")
            print("✅ Você pode fazer o deploy no Render agora!")
            
        except Exception as e:
            print(f"\n❌ ERRO NO TESTE: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_database_config() 