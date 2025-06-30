"""
Script para carregar as lojas do arquivo Excel para o banco de dados
"""
import openpyxl
from run import create_app
from app.models import Loja
from app.extensions import db
import os

def load_stores_from_excel():
    """Carrega as lojas do arquivo Excel usando openpyxl"""
    app = create_app()
    
    with app.app_context():
        excel_path = os.path.join('inputs', 'TABELA LOJAS.xlsx')
        
        if not os.path.exists(excel_path):
            print(f"Erro: Arquivo {excel_path} não encontrado!")
            return
        
        try:
            workbook = openpyxl.load_workbook(excel_path)
            sheet = workbook.active
            
            lojas_criadas = 0
            lojas_atualizadas = 0
            
            # Pula o cabeçalho
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row or row[0] is None or row[1] is None:
                    continue

                codigo = str(row[0]).strip()
                bandeira = str(row[1]).strip().upper()
                
                if bandeira not in ['BIG', 'ULTRA']:
                    print(f"Aviso: Bandeira inválida '{bandeira}' para loja {codigo}")
                    continue
                
                loja = Loja.query.filter_by(codigo=codigo).first()
                
                if loja:
                    loja.bandeira = bandeira
                    loja.ativo = True
                    lojas_atualizadas += 1
                else:
                    nome_parts = codigo.split(' - ', 1)
                    nome = nome_parts[1] if len(nome_parts) > 1 else codigo
                    
                    loja = Loja(
                        codigo=codigo,
                        nome=nome,
                        bandeira=bandeira,
                        ativo=True
                    )
                    db.session.add(loja)
                    lojas_criadas += 1
            
            db.session.commit()
            
            print(f"\nResumo da importação:")
            print(f"- Lojas criadas: {lojas_criadas}")
            print(f"- Lojas atualizadas: {lojas_atualizadas}")
            print(f"- Total de lojas no sistema: {Loja.query.count()}")
            
            lojas_big = Loja.query.filter_by(bandeira='BIG', ativo=True).count()
            lojas_ultra = Loja.query.filter_by(bandeira='ULTRA', ativo=True).count()
            
            print(f"\nLojas por bandeira:")
            print(f"- BIG: {lojas_big}")
            print(f"- ULTRA: {lojas_ultra}")
            
        except Exception as e:
            print(f"Erro ao processar arquivo Excel: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    load_stores_from_excel() 