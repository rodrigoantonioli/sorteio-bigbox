# 🎯 Sistema de Sorteios - Big Box & UltraBox

Sistema web completo para gerenciar sorteios semanais de ingressos do **Festival Na Praia** para colaboradores das lojas Big Box e UltraBox.

## 🚀 Funcionalidades Principais

### 🎲 Sorteios Semanais
- Sorteio automático de **1 loja BIG + 1 loja ULTRA** por semana
- Histórico completo de todos os sorteios realizados
- Interface intuitiva para visualização dos resultados
- Admin pode excluir sorteios quando necessário

### 👥 Gerenciamento Completo de Colaboradores
- **Upload de planilhas Excel** que **SUBSTITUI TODOS** os colaboradores da loja
- **Proteção automática** para colaboradores com histórico de sorteios
- **CRUD completo**: Criar, Editar, Ativar/Desativar, Excluir
- Listagem com filtros e controles por loja
- Relatórios detalhados de cada operação

### 🎁 Sistema de Prêmios
- **Cadastro de prêmios** pelo admin baseado no comunicado oficial
- Prêmios configuráveis: Shows e Day Use
- Gerentes selecionam prêmios específicos para cada sorteio
- Controle de prêmios ativos/inativos

### 🎯 Sorteios de Colaboradores
- **Sistema de confirmação obrigatória** antes do sorteio
- Seleção de prêmios cadastrados pelo admin
- Snapshot da lista de colaboradores no momento do sorteio
- Histórico individual de participações
- Transparência total: quem sorteou, quando, quantos participaram

## 🛡️ Comportamento Especial: Upload de Colaboradores

### ⚠️ IMPORTANTE: O upload SEMPRE substitui TODOS os colaboradores da loja específica

**✅ Como funciona:**
- Remove **TODOS** os colaboradores atuais da loja do gerente
- **PROTEGE automaticamente** colaboradores que já participaram de sorteios
- Adiciona os novos colaboradores da planilha
- Gera relatório detalhado do que foi feito
- Afeta **APENAS** a loja do gerente logado

**📊 Exemplo:**
```
Antes: 50 colaboradores na loja
Upload: 30 colaboradores novos
Resultado: 32 colaboradores (30 novos + 2 protegidos com histórico)
```

Veja detalhes completos no [📋 Guia de Upload](GUIA_UPLOAD_COLABORADORES.md).

## 🎯 Prêmios Disponíveis (Festival Na Praia 2025)

1. **Show Sexta - Alcione** (05/07/2025)
2. **Show Sábado - Wesley Safadão** (06/07/2025)
3. **Day Use Sábado** (06/07/2025)
4. **Show Domingo - Vintage Culture** (07/07/2025)
5. **Day Use Domingo** (07/07/2025)

## 🛠️ Tecnologias

- **Backend**: Python Flask 3.0+
- **Banco de Dados**: SQLite com SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5)
- **Autenticação**: Flask-Login com sessões seguras
- **Upload**: Pandas para processamento de planilhas Excel

## 🚀 Instalação e Execução

### 1. Clone o repositório
```bash
git clone https://github.com/rodrigoantonioli/sorteioBigbox.git
cd sorteioBigbox
```

### 2. Ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale dependências
```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação
```bash
python run.py
```

### 5. Acesse o sistema
- **URL**: http://127.0.0.1:5000
- **Admin**: admin@bigbox.com / BigBox2025!
- **Gerente**: gerente@big106norte.com / gerente123

## 🎯 Fluxo de Trabalho

### 1. **Admin** (Configuração)
- Gerencia usuários e lojas
- Cadastra e edita prêmios
- Realiza sorteios semanais de lojas
- Controla todos os sorteios realizados

### 2. **Gerente** (Operação)
- Faz upload de colaboradores (substitui todos)
- Gerencia colaboradores (CRUD completo)
- Realiza sorteios de colaboradores
- Confirma listas antes dos sorteios

### 3. **Público** (Transparência)
- Visualiza histórico completo
- Acompanha resultados em tempo real
- Acessa informações sobre prêmios

## 📚 Documentação

- [📋 Guia de Upload de Colaboradores](GUIA_UPLOAD_COLABORADORES.md)
- [📖 Documentação Completa](DOCUMENTACAO_FINAL.md)
- [🚀 Deploy no Render](DEPLOYMENT.md)

## 👨‍💻 Autor

**Rodrigo Antonioli**
- 📧 Email: rodrigoantonioli@gmail.com
- 🐙 GitHub: [@rodrigoantonioli](https://github.com/rodrigoantonioli)
- 💼 LinkedIn: [Rodrigo Antonioli](https://linkedin.com/in/rodrigoantonioli)
- 🌐 Especialista em: Python, Power BI, Solidity, Web3

---

<div align="center">

**⭐ Se este projeto foi útil, deixe uma estrela!**

**🎯 Sistema desenvolvido para automatizar e dar transparência aos sorteios do Festival Na Praia 2025**

</div> 