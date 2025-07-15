# 📚 Referência Técnica - Sistema de Sorteios

## 📋 Sumário
1. [Modelos](#modelos)
2. [Rotas Principais](#rotas-principais)
3. [Formulários](#formulários)
4. [Utilitários](#utilitários)
5. [Configuração](#configuração)
6. [Exemplos de Uso](#exemplos-de-uso)

## 🗄️ Modelos

### Usuários e Autenticação

#### `Usuario`
```python
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128))
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'admin' | 'assistente'
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'))
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=get_brazil_datetime)
    
    def set_password(self, password):
        """Define senha hash"""
    
    def check_password(self, password):
        """Verifica senha"""
```

#### `Loja`
```python
class Loja(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    bandeira = db.Column(db.String(10), nullable=False)  # 'BIG' | 'ULTRA'
    ativo = db.Column(db.Boolean, default=True)
```

### Colaboradores e Prêmios

#### `Colaborador`
```python
class Colaborador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(20), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(50), nullable=False)
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'))
    apto = db.Column(db.Boolean, default=True)
    
    # Constraint: matricula única por loja
    __table_args__ = (db.UniqueConstraint('matricula', 'loja_id'),)
```

#### `Premio`
```python
class Premio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    data_evento = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'show' | 'day_use'
    imagem = db.Column(db.String(100))
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'))
    
    def get_imagem_url(self):
        """Retorna URL da imagem ou padrão"""
```

### Sorteios

#### `SorteioSemanal`
```python
class SorteioSemanal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semana_inicio = db.Column(db.Date, nullable=False, unique=True)
    loja_big_id = db.Column(db.Integer, db.ForeignKey('lojas.id'))
    loja_ultra_id = db.Column(db.Integer, db.ForeignKey('lojas.id'))
    data_sorteio = db.Column(db.DateTime, default=get_brazil_datetime)
    sorteado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
```

#### `SorteioColaborador`
```python
class SorteioColaborador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sorteio_semanal_id = db.Column(db.Integer, db.ForeignKey('sorteios_semanais.id'))
    premio_id = db.Column(db.Integer, db.ForeignKey('premios.id'))
    colaborador_id = db.Column(db.Integer, db.ForeignKey('colaboradores.id'))
    data_sorteio = db.Column(db.DateTime, default=get_brazil_datetime)
    sorteado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    colaboradores_snapshot = db.Column(db.Text)  # Lista de colaboradores no momento
```

### Sistema Instagram

#### `SorteioInstagram`
```python
class SorteioInstagram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    palavra_chave = db.Column(db.String(100), nullable=False)
    max_tickets_por_pessoa = db.Column(db.Integer, default=30)
    quantidade_ganhadores = db.Column(db.Integer, default=1)
    sorteado = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=get_brazil_datetime)
```

#### `ParticipanteInstagram`
```python
class ParticipanteInstagram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sorteio_id = db.Column(db.Integer, db.ForeignKey('sorteios_instagram.id'))
    username = db.Column(db.String(100), nullable=False)
    nome_exibicao = db.Column(db.String(200))
    tickets = db.Column(db.Integer, default=0)
    ganhador = db.Column(db.Boolean, default=False)
```

## 🛣️ Rotas Principais

### Autenticação

#### `POST /auth/login`
```python
# Form: email, password, remember_me
# Response: Redirect to dashboard
```

#### `GET /auth/logout`
```python
# Response: Redirect to home
```

### Admin - Sorteios

#### `GET/POST /admin/sortear`
```python
# GET: Formulário de sorteio semanal
# POST: Realiza sorteio de lojas
```

#### `POST /admin/sortear/ajax`
```python
# Request: {"semana_inicio": "2024-01-02"}
# Response: {"success": true, "loja_big": "BIG01", "loja_ultra": "ULTRA01"}
```

### Admin - CRUD

#### `GET /admin/usuarios`
```python
# Response: Lista de usuários
```

#### `POST /admin/usuarios/novo`
```python
# Form: UsuarioForm
# Response: Redirect após criação
```

#### `GET /admin/premios`
```python
# Response: Lista de prêmios
```

#### `POST /admin/premios/<id>/atribuir`
```python
# Form: AtribuirPremioForm
# Response: Prêmio atribuído à loja
```

### Assistente - Colaboradores

#### `GET /assistente/colaboradores`
```python
# Query: ?sort=nome&order=asc
# Response: Lista de colaboradores da loja
```

#### `POST /assistente/colaboradores/upload`
```python
# Form: arquivo Excel
# Response: Colaboradores importados
```

#### `POST /assistente/sortear/ajax`
```python
# Request: {"premio_id": 1, "confirmar_lista": true}
# Response: {"success": true, "colaborador": {...}, "premio": {...}}
```

### Instagram

#### `GET /admin/instagram`
```python
# Response: Lista de sorteios Instagram
```

#### `POST /admin/instagram/novo`
```python
# Form: SorteioInstagramForm + arquivo comentários
# Response: Sorteio criado e participantes processados
```

#### `GET /admin/instagram/<id>/participantes`
```python
# Response: Interface de sorteio cinematográfico
```

#### `POST /admin/instagram/sorteio/<id>/salvar`
```python
# Request: {"ganhadores": [{"username": "user1"}, ...]}
# Response: {"success": true}
```

## 📝 Formulários

### WTForms Principais

#### `LoginForm`
```python
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')
```

#### `SorteioSemanalForm`
```python
class SorteioSemanalForm(FlaskForm):
    semana_inicio = DateField('Semana (terça-feira)', validators=[DataRequired()])
    submit = SubmitField('Sortear Lojas')
```

#### `ColaboradorForm`
```python
class ColaboradorForm(FlaskForm):
    matricula = StringField('Matrícula', validators=[DataRequired(), Length(1, 20)])
    nome = StringField('Nome', validators=[DataRequired(), Length(2, 100)])
    setor = StringField('Setor', validators=[DataRequired(), Length(2, 50)])
    apto = BooleanField('Apto para sorteios')
    submit = SubmitField('Salvar')
```

## 🔧 Utilitários

### Funções de Data/Hora
```python
from app.utils import get_brazil_datetime, get_brazil_date, format_brazil_datetime

# Datetime atual no Brasil (GMT-3)
now = get_brazil_datetime()

# Data atual no Brasil
today = get_brazil_date()

# Formatação brasileira
formatted = format_brazil_datetime(now)  # "25/12/2024 14:30:00"
```

### Upload de Arquivos
```python
def allowed_file(filename, extensions):
    """Verifica extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def save_secure_file(file, upload_folder):
    """Salva arquivo com nome seguro"""
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return filepath
```

### Processamento Instagram
```python
def parse_instagram_comments(content, palavra_chave):
    """Processa comentários e retorna participantes"""
    # Retorna: [(username, nome_exibicao, tickets), ...]
```

## ⚙️ Configuração

### Classes de Configuração
```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    UPLOAD_FOLDER = 'uploads'
    ITEMS_PER_PAGE = 20

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
```

### Variáveis de Ambiente
```bash
# Obrigatórias
ADMIN_EMAIL=admin@exemplo.com
ADMIN_PASSWORD=senha_segura
DATABASE_URL=postgresql://user:pass@host:port/db

# Opcionais
FLASK_ENV=production
SECRET_KEY=chave_secreta
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=email@gmail.com
MAIL_PASSWORD=senha_app
```

## 💡 Exemplos de Uso

### Criar Usuário Programaticamente
```python
from app.models import Usuario, Loja, db

# Criar loja
loja = Loja(codigo='BIG01 - 106 NORTE', nome='BIG Box 106 Norte', bandeira='BIG')
db.session.add(loja)
db.session.commit()

# Criar assistente
user = Usuario(
    email='assistente@big01.com',
    nome='João Silva',
    tipo='assistente',
    loja_id=loja.id
)
user.set_password('senha123')
db.session.add(user)
db.session.commit()
```

### Realizar Sorteio Semanal
```python
from app.models import SorteioSemanal, Loja
import random

# Obter lojas ativas
lojas_big = Loja.query.filter_by(bandeira='BIG', ativo=True).all()
lojas_ultra = Loja.query.filter_by(bandeira='ULTRA', ativo=True).all()

# Sortear
loja_big = random.choice(lojas_big)
loja_ultra = random.choice(lojas_ultra)

# Salvar sorteio
sorteio = SorteioSemanal(
    semana_inicio=date(2024, 1, 2),
    loja_big_id=loja_big.id,
    loja_ultra_id=loja_ultra.id,
    sorteado_por=current_user.id
)
db.session.add(sorteio)
db.session.commit()
```

### Processar Upload de Colaboradores
```python
import openpyxl
from app.models import Colaborador

def processar_excel_colaboradores(file_path, loja_id):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    
    count = 0
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if len(row) >= 4:
            matricula = str(row[2]).strip()
            nome = str(row[3]).strip()
            setor = str(row[4]).strip() if len(row) > 4 else 'Geral'
            
            # Verificar se já existe
            existente = Colaborador.query.filter_by(
                matricula=matricula, loja_id=loja_id
            ).first()
            
            if not existente:
                colaborador = Colaborador(
                    matricula=matricula,
                    nome=nome,
                    setor=setor,
                    loja_id=loja_id
                )
                db.session.add(colaborador)
                count += 1
    
    db.session.commit()
    return count
```

### Consultas Comuns
```python
# Sorteio mais recente
sorteio_atual = SorteioSemanal.query.order_by(
    SorteioSemanal.semana_inicio.desc()
).first()

# Colaboradores aptos de uma loja
colaboradores_aptos = Colaborador.query.filter_by(
    loja_id=loja_id, apto=True
).all()

# Prêmios disponíveis para sorteio
premios_disponiveis = Premio.query.filter(
    Premio.ativo == True,
    Premio.data_evento >= date.today(),
    db.or_(Premio.loja_id == loja_id, Premio.loja_id.is_(None))
).all()

# Estatísticas do dashboard
total_usuarios = Usuario.query.filter_by(ativo=True).count()
total_lojas = Loja.query.filter_by(ativo=True).count()
total_colaboradores = Colaborador.query.filter_by(apto=True).count()
```

---

**Para documentação completa de desenvolvimento, consulte [CLAUDE.md](CLAUDE.md)**