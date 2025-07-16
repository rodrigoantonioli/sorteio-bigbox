# 🤖 CLAUDE.md - Guia Completo para Assistentes de IA

## 📋 Visão Geral

O **Sistema de Endomarketing Grupo Big Box Ultrabox v1.4** é uma aplicação Flask robusta e completa para gerenciar sorteios internos de lojas, colaboradores e Instagram. Este documento fornece orientações específicas para assistentes de IA trabalharem eficientemente com o projeto.

## 🎯 Arquitetura do Sistema

### 🏗️ Estrutura Principal
```
sorteioBigbox/
├── app/
│   ├── models.py          # Modelos SQLAlchemy (7 tabelas principais)
│   ├── routes/            # Rotas organizadas por módulo
│   │   ├── admin.py       # Rotas administrativas (900+ linhas)
│   │   ├── auth.py        # Autenticação e autorização
│   │   ├── main.py        # Rotas públicas
│   │   └── manager.py     # Rotas de assistentes de loja
│   ├── forms/             # Formulários WTForms
│   ├── templates/         # Templates Jinja2 organizados
│   ├── static/            # Assets (CSS, JS, imagens)
│   └── utils.py           # Funções utilitárias
├── tests/                 # Suíte de testes completa (100% de sucesso)
├── migrations/            # Migrações Alembic
├── config.py              # Configurações por ambiente
└── run.py                 # Ponto de entrada da aplicação
```

### 🔑 Conceitos Chave

#### **Hierarquia de Usuários**
1. **Admin (`tipo: 'admin'`)**
   - Acesso total ao sistema
   - Gerencia usuários, lojas, prêmios
   - Realiza sorteios semanais de lojas
   - Gerencia sorteios Instagram

2. **Assistente (`tipo: 'assistente'`)**
   - Acesso restrito à sua loja
   - Gerencia colaboradores da loja
   - Realiza sorteios de colaboradores para prêmios

#### **Fluxo Principal de Negócio**
1. **Sorteio Semanal (Admin)** → Seleciona lojas ganhadoras (BIG e ULTRA)
2. **Atribuição de Prêmios (Admin)** → Vincula prêmios às lojas ganhadoras
3. **Sorteio de Colaboradores (Assistente)** → Sorteia colaboradores para prêmios

#### **Sistema Instagram (v1.4)**
- Processamento de comentários do Instagram
- Sistema de tickets ponderados
- Interface cinematográfica para sorteios
- Configurações personalizáveis
- Integração com Cloudinary para upload de imagens de prêmios
- Galeria de prêmios com visualização otimizada

## 🛠️ Comandos Essenciais

### 🚀 Inicialização
```bash
# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dependências
pip install -r requirements.txt

# Configuração inicial
cp .env.example .env  # Editar com suas configurações
flask init-db         # Inicializar banco e usuário admin

# Execução
python run.py
```

### 🧪 Testes
```bash
# Executar todos os testes
python tests/run_all_tests.py

# Teste específico
python -m unittest tests.test_models -v

# Teste com cobertura
python -m unittest discover -s tests -p "test_*.py" -v
```

### 🗄️ Banco de Dados
```bash
# Testar conexão
flask test-db

# Migrations
flask db migrate -m "Descrição"
flask db upgrade

# Reset completo (cuidado!)
flask db downgrade base
flask db upgrade
```

## 🔧 Tarefas Comuns para IAs

### 📝 Adicionando Nova Funcionalidade

#### 1. **Criar Modelo de Dados**
```python
# em app/models.py
class NovoModelo(db.Model):
    __tablename__ = 'nova_tabela'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    criado_em = db.Column(db.DateTime, default=get_brazil_datetime)
    
    def __repr__(self):
        return f'<NovoModelo {self.nome}>'
```

#### 2. **Criar Formulário**
```python
# em app/forms/admin.py ou app/forms/manager.py
class NovoModeloForm(FlaskForm):
    nome = StringField('Nome', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(min=2, max=100, message='Nome deve ter entre 2 e 100 caracteres')
    ])
    submit = SubmitField('Salvar')
```

