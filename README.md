# 🎬 Sistema de Endomarketing - Grupo Big Box Ultrabox - v1.3

![Status](https://img.shields.io/badge/Status-Desenvolvimento-yellow)
![Versão](https://img.shields.io/badge/Versão-1.3-blue)
![Testes](https://img.shields.io/badge/Testes-100%25-brightgreen)
![Grupo](https://img.shields.io/badge/Grupo-Big%20Box%20Ultrabox-orange)
![Instagram](https://img.shields.io/badge/Instagram-Sorteios-purple)

Sistema web completo para **endomarketing interno** do **Grupo Big Box Ultrabox**, gerenciando sorteios de lojas, colaboradores e **Instagram**. Desenvolvido com Flask, interface cinematográfica e otimizado para filmagem profissional. **Parceria Festival Na Praia 2025**.

## 🚀 Novidades da Versão 1.3

A versão 1.3 introduz o **Sistema de Sorteios Instagram**, complementando o sistema de endomarketing interno com funcionalidades avançadas para sorteios em redes sociais do Grupo Big Box Ultrabox.

### 📱 **Sistema de Sorteios Instagram**
- **Processamento de Comentários**: Upload e parsing automático de comentários do Instagram
- **Sistema de Tickets Ponderados**: Cada comentário gera tickets baseados em palavras-chave
- **Sorteio Cinematográfico**: Interface interativa com animações para filmagem
- **Gestão Completa**: CRUD completo para sorteios do Instagram
- **Configurações Flexíveis**: Palavras-chave e limites de tickets personalizáveis

### ✅ **Melhorias Técnicas**
- **Proteção CSRF**: Segurança reforçada com CSRFProtect
- **Testes Atualizados**: Novos testes para funcionalidades do Instagram
- **Interface Responsiva**: Layout adaptativo para todos os dispositivos
- **Código Otimizado**: Correções de importação e estrutura aprimorada

### 🎬 **Funcionalidades da v1.2 Mantidas**
- **Interface Cinematográfica** para filmagem profissional
- **Atualização Inteligente** com estados sempre sincronizados
- **Interface Polida** com dashboards contextuais e navegação premium
- **Visual Premium** com imagens reais dos prêmios e design responsivo

## 📋 Funcionalidades Principais

### 👨‍💼 **Admin (Administrador)**
- 🎲 Sorteio semanal de lojas (BIG e ULTRA)
- 🏆 Gestão completa de prêmios com imagens
- 👥 Gerenciamento de assistentes das lojas
- 📊 Dashboard com estatísticas em tempo real
- ⚙️ Configurações avançadas do sistema
- 📱 **Sorteios Instagram**: Criação, edição e gestão completa
- 🔧 **Configurações Instagram**: Palavras-chave e limites personalizáveis

### 🎯 **Assistente (Loja)**
- 🎲 Sorteio de colaboradores para prêmios
- 👤 Gestão de colaboradores da loja
- 📂 Upload em massa via Excel
- 📊 Dashboard com status da loja
- 🏆 Visualização de colaboradores sorteados

### 📱 **Sistema Instagram**
- 📤 **Upload de Comentários**: Processamento de arquivos de comentários
- 🎫 **Sistema de Tickets**: Geração automática baseada em palavras-chave
- 🎲 **Sorteio Interativo**: Interface cinematográfica para sorteio
- 👥 **Gestão de Participantes**: Lista completa com estatísticas
- 🏆 **Exibição de Ganhadores**: Resultados com links para perfis
- ⚙️ **Configurações**: Personalização de palavras-chave e limites

## 🎨 Interface Destacada

### 🎬 **Experiência Cinematográfica**
- Modais compactos que cabem em qualquer tela
- Resultado permanece visível para filmagem
- Animações suaves e profissionais
- Zero interrupções durante gravação
- **Layout 3-Colunas**: Informações, animação e resultados

### 📱 **Responsividade Total**
- Mobile: Layout single column otimizado
- Tablet: Grid adaptativo inteligente
- Desktop: Múltiplas colunas elegantes
- Todos dispositivos suportados

### 🎨 **Design Premium**
- Cards com gradientes animados
- Hover effects elegantes
- Border gradient no resultado
- Sparkle effects nos prêmios
- **Cores Personalizáveis**: Sistema de cores para ganhadores

## 🛠️ Tecnologias

- **Backend**: Python 3.8+ | Flask 2.3+
- **Frontend**: Bootstrap 5 | CSS3 Animado | JavaScript ES6
- **Banco**: SQLite (desenvolvimento) | PostgreSQL (produção)
- **Deploy**: Render.com ready
- **Testes**: `unittest` do Python
- **Upload**: Excel/XLSX suportado
- **Segurança**: CSRF Protection

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
- **Sorteios Instagram**: `/admin/instagram`
- **Configurações Instagram**: `/admin/instagram/config`
- **Festival**: `/festival`

## 📸 Recursos Visuais

### 🎬 **Para Filmagem**
- Resultado do sorteio permanece na tela
- Layout compacto cabe em qualquer resolução
- Animações profissionais e suaves
- Imagens reais dos prêmios
- **Layout 3-Colunas**: Organização visual otimizada

### 🎨 **Design Premium**
- Cards com gradientes animados
- Hover effects elegantes
- Border gradient no resultado
- Sparkle effects nos prêmios
- **Cores Dinâmicas**: Sistema de cores para ganhadores

## 🔧 Estrutura do Projeto

```
sorteioBigbox/
├── app/
│   ├── forms/          # Formulários WTForms
│   ├── models.py       # Modelos SQLAlchemy
│   ├── routes/         # Rotas organizadas
│   ├── static/         # CSS, JS, Imagens
│   └── templates/      # Templates Jinja2
│       ├── admin/      # Templates administrativos
│       └── partials/   # Componentes reutilizáveis
├── instance/           # Banco SQLite
├── tests/              # Testes automatizados (100% de sucesso)
├── uploads/            # Arquivos de upload
├── run.py              # Script principal
└── requirements.txt    # Dependências
```

## 📱 Como Usar o Sistema Instagram

### 1. **Configuração Inicial**
- Acesse `/admin/instagram/config`
- Configure palavra-chave padrão (ex: "eu quero")
- Defina limite máximo de tickets por usuário

### 2. **Criar Sorteio**
- Acesse `/admin/instagram/novo`
- Preencha informações do sorteio
- Defina número de ganhadores

### 3. **Processar Comentários**
- Faça upload do arquivo de comentários
- Sistema processa automaticamente
- Visualize estatísticas dos participantes

### 4. **Realizar Sorteio**
- Acesse a página do sorteio
- Clique em "Sortear Ganhadores"
- Interface cinematográfica executa o sorteio

### 5. **Visualizar Resultados**
- Ganhadores são exibidos com links para perfis
- Resultado permanece visível para filmagem
- Histórico completo disponível

## 🎯 Próximos Passos

Para desenvolvimento futuro:
- [ ] API REST para mobile
- [ ] Relatórios avançados PDF
- [ ] Notificações em tempo real
- [ ] Backup automático
- [ ] Multi-tenancy
- [ ] Integração com outras redes sociais

## 🏆 Créditos

Desenvolvido para **endomarketing interno** do **Grupo Big Box Ultrabox** com interface cinematográfica otimizada para filmagem profissional. **Parceria Festival Na Praia 2025**.

**Versão**: 1.3  
**Status**: Desenvolvimento  
**Última atualização**: Dezembro 2024

---

🎬 **Sistema de endomarketing completo do Grupo Big Box Ultrabox!** 🏆📱