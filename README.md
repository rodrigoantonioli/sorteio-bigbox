# Sistema de Sorteios - Big Box & UltraBox 🎉

## 📋 Visão Geral

Sistema web para gerenciamento de sorteios semanais de ingressos para o Festival Na Praia, destinado aos colaboradores das lojas Big Box e UltraBox. O sistema automatiza todo o processo desde o sorteio das lojas até a seleção dos colaboradores contemplados.

## 🎯 Objetivos

1. **Automatizar o processo de sorteio semanal** de uma loja de cada bandeira (BIG e ULTRA)
2. **Permitir que gerentes façam upload** de planilhas com colaboradores aptos
3. **Realizar sorteios internos** de colaboradores nas lojas sorteadas
4. **Exibir publicamente** os resultados dos sorteios
5. **Manter histórico** de todos os sorteios realizados

## 🚀 Funcionalidades Principais

### Para o Administrador
- **Login seguro** com controle de acesso
- **Sorteio semanal** de 1 loja BIG + 1 loja ULTRA
- **Configuração da semana** (datas dos shows, quantidade de ingressos)
- **Gerenciamento de usuários** (criar/editar gerentes)
- **Visualização de histórico** completo de sorteios
- **Dashboard** com estatísticas e resumos

### Para os Gerentes
- **Login individual** por loja
- **Upload de Excel** com colaboradores aptos (formato padrão)
- **Validação automática** dos dados do Excel
- **Sorteio interno** dos colaboradores
- **Visualização** dos colaboradores sorteados
- **Download de relatório** em PDF/Excel

### Para o Público
- **Página pública** sem necessidade de login
- **Visualização dos resultados** da semana atual
- **Histórico** das últimas semanas
- **Busca** por loja ou colaborador

## 📊 Regras de Negócio

### Critérios de Elegibilidade dos Colaboradores
- ✅ Presentes na loja (sem faltas injustificadas)
- ✅ Sem advertências
- ✅ Devem estar de FOLGA no dia do ingresso sorteado
- ❌ A escala de trabalho NÃO será alterada

### Cronograma Semanal
- **Terça-feira**: Sorteio das duas lojas (1 BIG + 1 ULTRA)
- **Quarta-feira**: Gerentes realizam sorteios internos
- **Quinta a Domingo**: Shows e eventos

### Distribuição de Ingressos
- **Sexta**: Apenas shows (sem Day Use)
- **Sábado e Domingo**: Shows + Day Use
- Alternância semanal entre as bandeiras para equilíbrio

## 🛠 Arquitetura Técnica

### Stack Tecnológica
- **Backend**: Python 3.9+ com Flask
- **Frontend**: HTML5, CSS3 (Bootstrap 5), JavaScript
- **Banco de Dados**: PostgreSQL (Render)
- **Hospedagem**: Render (Free Tier)
- **Autenticação**: Flask-Login + JWT
- **Upload de Arquivos**: pandas para Excel
- **Notificações**: Email via SendGrid/SMTP

### Estrutura do Banco de Dados

```sql
-- Tabela de Lojas
lojas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE,
    nome VARCHAR(100),
    bandeira ENUM('BIG', 'ULTRA'),
    ativo BOOLEAN DEFAULT true
)

-- Tabela de Usuários
usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE,
    senha_hash VARCHAR(255),
    nome VARCHAR(100),
    tipo ENUM('admin', 'gerente'),
    loja_id INTEGER REFERENCES lojas(id),
    ativo BOOLEAN DEFAULT true
)

-- Tabela de Colaboradores
colaboradores (
    id SERIAL PRIMARY KEY,
    matricula VARCHAR(20),
    nome VARCHAR(100),
    setor VARCHAR(50),
    loja_id INTEGER REFERENCES lojas(id),
    apto BOOLEAN DEFAULT true,
    ultima_atualizacao TIMESTAMP
)

-- Tabela de Sorteios Semanais
sorteios_semanais (
    id SERIAL PRIMARY KEY,
    semana_inicio DATE,
    loja_big_id INTEGER REFERENCES lojas(id),
    loja_ultra_id INTEGER REFERENCES lojas(id),
    data_sorteio TIMESTAMP,
    sorteado_por INTEGER REFERENCES usuarios(id)
)

-- Tabela de Sorteios de Colaboradores
sorteios_colaboradores (
    id SERIAL PRIMARY KEY,
    sorteio_semanal_id INTEGER REFERENCES sorteios_semanais(id),
    colaborador_id INTEGER REFERENCES colaboradores(id),
    tipo_ingresso VARCHAR(50),
    dia_evento DATE,
    data_sorteio TIMESTAMP,
    sorteado_por INTEGER REFERENCES usuarios(id)
)
```

