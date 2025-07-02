# 🧪 Testes do Sistema de Sorteios BigBox v1.0

Este diretório contém a suíte completa de testes para homologação do sistema de sorteios.

## 📋 Estrutura dos Testes

### 🗂️ Arquivos de Teste

- **`test_basic.py`** - Testes básicos de infraestrutura
- **`test_models.py`** - Testes dos modelos de dados
- **`test_auth.py`** - Testes de autenticação e autorização
- **`test_lojas.py`** - Testes de gestão de lojas
- **`test_colaboradores.py`** - Testes de gestão de colaboradores
- **`test_premios.py`** - Testes do sistema de prêmios
- **`test_sorteios.py`** - Testes do sistema de sorteios
- **`test_dashboard.py`** - Testes de dashboards e relatórios
- **`test_integration.py`** - Testes de integração de fluxos completos

### 🏃‍♂️ Executar Testes

```bash
# Executar todos os testes com relatório detalhado
python tests/run_all_tests.py

# Executar teste específico
python -m unittest tests.test_models -v

# Executar categoria específica
python -m unittest tests.test_auth tests.test_lojas -v
```

## 🎯 Cobertura de Testes

### ✅ Funcionalidades Testadas

#### 🔐 Autenticação e Autorização
- Login/logout de usuários
- Controle de acesso por tipo (admin/assistente)
- Proteção de rotas administrativas
- Sessões e cookies

#### 🏪 Gestão de Lojas
- CRUD completo de lojas
- Validação de códigos únicos
- Filtros por bandeira (BIG/ULTRA)
- Ativação/desativação

#### 👥 Gestão de Colaboradores
- CRUD de colaboradores
- Upload de arquivos Excel
- Constraint de matrícula única por loja
- Filtros por loja (assistentes)
- Status apto/inapto

#### 🎁 Sistema de Prêmios
- CRUD de prêmios
- Tipos de prêmio (show/day_use)
- Vinculação com lojas
- Pool geral de prêmios
- Validações de data

#### 🎲 Sistema de Sorteios
- Sorteios semanais de lojas
- Atribuição de prêmios
- Prevenção de duplicatas
- Snapshot de colaboradores
- Histórico auditável

#### 📊 Dashboards e Relatórios
- Dashboard administrativo
- Dashboard de assistentes
- Estatísticas em tempo real
- Histórico de sorteios
- Zona vermelha (admin)

#### 🔗 Integração
- Fluxos completos de usuário
- Cenários de uso real
- Controle de acesso integrado
- Auditoria de operações

## 🛠️ Configuração de Testes

### 📝 Requisitos

```bash
# Instalar dependências de teste
pip install openpyxl  # Para testes de upload Excel
```

### 🔧 Configuração do Ambiente

Os testes usam configuração específica:
- Banco de dados em memória (SQLite)
- CSRF desabilitado
- Dados sintéticos para cada teste

## 📊 Relatórios de Teste

### 🎯 Métricas de Qualidade

- **Cobertura de Código**: Testa todas as funcionalidades principais
- **Testes de Unidade**: Componentes individuais
- **Testes de Integração**: Fluxos completos
- **Testes de Regressão**: Evita quebras em funcionalidades existentes

### 📈 Categorias de Resultado

- 🟢 **EXCELENTE** (95-100%): Sistema pronto para produção
- 🟡 **BOM** (85-94%): Pequenos ajustes necessários
- 🟠 **ACEITÁVEL** (70-84%): Revisão recomendada
- 🔴 **CRÍTICO** (<70%): Correções urgentes necessárias

## 🚀 Homologação do Cliente

### ✅ Lista de Verificação

Antes de entregar ao cliente, certifique-se de que:

1. **Todos os testes passam** (taxa de sucesso 100%)
2. **Funcionalidades básicas funcionam**:
   - Login admin/assistente
   - Criação de lojas
   - Upload de colaboradores
   - Criação de prêmios
   - Sorteios semanais
   - Consulta de histórico

3. **Controles de segurança funcionam**:
   - Acesso negado para usuários não autorizados
   - Assistentes só veem dados da sua loja
   - Zona vermelha protegida

4. **Integridade de dados garantida**:
   - Constraints de banco respeitadas
   - Validações de negócio funcionando
   - Histórico auditável

### 🎯 Cenários de Teste para Cliente

1. **Cenário Admin**:
   - Login como admin
   - Criar 2 lojas (BIG e ULTRA)
   - Criar 2 assistentes
   - Criar alguns prêmios
   - Fazer sorteio semanal
   - Atribuir prêmios
   - Consultar histórico

2. **Cenário Assistente**:
   - Login como assistente
   - Fazer upload de colaboradores
   - Visualizar dashboard
   - Gerenciar colaboradores da loja
   - Consultar histórico

3. **Cenário de Segurança**:
   - Tentar acessar áreas restritas
   - Verificar isolamento de dados
   - Testar logout

## 🐛 Solução de Problemas

### ❌ Testes Falhando

1. **Erro de Importação**:
   ```bash
   # Verificar se está na raiz do projeto
   cd /e:/sorteioBigbox
   python tests/run_all_tests.py
   ```

2. **Erro de Banco de Dados**:
   ```bash
   # Limpar cache do Python
   find . -name "*.pyc" -delete
   find . -name "__pycache__" -type d -exec rm -rf {} +
   ```

3. **Erro de Dependências**:
   ```bash
   # Reinstalar dependências
   pip install -r requirements.txt
   pip install openpyxl
   ```

### 🔍 Debug de Testes

```bash
# Executar com mais verbosidade
python -m unittest tests.test_models.ModelsTestCase.test_usuario_model -v

# Parar no primeiro erro
python -m unittest tests.test_models --failfast
```

## 📞 Suporte

Para dúvidas sobre os testes:
1. Consulte os logs detalhados
2. Verifique se todas as dependências estão instaladas
3. Confirme que está executando da raiz do projeto
4. Revise a documentação do código

---

**Nota**: Estes testes garantem que o sistema está funcionando corretamente e pronto para uso em produção no Festival Na Praia 2025. 🎉 