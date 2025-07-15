# 🧪 Testes - Sistema de Sorteios BigBox

Suíte completa de testes com **100% de sucesso** para homologação do sistema.

## 🗂️ Arquivos de Teste

- **`test_basic.py`** - Infraestrutura básica
- **`test_models.py`** - Modelos de dados
- **`test_auth.py`** - Autenticação e autorização
- **`test_lojas.py`** - Gestão de lojas
- **`test_colaboradores.py`** - Gestão de colaboradores
- **`test_sorteios.py`** - Sistema de sorteios
- **`test_dashboard.py`** - Dashboards e relatórios
- **`test_integration.py`** - Fluxos completos

## 🏃‍♂️ Executar Testes

```bash
# Todos os testes
python tests/run_all_tests.py

# Específico
python -m unittest tests.test_models -v
```

## ✅ Cobertura Completa

### 🔐 Autenticação
- Login/logout de usuários
- Controle de acesso por tipo
- Proteção de rotas

### 🏪 Gestão de Lojas
- CRUD completo
- Validação de códigos únicos
- Filtros por bandeira (BIG/ULTRA)

### 👥 Colaboradores
- CRUD de colaboradores
- Upload de arquivos Excel
- Constraint de matrícula única por loja

### 🎁 Sistema de Prêmios
- CRUD de prêmios
- Tipos de prêmio (show/day_use)
- Vinculação com lojas

### 🎲 Sistema de Sorteios
- Sorteios semanais de lojas
- Atribuição de prêmios
- Prevenção de duplicatas
- Snapshot de colaboradores

### 📊 Dashboards
- Dashboard administrativo
- Dashboard de assistentes
- Estatísticas em tempo real

### 🔗 Integração
- Fluxos completos de usuário
- Cenários de uso real
- Controle de acesso integrado

## 🛠️ Configuração

### Ambiente de Teste
- Banco de dados em memória (SQLite)
- CSRF desabilitado
- Dados sintéticos para cada teste

### Requisitos
```bash
pip install openpyxl  # Para testes de upload Excel
```

## 🐛 Troubleshooting

### Testes Falhando
```bash
# Verificar dependências
pip install -r requirements.txt

# Limpar cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Debug específico
python -m unittest tests.test_models -v
```

---

**Sistema pronto para produção com 100% de sucesso nos testes** 🎉 