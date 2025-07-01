from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models import SorteioSemanal, SorteioColaborador, Loja
from datetime import datetime, timedelta
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial - Redireciona usuários logados para dashboard ou mostra vitrine"""
    # Se o usuário estiver logado, redireciona para seu dashboard
    if current_user.is_authenticated:
        if current_user.tipo == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('manager.dashboard'))
    
    # Para usuários não logados, mostra a página completa do festival
    # Busca o sorteio mais recente
    sorteio_atual = SorteioSemanal.query.order_by(desc(SorteioSemanal.semana_inicio)).first()
    
    # Busca TODOS os sorteios para histórico completo
    todos_sorteios = SorteioSemanal.query.order_by(desc(SorteioSemanal.semana_inicio)).all()
    
    # Se houver sorteio atual, busca os colaboradores sorteados
    colaboradores_sorteados = []
    if sorteio_atual:
        colaboradores_sorteados = SorteioColaborador.query.filter_by(
            sorteio_semanal_id=sorteio_atual.id
        ).order_by(SorteioColaborador.data_sorteio.desc()).all()
    
    # Busca todos os colaboradores sorteados de todos os sorteios
    todos_colaboradores = SorteioColaborador.query.order_by(SorteioColaborador.data_sorteio.desc()).all()
    
    return render_template('index.html', 
                         sorteio_atual=sorteio_atual,
                         colaboradores_sorteados=colaboradores_sorteados,
                         todos_sorteios=todos_sorteios,
                         todos_colaboradores=todos_colaboradores)

@main_bp.route('/festival')
def festival():
    """Página festival - Sempre mostra os resultados dos sorteios (mesmo para usuários logados)"""
    # Busca o sorteio mais recente
    sorteio_atual = SorteioSemanal.query.order_by(desc(SorteioSemanal.semana_inicio)).first()
    
    # Busca TODOS os sorteios para histórico completo (sem limite)
    todos_sorteios = SorteioSemanal.query.order_by(desc(SorteioSemanal.semana_inicio)).all()
    
    # Se houver sorteio atual, busca os colaboradores sorteados
    colaboradores_sorteados = []
    if sorteio_atual:
        colaboradores_sorteados = SorteioColaborador.query.filter_by(
            sorteio_semanal_id=sorteio_atual.id
        ).order_by(SorteioColaborador.data_sorteio.desc()).all()
    
    # Busca todos os colaboradores sorteados de todos os sorteios para estatísticas
    todos_colaboradores = SorteioColaborador.query.order_by(SorteioColaborador.data_sorteio.desc()).all()
    
    return render_template('index.html', 
                         sorteio_atual=sorteio_atual,
                         colaboradores_sorteados=colaboradores_sorteados,
                         todos_sorteios=todos_sorteios,
                         todos_colaboradores=todos_colaboradores)

@main_bp.route('/sobre')
def sobre():
    """Página sobre o projeto"""
    return render_template('sobre.html') 