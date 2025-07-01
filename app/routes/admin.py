from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Usuario, Loja, SorteioSemanal, SorteioColaborador, Colaborador, Premio
from app.forms.admin import SorteioSemanalForm, UsuarioForm, PremioForm
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
    # Estatísticas gerais
    total_lojas = Loja.query.filter_by(ativo=True).count()
    total_usuarios = Usuario.query.filter_by(tipo='assistente', ativo=True).count()
    total_colaboradores = Colaborador.query.filter_by(apto=True).count()
    
    # Sorteio atual
    sorteio_atual = SorteioSemanal.query.order_by(SorteioSemanal.semana_inicio.desc()).first()
    
    # Sorteios de colaboradores desta semana
    colaboradores_sorteados = []
    if sorteio_atual:
        colaboradores_sorteados = SorteioColaborador.query.filter_by(
            sorteio_semanal_id=sorteio_atual.id
        ).order_by(SorteioColaborador.data_sorteio.desc()).all()
    
    # Prêmios ativos
    premios_ativos = Premio.query.filter_by(ativo=True).count()
    
    # Sorteios recentes para o dashboard
    sorteios_recentes = SorteioSemanal.query.order_by(SorteioSemanal.semana_inicio.desc()).limit(5).all()
    
    # Contadores de sorteios de colaboradores por sorteio semanal
    sorteios_colaboradores_count = {}
    for sorteio in sorteios_recentes:
        count = SorteioColaborador.query.filter_by(sorteio_semanal_id=sorteio.id).count()
        sorteios_colaboradores_count[sorteio.id] = count
    
    return render_template('admin/dashboard.html',
                         total_lojas=total_lojas,
                         total_usuarios=total_usuarios,
                         total_colaboradores=total_colaboradores,
                         sorteio_atual=sorteio_atual,
                         colaboradores_sorteados=colaboradores_sorteados,
                         premios_ativos=premios_ativos,
                         sorteios_recentes=sorteios_recentes,
                         sorteios_colaboradores_count=sorteios_colaboradores_count)