## 🔒 Segurança

- **Senhas criptografadas** com bcrypt
- **Sessões seguras** com tokens JWT
- **Validação de uploads** (apenas .xlsx, tamanho máximo 5MB)
- **Sanitização de dados** de entrada
- **HTTPS obrigatório** em produção
- **Rate limiting** para prevenir ataques
- **Logs de auditoria** para todas as ações críticas

## 📱 Interface do Usuário

### Design Responsivo
- Mobile-first approach
- Interface intuitiva e moderna
- Cores das marcas (Big Box e UltraBox)
- Feedback visual para todas as ações
- Loading states e mensagens de erro claras

### Páginas Principais
1. **Home** - Resultados públicos
2. **Login** - Acesso seguro
3. **Dashboard Admin** - Painel de controle
4. **Dashboard Gerente** - Gestão da loja
5. **Histórico** - Consulta de sorteios anteriores

## 🚦 Fluxo de Trabalho

1. **Admin acessa o sistema** → Realiza sorteio semanal
2. **Sistema notifica** gerentes das lojas sorteadas
3. **Gerente faz upload** do Excel com colaboradores aptos
4. **Sistema valida** e importa os dados
5. **Gerente realiza sorteio** interno
6. **Sistema exibe** resultados publicamente
7. **Colaboradores** consultam os contemplados

## 📈 Melhorias Futuras

1. **App Mobile** nativo para consultas
2. **Notificações Push** para colaboradores
3. **Integração com RH** para validação automática
4. **QR Code** para validação de ingressos
5. **Dashboard Analytics** avançado
6. **API REST** para integrações
7. **Sorteio automático** com regras pré-definidas

## 🔧 Configuração do Ambiente

### Variáveis de Ambiente
```env
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=your-secret-key
FLASK_ENV=production
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-password
```

### Deploy no Render
1. Criar conta no Render
2. Conectar repositório GitHub
3. Configurar build command: `pip install -r requirements.txt`
4. Configurar start command: `gunicorn app:app`
5. Adicionar PostgreSQL database
6. Configurar variáveis de ambiente

## 📝 Notas Importantes

- O sistema mantém histórico completo para auditoria
- Backup automático diário do banco de dados
- Logs detalhados de todas as operações
- Suporte para múltiplos formatos de Excel
- Validação rigorosa de dados importados

## 📦 Setup e Execução Local

Siga os passos abaixo para configurar e rodar o projeto em sua máquina local.

### 1. Pré-requisitos
- Python 3.9+
- Git

### 2. Crie o arquivo de Ambiente

Crie um arquivo chamado `.env` na raiz do projeto. Copie e cole o conteúdo abaixo nele. Este arquivo define as variáveis de ambiente para o desenvolvimento local, usando um banco de dados SQLite para simplicidade.

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=uma-chave-secreta-bem-segura-aqui
DATABASE_URL=sqlite:///instance/sorteio.db
ADMIN_EMAIL=admin@bigbox.com
ADMIN_PASSWORD=BigBox2025!
```

### 3. Crie o Ambiente Virtual e Instale as Dependências

Abra o terminal na raiz do projeto e execute os seguintes comandos:

```bash
# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# No macOS/Linux:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 4. Popule o Banco de Dados

Com o ambiente virtual ainda ativado, execute o script para carregar a lista de lojas do Excel para o banco de dados:

```bash
python load_stores.py
```

O script irá criar o banco de dados e inserir todas as lojas dos arquivos `inputs`.

### 5. Execute a Aplicação

Finalmente, execute a aplicação Flask:

```bash
flask run
```

Acesse <http://127.0.0.1:5000> em seu navegador.

**Credenciais de Admin:**
- **Email:** `admin@bigbox.com`
- **Senha:** `BigBox2025!` 