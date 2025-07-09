# API Documentation - Sistema de Sorteios

## Table of Contents
1. [Overview](#overview)
2. [Application Structure](#application-structure)
3. [Configuration](#configuration)
4. [Models](#models)
5. [Forms](#forms)
6. [Utilities](#utilities)
7. [Routes & API Endpoints](#routes--api-endpoints)
8. [CLI Commands](#cli-commands)
9. [Authentication & Authorization](#authentication--authorization)
10. [File Uploads](#file-uploads)
11. [Database Operations](#database-operations)
12. [Examples](#examples)

## Overview

This is a Flask-based web application for managing weekly store drawings and employee prize distributions. The system supports two types of stores (BIG and ULTRA) and manages weekly drawings where stores are selected, and then employees from winning stores are drawn for prizes.

### Key Features
- Weekly store drawings (BIG and ULTRA)
- Employee management per store
- Prize management and assignment
- User authentication and authorization
- File upload for employee data
- Dashboard for administrators and store assistants

## Application Structure

```
├── run.py                 # Application entry point
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── app/
│   ├── __init__.py       # App initialization
│   ├── extensions.py     # Flask extensions
│   ├── models.py         # Database models
│   ├── utils.py          # Utility functions
│   ├── forms/            # Form definitions
│   ├── routes/           # Route handlers
│   ├── templates/        # HTML templates
│   └── static/           # Static files
```

## Configuration

### Configuration Classes

#### `Config` (Base Configuration)
Base configuration class with common settings.

**Key Attributes:**
- `SECRET_KEY`: Application secret key
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `UPLOAD_FOLDER`: File upload directory
- `MAX_CONTENT_LENGTH`: Maximum file upload size (5MB)
- `ITEMS_PER_PAGE`: Pagination limit (20 items)

**Usage:**
```python
from config import Config
app.config.from_object(Config)
```

#### `DevelopmentConfig`
Development environment configuration with debug enabled.

#### `ProductionConfig`
Production environment configuration with security settings.

#### `TestingConfig`
Testing environment configuration with in-memory database.

### Configuration Functions

#### `get_config()`
Returns the appropriate configuration based on `FLASK_ENV` environment variable.

**Returns:** Configuration class instance

**Usage:**
```python
from config import get_config
config = get_config()
```

## Models

### User Management

#### `Usuario` Model
Represents system users (administrators and store assistants).

**Attributes:**
- `id`: Primary key
- `email`: Unique email address
- `senha_hash`: Hashed password
- `nome`: Full name
- `tipo`: User type ('admin' or 'assistente')
- `loja_id`: Associated store ID (for assistants)
- `ativo`: Active status
- `criado_em`: Creation timestamp

**Methods:**
```python
# Password management
usuario.set_password(password)
usuario.check_password(password)
```

**Usage:**
```python
from app.models import Usuario

# Create new user
user = Usuario(
    email='assistant@store.com',
    nome='John Doe',
    tipo='assistente',
    loja_id=1
)
user.set_password('secure_password')
db.session.add(user)
db.session.commit()

# Authenticate user
user = Usuario.query.filter_by(email='assistant@store.com').first()
if user and user.check_password('secure_password'):
    login_user(user)
```

#### `Loja` Model
Represents stores in the system.

**Attributes:**
- `id`: Primary key
- `codigo`: Unique store code
- `nome`: Store name
- `bandeira`: Store brand ('BIG' or 'ULTRA')
- `ativo`: Active status
- `criado_em`: Creation timestamp

**Usage:**
```python
from app.models import Loja

# Create new store
loja = Loja(
    codigo='BIG01 - 106 NORTE',
    nome='BIG Box 106 Norte',
    bandeira='BIG'
)
db.session.add(loja)
db.session.commit()
```

### Employee Management

#### `Colaborador` Model
Represents store employees.

**Attributes:**
- `id`: Primary key
- `matricula`: Employee ID (unique per store)
- `nome`: Full name
- `setor`: Department
- `loja_id`: Associated store ID
- `apto`: Eligible for drawings
- `ultima_atualizacao`: Last update timestamp

**Constraints:**
- Unique constraint on `(matricula, loja_id)` to prevent duplicate employee IDs within the same store

**Usage:**
```python
from app.models import Colaborador

# Add employee
colaborador = Colaborador(
    matricula='12345',
    nome='Maria Silva',
    setor='Vendas',
    loja_id=1
)
db.session.add(colaborador)
db.session.commit()
```

### Prize Management

#### `Premio` Model
Represents prizes available for drawings.

**Attributes:**
- `id`: Primary key
- `nome`: Prize name
- `descricao`: Description
- `data_evento`: Event date
- `tipo`: Prize type ('show' or 'day_use')
- `imagem`: Image filename
- `loja_id`: Associated store (optional)
- `ativo`: Active status
- `criado_em`: Creation timestamp
- `criado_por`: Creator user ID

**Methods:**
```python
# Get image URL
premio.get_imagem_url()
```

**Usage:**
```python
from app.models import Premio

# Create prize
premio = Premio(
    nome='Show Nacional',
    descricao='Ingresso para show',
    data_evento=date(2024, 12, 25),
    tipo='show',
    criado_por=1
)
db.session.add(premio)
db.session.commit()

# Get image URL
image_url = premio.get_imagem_url()
```

### Drawing Management

#### `SorteioSemanal` Model
Represents weekly store drawings.

**Attributes:**
- `id`: Primary key
- `semana_inicio`: Week start date (Tuesday)
- `loja_big_id`: Winning BIG store ID
- `loja_ultra_id`: Winning ULTRA store ID
- `data_sorteio`: Drawing timestamp
- `sorteado_por`: User who performed the drawing

**Usage:**
```python
from app.models import SorteioSemanal

# Create weekly drawing
sorteio = SorteioSemanal(
    semana_inicio=date(2024, 1, 2),  # Tuesday
    loja_big_id=1,
    loja_ultra_id=2,
    sorteado_por=1
)
db.session.add(sorteio)
db.session.commit()
```

#### `SorteioColaborador` Model
Represents employee drawings for prizes.

**Attributes:**
- `id`: Primary key
- `sorteio_semanal_id`: Associated weekly drawing ID
- `premio_id`: Prize ID
- `colaborador_id`: Winning employee ID
- `data_sorteio`: Drawing timestamp
- `sorteado_por`: User who performed the drawing
- `lista_confirmada`: List confirmation status
- `colaboradores_snapshot`: Employee list snapshot

**Usage:**
```python
from app.models import SorteioColaborador

# Create employee drawing
sorteio_colab = SorteioColaborador(
    sorteio_semanal_id=1,
    premio_id=1,
    colaborador_id=1,
    sorteado_por=1
)
db.session.add(sorteio_colab)
db.session.commit()
```

## Forms

### Authentication Forms

#### `LoginForm`
Form for user authentication.

**Fields:**
- `email`: Email address (required, email validation)
- `password`: Password (required, min 6 characters)
- `remember_me`: Remember login checkbox

**Usage:**
```python
from app.forms.auth import LoginForm

form = LoginForm()
if form.validate_on_submit():
    # Process login
    user = Usuario.query.filter_by(email=form.email.data).first()
    if user and user.check_password(form.password.data):
        login_user(user, remember=form.remember_me.data)
```

### Admin Forms

#### `SorteioSemanalForm`
Form for creating weekly store drawings.

**Fields:**
- `semana_inicio`: Week start date (required)

#### `UsuarioForm`
Form for creating/editing users.

**Fields:**
- `nome`: Full name (required, 2-100 characters)
- `email`: Email address (required, email validation)
- `loja_id`: Associated store (required for assistants)
- `password`: Password (optional, 6-50 characters)

#### `PremioForm`
Form for creating/editing prizes.

**Fields:**
- `nome`: Prize name (required, 2-100 characters)
- `descricao`: Description (optional, max 500 characters)
- `data_evento`: Event date (required)
- `tipo`: Prize type - 'show' or 'day_use' (required)
- `imagem`: Image file (optional, JPG/PNG only)

#### `LojaForm`
Form for creating/editing stores.

**Fields:**
- `codigo`: Store code (required, 2-50 characters)
- `nome`: Store name (required, 2-100 characters)
- `bandeira`: Store brand - 'BIG' or 'ULTRA' (required)
- `ativo`: Active status checkbox

### Manager Forms

#### `UploadColaboradoresForm`
Form for uploading employee Excel files.

**Fields:**
- `arquivo`: Excel file (required, .xlsx/.xls only)
- `substituir_todos`: Replace all employees checkbox

#### `ColaboradorForm`
Form for creating/editing employees.

**Fields:**
- `matricula`: Employee ID (required, 1-20 characters)
- `nome`: Full name (required, 2-100 characters)
- `setor`: Department (required, 2-50 characters)
- `loja_id`: Store (optional, for admin use)
- `apto`: Eligible for drawings checkbox

#### `SorteioColaboradorForm`
Form for drawing employees for prizes.

**Fields:**
- `premio_id`: Prize selection (required)
- `confirmar_lista`: List confirmation checkbox (required)

## Utilities

### Date/Time Utilities

#### `get_brazil_datetime()`
Returns current datetime in Brazil timezone (GMT-3).

**Returns:** `datetime` object

**Usage:**
```python
from app.utils import get_brazil_datetime

current_time = get_brazil_datetime()
```

#### `get_brazil_date()`
Returns current date in Brazil timezone.

**Returns:** `date` object

**Usage:**
```python
from app.utils import get_brazil_date

today = get_brazil_date()
```

#### `format_brazil_datetime(dt)`
Formats datetime for Brazilian display format.

**Parameters:**
- `dt`: datetime object

**Returns:** Formatted string (dd/mm/yyyy HH:MM:SS)

**Usage:**
```python
from app.utils import format_brazil_datetime

formatted = format_brazil_datetime(datetime.now())
# Returns: "25/12/2024 14:30:00"
```

#### `format_brazil_date(dt)`
Formats date for Brazilian display format.

**Parameters:**
- `dt`: date object

**Returns:** Formatted string (dd/mm/yyyy)

**Usage:**
```python
from app.utils import format_brazil_date

formatted = format_brazil_date(date.today())
# Returns: "25/12/2024"
```

## Routes & API Endpoints

### Main Routes

#### `GET /`
**Purpose:** Home page - redirects authenticated users to dashboard or shows public showcase

**Response:** HTML template or redirect

**Usage:**
```python
# Redirects to appropriate dashboard based on user type
# Shows public showcase for unauthenticated users
```

#### `GET /festival`
**Purpose:** Festival page - always shows drawing results

**Response:** HTML template with drawing data

#### `GET /sobre`
**Purpose:** About page

**Response:** HTML template

### Authentication Routes

#### `GET/POST /auth/login`
**Purpose:** User login

**Methods:** GET, POST

**Form:** `LoginForm`

**Response:** 
- GET: Login form
- POST: Redirect to dashboard or requested page

**Usage:**
```python
# POST data
{
    "email": "user@example.com",
    "password": "password123",
    "remember_me": true
}
```

#### `GET /auth/logout`
**Purpose:** User logout

**Authentication:** Required

**Response:** Redirect to home page

### Admin Routes

#### `GET /admin/dashboard`
**Purpose:** Admin dashboard with statistics

**Authentication:** Required (admin only)

**Response:** HTML template with dashboard data

#### `GET/POST /admin/sortear`
**Purpose:** Weekly store drawing

**Authentication:** Required (admin only)

**Form:** `SorteioSemanalForm`

**Response:** Drawing form or redirect

#### `POST /admin/sortear/ajax`
**Purpose:** AJAX endpoint for store drawing

**Authentication:** Required (admin only)

**Request Body:**
```json
{
    "semana_inicio": "2024-01-02"
}
```

**Response:**
```json
{
    "success": true,
    "loja_big": "BIG01 - 106 NORTE",
    "loja_ultra": "ULTRA02 - ASA SUL"
}
```

#### `POST /admin/sortear/verificar`
**Purpose:** Check if drawing exists for week

**Authentication:** Required (admin only)

**Request Body:**
```json
{
    "semana_inicio": "2024-01-02"
}
```

**Response:**
```json
{
    "existe": true,
    "mensagem": "Sorteio já realizado para esta semana"
}
```

#### `GET /admin/usuarios`
**Purpose:** List all users

**Authentication:** Required (admin only)

**Response:** HTML template with user list

#### `GET/POST /admin/usuarios/novo`
**Purpose:** Create new user

**Authentication:** Required (admin only)

**Form:** `UsuarioForm`

#### `GET/POST /admin/usuarios/<id>/editar`
**Purpose:** Edit user

**Authentication:** Required (admin only)

**Form:** `UsuarioForm`

#### `GET /admin/usuarios/<id>/toggle`
**Purpose:** Toggle user active status

**Authentication:** Required (admin only)

#### `GET /admin/usuarios/<id>/excluir`
**Purpose:** Delete user

**Authentication:** Required (admin only)

#### `GET /admin/premios`
**Purpose:** List all prizes

**Authentication:** Required (admin only)

**Response:** HTML template with prize list

#### `GET/POST /admin/premios/novo`
**Purpose:** Create new prize

**Authentication:** Required (admin only)

**Form:** `PremioForm`

#### `GET/POST /admin/premios/<id>/editar`
**Purpose:** Edit prize

**Authentication:** Required (admin only)

**Form:** `PremioForm`

#### `GET/POST /admin/premios/<id>/atribuir`
**Purpose:** Assign prize to store

**Authentication:** Required (admin only)

**Form:** `AtribuirPremioForm`

#### `POST /admin/premios/<id>/desatribuir`
**Purpose:** Remove prize from store

**Authentication:** Required (admin only)

#### `POST /admin/premios/<id>/excluir`
**Purpose:** Delete prize

**Authentication:** Required (admin only)

#### `GET /admin/sorteios`
**Purpose:** List all drawings

**Authentication:** Required (admin only)

**Response:** HTML template with drawing history

#### `POST /admin/sorteios/resetar-pote`
**Purpose:** Reset store drawing pot

**Authentication:** Required (admin only)

#### `GET /admin/sorteios/semanal/<id>/excluir`
**Purpose:** Delete weekly drawing

**Authentication:** Required (admin only)

#### `GET /admin/sorteios/colaborador/<id>/excluir`
**Purpose:** Delete employee drawing

**Authentication:** Required (admin only)

#### `GET /admin/colaboradores`
**Purpose:** List all employees

**Authentication:** Required (admin only)

**Response:** HTML template with employee list

#### `GET/POST /admin/colaboradores/upload`
**Purpose:** Upload employee Excel file

**Authentication:** Required (admin only)

**Form:** `UploadColaboradoresForm`

#### `GET/POST /admin/colaboradores/adicionar`
**Purpose:** Add single employee

**Authentication:** Required (admin only)

**Form:** `ColaboradorForm`

#### `GET/POST /admin/colaboradores/<id>/editar`
**Purpose:** Edit employee

**Authentication:** Required (admin only)

**Form:** `ColaboradorForm`

#### `GET/POST /admin/colaboradores/<id>/toggle`
**Purpose:** Toggle employee eligibility

**Authentication:** Required (admin only)

#### `GET /admin/colaboradores/<id>/excluir`
**Purpose:** Delete employee

**Authentication:** Required (admin only)

#### `POST /admin/colaboradores/acoes-lote`
**Purpose:** Bulk employee actions

**Authentication:** Required (admin only)

**Request Body:**
```json
{
    "acao": "ativar",
    "colaboradores": [1, 2, 3]
}
```

#### `GET /admin/lojas`
**Purpose:** List all stores

**Authentication:** Required (admin only)

**Response:** HTML template with store list

#### `GET/POST /admin/lojas/adicionar`
**Purpose:** Add new store

**Authentication:** Required (admin only)

**Form:** `LojaForm`

#### `GET/POST /admin/lojas/<id>/editar`
**Purpose:** Edit store

**Authentication:** Required (admin only)

**Form:** `LojaForm`

#### `GET/POST /admin/lojas/<id>/toggle`
**Purpose:** Toggle store active status

**Authentication:** Required (admin only)

#### `GET /admin/lojas/<id>/excluir`
**Purpose:** Delete store

**Authentication:** Required (admin only)

#### `GET /admin/configuracoes`
**Purpose:** System configuration page

**Authentication:** Required (admin only)

#### `POST /admin/configuracoes/reset-completo`
**Purpose:** Complete system reset

**Authentication:** Required (admin only)

### Manager Routes

#### `GET /assistente/dashboard`
**Purpose:** Store assistant dashboard

**Authentication:** Required (assistant only)

**Response:** HTML template with store-specific data

#### `GET /assistente/colaboradores`
**Purpose:** List store employees

**Authentication:** Required (assistant only)

**Query Parameters:**
- `sort`: Sort field ('nome', 'matricula', 'setor')
- `order`: Sort order ('asc', 'desc')

**Response:** HTML template with employee list

#### `GET/POST /assistente/colaboradores/novo`
**Purpose:** Add new employee

**Authentication:** Required (assistant only)

**Form:** `ColaboradorForm`

#### `GET/POST /assistente/colaboradores/<id>/editar`
**Purpose:** Edit employee

**Authentication:** Required (assistant only)

**Form:** `ColaboradorForm`

#### `GET /assistente/colaboradores/<id>/toggle`
**Purpose:** Toggle employee eligibility

**Authentication:** Required (assistant only)

#### `GET /assistente/colaboradores/<id>/excluir`
**Purpose:** Delete employee

**Authentication:** Required (assistant only)

#### `POST /assistente/colaboradores/acao-lote`
**Purpose:** Bulk employee actions

**Authentication:** Required (assistant only)

#### `GET/POST /assistente/colaboradores/upload`
**Purpose:** Upload employee Excel file

**Authentication:** Required (assistant only)

**Form:** `UploadColaboradoresForm`

#### `GET/POST /assistente/sortear`
**Purpose:** Draw employees for prizes

**Authentication:** Required (assistant only)

**Form:** `SorteioColaboradorForm`

#### `POST /assistente/sortear/ajax`
**Purpose:** AJAX endpoint for employee drawing

**Authentication:** Required (assistant only)

**Request Body:**
```json
{
    "premio_id": 1,
    "confirmar_lista": true
}
```

**Response:**
```json
{
    "success": true,
    "colaborador": {
        "nome": "João Silva",
        "matricula": "12345",
        "setor": "Vendas"
    },
    "premio": {
        "nome": "Show Nacional",
        "tipo": "show"
    }
}
```

## CLI Commands

### Database Commands

#### `flask init-db`
**Purpose:** Initialize database and create admin user

**Usage:**
```bash
flask init-db
```

**Actions:**
- Creates all database tables
- Creates admin user from environment variables
- Loads stores from Excel file (if available)

**Environment Variables Required:**
- `ADMIN_EMAIL`: Admin email address
- `ADMIN_PASSWORD`: Admin password

#### `flask test-db`
**Purpose:** Test database connection

**Usage:**
```bash
flask test-db
```

**Output:**
- Database connection status
- Table list
- Record counts

## Authentication & Authorization

### User Types

1. **Admin (`tipo: 'admin'`)**
   - Full system access
   - Can manage all entities
   - Can perform weekly store drawings
   - Can create/edit users

2. **Assistant (`tipo: 'assistente'`)**
   - Store-specific access
   - Can manage store employees
   - Can perform employee drawings
   - Limited to assigned store

### Decorators

#### `@admin_required`
Ensures only admin users can access the route.

**Usage:**
```python
from app.routes.admin import admin_required

@admin_bp.route('/admin-only')
@admin_required
def admin_only_route():
    return "Admin only content"
```

#### `@manager_required`
Ensures only assistant users can access the route.

**Usage:**
```python
from app.routes.manager import manager_required

@manager_bp.route('/assistant-only')
@manager_required
def assistant_only_route():
    return "Assistant only content"
```

## File Uploads

### Supported Formats
- **Excel Files:** `.xlsx`, `.xls` (for employee data)
- **Images:** `.jpg`, `.jpeg`, `.png` (for prize images)

### Upload Limits
- **Maximum File Size:** 5MB
- **Upload Directory:** `uploads/` (temporary files)
- **Image Directory:** `app/static/images/premios/` (permanent storage)

### File Processing

#### Employee Excel Upload
The system automatically detects Excel file formats:

**Format 1 (5 columns):**
- A: Store Unit
- B: Brand
- C: Employee ID
- D: Name
- E: Department

**Format 2 (6+ columns):**
- A: Branch
- B: Store Unit
- C: Brand
- D: Employee ID
- E: Name
- F: Department

**Usage:**
```python
# Upload via form
form = UploadColaboradoresForm()
if form.validate_on_submit():
    file = form.arquivo.data
    # Process file automatically
```

#### Image Upload
Images are automatically processed and stored with unique filenames.

**Usage:**
```python
# Upload via form
form = PremioForm()
if form.validate_on_submit():
    image = form.imagem.data
    if image:
        filename = save_premio_image(image)
        premio.imagem = filename
```

## Database Operations

### Relationships

#### User-Store Relationship
```python
# User belongs to one store (for assistants)
usuario.loja = db.relationship('Loja', backref='usuarios')
```

#### Store-Employee Relationship
```python
# Store has many employees
colaborador.loja = db.relationship('Loja', backref='colaboradores')
```

#### Prize Relationships
```python
# Prize belongs to creator and optional store
premio.criador = db.relationship('Usuario', backref='premios_criados')
premio.loja = db.relationship('Loja', backref='premios_disponiveis')
```

#### Drawing Relationships
```python
# Weekly drawing relationships
sorteio_semanal.loja_big = db.relationship('Loja', foreign_keys=[loja_big_id])
sorteio_semanal.loja_ultra = db.relationship('Loja', foreign_keys=[loja_ultra_id])
sorteio_semanal.sorteador = db.relationship('Usuario', foreign_keys=[sorteado_por])

# Employee drawing relationships
sorteio_colaborador.sorteio_semanal = db.relationship('SorteioSemanal')
sorteio_colaborador.premio = db.relationship('Premio')
sorteio_colaborador.colaborador = db.relationship('Colaborador')
sorteio_colaborador.sorteador = db.relationship('Usuario', foreign_keys=[sorteado_por])
```

### Common Queries

#### Get Active Stores
```python
lojas_ativas = Loja.query.filter_by(ativo=True).all()
```

#### Get Store Employees
```python
colaboradores = Colaborador.query.filter_by(
    loja_id=loja_id,
    apto=True
).all()
```

#### Get Available Prizes
```python
premios_disponiveis = Premio.query.filter(
    Premio.ativo == True,
    Premio.data_evento >= date.today(),
    db.or_(Premio.loja_id == loja_id, Premio.loja_id.is_(None))
).all()
```

#### Get Weekly Drawing
```python
sorteio_atual = SorteioSemanal.query.order_by(
    SorteioSemanal.semana_inicio.desc()
).first()
```

#### Get Employee Drawings
```python
sorteios_colaboradores = SorteioColaborador.query.join(
    Colaborador
).filter(
    SorteioColaborador.sorteio_semanal_id == sorteio_id,
    Colaborador.loja_id == loja_id
).all()
```

## Examples

### Complete User Creation Flow

```python
from app.models import Usuario, Loja
from app.extensions import db

# 1. Create store
loja = Loja(
    codigo='BIG01 - 106 NORTE',
    nome='BIG Box 106 Norte',
    bandeira='BIG'
)
db.session.add(loja)
db.session.commit()

# 2. Create assistant user
assistant = Usuario(
    email='assistant@big01.com',
    nome='João Silva',
    tipo='assistente',
    loja_id=loja.id
)
assistant.set_password('secure123')
db.session.add(assistant)
db.session.commit()
```

### Weekly Drawing Process

```python
from app.models import SorteioSemanal, Loja
from app.utils import get_brazil_datetime
import random

# 1. Get all active stores by brand
lojas_big = Loja.query.filter_by(bandeira='BIG', ativo=True).all()
lojas_ultra = Loja.query.filter_by(bandeira='ULTRA', ativo=True).all()

# 2. Randomly select winners
loja_big_vencedora = random.choice(lojas_big)
loja_ultra_vencedora = random.choice(lojas_ultra)

# 3. Create weekly drawing
sorteio = SorteioSemanal(
    semana_inicio=date(2024, 1, 2),  # Tuesday
    loja_big_id=loja_big_vencedora.id,
    loja_ultra_id=loja_ultra_vencedora.id,
    data_sorteio=get_brazil_datetime(),
    sorteado_por=admin_user.id
)
db.session.add(sorteio)
db.session.commit()
```

### Employee Drawing Process

```python
from app.models import SorteioColaborador, Colaborador, Premio
from app.utils import get_brazil_datetime
import random

# 1. Get eligible employees from winning store
colaboradores_aptos = Colaborador.query.filter_by(
    loja_id=loja_vencedora.id,
    apto=True
).all()

# 2. Get available prizes
premios_disponiveis = Premio.query.filter(
    Premio.ativo == True,
    Premio.data_evento >= date.today(),
    db.or_(Premio.loja_id == loja_vencedora.id, Premio.loja_id.is_(None))
).all()

# 3. Draw employee for each prize
for premio in premios_disponiveis:
    if colaboradores_aptos:
        colaborador_sorteado = random.choice(colaboradores_aptos)
        
        sorteio = SorteioColaborador(
            sorteio_semanal_id=sorteio_semanal.id,
            premio_id=premio.id,
            colaborador_id=colaborador_sorteado.id,
            data_sorteio=get_brazil_datetime(),
            sorteado_por=assistant_user.id
        )
        db.session.add(sorteio)
        
        # Remove selected employee from pool
        colaboradores_aptos.remove(colaborador_sorteado)

db.session.commit()
```

### File Upload Processing

```python
import openpyxl
from app.models import Colaborador

def process_employee_file(file_path, loja_id, substituir_todos=False):
    """Process employee Excel file"""
    
    if substituir_todos:
        # Remove all existing employees
        Colaborador.query.filter_by(loja_id=loja_id).delete()
    
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    
    # Detect format automatically
    formato = detectar_formato_planilha(sheet)
    
    colaboradores_criados = 0
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not row or len(row) < formato['min_colunas']:
            continue
            
        matricula = str(row[formato['col_matricula']]).strip()
        nome = str(row[formato['col_nome']]).strip()
        setor = str(row[formato['col_setor']]).strip()
        
        if matricula and nome and setor:
            # Check for existing employee
            existente = Colaborador.query.filter_by(
                matricula=matricula,
                loja_id=loja_id
            ).first()
            
            if not existente:
                colaborador = Colaborador(
                    matricula=matricula,
                    nome=nome,
                    setor=setor,
                    loja_id=loja_id
                )
                db.session.add(colaborador)
                colaboradores_criados += 1
    
    workbook.close()
    db.session.commit()
    return colaboradores_criados
```

### API Response Examples

#### Successful Drawing Response
```json
{
    "success": true,
    "message": "Sorteio realizado com sucesso!",
    "data": {
        "loja_big": {
            "id": 1,
            "nome": "BIG Box 106 Norte",
            "codigo": "BIG01 - 106 NORTE"
        },
        "loja_ultra": {
            "id": 5,
            "nome": "UltraBox ASA SUL",
            "codigo": "ULTRA02 - ASA SUL"
        },
        "semana_inicio": "2024-01-02"
    }
}
```

#### Error Response
```json
{
    "success": false,
    "message": "Erro ao realizar sorteio",
    "error": "Semana já possui sorteio realizado"
}
```

#### Employee Drawing Response
```json
{
    "success": true,
    "colaborador": {
        "id": 123,
        "nome": "Maria Silva",
        "matricula": "12345",
        "setor": "Vendas"
    },
    "premio": {
        "id": 1,
        "nome": "Show Nacional",
        "tipo": "show",
        "data_evento": "2024-12-25"
    }
}
```

This comprehensive documentation covers all public APIs, functions, and components of the Flask application. The system provides a complete solution for managing weekly store drawings and employee prize distributions with proper authentication, authorization, and data management capabilities.