# 🎬 Sistema de Sorteios BigBox & UltraBox v1.7
## Festival Na Praia 2025 - Edição Cinematográfica

![Sistema de Sorteios](https://img.shields.io/badge/Versão-1.7%20Final-success?style=for-the-badge)
![Framework](https://img.shields.io/badge/Flask-2.3.3-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Pronto%20para%20Produção-green?style=for-the-badge)

---

## 🎯 **O QUE É**

Sistema web completo para gerenciar sorteios de ingressos do **Festival Na Praia 2025**, desenvolvido com interface cinematográfica premium para filmagem dos sorteios.

### **✨ Funcionalidades Principais**
- 🏆 **Sorteio Semanal de Lojas** (1 BIG + 1 ULTRA)
- 🎲 **Sorteio de Colaboradores** com interface cinematográfica
- 👤 **Gestão de Assistentes** das lojas
- 📊 **Dashboards Intuitivos** para admin e assistentes
- 🎨 **Design Premium** otimizado para filmagem
- 📱 **100% Responsivo** (mobile, tablet, desktop)

---

## ⚡ **INÍCIO RÁPIDO**

```bash
# 1. Clonar e instalar
git clone https://github.com/seu-usuario/sorteioBigbox.git
cd sorteioBigbox
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Inicializar banco
python -c "from run import create_app; app = create_app(); app.cli.main(['init-db'], standalone_mode=False)"

# 3. Executar
python run.py
```

**🌐 Acesse:** http://localhost:5000  
**👨‍💼 Admin:** admin@bigbox.com / admin123

---

## 📋 **DOCUMENTAÇÃO COMPLETA**

**📖 Leia:** [`DOCUMENTACAO.md`](./DOCUMENTACAO.md)

A documentação única contém:
- 🛠️ **Instalação e Configuração Detalhada**
- 🚀 **Guia de Deploy em Produção (Render)**
- 👥 **Manual Completo do Usuário (Admin + Assistente)**
- 💻 **Manual Técnico (Arquitetura + APIs)**
- 🧪 **Testes e Checklist de Funcionalidades**
- 📞 **Suporte e Solução de Problemas**

---

## 🎬 **NOVIDADES DA v1.7**

### **🏆 Interface Cinematográfica**
- **Design Compacto**: Resultado otimizado para filmagem
- **Elementos Limpos**: Removidas mensagens desnecessárias
- **Confetti Premium**: 240 peças animadas em 3 ondas
- **Backdrop Filter**: Fundo elegante com blur

### **🔧 Correções Técnicas**
- **Rotas AJAX**: Endpoints funcionando (Status 200)
- **Reload Automático**: Atualização silenciosa pós-sorteio
- **Validações**: Formulários robustos sem loops
- **Responsividade**: Perfeita em todos dispositivos

### **👥 UX Melhorada**
- **Terminologia**: "Assistentes" em todo sistema
- **Senhas Inteligentes**: Gerador automático + interface protegida
- **Layout Harmonioso**: Grid responsivo e cards elegantes
- **Performance**: Carregamento rápido e animações suaves

---

## 🧪 **STATUS DOS TESTES**

### **✅ Sistema 100% Funcional**
- ✅ **Rotas**: Todas principais funcionando (200/302)
- ✅ **Banco**: 46 lojas ativas + dados consistentes
- ✅ **Sorteios**: Lojas e colaboradores operacionais
- ✅ **Autenticação**: Admin e assistentes funcionando
- ✅ **Responsividade**: Mobile, tablet, desktop
- ✅ **Cross-browser**: Chrome, Firefox, Safari, Edge

### **🔍 Funcionalidades Testadas**
- 🏆 Sorteio de lojas com resultado compacto
- 🎲 Sorteio de colaboradores cinematográfico
- 👤 Gestão de assistentes com senha inteligente
- 📁 Upload de colaboradores via Excel
- 🔄 Reload automático silencioso
- 📱 Interface responsiva premium

---

## 🚀 **DEPLOY RÁPIDO**

### **Production no Render:**
1. Push para GitHub
2. Conectar repositório no [Render](https://render.com)
3. Configurar PostgreSQL
4. Deploy automático via `render.yaml`
5. Executar `flask init-db` no shell

**Ver guia completo:** [`DOCUMENTACAO.md#deploy`](./DOCUMENTACAO.md#deploy)

---

## 🏗️ **ARQUITETURA**

```
sorteioBigBox/
├── app/
│   ├── routes/          # admin.py, auth.py, manager.py, main.py
│   ├── templates/       # HTML organizados por módulo
│   ├── static/          # CSS (2000+ linhas), JS, imagens
│   ├── forms/           # WTForms para validação
│   ├── models.py        # SQLAlchemy models
│   └── utils.py         # Utilitários
├── config.py            # Configurações
├── run.py              # Ponto de entrada + Gunicorn
├── requirements.txt     # Dependências
├── render.yaml         # Deploy automático
└── DOCUMENTACAO.md     # Documentação completa
```

---

## 📞 **SUPORTE**

### **🚨 Problemas Comuns:**
- **Reset do sistema**: `.\reset_to_v1.ps1`
- **Upload Excel**: Colunas C=Matrícula, D=Nome, E=Setor
- **Senha assistente**: Campo vazio mantém atual

### **🔗 Links Úteis:**
- **📖 Documentação:** [`DOCUMENTACAO.md`](./DOCUMENTACAO.md)
- **🐛 Issues:** [GitHub Issues](https://github.com/seu-usuario/sorteioBigbox/issues)
- **🚀 Deploy:** [Render.com](https://render.com)

---

## 🎉 **TECNOLOGIAS**

- **Backend:** Flask 2.3.3, SQLAlchemy, WTForms
- **Frontend:** Bootstrap 5, Vanilla JS, CSS3 Animations
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Deploy:** Render.com, Gunicorn
- **Compatibilidade:** Chrome, Firefox, Safari, Edge

---

**🏆 Sistema v1.7 Completo - Pronto para o Festival Na Praia 2025!**

*Desenvolvido com ❤️ para criar momentos inesquecíveis*