#### 3. **Criar Rotas**
```python
# em app/routes/admin.py
@admin_bp.route('/novo-modelo')
@admin_required
def listar_novo_modelo():
    modelos = NovoModelo.query.all()
    return render_template('admin/novo_modelo_lista.html', modelos=modelos)

@admin_bp.route('/novo-modelo/criar', methods=['GET', 'POST'])
@admin_required
def criar_novo_modelo():
    form = NovoModeloForm()
    if form.validate_on_submit():
        modelo = NovoModelo(nome=form.nome.data)
        db.session.add(modelo)
        db.session.commit()
        flash('Modelo criado com sucesso!', 'success')
        return redirect(url_for('admin.listar_novo_modelo'))
    return render_template('admin/novo_modelo_form.html', form=form)
```

#### 4. **Criar Templates**
```html
<!-- em app/templates/admin/novo_modelo_form.html -->
{% extends "base.html" %}
{% block content %}
<form method="POST" enctype="multipart/form-data">
    {{ csrf_token() }}
    {{ form.hidden_tag() }}
    
    <div class="mb-3">
        {{ form.nome.label(class="form-label") }}
        {{ form.nome(class="form-control") }}
        {% if form.nome.errors %}
            <div class="text-danger">{{ form.nome.errors[0] }}</div>
        {% endif %}
    </div>
    
    {{ form.submit(class="btn btn-primary") }}
</form>
{% endblock %}
```

#### 5. **Criar Testes**
```python
# em tests/test_novo_modelo.py
import unittest
from app import create_app
from app.models import db, NovoModelo

class NovoModeloTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_criar_modelo(self):
        modelo = NovoModelo(nome='Teste')
        db.session.add(modelo)
        db.session.commit()
        
        self.assertEqual(modelo.nome, 'Teste')
        self.assertIsNotNone(modelo.criado_em)
```

### 🐛 Correção de Bugs

#### **Fluxo Recomendado**
1. **Identifique o problema** através dos logs ou testes
2. **Localize o código** usando a estrutura de pastas
3. **Crie teste que reproduza o bug**
4. **Implemente a correção**
5. **Valide com testes**
6. **Documente a correção**

#### **Exemplo de Correção CSRF**
```python
# Problema: Formulário sem token CSRF
# Solução: Adicionar token ao template
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <!-- resto do formulário -->
</form>
```

### 📊 Debugging e Monitoramento

#### **Logs Importantes**
```python
# Em desenvolvimento
app.logger.info(f"Usuário {current_user.email} realizou sorteio")
app.logger.error(f"Erro no sorteio: {str(e)}")

# Em produção
import logging
logging.basicConfig(level=logging.INFO)
```

#### **Queries Comuns**
```python
# Verificar sorteio da semana
sorteio_atual = SorteioSemanal.query.filter_by(
    semana_inicio=semana_inicio
).first()

# Colaboradores aptos de uma loja
colaboradores_aptos = Colaborador.query.filter_by(
    loja_id=loja_id, 
    apto=True
).all()

# Prêmios disponíveis para uma loja
premios_disponiveis = Premio.query.filter(
    Premio.ativo == True,
    Premio.data_evento >= date.today(),
    db.or_(Premio.loja_id == loja_id, Premio.loja_id.is_(None))
).all()
```

## 🎨 Frontend e Templates

### 🖼️ Sistema de Templates
```
templates/
├── base.html              # Layout principal
├── macros.html            # Macros reutilizáveis
├── admin/                 # Templates administrativos
│   ├── dashboard.html     # Dashboard admin
│   ├── sortear.html       # Sorteio de lojas (cinematográfico)
│   └── instagram_*.html   # Templates Instagram
├── manager/               # Templates assistentes
│   ├── dashboard.html     # Dashboard assistente
│   └── sortear.html       # Sorteio colaboradores
└── partials/              # Componentes reutilizáveis
```

### 🎬 Interface Cinematográfica
O sistema possui interface otimizada para filmagem:
- **Layout 3-colunas** para sorteios
- **Animações suaves** e profissionais
- **Resultado permanente** na tela
- **Responsividade total**

#### **Componentes Principais**
```javascript
// em app/static/js/script.js
class SorteioAnimado {
    constructor() {
        this.participantes = [];
        this.ganhadores = [];
    }
    
    // Animação "slot machine"
    animarSorteio() {
        // Lógica da animação
    }
    
    // Modal fullscreen
    criarModal() {
        // Criação do modal cinematográfico
    }
}
```

