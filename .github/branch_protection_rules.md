# 🛡️ Configuração de Proteção de Branch

Este documento contém as regras de proteção que devem ser aplicadas no repositório GitHub.

## 🎯 **Branch Principal (master)**

### **Configurações Recomendadas:**

#### **✅ Require pull request reviews before merging**
- **Reviewers obrigatórios:** 1
- **Dismiss stale reviews:** ✅ Ativado
- **Require review from code owners:** ✅ Ativado (se CODEOWNERS existir)

#### **✅ Require status checks to pass before merging**
- **Require branches to be up to date:** ✅ Ativado
- **Status checks:** (configurar quando CI/CD for implementado)

#### **✅ Require conversation resolution before merging**
- Todos os comentários devem ser resolvidos

#### **✅ Restrict pushes that create files larger than 100MB**
- Evita uploads acidentais de arquivos grandes

#### **✅ Allow force pushes**
- ❌ **DESATIVADO** (proteção contra force push)

#### **✅ Allow deletions** 
- ❌ **DESATIVADO** (proteção contra deleção acidental)

---

## 🔄 **Branch de Desenvolvimento (develop-v1.2)**

### **Configurações Recomendadas:**

#### **✅ Require pull request reviews before merging**
- **Reviewers obrigatórios:** 1
- **Dismiss stale reviews:** ✅ Ativado

#### **✅ Allow force pushes**
- ✅ **ATIVADO** (mais flexibilidade para desenvolvimento)

#### **✅ Allow deletions**
- ✅ **ATIVADO** (permite refatoração)

---

## 📋 **Como Aplicar no GitHub:**

### **Passo 1: Acessar Configurações**
1. Ir para `Settings` do repositório
2. Clicar em `Branches` no menu lateral

### **Passo 2: Configurar Branch master**
1. Clicar em `Add rule`
2. Em "Branch name pattern" digitar: `master`
3. Marcar todas as opções recomendadas acima
4. Salvar as configurações

### **Passo 3: Configurar Branch develop-v1.2**
1. Clicar em `Add rule` novamente  
2. Em "Branch name pattern" digitar: `develop-v1.2`
3. Aplicar configurações mais flexíveis
4. Salvar as configurações

---

## 🎯 **Fluxo de Trabalho Recomendado**

### **Para Desenvolvimento Normal:**
```bash
# 1. Criar feature branch a partir do develop-v1.2
git checkout develop-v1.2
git checkout -b feature/nova-funcionalidade

# 2. Desenvolver e commitar
git add .
git commit -m "feat: nova funcionalidade"

# 3. Push e PR para develop-v1.2
git push origin feature/nova-funcionalidade
# Abrir PR: feature/nova-funcionalidade → develop-v1.2
```

### **Para Release (Hotfix/Major):**
```bash
# 1. PR de develop-v1.2 para master
# Abrir PR: develop-v1.2 → master

# 2. Após merge e testes em produção
git checkout master
git tag -a v1.2.0 -m "v1.2.0 - Nova versão"
git push origin v1.2.0

# 3. Atualizar develop com master
git checkout develop-v1.2  
git merge master
git push origin develop-v1.2
```

### **Para Hotfix Crítico:**
```bash
# 1. Criar hotfix branch a partir do master
git checkout master
git checkout -b hotfix/critical-fix

# 2. Aplicar correção
git add .
git commit -m "fix: correção crítica"

# 3. PR direto para master
git push origin hotfix/critical-fix
# Abrir PR: hotfix/critical-fix → master

# 4. Após merge, atualizar develop
git checkout develop-v1.2
git merge master
git push origin develop-v1.2
```

---

## 🔍 **Verificação das Regras**

Após configurar, verificar se:

✅ Push direto para `master` é bloqueado  
✅ PR é obrigatório para `master`  
✅ Reviewers são necessários  
✅ Force push está desativado em `master`  
✅ `develop-v1.2` permite desenvolvimento flexível  

---

## 📊 **Status Atual do Projeto**

### **Versões:**
- **Produção (master):** v1.1.2 - Sistema estável  
- **Desenvolvimento (develop-v1.2):** Pronto para novas features  

### **Próximos Passos:**
1. Aplicar proteções de branch conforme este documento
2. Definir roadmap da v1.2
3. Implementar novas funcionalidades em feature branches
4. Configurar CI/CD pipeline quando necessário

---

**⚠️ IMPORTANTE:** Estas configurações devem ser aplicadas por um administrador do repositório GitHub. 