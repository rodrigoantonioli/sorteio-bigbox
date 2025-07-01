# 🚀 Configuração do GitHub - Repositório Privado

## 📋 Passos para Configurar o Repositório

### 1. Criar Repositório no GitHub

1. Acesse [GitHub.com](https://github.com)
2. Clique em **"New Repository"**
3. Configure o repositório:
   - **Repository name**: `sorteio-bigbox`
   - **Description**: `🎲 Sistema de Sorteios Big Box & UltraBox v1.0.0 - Gerenciamento completo de sorteios semanais do Festival Na Praia`
   - **Visibility**: ⚠️ **PRIVATE** (importante!)
   - **Initialize**: Não marque nenhuma opção (o repositório já existe localmente)

### 2. Conectar Repositório Local

```bash
# Adicionar origin (substitua SEU-USUARIO pelo seu username do GitHub)
git remote add origin https://github.com/SEU-USUARIO/sorteio-bigbox.git

# Verificar se foi adicionado corretamente
git remote -v

# Fazer push inicial com tag
git push -u origin master
git push origin v1.0.0
```

### 3. Configurar Repositório Privado

⚠️ **IMPORTANTE**: O repositório DEVE ser privado pois contém:
- Código proprietário da Big Box & UltraBox
- Configurações de sistema interno
- Dados sensíveis da empresa

### 4. Configurar Colaboradores (Opcional)

Se necessário adicionar colaboradores:
1. Vá para **Settings** > **Manage access**
2. Clique **Invite a collaborator**
3. Adicione email do usuário
4. Defina permissões apropriadas

### 5. Verificação Final

Após o push, verifique:
- ✅ Repositório está privado
- ✅ Todos os arquivos foram enviados
- ✅ README.md está sendo exibido corretamente
- ✅ Tag v1.0.0 está criada
- ✅ Histórico de commits está completo

## 🔧 Comandos de Manutenção

### Deploy no Render

1. Conectar GitHub ao Render
2. Selecionar o repositório `sorteio-bigbox`
3. Configurar variáveis de ambiente:
   ```bash
   SECRET_KEY=sua-chave-secreta-super-forte
   DATABASE_URL=postgresql://usuario:senha@host:porta/database
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=email@empresa.com
   MAIL_PASSWORD=senha-app-email
   ```

### Atualizações Futuras

```bash
# Para novas versões
git add .
git commit -m "🔄 v1.1.0 - Nova funcionalidade"
git tag -a v1.1.0 -m "Descrição da versão"
git push origin master
git push origin v1.1.0
```

## 📊 Status do Projeto

- **Versão Atual**: v1.0.0
- **Status**: ✅ Pronto para Produção
- **Funcionalidades**: 100% Implementadas
- **Testes**: ✅ Sistema funcionando
- **Documentação**: ✅ Completa
- **Deploy**: ✅ Configurado

---

**🎯 Sistema pronto para uso em produção!** 