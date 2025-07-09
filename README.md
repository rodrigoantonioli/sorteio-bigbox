# 🎬 Sistema de Sorteios Festival Na Praia 2025 - v1.2

![Status](https://img.shields.io/badge/Status-Desenvolvimento-yellow)
![Versão](https://img.shields.io/badge/Versão-1.2-blue)
![Testes](https://img.shields.io/badge/Testes-100%25-brightgreen)
![Festival](https://img.shields.io/badge/Festival-Na%20Praia%202025-orange)

Sistema web completo para gerenciamento de sorteios de lojas e colaboradores do **Festival Na Praia 2025**, desenvolvido com Flask, interface cinematográfica e otimizado para filmagem profissional.

## 🚀 Novidades da Versão 1.2

A versão 1.2 foca em robustez, qualidade de código e confiabilidade, garantindo que o sistema esteja mais estável do que nunca.

### ✅ **Suíte de Testes Completa**
- **100% de Sucesso**: Todos os 54 testes automatizados passam, garantindo a estabilidade das funcionalidades existentes.
- **Cobertura Abrangente**: Testes cobrem Models, Views e Controllers para todas as funcionalidades críticas do sistema.
- **Segurança Reforçada**: Remoção de senhas e dados sensíveis do código-fonte.
- **Código Limpo**: Eliminação de arquivos e scripts desnecessários, reduzindo a complexidade do projeto.

### 🎬 **Funcionalidades da v1.1 Mantidas**
- **Interface Cinematográfica** para filmagem profissional.
- **Atualização Inteligente** com estados sempre sincronizados.
- **Interface Polida** com dashboards contextuais e navegação premium.
- **Visual Premium** com imagens reais dos prêmios e design responsivo.

## 📋 Funcionalidades Principais

### 👨‍💼 **Admin (Administrador)**
- 🎲 Sorteio semanal de lojas (BIG e ULTRA)
- 🏆 Gestão completa de prêmios com imagens
- 👥 Gerenciamento de assistentes das lojas
- 📊 Dashboard com estatísticas em tempo real
- ⚙️ Configurações avançadas do sistema

### 🎯 **Assistente (Loja)**
- 🎲 Sorteio de colaboradores para prêmios
- 👤 Gestão de colaboradores da loja
- 📂 Upload em massa via Excel
- 📊 Dashboard com status da loja
- 🏆 Visualização de colaboradores sorteados

## 🎨 Interface Destacada

### 🎬 **Experiência Cinematográfica**
- Modais compactos que cabem em qualquer tela
- Resultado permanece visível para filmagem
- Animações suaves e profissionais
- Zero interrupções durante gravação

### 📱 **Responsividade Total**
- Mobile: Layout single column otimizado
- Tablet: Grid adaptativo inteligente
- Desktop: Múltiplas colunas elegantes
- Todos dispositivos suportados

## 🛠️ Tecnologias

- **Backend**: Python 3.8+ | Flask 2.3+
- **Frontend**: Bootstrap 5 | CSS3 Animado | JavaScript ES6
- **Banco**: SQLite (desenvolvimento) | PostgreSQL (produção)
- **Deploy**: Render.com ready
- **Testes**: `unittest` do Python
- **Upload**: Excel/XLSX suportado

## ⚡ Instalação Rápida

1. **Clone o repositório**
```bash
git clone https://github.com/rodrigoantonioli/sorteioBigbox.git
cd sorteioBigbox
```

2. **Configure ambiente**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. **Configure variáveis**
```bash
# Crie arquivo .env
ADMIN_EMAIL=admin@festival.com
ADMIN_PASSWORD=suasenha123
FLASK_ENV=development
```

4. **Inicialize banco**
```bash
flask init-db
```

5. **Execute sistema**
```bash
python run.py
```

## ✅ Executando os Testes

Para garantir a integridade do sistema, execute a suíte de testes completa:

```bash
python tests/run_all_tests.py
```

## 🌐 URLs Principais

- **Dashboard Admin**: `/admin/dashboard`
- **Dashboard Assistente**: `/assistente/dashboard`
- **Sorteio Lojas**: `/admin/sortear`
- **Sorteio Colaboradores**: `/assistente/sortear`
- **Festival**: `/festival`

## 📸 Recursos Visuais

### 🎬 **Para Filmagem**
- Resultado do sorteio permanece na tela
- Layout compacto cabe em qualquer resolução
- Animações profissionais e suaves
- Imagens reais dos prêmios

### 🎨 **Design Premium**
- Cards com gradientes animados
- Hover effects elegantes
- Border gradient no resultado
- Sparkle effects nos prêmios

## 🔧 Estrutura do Projeto

```
sorteioBigbox/
├── app/
│   ├── forms/          # Formulários WTForms
│   ├── models.py       # Modelos SQLAlchemy
│   ├── routes/         # Rotas organizadas
│   ├── static/         # CSS, JS, Imagens
│   └── templates/      # Templates Jinja2
├── instance/           # Banco SQLite
├── tests/              # Testes automatizados (100% de sucesso)
├── run.py              # Script principal
└── requirements.txt    # Dependências
```

## 🎯 Próximos Passos

Para desenvolvimento futuro:
- [ ] API REST para mobile
- [ ] Relatórios avançados PDF
- [ ] Notificações em tempo real
- [ ] Backup automático
- [ ] Multi-tenancy

## 🏆 Créditos

Desenvolvido especialmente para o **Festival Na Praia 2025** com interface cinematográfica otimizada para filmagem profissional.

**Versão**: 1.2  
**Status**: Desenvolvimento  
**Última atualização**: Julho 2025

---

🎬 **Sistema pronto para filmagem do Festival Na Praia 2025!** 🏆