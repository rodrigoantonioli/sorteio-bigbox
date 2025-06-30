from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Usuario
from app.forms.auth import LoginForm
from app.extensions import login_manager

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    """Carrega usuário para o Flask-Login"""
    return Usuario.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        # Redireciona baseado no tipo de usuário
        if current_user.tipo == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('manager.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Busca usuário
        usuario = Usuario.query.filter_by(email=form.email.data, ativo=True).first()
        
        if usuario and usuario.check_password(form.password.data):
            login_user(usuario, remember=form.remember_me.data)
            
            # Redireciona para página solicitada ou dashboard apropriado
            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('admin.dashboard') if usuario.tipo == 'admin' else url_for('manager.dashboard')
            
            flash(f'Bem-vindo, {usuario.nome}!', 'success')
            return redirect(next_page)
        else:
            flash('Email ou senha incorretos.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('main.index')) 