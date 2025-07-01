# 🚀 Guia de Deploy no Render - Sistema de Sorteios BigBox

## 📋 Pré-requisitos

### ✅ **Sistema Pronto**
- ✅ Código atualizado no GitHub
- ✅ Correções de upload implementadas
- ✅ Todas as funcionalidades testadas
- ✅ Configuração do Render preparada

### 🔧 **Arquivos de Configuração**
- ✅ `render.yaml` - Configuração do serviço
- ✅ `requirements.txt` - Dependências Python
- ✅ `config.py` - Configuração de produção
- ✅ `run.py` - Ponto de entrada com Gunicorn

## 🎯 **Processo de Deploy**

### **1. Acessar o Render**
1. Acesse: https://render.com
2. Faça login na sua conta
3. Vá para o Dashboard

### **2. Criar Novo Serviço**
1. Clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte seu repositório GitHub: `rodrigoantonioli/sorteioBigbox`
4. Clique em **"Connect"**

### **3. Configurar o Serviço**

#### **Configurações Básicas:**
- **Name:** `sorteio-bigbox`
- **Region:** `Oregon (US West)`
- **Branch:** `master`
- **Runtime:** `Python 3`

#### **Comandos de Build e Start:**
- **Build Command:** `pip install -r requirements.txt; pip install psycopg2-binary`
- **Start Command:** `gunicorn run:app`

#### **Configurações Avançadas:**
- **Auto-Deploy:** ✅ Habilitado
- **Health Check Path:** `/`

### **4. Configurar Banco de Dados PostgreSQL**

#### **Criar Database:**
1. No Dashboard, clique em **"New +"**
2. Selecione **"PostgreSQL"**
3. Configurações:
   - **Name:** `sorteio-bigbox-db`
   - **Database Name:** `sorteio_bigbox`
   - **User:** `sorteio_user`
   - **Region:** `Oregon (US West)`
4. Clique em **"Create Database"**

#### **Conectar Database ao Serviço:**
1. Vá para o seu Web Service
2. Na aba **"Environment"**
3. Adicione a variável:
   - **Key:** `DATABASE_URL`
   - **Value:** Selecione o database criado

### **5. Configurar Variáveis de Ambiente**

Na aba **"Environment"** do seu serviço, adicione:

```bash
# Ambiente
FLASK_ENV=production

# Segurança
SECRET_KEY=<será gerado automaticamente>

# Admin
ADMIN_EMAIL=admin@bigbox.com
ADMIN_PASSWORD=<sua_senha_admin_segura>

# Database (conectado automaticamente)
DATABASE_URL=<conectado_do_database>
```

### **6. Deploy e Inicialização**

#### **Primeira Deploy:**
1. Clique em **"Create Web Service"**
2. Aguarde o build completar (5-10 minutos)
3. Verifique os logs para erros

#### **Inicializar Banco de Dados:**
1. Acesse o **"Shell"** do seu serviço
2. Execute o comando:
```bash
flask init-db
```

#### **Verificar Funcionamento:**
1. Acesse a URL fornecida pelo Render
2. Teste o login admin
3. Verifique todas as funcionalidades

## 🔄 **Configuração Automática via render.yaml**

O sistema já está configurado para deploy automático via `render.yaml`:

```yaml
databases:
  - name: sorteio-bigbox-db
    databaseName: sorteio_bigbox
    user: sorteio_user
    region: oregon

services:
  - type: web
    name: sorteio-bigbox
    runtime: python
    region: oregon
    buildCommand: "pip install -r requirements.txt; pip install psycopg2-binary"
    startCommand: "gunicorn run:app"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: sorteio-bigbox-db
          property: connectionString
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: ADMIN_EMAIL
        value: admin@bigbox.com
      - key: ADMIN_PASSWORD
        sync: false
```

## 📊 **Pós-Deploy**

### **1. Configuração Inicial**
- ✅ Executar `flask init-db` no Shell
- ✅ Verificar criação do admin
- ✅ Verificar carregamento das lojas
- ✅ Testar login e funcionalidades

### **2. Configurações de Produção**
- ✅ HTTPS automático (Render)
- ✅ SSL/TLS configurado
- ✅ Backups automáticos do PostgreSQL
- ✅ Monitoramento de uptime

### **3. Dados Iniciais**
- ✅ Usuário admin criado
- ✅ Lojas carregadas do Excel
- ✅ Sistema pronto para uso

## 🛡️ **Segurança em Produção**

### **Configurações Aplicadas:**
- ✅ `DEBUG=False`
- ✅ `SESSION_COOKIE_SECURE=True` (HTTPS)
- ✅ `SECRET_KEY` gerado automaticamente
- ✅ Senhas criptografadas com bcrypt
- ✅ Validação de formulários (CSRF)

### **Banco de Dados:**
- ✅ PostgreSQL em produção
- ✅ Conexão SSL automática
- ✅ Backups automáticos
- ✅ Isolamento de dados

## 📈 **Monitoramento**

### **Métricas do Render:**
- ✅ Uptime monitoring
- ✅ Response time tracking
- ✅ Error rate monitoring
- ✅ Resource usage (CPU/Memory)

### **Logs:**
- ✅ Application logs
- ✅ Access logs
- ✅ Error logs
- ✅ Database logs

## 🔧 **Manutenção**

### **Updates Automáticos:**
- ✅ Auto-deploy no push para master
- ✅ Zero-downtime deployments
- ✅ Rollback automático em caso de erro

### **Backup:**
- ✅ Database backups automáticos
- ✅ Point-in-time recovery
- ✅ Retenção de 7 dias (plano gratuito)

## 🎯 **URLs de Produção**

Após o deploy, o sistema estará disponível em:
- **URL Principal:** `https://sorteio-bigbox.onrender.com`
- **Admin:** `https://sorteio-bigbox.onrender.com/admin`
- **Login:** `https://sorteio-bigbox.onrender.com/auth/login`

## 📞 **Suporte**

### **Logs de Debug:**
```bash
# Ver logs em tempo real
render logs -f

# Ver logs específicos
render logs --tail 100
```

### **Comandos Úteis:**
```bash
# Restart do serviço
render restart

# Shell interativo
render shell

# Status do serviço
render status
```

## ✅ **Checklist Final**

### **Antes do Deploy:**
- [ ] Código commitado e enviado para GitHub
- [ ] Variáveis de ambiente definidas
- [ ] Senha do admin definida
- [ ] Arquivo `render.yaml` configurado

### **Durante o Deploy:**
- [ ] Serviço criado no Render
- [ ] Database PostgreSQL criado
- [ ] Variáveis de ambiente configuradas
- [ ] Build completado com sucesso

### **Após o Deploy:**
- [ ] Comando `flask init-db` executado
- [ ] Login admin funcionando
- [ ] Upload de colaboradores testado
- [ ] Funcionalidades principais testadas
- [ ] Sistema em produção funcionando

---

**🚀 O sistema está pronto para produção!**
**📧 Admin:** admin@bigbox.com
**🔐 Senha:** Definir no ADMIN_PASSWORD
**🌐 URL:** https://sorteio-bigbox.onrender.com 