@admin_bp.route('/sortear', methods=['GET', 'POST'])
@admin_required
def sortear_lojas():
    """Sorteia lojas semanalmente"""
    form = SorteioSemanalForm()
    
    if form.validate_on_submit():
        semana_inicio = form.semana_inicio.data
        
        # Verifica se já existe sorteio para esta semana
        sorteio_existente = SorteioSemanal.query.filter_by(semana_inicio=semana_inicio).first()
        if sorteio_existente:
            flash(f'Já existe sorteio para a semana de {semana_inicio.strftime("%d/%m/%Y")}!', 'warning')
            return render_template('admin/sortear.html', form=form)
        
        # Busca lojas ativas
        lojas_big = Loja.query.filter_by(bandeira='BIG', ativo=True).all()
        lojas_ultra = Loja.query.filter_by(bandeira='ULTRA', ativo=True).all()
        
        if not lojas_big or not lojas_ultra:
            flash('Não há lojas suficientes para o sorteio!', 'danger')
            return render_template('admin/sortear.html', form=form)
        
        # Sorteia uma loja de cada bandeira
        loja_big_sorteada = random.choice(lojas_big)
        loja_ultra_sorteada = random.choice(lojas_ultra)
        
        # Cria o sorteio
        sorteio = SorteioSemanal(
            semana_inicio=semana_inicio,
            loja_big_id=loja_big_sorteada.id,
            loja_ultra_id=loja_ultra_sorteada.id,
            sorteado_por=current_user.id
        )
        
        db.session.add(sorteio)
        db.session.commit()
        
        flash(f'Sorteio realizado! Lojas sorteadas: {loja_big_sorteada.nome} (BIG) e {loja_ultra_sorteada.nome} (ULTRA)', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/sortear.html', form=form)

@admin_bp.route('/usuarios')
@admin_required
def usuarios():
    """Lista usuários assistentes"""
    usuarios = Usuario.query.filter_by(tipo='assistente').order_by(Usuario.nome).all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuarios/novo', methods=['GET', 'POST'])
@admin_required
def novo_usuario():
    """Criar novo usuário assistente"""
    form = UsuarioForm()
    
    # Popula lojas disponíveis
    lojas = Loja.query.filter_by(ativo=True).order_by(Loja.nome).all()
    form.loja_id.choices = [(0, 'Selecione uma loja')] + [(l.id, f"{l.codigo} - {l.nome}") for l in lojas]
    
    if form.validate_on_submit():
        # Verifica se email já existe
        usuario_existente = Usuario.query.filter_by(email=form.email.data).first()
        if usuario_existente:
            flash('Este email já está cadastrado!', 'danger')
            return render_template('admin/usuario_form.html', form=form, titulo='Novo Usuário')
        
        if not form.password.data:
            flash('Senha é obrigatória para novo usuário!', 'danger')
            return render_template('admin/usuario_form.html', form=form, titulo='Novo Usuário')
        
        usuario = Usuario(
            nome=form.nome.data,
            email=form.email.data,
            tipo='assistente',
            loja_id=form.loja_id.data if form.loja_id.data > 0 else None,
            ativo=True
        )
        usuario.set_password(form.password.data)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash(f'Usuário {usuario.nome} criado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/usuario_form.html', form=form, titulo='Novo Usuário')

@admin_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_usuario(id):
    """Editar usuário assistente"""
    usuario = Usuario.query.filter_by(id=id, tipo='assistente').first_or_404()
    
    form = UsuarioForm(obj=usuario)
    
    # Popula lojas disponíveis
    lojas = Loja.query.filter_by(ativo=True).order_by(Loja.nome).all()
    form.loja_id.choices = [(0, 'Selecione uma loja')] + [(l.id, f"{l.codigo} - {l.nome}") for l in lojas]
    
    if form.validate_on_submit():
        # Verifica se email já existe (exceto o próprio)
        usuario_existente = Usuario.query.filter_by(email=form.email.data).filter(Usuario.id != id).first()
        if usuario_existente:
            flash('Este email já está cadastrado por outro usuário!', 'danger')
            return render_template('admin/usuario_form.html', form=form, titulo='Editar Usuário')
        
        usuario.nome = form.nome.data
        usuario.email = form.email.data
        usuario.loja_id = form.loja_id.data if form.loja_id.data > 0 else None
        
        # Atualiza senha apenas se fornecida
        if form.password.data:
            usuario.set_password(form.password.data)
        
        db.session.commit()
        
        flash(f'Usuário {usuario.nome} atualizado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/usuario_form.html', form=form, titulo='Editar Usuário')

@admin_bp.route('/usuarios/<int:id>/toggle')
@admin_required
def toggle_usuario(id):
    """Ativar/desativar usuário"""
    usuario = Usuario.query.filter_by(id=id, tipo='assistente').first_or_404()
    
    usuario.ativo = not usuario.ativo
    db.session.commit()
    
    status = 'ativado' if usuario.ativo else 'desativado'
    flash(f'Usuário {usuario.nome} foi {status}.', 'success')
    
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/usuarios/<int:id>/excluir')
@admin_required
def excluir_usuario(id):
    """Excluir usuário assistente"""
    usuario = Usuario.query.filter_by(id=id, tipo='assistente').first_or_404()
    
    nome = usuario.nome
    db.session.delete(usuario)
    db.session.commit()
    
    flash(f'Usuário {nome} foi excluído com sucesso.', 'success')
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/premios')
@admin_required
def premios():
    """Lista prêmios"""
    premios = Premio.query.order_by(Premio.data_evento.desc(), Premio.nome).all()
    return render_template('admin/premios.html', premios=premios)

@admin_bp.route('/premios/novo', methods=['GET', 'POST'])
@admin_required
def novo_premio():
    """Criar novo prêmio"""
    form = PremioForm()
    
    # Popula lojas ganhadoras (apenas lojas que foram sorteadas)
    lojas_ganhadoras = []
    sorteios_ativos = SorteioSemanal.query.order_by(SorteioSemanal.semana_inicio.desc()).all()
    for sorteio in sorteios_ativos:
        if sorteio.loja_big not in [l[1] for l in lojas_ganhadoras]:
            lojas_ganhadoras.append((sorteio.loja_big.id, f"{sorteio.loja_big.codigo} - {sorteio.loja_big.nome} (BIG)"))
        if sorteio.loja_ultra not in [l[1] for l in lojas_ganhadoras]:
            lojas_ganhadoras.append((sorteio.loja_ultra.id, f"{sorteio.loja_ultra.codigo} - {sorteio.loja_ultra.nome} (ULTRA)"))
    
    form.loja_id.choices = [(0, 'Disponível para todas as lojas ganhadoras')] + lojas_ganhadoras
    
    if form.validate_on_submit():
        premio = Premio(
            nome=form.nome.data,
            descricao=form.descricao.data,
            data_evento=form.data_evento.data,
            tipo=form.tipo.data,
            loja_id=form.loja_id.data if form.loja_id.data > 0 else None,
            criado_por=current_user.id,
            ativo=True
        )
        
        db.session.add(premio)
        db.session.commit()
        
        flash(f'Prêmio "{premio.nome}" criado com sucesso!', 'success')
        return redirect(url_for('admin.premios'))
    
    return render_template('admin/premio_form.html', form=form, titulo='Novo Prêmio')

@admin_bp.route('/premios/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_premio(id):
    """Editar prêmio"""
    premio = Premio.query.get_or_404(id)
    
    form = PremioForm(obj=premio)
    
    # Popula lojas ganhadoras (apenas lojas que foram sorteadas)
    lojas_ganhadoras = []
    sorteios_ativos = SorteioSemanal.query.order_by(SorteioSemanal.semana_inicio.desc()).all()
    for sorteio in sorteios_ativos:
        if sorteio.loja_big not in [l[1] for l in lojas_ganhadoras]:
            lojas_ganhadoras.append((sorteio.loja_big.id, f"{sorteio.loja_big.codigo} - {sorteio.loja_big.nome} (BIG)"))
        if sorteio.loja_ultra not in [l[1] for l in lojas_ganhadoras]:
            lojas_ganhadoras.append((sorteio.loja_ultra.id, f"{sorteio.loja_ultra.codigo} - {sorteio.loja_ultra.nome} (ULTRA)"))
    
    form.loja_id.choices = [(0, 'Disponível para todas as lojas ganhadoras')] + lojas_ganhadoras
    
    if form.validate_on_submit():
        premio.nome = form.nome.data
        premio.descricao = form.descricao.data
        premio.data_evento = form.data_evento.data
        premio.tipo = form.tipo.data
        premio.loja_id = form.loja_id.data if form.loja_id.data > 0 else None
        
        db.session.commit()
        
        flash(f'Prêmio "{premio.nome}" atualizado com sucesso!', 'success')
        return redirect(url_for('admin.premios'))
    
    return render_template('admin/premio_form.html', form=form, titulo='Editar Prêmio')

@admin_bp.route('/premios/<int:id>/toggle')
@admin_required
def toggle_premio(id):
    """Ativar/desativar prêmio"""
    premio = Premio.query.get_or_404(id)
    
    premio.ativo = not premio.ativo
    db.session.commit()
    
    status = 'ativado' if premio.ativo else 'desativado'
    flash(f'Prêmio "{premio.nome}" foi {status}.', 'success')
    
    return redirect(url_for('admin.premios'))

@admin_bp.route('/sorteios')
@admin_required
def sorteios():
    """Lista todos os sorteios realizados"""
    # Sorteios semanais
    sorteios_semanais = SorteioSemanal.query.order_by(SorteioSemanal.semana_inicio.desc()).all()
    
    # Sorteios de colaboradores
    sorteios_colaboradores = SorteioColaborador.query.order_by(SorteioColaborador.data_sorteio.desc()).all()
    
    return render_template('admin/sorteios.html', 
                         sorteios_semanais=sorteios_semanais,
                         sorteios_colaboradores=sorteios_colaboradores)

@admin_bp.route('/sorteios/semanal/<int:id>/excluir')
@admin_required
def excluir_sorteio_semanal(id):
    """Excluir sorteio semanal e todos os sorteios de colaboradores associados"""
    sorteio = SorteioSemanal.query.get_or_404(id)
    
    # Exclui sorteios de colaboradores associados
    SorteioColaborador.query.filter_by(sorteio_semanal_id=id).delete()
    
    # Exclui o sorteio semanal
    semana = sorteio.semana_inicio.strftime('%d/%m/%Y')
    db.session.delete(sorteio)
    db.session.commit()
    
    flash(f'Sorteio da semana de {semana} foi excluído com sucesso.', 'success')
    return redirect(url_for('admin.sorteios'))

@admin_bp.route('/sorteios/colaborador/<int:id>/excluir')
@admin_required
def excluir_sorteio_colaborador(id):
    """Excluir sorteio específico de colaborador"""
    sorteio = SorteioColaborador.query.get_or_404(id)
    
    colaborador_nome = sorteio.colaborador.nome
    premio_nome = sorteio.premio.nome
    
    db.session.delete(sorteio)
    db.session.commit()
    
    flash(f'Sorteio de {colaborador_nome} para "{premio_nome}" foi excluído com sucesso.', 'success')
    return redirect(url_for('admin.sorteios')) 