### 🎨 Estilos CSS
```css
/* em app/static/css/style.css */
.sorteio-layout {
    display: flex;
    height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.resultado-final-juncao {
    /* Transição final cinematográfica */
    .sorteio-col-central { display: none; }
    .sorteio-col-ficha, .sorteio-col-ganhadores { width: 50%; }
}
```

## 📱 Sistema Instagram

### 🔄 Fluxo Completo
1. **Configuração** → Definir palavras-chave e limites
2. **Criação** → Novo sorteio Instagram
3. **Processamento** → Upload/parse de comentários
4. **Participantes** → Visualização em cards
5. **Sorteio** → Interface cinematográfica
6. **Resultados** → Exibição permanente

### 🎯 Modelos Instagram
```python
# em app/models.py
class SorteioInstagram(db.Model):
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    palavra_chave = db.Column(db.String(100), nullable=False)
    max_tickets_por_pessoa = db.Column(db.Integer, default=30)
    quantidade_ganhadores = db.Column(db.Integer, default=1)
    sorteado = db.Column(db.Boolean, default=False)
    
class ParticipanteInstagram(db.Model):
    username = db.Column(db.String(100), nullable=False)
    nome_exibicao = db.Column(db.String(200))
    tickets = db.Column(db.Integer, default=0)
    ganhador = db.Column(db.Boolean, default=False)
```

### 🎨 Interface de Sorteio
```html
<!-- Layout 3-colunas gerado dinamicamente -->
<div class="sorteio-layout">
    <div class="sorteio-col-ficha">
        <!-- Ficha do sorteio -->
    </div>
    <div class="sorteio-col-central">
        <!-- Animação central -->
    </div>
    <div class="sorteio-col-ganhadores">
        <!-- Lista de ganhadores -->
    </div>
</div>
```

## 🔒 Segurança

### 🛡️ Proteções Implementadas
- **CSRF Protection** em todos os formulários
- **Controle de acesso** por decoradores
- **Validação de entrada** em formulários
- **Sanitização** de uploads de arquivos
- **Sessões seguras** com Flask-Login

### 🔐 Autenticação
```python
# Decoradores de proteção
@admin_required    # Apenas administradores
@manager_required  # Apenas assistentes
@login_required    # Usuários autenticados

# Verificação de propriedade
def verificar_loja_assistente(loja_id):
    if current_user.tipo == 'assistente':
        return current_user.loja_id == loja_id
    return True  # Admin tem acesso total
```

## 🧪 Testes

### 📊 Cobertura Atual
- **8 arquivos** de teste
- **100% de sucesso** nos testes
- **Todos os módulos** cobertos
- **Integração completa** testada

### 🎯 Categorias de Teste
```python
# Testes de modelo
class ModelsTestCase(unittest.TestCase):
    def test_usuario_model(self):
        # Testa criação, senha, etc.
        
# Testes de rota
class RoutesTestCase(unittest.TestCase):
    def test_admin_dashboard(self):
        # Testa acesso e funcionalidade
        
# Testes de integração
class IntegrationTestCase(unittest.TestCase):
    def test_fluxo_completo_sorteio(self):
        # Testa fluxo end-to-end
```

### 🔍 Executando Testes
```bash
# Todos os testes com relatório
python tests/run_all_tests.py

# Específicos
python -m unittest tests.test_models.ModelsTestCase.test_usuario_model -v

# Com falha rápida
python -m unittest tests.test_models --failfast
```

## 🚀 Deploy

### 🌐 Render.com (Configurado)
```yaml
# render.yaml
services:
  - type: web
    name: sorteio-bigbox
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn run:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: sorteio-db
          property: connectionString
```

### 🔧 Variáveis de Ambiente
```bash
# Obrigatórias
ADMIN_EMAIL=admin@exemplo.com
ADMIN_PASSWORD=senha_segura
DATABASE_URL=postgresql://...

# Opcionais
FLASK_ENV=production
SECRET_KEY=chave_super_secreta
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=email@gmail.com
MAIL_PASSWORD=senha_app
```

## 📈 Novidades da Versão 1.4

### 🎯 Principais Melhorias
1. **Integração Cloudinary** → Upload e gerenciamento de imagens de prêmios
2. **Galeria de Prêmios** → Visualização otimizada no dashboard do assistente
3. **Melhor UX** → Interface aprimorada para sorteios e modais
4. **Correções CSRF** → Proteção aprimorada em formulários POST
5. **Layout Responsivo** → Melhor experiência mobile
6. **Sistema de Fotos** → Gestão completa de imagens de prêmios

