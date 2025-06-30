from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Usuario, Loja, SorteioSemanal, SorteioColaborador, Colaborador
from app.forms.admin import SorteioSemanalForm, UsuarioForm
from datetime import datetime, date, timedelta
from functools import wraps
import random

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator para verificar se usuário é admin"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.tipo != 'admin':
            flash('Acesso negado. Apenas administradores.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Dashboard do administrador"""
    # Estatísticas
    total_lojas = Loja.query.filter_by(ativo=True).count()
    total_lojas_big = Loja.query.filter_by(bandeira='BIG', ativo=True).count()
    total_lojas_ultra = Loja.query.filter_by(bandeira='ULTRA', ativo=True).count()
    total_gerentes = Usuario.query.filter_by(tipo='gerente', ativo=True).count()
    
    # Último sorteio
    ultimo_sorteio = SorteioSemanal.query.order_by(SorteioSemanal.semana_inicio.desc()).first()
    
    # Próxima semana (próxima terça-feira)
    hoje = date.today()
    dias_ate_terca = (1 - hoje.weekday()) % 7  # 1 = terça-feira
    if dias_ate_terca == 0:  # Se hoje é terça
        dias_ate_terca = 7
    proxima_semana = hoje + timedelta(days=dias_ate_terca)
    
    return render_template('admin/dashboard.html',
                         total_lojas=total_lojas,
                         total_lojas_big=total_lojas_big,
                         total_lojas_ultra=total_lojas_ultra,
                         total_gerentes=total_gerentes,
                         ultimo_sorteio=ultimo_sorteio,
                         proxima_semana=proxima_semana)

@admin_bp.route('/sortear', methods=['GET', 'POST'])
@admin_required
def sortear():
    """Realiza sorteio semanal de lojas"""
    form = SorteioSemanalForm()
    
    if form.validate_on_submit():
        # Verifica se já existe sorteio para esta semana
        sorteio_existente = SorteioSemanal.query.filter_by(
            semana_inicio=form.semana_inicio.data
        ).first()
        
        if sorteio_existente:
            flash('Já existe um sorteio para esta semana!', 'warning')
            return redirect(url_for('admin.dashboard'))
        
        # Busca lojas ativas
        lojas_big = Loja.query.filter_by(bandeira='BIG', ativo=True).all()
        lojas_ultra = Loja.query.filter_by(bandeira='ULTRA', ativo=True).all()
        
        if not lojas_big or not lojas_ultra:
            flash('Não há lojas suficientes para realizar o sorteio!', 'danger')
            return redirect(url_for('admin.dashboard'))
        
        # Realiza o sorteio
        loja_big_sorteada = random.choice(lojas_big)
        loja_ultra_sorteada = random.choice(lojas_ultra)
        
        # Cria registro do sorteio
        sorteio = SorteioSemanal(
            semana_inicio=form.semana_inicio.data,
            loja_big_id=loja_big_sorteada.id,
            loja_ultra_id=loja_ultra_sorteada.id,
            sorteado_por=current_user.id
        )
        
        db.session.add(sorteio)
        db.session.commit()
        
        flash(f'Sorteio realizado com sucesso! BIG: {loja_big_sorteada.nome} | ULTRA: {loja_ultra_sorteada.nome}', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/sortear.html', form=form)

@admin_bp.route('/usuarios')
@admin_required
def usuarios():
    """Lista de usuários (gerentes)"""
    usuarios = Usuario.query.filter_by(tipo='gerente').order_by(Usuario.nome).all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuarios/novo', methods=['GET', 'POST'])
@admin_required
def novo_usuario():
    """Criar novo usuário gerente"""
    form = UsuarioForm()
    
    # Popula choices do select de lojas
    form.loja_id.choices = [(0, 'Selecione uma loja')] + [
        (l.id, f'{l.codigo} - {l.nome}') for l in Loja.query.filter_by(ativo=True).order_by(Loja.nome).all()
    ]
    
    if form.validate_on_submit():
        # Verifica se email já existe
        if Usuario.query.filter_by(email=form.email.data).first():
            flash('Este email já está cadastrado!', 'danger')
            return render_template('admin/usuario_form.html', form=form, titulo='Novo Gerente')
        
        # Cria novo usuário
        usuario = Usuario(
            email=form.email.data,
            nome=form.nome.data,
            tipo='gerente',
            loja_id=form.loja_id.data if form.loja_id.data != 0 else None,
            ativo=True
        )
        usuario.set_password(form.password.data)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash(f'Gerente {usuario.nome} criado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/usuario_form.html', form=form, titulo='Novo Gerente')

@admin_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_usuario(id):
    """Editar usuário gerente"""
    usuario = Usuario.query.get_or_404(id)
    
    if usuario.tipo == 'admin':
        flash('Não é possível editar administradores por aqui.', 'warning')
        return redirect(url_for('admin.usuarios'))
    
    form = UsuarioForm(obj=usuario)
    
    # Popula choices do select de lojas
    form.loja_id.choices = [(0, 'Selecione uma loja')] + [
        (l.id, f'{l.codigo} - {l.nome}') for l in Loja.query.filter_by(ativo=True).order_by(Loja.nome).all()
    ]
    
    if form.validate_on_submit():
        usuario.nome = form.nome.data
        usuario.email = form.email.data
        usuario.loja_id = form.loja_id.data if form.loja_id.data != 0 else None
        
        # Só atualiza senha se foi fornecida
        if form.password.data:
            usuario.set_password(form.password.data)
        
        db.session.commit()
        flash(f'Gerente {usuario.nome} atualizado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    # Preenche o formulário com dados atuais
    form.loja_id.data = usuario.loja_id or 0
    
    return render_template('admin/usuario_form.html', form=form, titulo='Editar Gerente')

@admin_bp.route('/usuarios/<int:id>/toggle')
@admin_required
def toggle_usuario(id):
    """Ativa/desativa usuário"""
    usuario = Usuario.query.get_or_404(id)
    
    if usuario.tipo == 'admin':
        flash('Não é possível desativar administradores.', 'warning')
        return redirect(url_for('admin.usuarios'))
    
    usuario.ativo = not usuario.ativo
    db.session.commit()
    
    status = 'ativado' if usuario.ativo else 'desativado'
    flash(f'Usuário {usuario.nome} foi {status}.', 'success')
    
    return redirect(url_for('admin.usuarios')) 