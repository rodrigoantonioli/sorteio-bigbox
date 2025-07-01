from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Usuario, Loja, SorteioSemanal, SorteioColaborador, Colaborador, Premio
from app.forms.admin import SorteioSemanalForm, UsuarioForm, PremioForm, LojaForm
from datetime import datetime, date, timedelta
from functools import wraps
import random
import os
import glob

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
    """Sorteia lojas semanalmente"""
    form = SorteioSemanalForm()
    
    # Busca lojas ativas para o frontend
    lojas_big = Loja.query.filter_by(bandeira='BIG', ativo=True).all()
    lojas_ultra = Loja.query.filter_by(bandeira='ULTRA', ativo=True).all()
    
    # Serializa lojas para JSON
    lojas_big_json = [{'id': l.id, 'codigo': l.codigo, 'nome': l.nome} for l in lojas_big]
    lojas_ultra_json = [{'id': l.id, 'codigo': l.codigo, 'nome': l.nome} for l in lojas_ultra]
    
    if form.validate_on_submit():
        semana_inicio = form.semana_inicio.data
        
        # Verifica se já existe sorteio para esta semana
        sorteio_existente = SorteioSemanal.query.filter_by(semana_inicio=semana_inicio).first()
        if sorteio_existente:
            flash(f'Já existe sorteio para a semana de {semana_inicio.strftime("%d/%m/%Y")}!', 'warning')
            return render_template('admin/sortear.html', form=form, lojas_big=lojas_big_json, lojas_ultra=lojas_ultra_json)
        
        if not lojas_big or not lojas_ultra:
            flash('Não há lojas suficientes para o sorteio!', 'danger')
            return render_template('admin/sortear.html', form=form, lojas_big=lojas_big_json, lojas_ultra=lojas_ultra_json)
        
        # Verifica se é sorteio animado (com IDs das lojas escolhidas)
        loja_big_id = request.form.get('loja_big_id', type=int)
        loja_ultra_id = request.form.get('loja_ultra_id', type=int)
        
        if loja_big_id and loja_ultra_id:
            # Sorteio animado - usa as lojas escolhidas pela animação
            loja_big_sorteada = Loja.query.get(loja_big_id)
            loja_ultra_sorteada = Loja.query.get(loja_ultra_id)
        else:
            # Sorteio simples - sorteia aleatoriamente
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
    
    return render_template('admin/sortear.html', form=form, lojas_big=lojas_big_json, lojas_ultra=lojas_ultra_json)

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
                    lojas_map = {loja_especifica.codigo: loja_especifica.id}
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
                if not row or len(row) < 4:
                    continue
                
                try:
                    codigo_loja = str(row[0]).strip() if row[0] else ''
                    matricula = str(row[2]).strip() if row[2] else ''
                    nome = str(row[3]).strip() if row[3] else ''
                    setor = str(row[4]).strip() if row[4] else ''
                    
                    if not all([codigo_loja, matricula, nome, setor]):
                        erros.append(f"Linha {row_num}: Dados incompletos")
                        continue
                    
                    # Verifica se a loja existe no mapeamento (filtrado ou completo)
                    if codigo_loja not in lojas_map:
                        if loja_especifica_id:
                            # Se filtro por loja específica, pula linhas de outras lojas
                            continue
                        else:
                            erros.append(f"Linha {row_num}: Loja '{codigo_loja}' não encontrada")
                            continue
                    
                    loja_id = lojas_map[codigo_loja]
                    
                    # Verifica se colaborador já existe
                    colaborador_existente = Colaborador.query.filter_by(
                        matricula=matricula, 
                        loja_id=loja_id
                    ).first()
                    
                    if colaborador_existente:
                        # Atualiza dados
                        colaborador_existente.nome = nome
                        colaborador_existente.setor = setor
                        colaborador_existente.ultima_atualizacao = datetime.utcnow()
                        colaboradores_atualizados += 1
                    else:
                        # Cria novo colaborador
                        novo_colaborador = Colaborador(
                            matricula=matricula,
                            nome=nome,
                            setor=setor,
                            loja_id=loja_id,
                            apto=True,
                            ultima_atualizacao=datetime.utcnow()
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
            ultima_atualizacao=datetime.utcnow()
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
        colaborador.ultima_atualizacao = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Colaborador {colaborador.nome} atualizado com sucesso!', 'success')
        return redirect(url_for('admin.colaboradores'))
    
    return render_template('admin/colaborador_form.html', form=form, titulo='Editar Colaborador')

@admin_bp.route('/colaboradores/<int:id>/toggle')
@admin_required
def toggle_colaborador(id):
    """Ativar/desativar colaborador pelo admin"""
    colaborador = Colaborador.query.get_or_404(id)
    
    colaborador.apto = not colaborador.apto
    colaborador.ultima_atualizacao = datetime.utcnow()
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
    from app.forms.admin import LojaForm
    
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
    from app.forms.admin import LojaForm
    
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

@admin_bp.route('/lojas/<int:id>/toggle')
@admin_required
def toggle_loja(id):
    """Ativar/desativar loja"""
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