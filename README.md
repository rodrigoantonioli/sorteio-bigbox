# 🎬 Sistema de Sorteios Big Box & UltraBox v1.7

**Sistema web cinematográfico para sorteios do Festival Na Praia 2025** 🚀

Sistema completo para gerenciar sorteios entre lojas Big Box e UltraBox, com **interface premium de nível hollywoodiano** e experiência de usuário sofisticada.

## ✨ Funcionalidades

### 🏪 Gestão de Lojas
- Interface visual com status de assistentes e colaboradores
- Dashboard informativo com estatísticas em tempo real
- Cadastro e edição de lojas BIG Box e UltraBox

### 🎁 Sistema de Prêmios
- Pool geral de prêmios disponíveis
- Atribuição controlada a lojas ganhadoras
- Sorteios individuais por assistente de loja
- Histórico completo de ganhadores

### 👥 Gestão de Colaboradores
- Upload via planilha Excel para importação em massa
- Cadastro individual com validações
- Controle de aptidão para participar dos sorteios

### 🎬 Sorteios Cinematográficos v1.7
- **Interface Premium**: Experiência visual de alto nível com animações sofisticadas
- **Pote Elegante**: Cards de colaboradores com avatar, hover effects e shimmer
- **Resultado Compacto**: Design harmonioso que se encaixa perfeitamente na tela
- **Confetti Dinâmico**: 3 ondas de 240 peças coloridas com rotação complexa
- **Loja em Destaque**: Informações da loja integradas ao resultado final
- Sorteio semanal automático de lojas (1 BIG + 1 ULTRA)
- Algoritmo que evita repetições recentes

### 🔐 Controle de Acesso
- **Administrador**: Acesso total ao sistema
- **Assistente**: Acesso apenas à sua loja específica

## 🛠️ Instalação

### Requisitos
- Python 3.8+
- SQLite (desenvolvimento) / PostgreSQL (produção)

### Setup Local
```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/sorteioBigbox.git
cd sorteioBigbox

# 2. Crie ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Execute a aplicação
python run.py
```

**Login inicial:**
- Email: `admin@bigbox.com.br`
- Senha: `BigBox2025!`

## 🎯 Como Usar

### Administrador
1. Cadastre lojas Big Box e UltraBox
2. Crie usuários assistentes para cada loja
3. Faça upload de colaboradores via Excel
4. Configure prêmios no sistema
5. Execute sorteios semanais

### Assistente de Loja
1. Acesse com suas credenciais
2. Visualize prêmios disponíveis para sua loja
3. Execute sorteios entre colaboradores aptos

## 📊 Fluxo de Prêmios
```
1. Admin cria prêmio → Pool geral
2. Admin atribui prêmio → Loja ganhadora
3. Assistente sorteia → Colaborador ganhador
4. Sistema registra → Histórico completo
```

## 🎨 Interface Cinematográfica v1.7
- **Design Premium**: Gradientes específicos, backdrop-filter e sombras profissionais
- **Animações Sofisticadas**: Float, pulse, shimmer, hover effects e confetti dinâmico
- **Layout Responsivo**: Grid adaptativo perfeito em desktop, tablet e mobile
- **Compatibilidade Total**: Safari, Chrome, Firefox com prefixos webkit
- Bootstrap 5 responsivo com classes customizadas elegantes
- Cards informativos com estatísticas visuais impactantes

## 🔒 Segurança
- Autenticação por sessão
- Proteção CSRF
- Controle de acesso por roles
- Validação robusta de dados

## 📋 Upload de Colaboradores

Planilhas Excel (.xlsx/.xls) com formato:
- **Coluna A**: Código da Loja
- **Coluna C**: Matrícula do Colaborador
- **Coluna D**: Nome Completo
- **Coluna E**: Setor

## 🚀 Deploy Render.com
1. Fork este repositório
2. Conecte ao Render.com
3. Use configuração do `render.yaml`
4. Configure variáveis de ambiente

---

**Desenvolvido para Festival Na Praia 2025**

**Sistema de Sorteios v1.7** 🎬  
*Edição Cinematográfica Premium* ✨ 