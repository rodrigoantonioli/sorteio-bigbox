from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from app.models import db, Usuario, Loja, SorteioSemanal, SorteioColaborador, Colaborador, Premio, SorteioInstagram, ParticipanteInstagram, ConfiguracaoInstagram
from app.forms.admin import SorteioSemanalForm, UsuarioForm, PremioForm, LojaForm, AtribuirPremioForm, SorteioInstagramForm, ConfiguracaoInstagramForm

# Formulário vazio apenas para proteção CSRF em ações de POST via link/botão
class CSRFProtectionForm(FlaskForm):
    pass
from app.utils import get_brazil_datetime, get_brazil_date, format_brazil_datetime, parse_instagram_comments, validar_arquivo_instagram
from datetime import datetime, date, timedelta
from functools import wraps
from werkzeug.utils import secure_filename
import random
import os
import glob
import uuid
import json
from sqlalchemy import func
from collections import namedtuple
from sqlalchemy.orm import joinedload

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorador para verificar se o usuário é admin"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo != 'admin':
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def cleanup_temp_files():
    """Remove arquivos temporários antigos da pasta uploads"""
    try:
        uploads_dir = 'uploads'
        if not os.path.exists(uploads_dir):
            return
        
        # Remove arquivos temporários com mais de 1 hora
        cutoff_time = datetime.now() - timedelta(hours=1)
        temp_files = glob.glob(os.path.join(uploads_dir, 'temp_colaboradores_*.xlsx'))
        
        for temp_file in temp_files:
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(temp_file))
                if file_time < cutoff_time:
                    os.remove(temp_file)
            except:
                pass  # Ignora erros individuais de arquivos
    except:
        pass  # Ignora erros gerais de limpeza

def safe_remove_file(filepath):
    """Remove arquivo de forma segura com fallback"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except PermissionError:
        # Se não conseguir remover imediatamente, agenda para remoção posterior
        import threading
        import time
        def remove_later():
            time.sleep(3)  # Aguarda 3 segundos
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass
        
        thread = threading.Thread(target=remove_later)
        thread.daemon = True
        thread.start()
        return False
    except Exception:
        return False

def allowed_image_file(filename):
    """Verifica se o arquivo de imagem é permitido"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png']

def save_premio_image(image_file):
    """Salva a imagem do prêmio e retorna o nome do arquivo"""
    # Verifica se é um objeto FileStorage válido
    if (image_file and 
        hasattr(image_file, 'filename') and 
        image_file.filename and 
        allowed_image_file(image_file.filename)):
        
        # Gera nome único para o arquivo
        filename = secure_filename(image_file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Cria diretório se não existir
        upload_dir = 'app/static/images/premios'
        os.makedirs(upload_dir, exist_ok=True)
        
        # Salva arquivo
        filepath = os.path.join(upload_dir, unique_filename)
        image_file.save(filepath)
        
        return unique_filename
    return None

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
    
    # Lojas ganhadoras (todas as lojas que já foram sorteadas)
    lojas_ganhadoras = []
    if sorteio_atual:
        # Loja BIG ganhadora
        lojas_ganhadoras.append({
            'loja': sorteio_atual.loja_big,
            'tipo': 'BIG',
            'semana': sorteio_atual.semana_inicio,
            'colaboradores_sorteados': SorteioColaborador.query.join(Colaborador).filter(
                SorteioColaborador.sorteio_semanal_id == sorteio_atual.id,
                Colaborador.loja_id == sorteio_atual.loja_big_id
            ).count(),
            'premios_disponiveis': Premio.query.filter(
                db.or_(Premio.loja_id == sorteio_atual.loja_big_id, Premio.loja_id.is_(None)),
                Premio.ativo == True
            ).count()
        })
        
        # Loja ULTRA ganhadora
        lojas_ganhadoras.append({
            'loja': sorteio_atual.loja_ultra,
            'tipo': 'ULTRA',
            'semana': sorteio_atual.semana_inicio,
            'colaboradores_sorteados': SorteioColaborador.query.join(Colaborador).filter(
                SorteioColaborador.sorteio_semanal_id == sorteio_atual.id,
                Colaborador.loja_id == sorteio_atual.loja_ultra_id
            ).count(),
            'premios_disponiveis': Premio.query.filter(
                db.or_(Premio.loja_id == sorteio_atual.loja_ultra_id, Premio.loja_id.is_(None)),
                Premio.ativo == True
            ).count()
        })
    
    # Sorteios de colaboradores desta semana
    colaboradores_sorteados = []
    if sorteio_atual:
        colaboradores_sorteados = SorteioColaborador.query.filter_by(
            sorteio_semanal_id=sorteio_atual.id
        ).order_by(SorteioColaborador.data_sorteio.desc()).all()
    
    # Prêmios ativos
    premios_ativos = Premio.query.filter_by(ativo=True).count()
    premios_por_loja = Premio.query.filter(Premio.loja_id.isnot(None), Premio.ativo == True).count()
    premios_gerais = premios_ativos - premios_por_loja
    
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
                         lojas_ganhadoras=lojas_ganhadoras,
                         colaboradores_sorteados=colaboradores_sorteados,
                         premios_ativos=premios_ativos,
                         premios_por_loja=premios_por_loja,
                         premios_gerais=premios_gerais,
                         sorteios_recentes=sorteios_recentes,
                         sorteios_colaboradores_count=sorteios_colaboradores_count)