### 📸 Sistema de Fotos (v1.4)
```python
# Configuração Cloudinary
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# Upload de imagens
foto_url = upload_image_to_cloudinary(foto_file)
premio.foto_url = foto_url
```

### 🎨 Galeria de Prêmios
- **Cards responsivos** com imagens otimizadas
- **Links diretos** para sorteio de cada prêmio
- **Visualização aprimorada** no dashboard
- **Fallback gracioso** para prêmios sem foto

## 📈 Melhorias Futuras

### 🎯 Roadmap Sugerido
1. **API REST** para integração mobile
2. **Websockets** para atualizações em tempo real
3. **Relatórios PDF** avançados
4. **Backup automático** de dados
5. **Multi-tenancy** para outras empresas
6. **Integração outras redes sociais**

### 🔧 Refatorações Recomendadas
```python
# Separar lógica de negócio
class SorteioService:
    @staticmethod
    def sortear_lojas(semana_inicio):
        # Lógica de sorteio isolada
        
    @staticmethod
    def sortear_colaboradores(loja_id, premio_id):
        # Lógica de sorteio isolada
```

## 🤝 Contribuindo

### 📝 Padrões de Código
- **PEP 8** para Python
- **Templates** com indentação de 4 espaços
- **Commits** descritivos em português
- **Testes** obrigatórios para novas funcionalidades

### 🔄 Fluxo de Trabalho
1. **Criar branch** para funcionalidade
2. **Implementar** com testes
3. **Validar** com `python tests/run_all_tests.py`
4. **Criar PR** com descrição detalhada
5. **Merge** após revisão

### 📋 Checklist de PR
- [ ] Todos os testes passam
- [ ] Funcionalidade documentada
- [ ] CSRF protection implementado
- [ ] Controle de acesso verificado
- [ ] Templates responsivos
- [ ] Logs adequados

## 🆘 Troubleshooting

### 🐛 Problemas Comuns

#### **Erro CSRF Token Missing**
```python
# Solução: Adicionar token ao formulário
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

#### **Erro de Importação**
```python
# Verificar estrutura de imports
from app.models import db, Usuario
from app.utils import get_brazil_datetime
```

#### **Erro de Banco de Dados**
```bash
# Verificar conexão
flask test-db

# Recriar banco
flask db downgrade base
flask db upgrade
```

#### **Erro de Permissão**
```python
# Verificar decorador
@admin_required
def minha_funcao():
    # Código aqui
```

### 🔍 Debug Útil
```python
# Logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# Queries SQL
app.config['SQLALCHEMY_ECHO'] = True

# Variáveis de template
{{ debug() }}  # No template Jinja2
```

## 📚 Recursos Adicionais

### 📖 Documentação
- **README.md** → Visão geral e instalação
- **API_DOCUMENTATION.md** → Documentação técnica completa
- **AGENTS.md** → Guia específico para layout Instagram
- **INSTAGRAM_FEATURE.md** → Funcionalidades Instagram
- **tests/README.md** → Documentação de testes

### 🔗 Links Úteis
- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **WTForms**: https://wtforms.readthedocs.io/
- **Bootstrap 5**: https://getbootstrap.com/docs/5.0/
- **Jinja2**: https://jinja.palletsprojects.com/

---

## 🎯 Resumo para IAs

### ⚡ Comandos Rápidos
```bash
# Setup completo
git clone https://github.com/rodrigoantonioli/sorteio-bigbox.git
cd sorteio-bigbox
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
flask init-db
python run.py

# Desenvolvimento
python tests/run_all_tests.py  # Sempre antes de commit
flask test-db                  # Verificar banco
python run.py                  # Executar servidor
```

### 🎯 Pontos Críticos
1. **Sempre** adicionar token CSRF em formulários
2. **Sempre** usar decoradores de autenticação
3. **Sempre** testar funcionalidades novas
4. **Sempre** verificar controle de acesso
5. **Sempre** validar entrada de usuário

### 🚀 Próximos Passos
- Familiarize-se com a estrutura de pastas
- Execute os testes para entender o comportamento
- Teste o fluxo completo no navegador
- Explore os templates para entender o layout
- Leia o código das rotas principais

**Este é um sistema robusto e bem estruturado. Use esta documentação como referência para trabalhar eficientemente com o projeto!** 🎉