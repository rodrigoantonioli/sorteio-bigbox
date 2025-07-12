from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models import SorteioSemanal, SorteioColaborador, Loja, Colaborador
from datetime import datetime, timedelta
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

def format_date_pt_br(d):
    """Formata uma data para o padrão brasileiro, ex: '07 de Julho de 2025'."""
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    return f"{d.day:02d} de {meses[d.month - 1]} de {d.year}"

def formatar_intervalo_semana(data_base):
    """Calcula e formata o intervalo da semana (seg-dom) de uma data."""
    inicio_semana = data_base - timedelta(days=data_base.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    if inicio_semana.month == fim_semana.month:
        return f"{inicio_semana.day:02d} a {fim_semana.day:02d} de {meses[fim_semana.month - 1]} de {fim_semana.year}"
    else:
        return f"{inicio_semana.day:02d} de {meses[inicio_semana.month - 1]} a {fim_semana.day:02d} de {meses[fim_semana.month - 1]} de {fim_semana.year}"

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
    todos_sorteios_semanais = SorteioSemanal.query.order_by(desc(SorteioSemanal.semana_inicio)).all()
    
    # Separa o sorteio atual (se existir) do histórico
    sorteio_atual_dados = None
    historico_semanal = []
    
    if todos_sorteios_semanais:
        # Pega o primeiro como o sorteio da semana atual
        semana_atual = todos_sorteios_semanais[0]
        vencedores_big_atual = SorteioColaborador.query.join(Colaborador).filter(SorteioColaborador.sorteio_semanal_id == semana_atual.id, Colaborador.loja_id == semana_atual.loja_big_id).all()
        vencedores_ultra_atual = SorteioColaborador.query.join(Colaborador).filter(SorteioColaborador.sorteio_semanal_id == semana_atual.id, Colaborador.loja_id == semana_atual.loja_ultra_id).all()
        
        sorteio_atual_dados = {
            'intervalo_semana': formatar_intervalo_semana(semana_atual.semana_inicio),
            'loja_big': semana_atual.loja_big,
            'loja_ultra': semana_atual.loja_ultra,
            'vencedores_big': vencedores_big_atual,
            'vencedores_ultra': vencedores_ultra_atual
        }
        
        # Pega o restante como histórico
        historico_semanal_bruto = todos_sorteios_semanais[1:]
        for sorteio in historico_semanal_bruto:
            vencedores_big = SorteioColaborador.query.join(Colaborador).filter(
                SorteioColaborador.sorteio_semanal_id == sorteio.id,
                Colaborador.loja_id == sorteio.loja_big_id
            ).all()
            vencedores_ultra = SorteioColaborador.query.join(Colaborador).filter(
                SorteioColaborador.sorteio_semanal_id == sorteio.id,
                Colaborador.loja_id == sorteio.loja_ultra_id
            ).all()
            historico_semanal.append({
                'intervalo_semana': formatar_intervalo_semana(sorteio.semana_inicio),
                'loja_big': sorteio.loja_big,
                'loja_ultra': sorteio.loja_ultra,
                'vencedores_big': vencedores_big,
                'vencedores_ultra': vencedores_ultra
            })

        # Se houver apenas um sorteio, inclui o atual no histórico
        if len(todos_sorteios_semanais) == 1:
            historico_semanal.append(sorteio_atual_dados)

    return render_template('index.html',
                         sorteio_da_semana=sorteio_atual_dados,
                         historico_semanal=historico_semanal) 