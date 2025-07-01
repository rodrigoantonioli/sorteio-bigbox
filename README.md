# 🎲 Sistema de Sorteios Big Box & UltraBox v1.0.0

## 📋 Descrição

Sistema web completo para gerenciamento de sorteios semanais de ingressos do Festival Na Praia para colaboradores das lojas Big Box e UltraBox. 

### ✨ Funcionalidades Principais

- **Sorteios Semanais de Lojas**: Sistema automático que sorteia 1 loja BIG e 1 loja ULTRA por semana
- **Gerenciamento de Colaboradores**: Upload via Excel e gerenciamento individual
- **Sistema de Prêmios**: Cadastro e atribuição de prêmios específicos por loja ou gerais
- **Controle de Usuários**: Sistema com administrador e assistentes das lojas
- **Histórico Completo**: Acompanhamento de todos os sorteios realizados
- **Interface Responsiva**: Design moderno e amigável

### 🔧 Funcionalidades Administrativas

#### Zona Verde (Operações Seguras)
- ✅ Gerenciamento de Lojas
- ✅ Gerenciamento de Usuários Assistentes
- ✅ Gerenciamento de Prêmios
- ✅ Upload de Colaboradores via Excel
- ✅ Histórico de Sorteios

#### Zona Vermelha (Operações Perigosas)
- ⚠️ **Resetar Pote de Lojas**: Remove todos os sorteios permitindo que todas as lojas participem novamente
- 🚨 **Reset Completo**: Remove TODOS os dados exceto lojas e administrador

### 🏗️ Arquitetura

```
sorteioBigbox/
├── app/                    # Aplicação principal
│   ├── models.py          # Modelos de dados (5 tabelas)
│   ├── extensions.py      # Extensões Flask
│   ├── forms/            # Formulários WTForms
│   ├── routes/           # Rotas organizadas por módulo
│   ├── templates/        # Templates Jinja2
│   └── static/           # CSS, JS e assets
├── config.py             # Configurações
├── run.py               # Arquivo principal
├── requirements.txt     # Dependências
└── render.yaml         # Configuração para deploy
```

### 📊 Modelos de Dados

1. **usuarios**: Administradores e assistentes
2. **lojas**: Lojas BIG e ULTRA 
3. **colaboradores**: Funcionários aptos para sorteios
4. **sorteios_semanais**: Sorteios de lojas por semana
5. **sorteios_colaboradores**: Sorteios individuais de prêmios

### 🚀 Instalação e Configuração

#### Desenvolvimento Local

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/sorteio-bigbox.git
cd sorteio-bigbox

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure variáveis de ambiente
set FLASK_APP=run.py
set FLASK_ENV=development
set SECRET_KEY=sua-chave-secreta-aqui

# 4. Execute a aplicação
python run.py
```

#### Deploy no Render

1. Conecte seu repositório GitHub ao Render
2. Use as configurações do `render.yaml`
3. Configure as variáveis de ambiente:
   - `SECRET_KEY`
   - `DATABASE_URL` (PostgreSQL)
   - `MAIL_*` (configurações de email)

### 📧 Configuração de Email

Para envio de notificações, configure:

```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-app
```

### 👥 Usuários Padrão

**Administrador:**
- Email: admin@bigbox.com.br
- Senha: BigBox2025!

### 📁 Upload de Colaboradores

O sistema aceita planilhas Excel (.xlsx/.xls) com o formato:
- **Coluna A**: Código da Loja
- **Coluna C**: Matrícula
- **Coluna D**: Nome
- **Coluna E**: Setor

### 🔒 Segurança

- ✅ Autenticação por sessão
- ✅ Proteção CSRF
- ✅ Validação de formulários
- ✅ Controle de acesso por roles
- ✅ Confirmações para operações perigosas

### 🎨 Interface

- **Bootstrap 5**: Framework CSS responsivo
- **Font Awesome**: Ícones
- **JavaScript**: Animações de sorteio
- **Design Moderno**: Interface intuitiva e profissional

### 📱 Responsividade

- ✅ Desktop (1200px+)
- ✅ Tablet (768px - 1199px)
- ✅ Mobile (< 768px)

### 📈 Estatísticas

O sistema fornece estatísticas em tempo real:
- Total de lojas, colaboradores e prêmios
- Sorteios realizados
- Colaboradores por loja
- Histórico completo

### 🆔 Versão

**v1.0.0** - Sistema completo e funcional
- ✅ Todas as funcionalidades implementadas
- ✅ Interface totalmente responsiva
- ✅ Sistema de configurações avançadas
- ✅ Zona vermelha para operações administrativas
- ✅ Pronto para produção

### 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

### 📝 Licença

Este projeto é proprietário da Big Box & UltraBox.

### 🐛 Suporte

Para suporte técnico, entre em contato com a equipe de desenvolvimento.

---

**Desenvolvido com ❤️ para Big Box & UltraBox** 