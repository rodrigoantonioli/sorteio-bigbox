from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models import SorteioSemanal, SorteioColaborador, Loja, Colaborador
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
    
    # Para usuários não logados, processa os dados para a vitrine do festival
    return processar_dados_vitrine()

@main_bp.route('/festival')
def festival():
    """Página festival - Sempre mostra os resultados dos sorteios (mesmo para usuários logados)"""
    return processar_dados_vitrine()

@main_bp.route('/sobre')
def sobre():
    """Página sobre o projeto"""
    return render_template('sobre.html')

def processar_dados_vitrine():
    """Busca e organiza os dados para a página principal e de festival."""
    # Busca o sorteio mais recente para o destaque
    sorteio_atual = SorteioSemanal.query.order_by(desc(SorteioSemanal.semana_inicio)).first()

    # Monta o histórico completo
    historico_semanal = []
    sorteios_semanais = SorteioSemanal.query.order_by(desc(SorteioSemanal.semana_inicio)).all()

    for sorteio in sorteios_semanais:
        vencedores_big = SorteioColaborador.query.join(Colaborador).filter(
            SorteioColaborador.sorteio_semanal_id == sorteio.id,
            Colaborador.loja_id == sorteio.loja_big_id
        ).all()
        
        vencedores_ultra = SorteioColaborador.query.join(Colaborador).filter(
            SorteioColaborador.sorteio_semanal_id == sorteio.id,
            Colaborador.loja_id == sorteio.loja_ultra_id
        ).all()

        historico_semanal.append({
            'semana_inicio': sorteio.semana_inicio,
            'loja_big': sorteio.loja_big,
            'loja_ultra': sorteio.loja_ultra,
            'vencedores_big': vencedores_big,
            'vencedores_ultra': vencedores_ultra
        })

    return render_template('index.html',
                         sorteio_atual=sorteio_atual,
                         historico_semanal=historico_semanal) 