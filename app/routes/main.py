from flask import Blueprint, render_template
from app.models import SorteioSemanal, SorteioColaborador, Loja
from datetime import datetime, timedelta
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial - Mostra resultados dos sorteios"""
    # Busca o sorteio mais recente
    sorteio_atual = SorteioSemanal.query.order_by(desc(SorteioSemanal.semana_inicio)).first()
    
    # Busca histórico das últimas 4 semanas
    historico = SorteioSemanal.query.order_by(desc(SorteioSemanal.semana_inicio)).limit(4).all()
    
    # Se houver sorteio atual, busca os colaboradores sorteados
    colaboradores_sorteados = []
    if sorteio_atual:
        colaboradores_sorteados = SorteioColaborador.query.filter_by(
            sorteio_semanal_id=sorteio_atual.id
        ).order_by(SorteioColaborador.dia_evento).all()
    
    return render_template('index.html', 
                         sorteio_atual=sorteio_atual,
                         colaboradores_sorteados=colaboradores_sorteados,
                         historico=historico)

@main_bp.route('/sobre')
def sobre():
    """Página sobre o projeto"""
    return render_template('sobre.html')

@main_bp.route('/historico')
def historico():
    """Página com histórico completo de sorteios"""
    # Busca todos os sorteios com paginação
    page = 1  # Por enquanto sem paginação
    sorteios = SorteioSemanal.query.order_by(desc(SorteioSemanal.semana_inicio)).all()
    
    return render_template('historico.html', sorteios=sorteios) 