@admin_bp.route('/sortear', methods=['GET', 'POST'])
@admin_required
def sortear_lojas():
    """Sortear lojas ganhadoras da semana"""
    from datetime import date, timedelta
    
    # Calcula a terça-feira da semana atual
    hoje = date.today()
    dias_para_terca = (1 - hoje.weekday()) % 7  # 1 = terça-feira (0=segunda, 1=terça, etc.)
    if dias_para_terca == 0 and hoje.weekday() > 1:  # Se já passou da terça
        dias_para_terca = 7  # Próxima terça
    terca_feira_atual = hoje + timedelta(days=dias_para_terca)
    
    form = SorteioSemanalForm()
    
    # Pré-seleciona a data da terça-feira atual
    if not form.semana_inicio.data:
        form.semana_inicio.data = terca_feira_atual
    
    # Busca lojas por bandeira
    todas_lojas_big = Loja.query.filter_by(bandeira='BIG', ativo=True).all()
    todas_lojas_ultra = Loja.query.filter_by(bandeira='ULTRA', ativo=True).all()
    
    # Busca sorteios já realizados para filtrar lojas
    sorteios_realizados = SorteioSemanal.query.all()
    lojas_big_sorteadas_ids = {s.loja_big_id for s in sorteios_realizados}
    lojas_ultra_sorteadas_ids = {s.loja_ultra_id for s in sorteios_realizados}
    
    # Filtra lojas disponíveis (que não foram sorteadas)
    lojas_big_disponiveis = [l for l in todas_lojas_big if l.id not in lojas_big_sorteadas_ids]
    lojas_ultra_disponiveis = [l for l in todas_lojas_ultra if l.id not in lojas_ultra_sorteadas_ids]
    
    # Lojas já sorteadas
    lojas_big_sorteadas = [l for l in todas_lojas_big if l.id in lojas_big_sorteadas_ids]
    lojas_ultra_sorteadas = [l for l in todas_lojas_ultra if l.id in lojas_ultra_sorteadas_ids]
    
    # Converte para JSON serializável
    lojas_big_json = [{'id': l.id, 'codigo': l.codigo, 'nome': l.nome} for l in lojas_big_disponiveis]
    lojas_ultra_json = [{'id': l.id, 'codigo': l.codigo, 'nome': l.nome} for l in lojas_ultra_disponiveis]
    lojas_big_sorteadas_json = [{'id': l.id, 'codigo': l.codigo, 'nome': l.nome} for l in lojas_big_sorteadas]
    lojas_ultra_sorteadas_json = [{'id': l.id, 'codigo': l.codigo, 'nome': l.nome} for l in lojas_ultra_sorteadas]
    
    # Verifica se já existe sorteio para a data atual
    sorteio_existente = None
    if form.semana_inicio.data:
        sorteio_existente = SorteioSemanal.query.filter_by(semana_inicio=form.semana_inicio.data).first()
    
    if request.method == 'POST' and form.validate_on_submit():
        # Verifica novamente se já existe sorteio
        if sorteio_existente:
            flash('Já existe um sorteio para esta semana!', 'warning')
            return render_template('admin/sortear.html', 
                                 form=form,
                                 lojas_big=lojas_big_json,
                                 lojas_ultra=lojas_ultra_json,
                                 lojas_big_sorteadas=lojas_big_sorteadas_json,
                                 lojas_ultra_sorteadas=lojas_ultra_sorteadas_json,
                                 sorteio_existente=sorteio_existente)
        
        # Sorteia uma loja de cada bandeira
        if not lojas_big_disponiveis or not lojas_ultra_disponiveis:
            flash('Não há lojas suficientes para sortear!', 'danger')
            return render_template('admin/sortear.html', 
                                 form=form,
                                 lojas_big=lojas_big_json,
                                 lojas_ultra=lojas_ultra_json,
                                 lojas_big_sorteadas=lojas_big_sorteadas_json,
                                 lojas_ultra_sorteadas=lojas_ultra_sorteadas_json,
                                 sorteio_existente=sorteio_existente)
        
        # Realiza o sorteio
        import random
        loja_big = random.choice(lojas_big_disponiveis)
        loja_ultra = random.choice(lojas_ultra_disponiveis)
        
        # Salva no banco
        sorteio = SorteioSemanal(
            semana_inicio=form.semana_inicio.data,
            loja_big_id=loja_big.id,
            loja_ultra_id=loja_ultra.id,
            sorteado_por=current_user.id
        )
        
        db.session.add(sorteio)
        db.session.commit()
        
        flash(f'Sorteio realizado! Lojas sorteadas: {loja_big.nome} (BIG) e {loja_ultra.nome} (ULTRA)', 'success')
        return redirect(url_for('admin.sortear_lojas'))
    
    return render_template('admin/sortear.html',
                         form=form,
                         lojas_big=lojas_big_json,
                         lojas_ultra=lojas_ultra_json,
                         lojas_big_sorteadas=lojas_big_sorteadas_json,
                         lojas_ultra_sorteadas=lojas_ultra_sorteadas_json,
                         sorteio_existente=sorteio_existente)

