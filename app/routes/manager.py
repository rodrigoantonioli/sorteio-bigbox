from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models import db, Colaborador, SorteioSemanal, SorteioColaborador
from app.forms.manager import UploadColaboradoresForm, SorteioColaboradorForm
from datetime import datetime, date, timedelta
from functools import wraps
import os
import random

manager_bp = Blueprint('manager', __name__)

def manager_required(f):
    """Decorator para verificar se usuário é gerente"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.tipo != 'gerente':
            flash('Acesso negado. Apenas gerentes.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Verifica se arquivo é permitido"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@manager_bp.route('/dashboard')
@manager_required
def dashboard():
    """Dashboard do gerente"""
    if not current_user.loja:
        flash('Você não está associado a nenhuma loja. Contate o administrador.', 'warning')
        return redirect(url_for('main.index'))
    
    # Verifica se a loja foi sorteada esta semana
    sorteio_atual = SorteioSemanal.query.order_by(SorteioSemanal.semana_inicio.desc()).first()
    loja_sorteada = False
    colaboradores_sorteados = []
    
    if sorteio_atual:
        # Verifica se a loja do gerente foi sorteada
        if (current_user.loja_id == sorteio_atual.loja_big_id or 
            current_user.loja_id == sorteio_atual.loja_ultra_id):
            loja_sorteada = True
            
            # Busca colaboradores já sorteados
            colaboradores_sorteados = SorteioColaborador.query.join(
                Colaborador
            ).filter(
                SorteioColaborador.sorteio_semanal_id == sorteio_atual.id,
                Colaborador.loja_id == current_user.loja_id
            ).all()
    
    # Estatísticas da loja
    total_colaboradores = Colaborador.query.filter_by(
        loja_id=current_user.loja_id,
        apto=True
    ).count()
    
    return render_template('manager/dashboard.html',
                         loja=current_user.loja,
                         loja_sorteada=loja_sorteada,
                         sorteio_atual=sorteio_atual,
                         colaboradores_sorteados=colaboradores_sorteados,
                         total_colaboradores=total_colaboradores)

@manager_bp.route('/colaboradores')
@manager_required
def colaboradores():
    """Lista colaboradores da loja"""
    if not current_user.loja:
        flash('Você não está associado a nenhuma loja.', 'warning')
        return redirect(url_for('main.index'))
    
    colaboradores = Colaborador.query.filter_by(
        loja_id=current_user.loja_id
    ).order_by(Colaborador.nome).all()
    
    return render_template('manager/colaboradores.html', 
                         colaboradores=colaboradores,
                         loja=current_user.loja)

@manager_bp.route('/colaboradores/upload', methods=['GET', 'POST'])
@manager_required
def upload_colaboradores():
    """Upload de planilha de colaboradores"""
    flash('Funcionalidade de upload temporariamente desabilitada.', 'info')
    return redirect(url_for('manager.colaboradores'))

@manager_bp.route('/sortear', methods=['GET', 'POST'])
@manager_required
def sortear_colaboradores():
    """Sorteia colaboradores para os ingressos"""
    if not current_user.loja:
        flash('Você não está associado a nenhuma loja.', 'warning')
        return redirect(url_for('main.index'))
    
    # Verifica se a loja foi sorteada
    sorteio_atual = SorteioSemanal.query.order_by(SorteioSemanal.semana_inicio.desc()).first()
    
    if not sorteio_atual or (current_user.loja_id != sorteio_atual.loja_big_id and 
                           current_user.loja_id != sorteio_atual.loja_ultra_id):
        flash('Sua loja não foi sorteada esta semana.', 'info')
        return redirect(url_for('manager.dashboard'))
    
    # Verifica se já houve sorteio
    ja_sorteado = SorteioColaborador.query.join(
        Colaborador
    ).filter(
        SorteioColaborador.sorteio_semanal_id == sorteio_atual.id,
        Colaborador.loja_id == current_user.loja_id
    ).first()
    
    if ja_sorteado:
        flash('O sorteio já foi realizado para sua loja esta semana.', 'warning')
        return redirect(url_for('manager.dashboard'))
    
    form = SorteioColaboradorForm()
    
    if form.validate_on_submit():
        # Busca colaboradores aptos
        colaboradores_aptos = Colaborador.query.filter_by(
            loja_id=current_user.loja_id,
            apto=True
        ).all()
        
        if len(colaboradores_aptos) < form.quantidade_ingressos.data:
            flash(f'Não há colaboradores suficientes. Disponíveis: {len(colaboradores_aptos)}', 'warning')
            return render_template('manager/sortear.html', form=form)
        
        # Realiza o sorteio
        sorteados = random.sample(colaboradores_aptos, form.quantidade_ingressos.data)
        
        # Registra os sorteados
        for colaborador in sorteados:
            sorteio = SorteioColaborador(
                sorteio_semanal_id=sorteio_atual.id,
                colaborador_id=colaborador.id,
                tipo_ingresso=form.tipo_ingresso.data,
                dia_evento=form.dia_evento.data,
                sorteado_por=current_user.id
            )
            db.session.add(sorteio)
        
        db.session.commit()
        
        flash(f'Sorteio realizado com sucesso! {len(sorteados)} colaboradores sorteados.', 'success')
        return redirect(url_for('manager.dashboard'))
    
    # Define data padrão baseada no dia da semana
    hoje = date.today()
    if hoje.weekday() < 4:  # Segunda a Quinta
        form.dia_evento.data = hoje + timedelta(days=(4-hoje.weekday()))  # Próxima sexta
    else:
        form.dia_evento.data = hoje
    
    return render_template('manager/sortear.html', form=form) 