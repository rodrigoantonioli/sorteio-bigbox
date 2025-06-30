# Instruções de Deploy no Render

## Pré-requisitos

1. Conta no GitHub
2. Conta no Render (gratuita)
3. Este repositório no seu GitHub

## Passo a Passo

### 1. Preparar o Repositório

1. Faça o fork ou clone deste repositório para sua conta GitHub
2. Certifique-se de que todos os arquivos estão commitados

### 2. Configurar no Render

1. Acesse [render.com](https://render.com) e faça login
2. Clique em "New +" e selecione "Web Service"
3. Conecte sua conta GitHub se ainda não estiver conectada
4. Selecione o repositório do projeto
5. Preencha as configurações:
   - **Name**: sorteio-bigbox (ou outro nome de sua preferência)
   - **Region**: Oregon (US West)
   - **Branch**: main
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 3. Configurar Banco de Dados

1. Na dashboard do Render, clique em "New +" e selecione "PostgreSQL"
2. Configure:
   - **Name**: sorteio-bigbox-db
   - **Database**: sorteio_bigbox
   - **User**: sorteio_user
   - **Region**: Oregon (mesma região do app)
   - **Plan**: Free

### 4. Variáveis de Ambiente

No painel do seu Web Service, vá em "Environment" e adicione:

```
DATABASE_URL=[será preenchido automaticamente quando conectar ao PostgreSQL]
SECRET_KEY=[clique em "Generate" para criar uma chave segura]
FLASK_ENV=production
ADMIN_EMAIL=admin@bigbox.com
ADMIN_PASSWORD=SuaSenhaSegura123!
```

### 5. Conectar Banco ao App

1. No painel do Web Service, vá em "Environment"
2. Clique em "Add Environment Variable"
3. Selecione "Add from database"
4. Escolha o banco PostgreSQL criado
5. Selecione "Internal Database URL"

### 6. Deploy

1. O Render iniciará o deploy automaticamente
2. Aguarde o build e deploy finalizarem (cerca de 5-10 minutos)
3. Quando concluído, você verá a URL do seu app

### 7. Carregar Dados Iniciais

Após o deploy:

1. Acesse a URL do seu app
2. Faça login com as credenciais do admin definidas
3. Execute o script para carregar as lojas:

```bash
# No terminal local, com o projeto clonado:
python load_stores.py
```

Ou faça manualmente pelo painel admin após criar alguns gerentes.

## Manutenção

### Atualizações

1. Faça as alterações no código
2. Commit e push para o GitHub
3. O Render detectará e fará o deploy automaticamente

### Backup do Banco

O Render faz backups automáticos diários no plano gratuito.

### Monitoramento

- Verifique os logs no painel do Render
- Configure alertas de email para downtime

## Troubleshooting

### Erro de Conexão com Banco

- Verifique se a variável DATABASE_URL está configurada
- Confirme que o banco está na mesma região do app

### Erro 500

- Verifique os logs no painel do Render
- Confirme que todas as variáveis de ambiente estão configuradas

### App não inicia

- Verifique se o arquivo requirements.txt está completo
- Confirme que o comando de start está correto

## Segurança

1. **Sempre** mude a senha do admin após o primeiro login
2. Use senhas fortes para todos os usuários
3. Mantenha o SECRET_KEY seguro e nunca o compartilhe
4. Configure HTTPS (o Render fornece automaticamente)

## Custos

O plano gratuito do Render inclui:
- 750 horas de execução por mês
- PostgreSQL com 1GB de armazenamento
- Deploy automático do GitHub
- HTTPS gratuito

Para uso básico do sistema de sorteios, o plano gratuito é suficiente. 