@admin_bp.route('/sortear/ajax', methods=['POST'])
@admin_required
def sortear_lojas_ajax():
    """Sorteia lojas via AJAX sem redirecionamento"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        semana_inicio_str = data.get('semana_inicio')
        loja_big_id = data.get('loja_big_id')
        loja_ultra_id = data.get('loja_ultra_id')
        
        if not all([semana_inicio_str, loja_big_id, loja_ultra_id]):
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
        # Converte data
        semana_inicio = datetime.strptime(semana_inicio_str, '%Y-%m-%d').date()
        
        # Verifica se já existe sorteio para esta semana
        sorteio_existente = SorteioSemanal.query.filter_by(semana_inicio=semana_inicio).first()
        if sorteio_existente:
            return jsonify({
                'success': False, 
                'message': f'Já existe sorteio para a semana de {semana_inicio.strftime("%d/%m/%Y")}!'
            }), 400
        
        # Busca as lojas
        loja_big = Loja.query.get(loja_big_id)
        loja_ultra = Loja.query.get(loja_ultra_id)
        
        if not loja_big or not loja_ultra:
            return jsonify({'success': False, 'message': 'Lojas não encontradas'}), 400
        
        # Cria o sorteio
        sorteio = SorteioSemanal(
            semana_inicio=semana_inicio,
            loja_big_id=loja_big.id,
            loja_ultra_id=loja_ultra.id,
            sorteado_por=current_user.id
        )
        
        db.session.add(sorteio)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Sorteio realizado! Lojas sorteadas: {loja_big.nome} (BIG) e {loja_ultra.nome} (ULTRA)',
            'data': {
                'semana': semana_inicio.strftime('%d/%m/%Y'),
                'loja_big': {'nome': loja_big.nome, 'codigo': loja_big.codigo},
                'loja_ultra': {'nome': loja_ultra.nome, 'codigo': loja_ultra.codigo}
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@admin_bp.route('/sortear/verificar', methods=['POST'])
@admin_required
def verificar_sorteio_existente():
    """Verifica se já existe sorteio para uma data específica ou semana corrente"""
    try:
        data = request.get_json()
        semana_inicio_str = data.get('semana_inicio')
        
        if not semana_inicio_str:
            return jsonify({'success': False, 'message': 'Data não fornecida'}), 400
        
        # Converte data
        data_selecionada = datetime.strptime(semana_inicio_str, '%Y-%m-%d').date()
        
        # CORREÇÃO: Calcula o intervalo da semana (segunda a domingo)
        # Descobre que dia da semana é a data selecionada
        dia_semana = data_selecionada.weekday()  # 0=segunda, 1=terça, ..., 6=domingo
        
        # Calcula segunda-feira da semana da data selecionada
        segunda_feira = data_selecionada - timedelta(days=dia_semana)
        # Calcula domingo da mesma semana
        domingo = segunda_feira + timedelta(days=6)
        
        # Verifica se JÁ EXISTE qualquer sorteio na semana corrente (segunda a domingo)
        sorteio_na_semana = SorteioSemanal.query.filter(
            SorteioSemanal.semana_inicio >= segunda_feira,
            SorteioSemanal.semana_inicio <= domingo
        ).first()
        
        if sorteio_na_semana:
            return jsonify({
                'existe': True,
                'bloqueio_semanal': True,  # Flag para indicar bloqueio por semana
                'data': {
                    'semana': sorteio_na_semana.semana_inicio.strftime('%d/%m/%Y'),
                    'semana_completa': f"{segunda_feira.strftime('%d/%m')} a {domingo.strftime('%d/%m/%Y')}",
                    'loja_big': {
                        'nome': sorteio_na_semana.loja_big.nome,
                        'codigo': sorteio_na_semana.loja_big.codigo
                    },
                    'loja_ultra': {
                        'nome': sorteio_na_semana.loja_ultra.nome, 
                        'codigo': sorteio_na_semana.loja_ultra.codigo
                    },
                    'data_sorteio': sorteio_na_semana.data_sorteio.strftime('%d/%m/%Y %H:%M'),
                    'motivo_bloqueio': f'Já existe sorteio na semana de {segunda_feira.strftime("%d/%m")} a {domingo.strftime("%d/%m/%Y")}' + 
                                     f' (realizado na terça-feira {sorteio_na_semana.semana_inicio.strftime("%d/%m/%Y")})'
                }
            })
        else:
            return jsonify({'existe': False})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

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
    form.loja_id.choices = [(l.id, f"{l.nome} ({l.codigo})") for l in lojas]
    
    # Se loja_id foi passada como parâmetro, pré-seleciona
    loja_id_param = request.args.get('loja_id', type=int)
    if loja_id_param and request.method == 'GET':
        form.loja_id.data = loja_id_param
    
    if form.validate_on_submit():
        # Na criação, senha é obrigatória
        if not form.password.data:
            flash('Senha é obrigatória para novo assistente!', 'danger')
            return render_template('admin/usuario_form.html', form=form, titulo='Novo Assistente')
        
        # Verifica se email já existe
        usuario_existente = Usuario.query.filter_by(email=form.email.data).first()
        if usuario_existente:
            flash('Este email já está cadastrado!', 'danger')
            return render_template('admin/usuario_form.html', form=form, titulo='Novo Assistente')
        
        usuario = Usuario(
            nome=form.nome.data,
            email=form.email.data,
            tipo='assistente',
            loja_id=form.loja_id.data,
            ativo=True
        )
        usuario.set_password(form.password.data)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash(f'Assistente {usuario.nome} criado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/usuario_form.html', form=form, titulo='Novo Assistente')

@admin_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_usuario(id):
    """Editar usuário assistente"""
    usuario = Usuario.query.filter_by(id=id, tipo='assistente').first_or_404()
    
    form = UsuarioForm(obj=usuario)
    
    # Popula lojas disponíveis
    lojas = Loja.query.filter_by(ativo=True).order_by(Loja.nome).all()
    form.loja_id.choices = [(l.id, f"{l.nome} ({l.codigo})") for l in lojas]
    
    if form.validate_on_submit():
        # Verifica se email já existe (exceto o próprio)
        usuario_existente = Usuario.query.filter_by(email=form.email.data).filter(Usuario.id != id).first()
        if usuario_existente:
            flash('Este email já está cadastrado por outro assistente!', 'danger')
            return render_template('admin/usuario_form.html', form=form, titulo='Editar Assistente', usuario=usuario)
        
        usuario.nome = form.nome.data
        usuario.email = form.email.data
        usuario.loja_id = form.loja_id.data
        
        # Atualiza senha apenas se fornecida
        if form.password.data:
            usuario.set_password(form.password.data)
        
        db.session.commit()
        
        flash(f'Assistente {usuario.nome} atualizado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/usuario_form.html', form=form, titulo='Editar Assistente', usuario=usuario)

@admin_bp.route('/usuarios/<int:id>/toggle')
@admin_required
def toggle_usuario(id):
    """Ativar/desativar usuário"""
    usuario = Usuario.query.filter_by(id=id, tipo='assistente').first_or_404()
    
    usuario.ativo = not usuario.ativo
    db.session.commit()
    
    status = 'ativado' if usuario.ativo else 'desativado'
    flash(f'Assistente {usuario.nome} foi {status}.', 'success')
    
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/usuarios/<int:id>/excluir')
@admin_required
def excluir_usuario(id):
    """Excluir usuário assistente"""
    usuario = Usuario.query.filter_by(id=id, tipo='assistente').first_or_404()
    
    nome = usuario.nome
    db.session.delete(usuario)
    db.session.commit()
    
    flash(f'Assistente {nome} foi excluído com sucesso.', 'success')
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/premios')
@admin_required
def premios():
    """Lista prêmios com status de atribuição"""
    premios = Premio.query.order_by(Premio.data_evento.desc(), Premio.nome).all()
    
    # Separar prêmios por status
    premios_sem_loja = []
    premios_com_loja = []
    premios_sorteados = []
    
    for premio in premios:
        # Verifica se já foi sorteado
        sorteio_colaborador = SorteioColaborador.query.filter_by(premio_id=premio.id).first()
        
        if sorteio_colaborador:
            premios_sorteados.append({
                'premio': premio,
                'colaborador': sorteio_colaborador.colaborador,
                'sorteio': sorteio_colaborador
            })
        elif premio.loja_id:
            premios_com_loja.append(premio)
        else:
            premios_sem_loja.append(premio)
    
    return render_template('admin/premios.html', 
                         premios_sem_loja=premios_sem_loja,
                         premios_com_loja=premios_com_loja,
                         premios_sorteados=premios_sorteados)

@admin_bp.route('/premios/novo', methods=['GET', 'POST'])
@admin_required
def novo_premio():
    """Criar novo prêmio (sem loja por padrão)"""
    form = PremioForm()
    
    if form.validate_on_submit():
        # Processa upload de imagem APENAS se há um arquivo válido
        imagem_filename = None
        if (form.imagem.data and 
            hasattr(form.imagem.data, 'filename') and 
            form.imagem.data.filename):
            imagem_filename = save_premio_image(form.imagem.data)
        
        premio = Premio(
            nome=form.nome.data,
            descricao=form.descricao.data,
            data_evento=form.data_evento.data,
            tipo=form.tipo.data,
            imagem=imagem_filename,
            loja_id=None,  # Sempre sem loja por padrão
            criado_por=current_user.id,
            ativo=True
        )
        
        db.session.add(premio)
        db.session.commit()
        
        flash(f'✅ Prêmio "{premio.nome}" criado com sucesso! Você pode agora atribuí-lo a uma loja ganhadora.', 'success')
        return redirect(url_for('admin.premios'))
    
    return render_template('admin/premio_form.html', form=form, titulo='Novo Prêmio')

@admin_bp.route('/premios/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_premio(id):
    """Editar prêmio (apenas se não foi sorteado)"""
    premio = Premio.query.get_or_404(id)
    
    # Verifica se já foi sorteado
    sorteio_colaborador = SorteioColaborador.query.filter_by(premio_id=id).first()
    if sorteio_colaborador:
        flash('❌ Não é possível editar um prêmio que já foi sorteado!', 'danger')
        return redirect(url_for('admin.premios'))
    
    form = PremioForm(obj=premio)
    
    if form.validate_on_submit():
        # Verifica se deve remover a imagem
        remover_imagem = request.form.get('remover_imagem') == 'true'
        
        if remover_imagem:
            # Remove imagem atual se existir
            if premio.imagem:
                old_image_path = os.path.join('app/static/images/premios', premio.imagem)
                safe_remove_file(old_image_path)
            
            # Define como None para usar imagem padrão
            premio.imagem = None
            
        elif (form.imagem.data and 
              hasattr(form.imagem.data, 'filename') and 
              form.imagem.data.filename):
            
            # Remove imagem anterior se existir
            if premio.imagem:
                old_image_path = os.path.join('app/static/images/premios', premio.imagem)
                safe_remove_file(old_image_path)
            
            # Salva nova imagem
            nova_imagem = save_premio_image(form.imagem.data)
            if nova_imagem:
                premio.imagem = nova_imagem
        
        premio.nome = form.nome.data
        premio.descricao = form.descricao.data
        premio.data_evento = form.data_evento.data
        premio.tipo = form.tipo.data
        # Não permite alterar loja_id aqui - usa rota específica para isso
        
        db.session.commit()
        
        flash(f'✅ Prêmio "{premio.nome}" atualizado com sucesso!', 'success')
        return redirect(url_for('admin.premios'))
    
    return render_template('admin/premio_form.html', form=form, titulo='Editar Prêmio', premio=premio)

@admin_bp.route('/premios/<int:id>/atribuir', methods=['GET', 'POST'])
@admin_required
def atribuir_premio(id):
    """Atribuir prêmio a uma loja ganhadora"""
    premio = Premio.query.get_or_404(id)
    
    # Verifica se já foi sorteado
    sorteio_colaborador = SorteioColaborador.query.filter_by(premio_id=id).first()
    if sorteio_colaborador:
        flash('❌ Não é possível atribuir um prêmio que já foi sorteado!', 'danger')
        return redirect(url_for('admin.premios'))
    
    form = AtribuirPremioForm()
    
    # Popula apenas com as lojas ganhadoras da semana atual
    lojas_ganhadoras = []
    sorteio_atual = SorteioSemanal.query.order_by(SorteioSemanal.semana_inicio.desc()).first()
    
    if sorteio_atual:
        lojas_ganhadoras.append((sorteio_atual.loja_big.id, f"{sorteio_atual.loja_big.codigo} - {sorteio_atual.loja_big.nome} (BIG)"))
        lojas_ganhadoras.append((sorteio_atual.loja_ultra.id, f"{sorteio_atual.loja_ultra.codigo} - {sorteio_atual.loja_ultra.nome} (ULTRA)"))
    
    if not lojas_ganhadoras:
        flash('❌ Não há um sorteio semanal ativo! Realize um sorteio primeiro.', 'warning')
        return redirect(url_for('admin.premios'))
    
    form.loja_id.choices = lojas_ganhadoras
    
    if form.validate_on_submit():
        loja = Loja.query.get(form.loja_id.data)
        premio.loja_id = form.loja_id.data
        
        db.session.commit()
        
        flash(f'✅ Prêmio "{premio.nome}" atribuído à loja {loja.codigo} - {loja.nome}!', 'success')
        return redirect(url_for('admin.premios'))
    
    return render_template('admin/atribuir_premio.html', form=form, premio=premio, titulo='Atribuir Prêmio à Loja')

@admin_bp.route('/premios/<int:id>/desatribuir', methods=['POST'])
@admin_required
def desatribuir_premio(id):
    """Remover atribuição de prêmio (voltar para pool geral)"""
    premio = Premio.query.get_or_404(id)
    
    # Verifica se já foi sorteado
    sorteio_colaborador = SorteioColaborador.query.filter_by(premio_id=id).first()
    if sorteio_colaborador:
        flash('❌ Não é possível desatribuir um prêmio que já foi sorteado!', 'danger')
        return redirect(url_for('admin.premios'))
    
    loja_nome = premio.loja.nome if premio.loja else 'desconhecida'
    premio.loja_id = None
    
    db.session.commit()
    
    flash(f'✅ Prêmio "{premio.nome}" removido da loja {loja_nome} e voltou para o pool geral.', 'success')
    return redirect(url_for('admin.premios'))

@admin_bp.route('/premios/<int:id>/excluir', methods=['POST'])
@admin_required
def excluir_premio(id):
    """Excluir prêmio (apenas se não foi atribuído nem sorteado)"""
    premio = Premio.query.get_or_404(id)

    # Verifica se já foi sorteado
    sorteio_existente = SorteioColaborador.query.filter_by(premio_id=id).first()
    if sorteio_existente:
        flash('❌ Não é possível excluir um prêmio que já foi sorteado!', 'danger')
        return redirect(url_for('admin.premios'))

    # Verifica se está atribuído a uma loja
    if premio.loja_id:
        flash('❌ Não é possível excluir um prêmio que está atribuído a uma loja!', 'danger')
        return redirect(url_for('admin.premios'))

    # Se passou nas verificações, exclui
    nome_premio = premio.nome
    db.session.delete(premio)
    db.session.commit()

    flash(f'✅ Prêmio "{nome_premio}" foi excluído com sucesso.', 'success')
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

@admin_bp.route('/sorteios/resetar-pote', methods=['POST'])
@admin_required
def resetar_pote_lojas():
    """Reseta o pote de lojas - permite que todas as lojas voltem a participar dos sorteios"""
    try:
        # Conta quantos sorteios serão removidos
        total_sorteios = SorteioSemanal.query.count()
        total_colaboradores = SorteioColaborador.query.count()
        
        if total_sorteios == 0:
            flash('Não há sorteios para resetar.', 'info')
            return redirect(url_for('admin.configuracoes'))
        
        # Remove todos os sorteios de colaboradores primeiro (FK constraint)
        SorteioColaborador.query.delete()
        
        # Remove todos os sorteios semanais
        SorteioSemanal.query.delete()
        
        db.session.commit()
        
        flash(f'✅ Pote de lojas resetado com sucesso! {total_sorteios} sorteios semanais e {total_colaboradores} sorteios de colaboradores foram removidos. Todas as lojas podem participar novamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erro ao resetar pote de lojas: {str(e)}', 'danger')
    
    return redirect(url_for('admin.configuracoes'))

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

@admin_bp.route('/colaboradores')
@admin_required
def colaboradores():
    """Lista todos os colaboradores com filtro por loja"""
    loja_id = request.args.get('loja_id', type=int)
    sort = request.args.get('sort', 'nome')
    order = request.args.get('order', 'asc')
    
    # Query base
    query = Colaborador.query
    
    # Filtro por loja se especificado
    if loja_id:
        query = query.filter_by(loja_id=loja_id)
    
    # Ordenação
    if sort == 'nome':
        if order == 'desc':
            query = query.order_by(Colaborador.nome.desc())
        else:
            query = query.order_by(Colaborador.nome.asc())
    elif sort == 'matricula':
        if order == 'desc':
            query = query.order_by(Colaborador.matricula.desc())
        else:
            query = query.order_by(Colaborador.matricula.asc())
    elif sort == 'setor':
        if order == 'desc':
            query = query.order_by(Colaborador.setor.desc())
        else:
            query = query.order_by(Colaborador.setor.asc())
    elif sort == 'loja':
        if order == 'desc':
            query = query.join(Loja).order_by(Loja.nome.desc())
        else:
            query = query.join(Loja).order_by(Loja.nome.asc())
    
    colaboradores = query.all()
    
    # Lista de lojas para o filtro
    lojas = Loja.query.filter_by(ativo=True).order_by(Loja.codigo).all()
    
    return render_template('admin/colaboradores.html', 
                         colaboradores=colaboradores,
                         lojas=lojas,
                         loja_selecionada=loja_id,
                         current_sort=sort,
                         current_order=order)

@admin_bp.route('/colaboradores/upload', methods=['GET', 'POST'])
@admin_required
def upload_colaboradores():
    """Upload de colaboradores pelo admin usando planilha Excel"""
    # Limpa arquivos temporários antigos
    cleanup_temp_files()
    
    if request.method == 'POST':
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo selecionado!', 'danger')
            return redirect(request.url)
        
        arquivo = request.files['arquivo']
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado!', 'danger')
            return redirect(request.url)
        
        if not arquivo.filename.lower().endswith(('.xlsx', '.xls')):
            flash('Apenas arquivos Excel (.xlsx, .xls) são permitidos!', 'danger')
            return redirect(request.url)
        
        # Pega a opção de loja específica
        loja_especifica_id = request.form.get('loja_especifica')
        loja_especifica_id = int(loja_especifica_id) if loja_especifica_id and loja_especifica_id != '' else None
        
        workbook = None
        filepath = None
        
        try:
            import openpyxl
            import os
            from datetime import datetime
            
            # Salva arquivo temporariamente
            filename = f"temp_colaboradores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join('uploads', filename)
            arquivo.save(filepath)
            
            # Carrega planilha
            workbook = openpyxl.load_workbook(filepath)
            sheet = workbook.active
            
            # Detecta automaticamente o formato da planilha (importa função do manager)
            from app.routes.manager import detectar_formato_planilha
            formato_detectado = detectar_formato_planilha(sheet)
            
            colaboradores_processados = 0
            colaboradores_atualizados = 0
            colaboradores_criados = 0
            erros = []
            
            # Mapeia códigos de loja para IDs
            lojas_map = {}
            for loja in Loja.query.all():
                lojas_map[loja.codigo] = loja.id
            
            # Se loja específica foi selecionada, filtra apenas ela
            if loja_especifica_id:
                loja_especifica = Loja.query.get(loja_especifica_id)
                if loja_especifica:
                    # Mantém mapeamento completo para identificar todas as lojas da planilha
                    # mas processa apenas a loja selecionada
                    pass
                else:
                    flash('Loja específica não encontrada!', 'danger')
                    # Limpa recursos e retorna
                    if workbook:
                        workbook.close()
                    if filepath:
                        safe_remove_file(filepath)
                    return redirect(request.url)
            
            # Processa cada linha (pula cabeçalho)
            for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                if not row or len(row) < formato_detectado["min_colunas"]:
                    continue
                
                try:
                    # Extrai código da loja baseado no formato detectado
                    if formato_detectado["min_colunas"] == 5:  # Formato 1
                        codigo_loja = str(row[0]).strip() if row[0] else ''  # Coluna A (Unidade)
                    else:  # Formato 2
                        codigo_loja = str(row[1]).strip() if row[1] else ''  # Coluna B (Unidade)
                    
                    # Extrai outros dados baseado no formato detectado
                    matricula = str(row[formato_detectado["col_matricula"]]).strip() if row[formato_detectado["col_matricula"]] else ''
                    nome = str(row[formato_detectado["col_nome"]]).strip() if row[formato_detectado["col_nome"]] else ''
                    setor = str(row[formato_detectado["col_setor"]]).strip() if row[formato_detectado["col_setor"]] else ''
                    
                    if not all([codigo_loja, matricula, nome, setor]):
                        erros.append(f"Linha {row_num}: Dados incompletos")
                        continue
                    
                    # Verifica se a loja existe no mapeamento (sempre completo)
                    if codigo_loja not in lojas_map:
                        erros.append(f"Linha {row_num}: Loja '{codigo_loja}' não encontrada")
                        continue
                    
                    loja_id = lojas_map[codigo_loja]
                    
                    # Se filtro por loja específica, pula linhas de outras lojas
                    if loja_especifica_id and loja_id != loja_especifica_id:
                        continue
                    
                    # Verifica se colaborador já existe
                    colaborador_existente = Colaborador.query.filter_by(
                        matricula=matricula, 
                        loja_id=loja_id
                    ).first()
                    
                    if colaborador_existente:
                        # Atualiza dados
                        colaborador_existente.nome = nome
                        colaborador_existente.setor = setor
                        colaborador_existente.ultima_atualizacao = get_brazil_datetime()
                        colaboradores_atualizados += 1
                    else:
                        # Cria novo colaborador
                        novo_colaborador = Colaborador(
                            matricula=matricula,
                            nome=nome,
                            setor=setor,
                            loja_id=loja_id,
                            apto=True,
                            ultima_atualizacao=get_brazil_datetime()
                        )
                        db.session.add(novo_colaborador)
                        colaboradores_criados += 1
                    
                    colaboradores_processados += 1
                    
                except Exception as e:
                    erros.append(f"Linha {row_num}: {str(e)}")
            
            # Fecha o workbook antes de salvar no banco
            if workbook:
                workbook.close()
                workbook = None
            
            # Salva no banco
            db.session.commit()
            
            # Mensagem de sucesso
            mensagem = f"✅ Processamento concluído!\n"
            mensagem += f"📋 {formato_detectado['nome']}\n"
            if loja_especifica_id:
                mensagem += f"🏪 Loja específica: {loja_especifica.nome}\n"
            mensagem += f"📊 Colaboradores processados: {colaboradores_processados}\n"
            mensagem += f"🆕 Novos colaboradores: {colaboradores_criados}\n"
            mensagem += f"🔄 Colaboradores atualizados: {colaboradores_atualizados}"
            
            if erros:
                mensagem += f"\n⚠️ Erros encontrados ({len(erros)}):\n" + "\n".join(erros[:5])
                if len(erros) > 5:
                    mensagem += f"\n... e mais {len(erros) - 5} erros."
            
            flash(mensagem, 'success' if not erros else 'warning')
            
            # Remove arquivo temporário
            if filepath:
                safe_remove_file(filepath)
            
            return redirect(url_for('admin.colaboradores'))
            
        except Exception as e:
            flash(f'Erro ao processar arquivo: {str(e)}', 'danger')
            
            # Limpa recursos em caso de erro
            if workbook:
                try:
                    workbook.close()
                except:
                    pass
            
            if filepath:
                safe_remove_file(filepath)
    
    # Carrega lojas para o formulário
    lojas = Loja.query.filter_by(ativo=True).order_by(Loja.codigo).all()
    return render_template('admin/upload_colaboradores.html', lojas=lojas)

@admin_bp.route('/colaboradores/adicionar', methods=['GET', 'POST'])
@admin_required
def adicionar_colaborador():
    """Adicionar novo colaborador pelo admin"""
    from app.forms.manager import ColaboradorForm
    
    form = ColaboradorForm()
    
    # Popula lojas disponíveis
    lojas = Loja.query.filter_by(ativo=True).order_by(Loja.nome).all()
    form.loja_id.choices = [(l.id, f"{l.codigo} - {l.nome}") for l in lojas]
    
    # Se loja_id foi passada como parâmetro, pré-seleciona
    loja_id_param = request.args.get('loja_id', type=int)
    if loja_id_param and request.method == 'GET':
        form.loja_id.data = loja_id_param
    
    if form.validate_on_submit():
        # Verifica se matrícula já existe nesta loja
        colaborador_existente = Colaborador.query.filter_by(
            matricula=form.matricula.data,
            loja_id=form.loja_id.data
        ).first()
        
        if colaborador_existente:
            flash('Já existe um colaborador com esta matrícula nesta loja!', 'danger')
            return render_template('admin/colaborador_form.html', form=form, titulo='Adicionar Colaborador')
        
        # Cria novo colaborador
        novo_colaborador = Colaborador(
            matricula=form.matricula.data,
            nome=form.nome.data,
            setor=form.setor.data,
            loja_id=form.loja_id.data,
            apto=form.apto.data,
            ultima_atualizacao=get_brazil_datetime()
        )
        
        db.session.add(novo_colaborador)
        db.session.commit()
        
        flash(f'Colaborador {novo_colaborador.nome} criado com sucesso!', 'success')
        return redirect(url_for('admin.colaboradores'))
    
    return render_template('admin/colaborador_form.html', form=form, titulo='Adicionar Colaborador')

@admin_bp.route('/colaboradores/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_colaborador(id):
    """Editar colaborador pelo admin"""
    from app.forms.manager import ColaboradorForm
    
    colaborador = Colaborador.query.get_or_404(id)
    form = ColaboradorForm(obj=colaborador)
    
    # Popula lojas disponíveis
    lojas = Loja.query.filter_by(ativo=True).order_by(Loja.nome).all()
    form.loja_id.choices = [(l.id, f"{l.codigo} - {l.nome}") for l in lojas]
    
    if form.validate_on_submit():
        # Verifica se matrícula já existe em outra loja
        colaborador_existente = Colaborador.query.filter_by(
            matricula=form.matricula.data,
            loja_id=form.loja_id.data
        ).filter(Colaborador.id != id).first()
        
        if colaborador_existente:
            flash('Já existe um colaborador com esta matrícula nesta loja!', 'danger')
            return render_template('admin/colaborador_form.html', form=form, titulo='Editar Colaborador')
        
        colaborador.matricula = form.matricula.data
        colaborador.nome = form.nome.data
        colaborador.setor = form.setor.data
        colaborador.loja_id = form.loja_id.data
        colaborador.apto = form.apto.data
        colaborador.ultima_atualizacao = get_brazil_datetime()
        
        db.session.commit()
        
        flash(f'Colaborador {colaborador.nome} atualizado com sucesso!', 'success')
        return redirect(url_for('admin.colaboradores'))
    
    return render_template('admin/colaborador_form.html', form=form, titulo='Editar Colaborador')

@admin_bp.route('/colaboradores/<int:id>/toggle', methods=['GET', 'POST'])
@admin_required
def toggle_colaborador(id):
    """Ativa ou inativa um colaborador"""
    colaborador = Colaborador.query.get_or_404(id)
    
    colaborador.apto = not colaborador.apto
    colaborador.ultima_atualizacao = get_brazil_datetime()
    db.session.commit()
    
    status = 'ativado' if colaborador.apto else 'desativado'
    flash(f'Colaborador {colaborador.nome} foi {status}.', 'success')
    
    return redirect(url_for('admin.colaboradores'))

@admin_bp.route('/colaboradores/<int:id>/excluir')
@admin_required
def excluir_colaborador(id):
    """Excluir colaborador pelo admin"""
    colaborador = Colaborador.query.get_or_404(id)
    
    # Verifica se colaborador tem histórico de sorteios
    tem_historico = SorteioColaborador.query.filter_by(colaborador_id=id).first()
    if tem_historico:
        flash(f'Não é possível excluir {colaborador.nome} pois ele tem histórico de sorteios.', 'warning')
        return redirect(url_for('admin.colaboradores'))
    
    nome = colaborador.nome
    db.session.delete(colaborador)
    db.session.commit()
    
    flash(f'Colaborador {nome} foi excluído com sucesso.', 'success')
    return redirect(url_for('admin.colaboradores'))

@admin_bp.route('/colaboradores/acoes-lote', methods=['POST'])
@admin_required
def colaboradores_acoes_lote():
    """Executar ações em lote nos colaboradores selecionados"""
    try:
        # Pega os IDs dos colaboradores selecionados
        colaboradores_ids = request.form.getlist('colaboradores_ids[]')
        acao = request.form.get('acao')
        
        if not colaboradores_ids:
            flash('Nenhum colaborador selecionado!', 'warning')
            return redirect(url_for('admin.colaboradores'))
        
        if not acao:
            flash('Nenhuma ação selecionada!', 'warning')
            return redirect(url_for('admin.colaboradores'))
        
        # Converte IDs para inteiros
        colaboradores_ids = [int(id) for id in colaboradores_ids]
        
        # Busca colaboradores
        colaboradores = Colaborador.query.filter(Colaborador.id.in_(colaboradores_ids)).all()
        
        if not colaboradores:
            flash('Colaboradores não encontrados!', 'danger')
            return redirect(url_for('admin.colaboradores'))
        
        # Executa ação conforme solicitado
        if acao == 'ativar':
            for colaborador in colaboradores:
                colaborador.apto = True
                colaborador.ultima_atualizacao = get_brazil_datetime()
            db.session.commit()
            flash(f'✅ {len(colaboradores)} colaborador(es) ativado(s) com sucesso!', 'success')
            
        elif acao == 'desativar':
            for colaborador in colaboradores:
                colaborador.apto = False
                colaborador.ultima_atualizacao = get_brazil_datetime()
            db.session.commit()
            flash(f'❌ {len(colaboradores)} colaborador(es) desativado(s) com sucesso!', 'warning')
            
        elif acao == 'excluir':
            # Verifica quais têm histórico
            excluidos = 0
            com_historico = 0
            
            for colaborador in colaboradores:
                tem_historico = SorteioColaborador.query.filter_by(colaborador_id=colaborador.id).first()
                if tem_historico:
                    com_historico += 1
                else:
                    db.session.delete(colaborador)
                    excluidos += 1
            
            db.session.commit()
            
            mensagem = f'🗑️ {excluidos} colaborador(es) excluído(s) com sucesso!'
            if com_historico > 0:
                mensagem += f' ({com_historico} não puderam ser excluídos por terem histórico de sorteios)'
            
            flash(mensagem, 'info' if excluidos > 0 else 'warning')
        
        else:
            flash('Ação inválida!', 'danger')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao executar ação em lote: {str(e)}', 'danger')
    
    return redirect(url_for('admin.colaboradores'))

@admin_bp.route('/lojas')
@admin_required
def lojas():
    """Lista todas as lojas"""
    sort = request.args.get('sort', 'codigo')
    order = request.args.get('order', 'asc')
    bandeira = request.args.get('bandeira', '')
    
    # Query base
    query = Loja.query
    
    # Filtro por bandeira
    if bandeira:
        query = query.filter_by(bandeira=bandeira)
    
    # Ordenação
    if sort == 'codigo':
        if order == 'desc':
            query = query.order_by(Loja.codigo.desc())
        else:
            query = query.order_by(Loja.codigo.asc())
    elif sort == 'nome':
        if order == 'desc':
            query = query.order_by(Loja.nome.desc())
        else:
            query = query.order_by(Loja.nome.asc())
    elif sort == 'bandeira':
        if order == 'desc':
            query = query.order_by(Loja.bandeira.desc())
        else:
            query = query.order_by(Loja.bandeira.asc())
    
    lojas = query.all()
    
    # Estatísticas
    total_lojas = len(lojas)
    lojas_big = len([l for l in lojas if l.bandeira == 'BIG'])
    lojas_ultra = len([l for l in lojas if l.bandeira == 'ULTRA'])
    lojas_ativas = len([l for l in lojas if l.ativo])
    
    return render_template('admin/lojas.html', 
                         lojas=lojas,
                         current_sort=sort,
                         current_order=order,
                         bandeira_selecionada=bandeira,
                         total_lojas=total_lojas,
                         lojas_big=lojas_big,
                         lojas_ultra=lojas_ultra,
                         lojas_ativas=lojas_ativas)

@admin_bp.route('/lojas/adicionar', methods=['GET', 'POST'])
@admin_required
def adicionar_loja():
    """Adicionar nova loja"""
    
    form = LojaForm()
    
    if form.validate_on_submit():
        # Verifica se código já existe
        loja_existente = Loja.query.filter_by(codigo=form.codigo.data).first()
        
        if loja_existente:
            flash('Já existe uma loja com este código!', 'danger')
            return render_template('admin/loja_form.html', form=form, titulo='Adicionar Loja')
        
        # Cria nova loja
        nova_loja = Loja(
            codigo=form.codigo.data,
            nome=form.nome.data,
            bandeira=form.bandeira.data,
            ativo=form.ativo.data
        )
        
        db.session.add(nova_loja)
        db.session.commit()
        
        flash(f'Loja {nova_loja.codigo} - {nova_loja.nome} criada com sucesso!', 'success')
        return redirect(url_for('admin.lojas'))
    
    return render_template('admin/loja_form.html', form=form, titulo='Adicionar Loja')

@admin_bp.route('/lojas/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_loja(id):
    """Editar loja"""
    
    loja = Loja.query.get_or_404(id)
    form = LojaForm(obj=loja)
    
    if form.validate_on_submit():
        # Verifica se código já existe em outra loja
        loja_existente = Loja.query.filter_by(codigo=form.codigo.data).filter(Loja.id != id).first()
        
        if loja_existente:
            flash('Já existe uma loja com este código!', 'danger')
            return render_template('admin/loja_form.html', form=form, titulo='Editar Loja')
        
        loja.codigo = form.codigo.data
        loja.nome = form.nome.data
        loja.bandeira = form.bandeira.data
        loja.ativo = form.ativo.data
        
        db.session.commit()
        
        flash(f'Loja {loja.codigo} - {loja.nome} atualizada com sucesso!', 'success')
        return redirect(url_for('admin.lojas'))
    
    return render_template('admin/loja_form.html', form=form, titulo='Editar Loja')

@admin_bp.route('/lojas/<int:id>/toggle', methods=['GET', 'POST'])
@admin_required
def toggle_loja(id):
    """Ativa ou inativa uma loja"""
    loja = Loja.query.get_or_404(id)
    loja.ativo = not loja.ativo
    db.session.commit()
    status = 'ativada' if loja.ativo else 'desativada'
    flash(f'Loja {loja.codigo} - {loja.nome} foi {status}.', 'success')
    return redirect(url_for('admin.lojas'))

@admin_bp.route('/lojas/<int:id>/excluir')
@admin_required
def excluir_loja(id):
    """Excluir loja"""
    loja = Loja.query.get_or_404(id)
    
    # Verifica se loja tem colaboradores
    tem_colaboradores = Colaborador.query.filter_by(loja_id=id).first()
    if tem_colaboradores:
        flash(f'Não é possível excluir a loja {loja.codigo} pois ela possui colaboradores cadastrados.', 'warning')
        return redirect(url_for('admin.lojas'))
    
    # Verifica se loja tem usuários
    tem_usuarios = Usuario.query.filter_by(loja_id=id).first()
    if tem_usuarios:
        flash(f'Não é possível excluir a loja {loja.codigo} pois ela possui usuários cadastrados.', 'warning')
        return redirect(url_for('admin.lojas'))
    
    codigo = loja.codigo
    nome = loja.nome
    db.session.delete(loja)
    db.session.commit()
    
    flash(f'Loja {codigo} - {nome} foi excluída com sucesso.', 'success')
    return redirect(url_for('admin.lojas'))

@admin_bp.route('/configuracoes')
@admin_required
def configuracoes():
    """Página de configurações avançadas do sistema"""
    # Estatísticas para mostrar o impacto das operações
    total_sorteios = SorteioSemanal.query.count()
    total_sorteios_colaboradores = SorteioColaborador.query.count()
    total_colaboradores = Colaborador.query.count()
    total_usuarios = Usuario.query.filter_by(tipo='assistente').count()
    total_premios = Premio.query.count()
    
    return render_template('admin/configuracoes.html',
                         total_sorteios=total_sorteios,
                         total_sorteios_colaboradores=total_sorteios_colaboradores,
                         total_colaboradores=total_colaboradores,
                         total_usuarios=total_usuarios,
                         total_premios=total_premios)

@admin_bp.route('/configuracoes/reset-completo', methods=['POST'])
@admin_required
def reset_completo():
    """OPERAÇÃO PERIGOSA: Reseta o sistema para configurações iniciais - mantém apenas lojas e admin"""
    try:
        # Confirma que é o admin principal
        if not current_user.is_authenticated or current_user.tipo != 'admin':
            flash('❌ Acesso negado. Apenas administradores podem executar esta operação.', 'danger')
            return redirect(url_for('admin.configuracoes'))
        
        # Remove todos os sorteios de colaboradores
        sorteios_colaboradores_removidos = SorteioColaborador.query.count()
        SorteioColaborador.query.delete()
        
        # Remove todos os sorteios semanais
        sorteios_semanais_removidos = SorteioSemanal.query.count()
        SorteioSemanal.query.delete()
        
        # Remove todos os prêmios
        premios_removidos = Premio.query.count()
        Premio.query.delete()
        
        # Remove todos os colaboradores
        colaboradores_removidos = Colaborador.query.count()
        Colaborador.query.delete()
        
        # Remove todos os usuários assistentes (mantém apenas admin)
        usuarios_removidos = Usuario.query.filter_by(tipo='assistente').count()
        Usuario.query.filter_by(tipo='assistente').delete()
        
        db.session.commit()
        
        flash(f'⚠️ RESET COMPLETO EXECUTADO COM SUCESSO!\n'
              f'📊 Dados removidos:\n'
              f'• {sorteios_colaboradores_removidos} sorteios de colaboradores\n'
              f'• {sorteios_semanais_removidos} sorteios semanais\n'
              f'• {premios_removidos} prêmios\n'
              f'• {colaboradores_removidos} colaboradores\n'
              f'• {usuarios_removidos} usuários assistentes\n\n'
              f'✅ Sistema resetado para configurações iniciais!\n'
              f'Apenas lojas e usuário administrador foram mantidos.', 'warning')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erro ao executar reset completo: {str(e)}', 'danger')
    
    return redirect(url_for('admin.configuracoes')) 

# ===== ROTAS DO INSTAGRAM =====

@admin_bp.route('/instagram')
@admin_required
def instagram_lista():
    """Lista todos os sorteios do Instagram com estatísticas (versão otimizada)."""
    from sqlalchemy import func, select

    # Subquery para calcular estatísticas de forma eficiente no banco de dados
    stats_sq = select(
        ParticipanteInstagram.sorteio_id.label("sorteio_id"),
        func.count(ParticipanteInstagram.id).label("total_participantes"),
        func.sum(ParticipanteInstagram.comentarios_validos).label("total_comentarios"),
        func.sum(ParticipanteInstagram.tickets).label("total_tickets")
    ).group_by(ParticipanteInstagram.sorteio_id).subquery()

    # Query principal que junta os sorteios com suas estatísticas já calculadas
    sorteios_query = db.session.query(
        SorteioInstagram,
        stats_sq.c.total_participantes,
        stats_sq.c.total_comentarios,
        stats_sq.c.total_tickets
    ).outerjoin(stats_sq, SorteioInstagram.id == stats_sq.c.sorteio_id)\
     .order_by(SorteioInstagram.data_criacao.desc())\
     .all()

    # Estrutura os dados para o template
    sorteios_stats = []
    for sorteio, participantes, comentarios, tickets in sorteios_query:
        sorteios_stats.append({
            'sorteio': sorteio,
            'total_participantes': participantes or 0,
            'total_comentarios': comentarios or 0,
            'total_tickets': tickets or 0
        })

    # Formulário para proteção CSRF no botão de reset
    csrf_form = CSRFProtectionForm()

    return render_template('admin/instagram_lista.html', sorteios_stats=sorteios_stats, csrf_form=csrf_form)

@admin_bp.route('/instagram/novo', methods=['GET', 'POST'])
@admin_required
def instagram_novo():
    """Criar novo sorteio do Instagram."""
    form = SorteioInstagramForm()
    
    # Preenche com valores padrão da configuração
    if request.method == 'GET':
        config = db.session.get(ConfiguracaoInstagram, 1)
        if config:
            form.palavra_chave.data = config.palavra_chave_padrao
            form.tickets_maximos.data = config.tickets_maximos_padrao
            form.quantidade_vencedores.data = 1

    if form.validate_on_submit():
        novo_sorteio = SorteioInstagram(
            titulo=form.titulo.data,
            descricao=form.descricao.data,
            palavra_chave=form.palavra_chave.data.upper(),
            tickets_maximos=form.tickets_maximos.data,
            quantidade_vencedores=form.quantidade_vencedores.data,
            texto_original=form.texto_original.data,
            criado_por=current_user.id
        )
        db.session.add(novo_sorteio)
        db.session.commit()

        flash(f'Sorteio "{novo_sorteio.titulo}" criado! O processamento dos comentários será iniciado.', 'success')
        return redirect(url_for('admin.instagram_lista'))

    return render_template('admin/instagram_novo.html', form=form)


@admin_bp.route('/instagram/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def instagram_editar(id):
    """Editar um sorteio do Instagram."""
    sorteio = db.session.get(SorteioInstagram, id)
    if not sorteio:
        flash('Sorteio não encontrado.', 'danger')
        return redirect(url_for('admin.instagram_lista'))
        
    form = SorteioInstagramForm()

    if form.validate_on_submit():
        sorteio.titulo = form.titulo.data
        sorteio.descricao = form.descricao.data
        sorteio.palavra_chave = form.palavra_chave.data.upper()
        sorteio.tickets_maximos = form.tickets_maximos.data
        sorteio.quantidade_vencedores = form.quantidade_vencedores.data
        
        texto_original_form = form.texto_original.data
        if sorteio.texto_original != texto_original_form and sorteio.status != 'sorteado':
             sorteio.texto_original = texto_original_form
             sorteio.status = 'processando'
             ParticipanteInstagram.query.filter_by(sorteio_id=sorteio.id).delete()
             flash('Texto do post alterado. Os comentários serão reprocessados.', 'info')
        
        db.session.commit()
        flash('Sorteio atualizado com sucesso!', 'success')
        return redirect(url_for('admin.instagram_lista'))
    
    elif request.method == 'GET':
        form.titulo.data = sorteio.titulo
        form.descricao.data = sorteio.descricao
        form.palavra_chave.data = sorteio.palavra_chave
        form.tickets_maximos.data = sorteio.tickets_maximos
        form.texto_original.data = sorteio.texto_original
        form.quantidade_vencedores.data = sorteio.quantidade_vencedores or 1
        
    if sorteio.status in ['pronto', 'sorteado']:
        form.texto_original.render_kw = {'readonly': True, 'title': 'O texto não pode ser editado após o processamento.'}

    return render_template('admin/instagram_editar.html', form=form, sorteio=sorteio)


@admin_bp.route('/instagram/<int:id>/participantes')
@admin_required
def instagram_participantes(id):
    """Exibe os detalhes e participantes de um sorteio do Instagram."""
    sorteio = db.session.query(SorteioInstagram).options(
        joinedload(SorteioInstagram.participantes)
    ).filter_by(id=id).first_or_404()

    participantes = sorteio.participantes
    total_comentarios = sum(p.comentarios_validos for p in participantes)
    total_tickets = sum(p.tickets for p in participantes)

    # Prepara um JSON com os dados dos participantes para o sorteio no frontend
    participantes_json = json.dumps([
        {'username': p.username, 'tickets': p.tickets} for p in participantes
    ])
    
    # Busca os ganhadores se o sorteio já foi realizado
    ganhadores = []
    if sorteio.status == 'sorteado':
        ganhadores = ParticipanteInstagram.query.filter_by(sorteio_id=id, vencedor=True).all()

    return render_template('admin/instagram_participantes.html', 
                             sorteio=sorteio,
                             participantes=participantes,
                             total_comentarios=total_comentarios,
                             total_tickets=total_tickets,
                             participantes_json=participantes_json,
                             ganhadores=ganhadores)

@admin_bp.route('/instagram/sorteio/<int:sorteio_id>/salvar', methods=['POST'])
@admin_required
def salvar_sorteio_instagram_ajax(sorteio_id):
    """Salva os vencedores de um sorteio do Instagram via AJAX."""
    try:
        data = request.get_json()
        vencedores_data = data.get('vencedores')

        if not vencedores_data:
            return jsonify({'success': False, 'message': 'Dados dos vencedores não fornecidos.'}), 400

        sorteio = db.session.get(SorteioInstagram, sorteio_id)
        if not sorteio:
            return jsonify({'success': False, 'message': 'Sorteio não encontrado.'}), 404

        if sorteio.status == 'sorteado':
            return jsonify({'success': False, 'message': 'Este sorteio já foi finalizado.'}), 400

        vencedores_objs = []
        for vencedor_info in vencedores_data:
            username = vencedor_info.get('username')
            participante = ParticipanteInstagram.query.filter_by(sorteio_id=sorteio_id, username=username).first()
            
            if participante:
                participante.vencedor = True
                vencedores_objs.append(participante)
            else:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Participante @{username} não encontrado.'}), 404

        sorteio.status = 'sorteado'
        sorteio.data_sorteio = get_brazil_datetime()
        
        db.session.commit()

        # Renderiza o template parcial com os dados dos vencedores
        html_response = render_template(
            'admin/partials/_ganhadores_instagram.html',
            vencedores=vencedores_objs,
            sorteio=sorteio
        )
        
        return jsonify({'success': True, 'html': html_response})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@admin_bp.route('/instagram/<int:id>/excluir', methods=['POST'])
@admin_required
def instagram_excluir(id):
    """Excluir sorteio do Instagram"""
    sorteio = SorteioInstagram.query.get_or_404(id)
    
    if sorteio.status == 'sorteado':
        flash('Não é possível excluir um sorteio já realizado!', 'warning')
        return redirect(url_for('admin.instagram_lista'))
    
    titulo = sorteio.titulo
    db.session.delete(sorteio)
    db.session.commit()
    
    flash(f'Sorteio "{titulo}" excluído com sucesso!', 'success')
    return redirect(url_for('admin.instagram_lista'))

@admin_bp.route('/instagram/<int:id>/resetar', methods=['POST'])
@admin_required
def instagram_resetar(id):
    """Reseta um sorteio, removendo o vencedor e permitindo um novo sorteio."""
    sorteio = SorteioInstagram.query.get_or_404(id)
    
    # Remove o status de vencedor de todos os participantes
    for p in sorteio.participantes:
        p.vencedor = False
        
    # Reseta o status e data do sorteio
    sorteio.status = 'pronto'
    sorteio.data_sorteio = None
    
    db.session.commit()
    flash(f'Sorteio "{sorteio.titulo}" foi resetado. Você pode realizar o sorteio novamente.', 'success')
    return redirect(url_for('admin.instagram_participantes', id=id))

@admin_bp.route('/instagram/config', methods=['GET', 'POST'])
@admin_required
def instagram_config():
    """Configurações do Instagram"""
    config = ConfiguracaoInstagram.query.first()
    
    if not config:
        # Cria configuração padrão
        config = ConfiguracaoInstagram(
            palavra_chave_padrao='EU QUERO',
            tickets_maximos_padrao=30
        )
        db.session.add(config)
        db.session.commit()
    
    form = ConfiguracaoInstagramForm(obj=config)
    
    if form.validate_on_submit():
        config.palavra_chave_padrao = form.palavra_chave_padrao.data
        config.tickets_maximos_padrao = form.tickets_maximos_padrao.data
        config.atualizado_em = get_brazil_datetime()
        config.atualizado_por = current_user.id
        
        db.session.commit()
        flash('Configurações atualizadas com sucesso!', 'success')
        return redirect(url_for('admin.instagram_config'))
    
    return render_template('admin/instagram_config.html', form=form) 