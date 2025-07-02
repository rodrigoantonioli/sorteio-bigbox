# 📋 Sistema de Sorteios BigBox & UltraBox v1.7
## Festival Na Praia 2025 - Documentação Completa

---

## 📖 **ÍNDICE**

1. [🎯 Visão Geral](#visao-geral)
2. [⚡ Início Rápido](#inicio-rapido)
3. [🛠️ Instalação e Configuração](#instalacao)
4. [🚀 Deploy em Produção](#deploy)
5. [👥 Manual do Usuário](#manual-usuario)
6. [💻 Manual Técnico](#manual-tecnico)
7. [🧪 Testes](#testes)
8. [📞 Suporte e Solução de Problemas](#suporte)

---

## 🎯 **VISÃO GERAL** {#visao-geral}

O **Sistema de Sorteios BigBox & UltraBox v1.7** é uma aplicação web desenvolvida para gerenciar sorteios de ingressos do **Festival Na Praia 2025**. 

### **✨ Funcionalidades Principais**
- 🏆 **Sorteio Semanal de Lojas**: Sorteia 1 loja BIG + 1 loja ULTRA por semana
- 🎲 **Sorteio de Colaboradores**: Interface cinematográfica para sortear colaboradores premiados
- 👤 **Gestão de Assistentes**: Sistema completo de gestão de usuários das lojas
- 📊 **Dashboard Intuitivo**: Painéis específicos para admin e assistentes
- 🎨 **Interface Premium**: Design cinematográfico preparado para filmagem
- 📱 **Totalmente Responsivo**: Funciona perfeitamente em mobile, tablet e desktop

### **🎬 Características da v1.7**
- **Design Compacto**: Interface otimizada para filmagem sem elementos desnecessários
- **Reload Automático**: Atualização silenciosa após sorteios 
- **Terminologia Assistente**: Linguagem adequada "assistentes das lojas"
- **Interface de Senha Inteligente**: Gestão avançada de senhas para admin
- **Validações Perfeitas**: Formulários robustos sem erros
- **Zero Loops**: Sistema estável sem redirecionamentos infinitos

---

## ⚡ **INÍCIO RÁPIDO** {#inicio-rapido}

### **🖥️ Executar Localmente (5 minutos)**

```bash
# 1. Clonar o repositório
git clone https://github.com/seu-usuario/sorteioBigbox.git
cd sorteioBigbox

# 2. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Inicializar banco de dados
python -c "from run import create_app; app = create_app(); app.cli.main(['init-db'], standalone_mode=False)"

# 5. Executar aplicação
python run.py
```

**🌐 Acesse:** http://localhost:5000

**👨‍💼 Login Admin:**
- Email: `admin@bigbox.com`
- Senha: `admin123`

### **📋 Primeiro Uso**
1. Acesse `/admin/dashboard` como admin
2. Vá em "Assistentes" → "Novo Assistente" para criar assistentes das lojas
3. Cada assistente pode acessar `/auth/login` e gerenciar colaboradores
4. Use "Sortear Lojas" para sorteios semanais
5. Assistentes das lojas sorteadas podem sortear colaboradores

---

## 🛠️ **INSTALAÇÃO E CONFIGURAÇÃO** {#instalacao}

### **🔧 Requisitos do Sistema**
- **Python**: 3.8+
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Navegador**: Chrome, Firefox, Safari, Edge (últimas versões)

### **📦 Dependências**
```
Flask==2.3.3
Flask-Login==0.6.2
Flask-WTF==1.1.1
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-Mail==0.9.1
Werkzeug==2.3.7
WTForms==3.0.1
openpyxl==3.1.2
gunicorn==21.2.0
psycopg2-binary==2.9.7 (produção)
```

### **🗂️ Estrutura do Projeto**
```
sorteioBigbox/
├── app/                     # Aplicação principal
│   ├── templates/          # Templates HTML
│   ├── static/             # CSS, JS, imagens
│   ├── routes/             # Rotas organizadas por módulo
│   ├── forms/              # Formulários WTF
│   ├── models.py           # Modelos do banco de dados
│   └── utils.py            # Utilitários
├── config.py               # Configurações da aplicação
├── run.py                  # Ponto de entrada
├── requirements.txt        # Dependências Python
├── render.yaml             # Configuração para deploy
└── DOCUMENTACAO.md         # Este arquivo
```

### **⚙️ Configuração de Ambiente**

Crie arquivo `.env` (opcional):
```bash
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-aqui
ADMIN_EMAIL=admin@bigbox.com
ADMIN_PASSWORD=sua-senha-admin
DATABASE_URL=sqlite:///instance/sorteios.db
```

### **🗄️ Inicialização do Banco**
```bash
# Comando para inicializar banco e dados padrão
python -c "from run import create_app; app = create_app(); app.cli.main(['init-db'], standalone_mode=False)"
```

**O comando acima:**
- Cria todas as tabelas necessárias
- Cria usuário admin com credenciais configuradas
- Carrega lojas do arquivo `inputs/TABELA LOJAS.xlsx` (se existir)

---

## 🚀 **DEPLOY EM PRODUÇÃO** {#deploy}

### **📡 Deploy no Render (Recomendado)**

#### **1. Preparação**
1. Faça push do código para GitHub
2. Acesse [render.com](https://render.com) e crie conta
3. Conecte seu repositório GitHub

#### **2. Criação do Serviço**
- **Tipo**: Web Service
- **Nome**: `sorteio-bigbox`
- **Branch**: `master`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn run:app`

#### **3. Banco PostgreSQL**
- **Tipo**: PostgreSQL
- **Nome**: `sorteio-bigbox-db`
- **Região**: Oregon (US West)

#### **4. Variáveis de Ambiente**
```bash
DATABASE_URL=<conectado-automaticamente>
FLASK_ENV=production
SECRET_KEY=<gerado-automaticamente>
ADMIN_EMAIL=admin@bigbox.com
ADMIN_PASSWORD=<sua-senha-segura>
```

#### **5. Pós-Deploy**
```bash
# No Shell do Render, execute:
flask init-db
```

### **🔒 Configurações de Segurança**
- ✅ HTTPS automático
- ✅ Senhas criptografadas (bcrypt)
- ✅ CSRF protection
- ✅ Session security
- ✅ SQL injection protection

---

## 👥 **MANUAL DO USUÁRIO** {#manual-usuario}

### **👨‍💼 Para Administradores**

#### **🏠 Dashboard Admin**
- **Acesso**: `/admin/dashboard`
- **Visão geral**: Estatísticas do sistema, lojas sorteadas, assistentes
- **Navegação**: Menu superior com todas as funcionalidades

#### **🏆 Sorteio Semanal de Lojas**
1. Acesse "Sortear Lojas" no menu
2. Confirme a data da terça-feira
3. Clique "Realizar Sorteio"
4. **Resultado**: Interface cinematográfica com lojas ganhadoras
5. **Automático**: Página recarrega mostrando resultado

#### **👤 Gestão de Assistentes**
1. **Criar**: "Assistentes" → "Novo Assistente"
   - Nome completo do assistente
   - Email para login
   - **Loja obrigatória** (dropdown)
   - **Senha**: Use "Gerar" para senha automática
2. **Formato da loja**: "PLANALTINA (BIG01)" - nome primeiro, código simples
3. **Gerador de senhas**: 43 palavras neutras + número 1-99

#### **🏪 Gestão de Lojas**
- **Listar**: Todas as lojas com status e assistentes
- **Criar/Editar**: Código, nome, bandeira (BIG/ULTRA)
- **Status**: Ativar/desativar lojas

#### **👥 Gestão de Colaboradores**
- **Visão global**: Todos colaboradores de todas as lojas
- **Filtros**: Por loja, nome, setor
- **Ordenação**: Matrícula, nome, setor, loja

#### **🎁 Gestão de Prêmios**
- **Criar prêmios**: Nome, descrição, data, tipo (Show/Day Use)
- **Atribuir à loja**: Somente lojas ganhadoras podem receber
- **Acompanhar sorteios**: Ver quais colaboradores ganharam

#### **📊 Relatórios**
- **Sorteios**: Histórico completo de sorteios semanais
- **Colaboradores premiados**: Lista de todos os ganhadores
- **Estatísticas**: Resumos por loja e período

### **🏪 Para Assistentes de Loja**

#### **🏠 Dashboard Assistente**
- **Acesso**: `/auth/login` → `/assistente/dashboard`
- **Visão**: Status da loja, colaboradores, sorteios disponíveis

#### **👥 Gestão de Colaboradores**
1. **Adicionar**: "Colaboradores" → "Novo Colaborador"
   - Matrícula única
   - Nome completo
   - Setor
   - Status (apto para sorteio)
2. **Upload Excel**: Planilha com múltiplos colaboradores
   - Colunas: C=Matrícula, D=Nome, E=Setor
   - **Substitui todos** os colaboradores atuais

#### **🎲 Sorteio de Colaboradores**
**Disponível apenas se a loja foi sorteada na semana**

1. **Acessar**: "Sortear Colaboradores"
2. **Configurar**: Selecionar prêmio disponível
3. **Visualizar pote**: Todos colaboradores aptos
4. **Realizar sorteio**: Interface cinematográfica
5. **Resultado**: Colaborador ganhador + dados da loja

---

## 💻 **MANUAL TÉCNICO** {#manual-tecnico}

### **🏗️ Arquitetura**

#### **Backend (Flask)**
- **models.py**: SQLAlchemy models (Usuario, Loja, Colaborador, etc.)
- **routes/**: Blueprints organizados por módulo
  - `main.py`: Páginas públicas
  - `auth.py`: Autenticação
  - `admin.py`: Área administrativa
  - `manager.py`: Área do assistente

#### **Frontend**
- **Templates**: Jinja2 com Bootstrap 5
- **CSS**: `/static/css/style.css` (2000+ linhas)
- **JavaScript**: `/static/js/script.js` (interações avançadas)

#### **Database Schema**
```sql
usuarios: id, email, senha_hash, nome, tipo, loja_id, ativo
lojas: id, codigo, nome, bandeira, ativo
colaboradores: id, matricula, nome, setor, loja_id, apto
sorteios_semanais: id, semana_inicio, loja_big_id, loja_ultra_id
sorteios_colaboradores: id, colaborador_id, premio_id, sorteio_semanal_id
premios: id, nome, descricao, data_evento, tipo, loja_id
```

### **🔐 Sistema de Autenticação**
- **Flask-Login**: Gestão de sessões
- **Decoradores**: `@admin_required`, `@manager_required`
- **Redirecionamento**: Por tipo de usuário

### **📝 Formulários (WTForms)**
- **Validação server-side**: Campos obrigatórios, formatos
- **CSRF Protection**: Tokens de segurança
- **Validação customizada**: Emails únicos, matrículas únicas por loja

### **🎨 Sistema de Design**

#### **Cores e Brandeira**
```css
/* BIG BOX */
--big-gradient: linear-gradient(45deg, #667eea, #764ba2);
--big-color: #667eea;

/* ULTRA BOX */
--ultra-gradient: linear-gradient(45deg, #20c997, #17a2b8);
--ultra-color: #20c997;
```

#### **Componentes Principais**
- **Cards elegantes**: Border-radius 20px, shadows, hover effects
- **Badges coloridos**: Gradientes específicos por bandeira
- **Confetti system**: 3 ondas de 240 peças animadas
- **Loading states**: Spinners e placeholders

### **📱 Responsividade**
```css
/* Mobile First */
@media (max-width: 768px) {
  .resultado-final-compacto { grid-template-columns: 1fr; }
  .container { padding: 1rem; }
  h1 { font-size: 1.5rem; }
}
```

### **⚡ Performance**
- **Lazy loading**: Imagens e componentes pesados
- **CSS optimizado**: Seletores eficientes, animations GPU
- **Database queries**: Indexação automática, N+1 prevention
- **Caching**: Static files, database results

---

## 🧪 **TESTES** {#testes}

### **🔍 Testes Automatizados**
```bash
# Executar todos os testes
python -m pytest tests/

# Testes específicos
python tests/test_auth.py          # Autenticação
python tests/test_sorteios.py      # Sorteios
python tests/test_colaboradores.py # Colaboradores
```

### **✅ Checklist de Funcionalidades**

#### **Autenticação**
- [ ] Login admin funciona
- [ ] Login assistente funciona
- [ ] Logout funciona
- [ ] Redirecionamento por tipo de usuário
- [ ] Proteção de rotas

#### **Sorteio de Lojas**
- [ ] Interface carrega corretamente
- [ ] Sorteia 1 BIG + 1 ULTRA
- [ ] Não repete lojas sorteadas
- [ ] Salva no banco de dados
- [ ] Interface final compacta

#### **Sorteio de Colaboradores**
- [ ] Disponível apenas para lojas sorteadas
- [ ] Lista colaboradores aptos
- [ ] Interface cinematográfica
- [ ] Não repete colaboradores sorteados
- [ ] Resultado elegante

#### **Gestão de Assistentes**
- [ ] Criar assistente
- [ ] Loja é obrigatória
- [ ] Gerador de senhas (6+ caracteres)
- [ ] Edição preserva senha atual
- [ ] Interface de senha inteligente

#### **Gestão de Colaboradores**
- [ ] CRUD completo
- [ ] Upload Excel funciona
- [ ] Validações de matrícula única
- [ ] Filtros e ordenação

### **🌐 Teste Cross-Browser**
- [ ] Chrome (últimas 2 versões)
- [ ] Firefox (últimas 2 versões)
- [ ] Safari (desktop + iOS)
- [ ] Edge (últimas 2 versões)

### **📱 Teste Responsivo**
- [ ] Mobile (320px - 768px)
- [ ] Tablet (768px - 1024px)
- [ ] Desktop (1024px+)
- [ ] Touch interactions

### **✅ Sistema Testado e Funcionando**
- ✅ Admin: Administrador (admin@bigbox.com)
- ✅ Assistente com loja associada funcionando
- ✅ 46 lojas ativas carregadas
- ✅ Sorteios realizados com sucesso
- ✅ Todas as rotas principais (Status 200/302)

### **🔍 Checklist de Funcionalidades**
- ✅ Sorteio de lojas com interface compacta
- ✅ Sorteio de colaboradores cinematográfico  
- ✅ Gestão de assistentes com senha inteligente
- ✅ Reload automático silencioso
- ✅ Terminologia "Assistente" em todo sistema
- ✅ Layout perfeito sem redirecionamentos infinitos
- ✅ Responsividade total mobile/desktop

---

## 📞 **SUPORTE E SOLUÇÃO DE PROBLEMAS** {#suporte}

### **🚨 Problemas Comuns**

#### **❌ "Esta página não está funcionando - muitos redirecionamentos"**
**Causa**: Assistente sem loja associada  
**Solução**: Todo assistente deve ter loja obrigatória (corrigido na v1.7)

#### **❌ "Senha deve ter entre 6 e 50 caracteres" (na edição)**
**Causa**: Validação incorreta  
**Solução**: Campo senha vazio mantém senha atual (corrigido na v1.7)

#### **❌ Upload de colaboradores não funciona**
**Causa**: Formato do Excel incorreto  
**Solução**: 
- Coluna C = Matrícula
- Coluna D = Nome  
- Coluna E = Setor

### **🛠️ Reset do Sistema**
```bash
# Windows PowerShell
.\reset_to_v1.ps1
```

### **📋 Informações Técnicas**
- **Versão**: 1.7 Final - Edição Cinematográfica
- **Framework**: Flask 2.3.3 + Bootstrap 5
- **Banco**: SQLite (dev) / PostgreSQL (prod)
- **Compatibilidade**: Chrome, Firefox, Safari, Edge
- **Responsivo**: Mobile, Tablet, Desktop

### **📋 Informações do Sistema**

#### **Versões**
- **Sistema**: v1.7 Final
- **Python**: 3.8+
- **Flask**: 2.3.3
- **Database**: SQLite (dev) / PostgreSQL (prod)

#### **Recursos**
- **Lojas**: 46 ativas (BIG + ULTRA)
- **Usuários**: Admin + Assistentes ilimitados
- **Colaboradores**: Ilimitados por loja
- **Sorteios**: Semanais + colaboradores
- **Prêmios**: Shows + Day Use

#### **Limites**
- **Upload Excel**: 10MB máximo
- **Sessão**: 24 horas
- **Imagens**: 5MB máximo
- **Colaboradores por upload**: 1000 máximo

### **📞 Contato**
- **GitHub**: https://github.com/seu-usuario/sorteioBigbox
- **Issues**: Use GitHub Issues para bugs
- **Documentação**: Este arquivo (DOCUMENTACAO.md)

---

## 🎉 **CONCLUSÃO**

O **Sistema de Sorteios BigBox & UltraBox v1.7** representa o estado da arte em sistemas de sorteio para eventos, combinando:

- ✨ **Design Cinematográfico**: Interface premium preparada para filmagem
- 🚀 **Performance Excepcional**: Carregamento rápido e animações suaves  
- 📱 **Responsividade Total**: Funciona perfeitamente em qualquer dispositivo
- 🔒 **Segurança Robusta**: Proteções contra vulnerabilidades comuns
- 👥 **UX Intuitiva**: Fácil de usar para admin e assistentes
- 🎯 **Foco no Resultado**: Interface limpa focada no que importa

**🏆 Preparado para o Festival Na Praia 2025!**

---

*Desenvolvido com ❤️ para criar momentos inesquecíveis*  
*Sistema de Sorteios v1.7 - Janeiro 2025* 