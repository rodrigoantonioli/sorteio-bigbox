# 🎬 Sistema de Endomarketing - Grupo Big Box Ultrabox

![Status](https://img.shields.io/badge/Status-Produção-green)
![Versão](https://img.shields.io/badge/Versão-1.3-blue)
![Testes](https://img.shields.io/badge/Testes-100%25-brightgreen)
![Flask](https://img.shields.io/badge/Flask-3.1.0-red)

Sistema web completo para **endomarketing interno** do **Grupo Big Box Ultrabox**, gerenciando sorteios de lojas, colaboradores e **Instagram**. Interface cinematográfica otimizada para filmagem profissional.

## 🚀 Funcionalidades

### 👨‍💼 **Admin**
- 🎲 Sorteio semanal de lojas (BIG e ULTRA)
- 🏆 Gestão de prêmios com imagens
- 👥 Gerenciamento de usuários
- 📱 Sorteios Instagram com interface cinematográfica
- 📊 Dashboard com estatísticas

### 🎯 **Assistente**
- 🎲 Sorteio de colaboradores para prêmios
- 👤 Gestão de colaboradores da loja
- 📂 Upload em massa via Excel
- 📊 Dashboard com status da loja

### 🎬 **Interface Cinematográfica**
- Layout 3-colunas otimizado para filmagem
- Animações suaves e profissionais
- Resultado permanece visível na tela
- Responsivo em todos os dispositivos

## 🛠️ Tecnologias

- **Backend**: Python 3.12+ | Flask 3.1+
- **Frontend**: Bootstrap 5 | JavaScript ES6
- **Banco**: SQLite/PostgreSQL
- **Deploy**: Render.com
- **Testes**: unittest (100% sucesso)

## ⚡ Instalação

```bash
# Clone e configure
git clone https://github.com/rodrigoantonioli/sorteio-bigbox.git
cd sorteio-bigbox
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# Configure ambiente (.env)
ADMIN_EMAIL=admin@exemplo.com
ADMIN_PASSWORD=sua_senha
FLASK_ENV=development

# Inicialize e execute
flask init-db
python run.py
```

## 🧪 Testes

```bash
python tests/run_all_tests.py
```

## 🌐 URLs Principais

- **Admin**: `/admin/dashboard`
- **Assistente**: `/assistente/dashboard`
- **Sorteio Lojas**: `/admin/sortear`
- **Instagram**: `/admin/instagram`

## 📚 Documentação

- **[CLAUDE.md](CLAUDE.md)** - Guia completo para desenvolvedores
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Referência técnica
- **[tests/README.md](tests/README.md)** - Documentação de testes

---

**Versão**: 1.3 | **Status**: Produção | **Grupo Big Box Ultrabox**