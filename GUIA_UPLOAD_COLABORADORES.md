# 📋 Guia: Upload de Colaboradores

## ⚠️ COMPORTAMENTO IMPORTANTE

### Como Funciona o Upload
Quando um gerente faz o upload de uma planilha de colaboradores:

**✅ O QUE ACONTECE:**
- **SUBSTITUI TODOS** os colaboradores da loja específica do gerente
- Remove todos os colaboradores atuais da loja (exceto os protegidos)
- Adiciona os novos colaboradores da planilha
- Gera relatório detalhado do que foi feito

**🛡️ PROTEÇÃO AUTOMÁTICA:**
- Colaboradores que já participaram de sorteios são **PROTEGIDOS**
- Eles NÃO são removidos, mesmo no upload
- Mantém histórico de sorteios intacto

**🎯 ESCOPO:**
- Afeta APENAS a loja do gerente logado
- Outras lojas permanecem inalteradas
- Processo é totalmente isolado por loja

## 📊 Exemplo Prático

### Situação Inicial
**Loja: 106 NORTE**
- João Silva (sem histórico de sorteios)
- Maria Santos (JÁ participou de sorteio - PROTEGIDA)
- Pedro Costa (sem histórico de sorteios)

### Upload da Nova Planilha
```
Ana Nova
Carlos Novo
```

### Resultado Final
**Loja: 106 NORTE**
- ~~João Silva~~ ❌ (removido)
- Maria Santos ✅ (mantida - protegida)
- ~~Pedro Costa~~ ❌ (removido)
- Ana Nova ➕ (adicionada)
- Carlos Novo ➕ (adicionada)

### Relatório Gerado
```
📊 RELATÓRIO DE UPLOAD - Loja: 106 NORTE
🗑️  Colaboradores removidos: 2
🛡️  Colaboradores mantidos (protegidos): 1
➕ Novos colaboradores adicionados: 2
📈 Total final: 3 colaboradores
```

## 🚨 Avisos Importantes

### Interface do Sistema
- Checkbox obrigatório: "Confirmo que esta lista está correta"
- Aviso claro: "Este upload irá SUBSTITUIR todos os colaboradores atuais"
- Não é possível prosseguir sem confirmar

### Transparência Total
- Relatório detalhado após cada upload
- Histórico de todas as operações
- Colaboradores protegidos claramente identificados

### Segurança
- Colaboradores com histórico de sorteios são SEMPRE protegidos
- Não há como remover acidentalmente colaboradores importantes
- Processo reversível através do admin

## 📝 Formato da Planilha

### Colunas Obrigatórias
1. **Matrícula** - Identificador único
2. **Nome** - Nome completo do colaborador
3. **Setor** - Setor de trabalho

### Exemplo de Planilha Excel/CSV
```
Matrícula | Nome              | Setor
----------|-------------------|----------
12345     | Ana Silva         | VENDAS
67890     | Carlos Santos     | ESTOQUE
11111     | Maria Oliveira    | CAIXA
```

## 🔧 Para Desenvolvedores

### Lógica de Proteção
```python
# Verifica se colaborador tem histórico
tem_sorteios = SorteioColaborador.query.filter_by(
    colaborador_id=colaborador.id
).first()

if not tem_sorteios:
    # Pode ser removido
    db.session.delete(colaborador)
else:
    # PROTEGIDO - mantém no sistema
    print(f"Mantido: {colaborador.nome} (com histórico)")
```

### Isolamento por Loja
```python
# Afeta apenas colaboradores da loja do gerente
colaboradores_existentes = Colaborador.query.filter_by(
    loja_id=current_user.loja_id
).all()
```

## ✅ Casos de Uso

### Renovação Mensal da Equipe
- Gerente recebe nova lista de colaboradores do RH
- Faz upload da nova planilha
- Sistema automaticamente atualiza a equipe
- Colaboradores veteranos (com histórico) são mantidos

### Correção de Dados
- Gerente identifica erros na lista atual
- Corrige a planilha localmente
- Faz novo upload com dados corretos
- Sistema substitui dados antigos pelos novos

### Início de Nova Campanha
- Nova campanha de sorteios
- Lista atualizada de colaboradores elegíveis
- Upload da nova lista
- Sistema fica pronto para novos sorteios

---

**💡 RESUMO:** O upload sempre substitui TODOS os colaboradores da loja específica, mas protege automaticamente aqueles com histórico de sorteios, garantindo transparência e segurança no processo. 