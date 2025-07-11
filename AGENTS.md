# Sistema de Sorteios Instagram - Documentação para IAs

## Visão Geral

Este sistema implementa um sorteio profissional e elegante para Instagram com layout em 3 colunas, animações fluidas e transições cinematográficas. O sistema foi projetado para ser filmado e transmitido ao vivo.

## Estrutura do Layout

### Layout em 3 Colunas

```
┌─────────────────┬─────────────────┬─────────────────┐
│   Ficha do      │   Sorteio       │   Ganhadores    │
│   Sorteio       │   Central       │   (Direita)     │
│   (Esquerda)    │                 │                 │
│   25% width     │   50% width     │   25% width     │
└─────────────────┴─────────────────┴─────────────────┘
```

### Transição Final

Após o sorteio, o layout se transforma:

```
┌─────────────────────────┬─────────────────────────┐
│     Ficha do Sorteio    │      Ganhadores         │
│      (50% width)        │      (50% width)        │
│                         │                         │
│  - Título               │  - Grid responsivo      │
│  - Descrição            │  - Animações sequenciais│
│  - Estatísticas         │  - Confetti             │
│  - Resultado final      │                         │
└─────────────────────────┴─────────────────────────┘
```

## Componentes Principais

### 1. Coluna Esquerda - Ficha do Sorteio
- **Função**: Exibe informações do sorteio
- **Conteúdo**: Título, descrição, estatísticas, resultado final
- **Estilo**: Gradiente escuro com elementos destacados
- **Responsividade**: Adapta-se ao conteúdo

### 2. Coluna Central - Sorteio
- **Função**: Área principal de animação
- **Elementos**:
  - Relógio elegante em tempo real
  - Status do sorteio
  - Display de animação "slot machine"
  - Efeitos visuais (confetti, brilhos)
- **Animações**: Efeito de rolagem rápida com desaceleração

### 3. Coluna Direita - Ganhadores
- **Função**: Lista de ganhadores em tempo real
- **Características**:
  - Grid responsivo (1-4 colunas)
  - Animações sequenciais
  - Efeitos hover
  - Scroll suave

## Sistema de Grid Responsivo

### Lógica de Colunas
```javascript
if (ganhadores.length <= 5) {
    numColunas = 1;
} else if (ganhadores.length <= 10) {
    numColunas = 2;
} else if (ganhadores.length <= 15) {
    numColunas = 3;
} else {
    numColunas = 4;
}
```

### Breakpoints CSS
- **Desktop (>1400px)**: Até 4 colunas
- **Tablet (1200px-1400px)**: Máximo 3 colunas
- **Mobile (<768px)**: Sempre 1 coluna

## Animações e Transições

### 1. Animação do Sorteio
- **Técnica**: "Slot Machine" com velocidade variável
- **Velocidade inicial**: 50ms
- **Velocidade mínima**: 10ms
- **Desaceleração**: Gradual com chance de parada
- **Duração mínima**: 50 iterações

### 2. Transição Final
- **Duração**: 1.2 segundos
- **Easing**: `cubic-bezier(0.4, 0, 0.2, 1)`
- **Efeito**: Coluna central desaparece, laterais se expandem

### 3. Animações de Ganhadores
- **Entrada**: `animate__bounceIn` com delay sequencial
- **Hover**: Elevação e brilho
- **Grid**: Transição suave entre layouts

## Relógio Elegante

### Características
- **Fonte**: Courier New (monospace)
- **Tamanho**: 3rem
- **Efeitos**: 
  - Gradiente de fundo
  - Brilho animado
  - Sombra de texto
- **Atualização**: Tempo real (1 segundo)

### CSS do Relógio
```css
.relogio {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    position: relative;
    overflow: hidden;
}

.relogio::before {
    content: '';
    position: absolute;
    background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
    animation: relogioShine 3s ease-in-out infinite;
}
```

## Efeitos Visuais

### 1. Confetti de Celebração
- **Quantidade**: 80 peças por onda
- **Ondas**: 3 ondas com delay de 1s
- **Cores**: 8 cores variadas
- **Animação**: Queda com rotação

### 2. Brilhos e Gradientes
- **Relógio**: Brilho deslizante
- **Ganhadores**: Efeito hover com brilho
- **Display**: Sombra de texto animada

### 3. Transições Suaves
- **Layout**: 1.2s cubic-bezier
- **Grid**: 0.5s ease
- **Hover**: 0.3s ease

## Responsividade

### Breakpoints Principais
```css
@media (max-width: 1200px) {
    .sorteio-layout {
        flex-direction: column;
        height: auto;
    }
    
    .sorteio-col-ficha,
    .sorteio-col-central,
    .sorteio-col-ganhadores {
        width: 100% !important;
    }
}

@media (max-width: 768px) {
    .hora-atual {
        font-size: 2rem;
    }
    
    .sorteio-display-central .nome-sorteio {
        font-size: 2rem;
    }
}
```

## Integração Backend

### Rota de Salvamento
```python
@admin_bp.route('/instagram/sorteio/<int:sorteio_id>/salvar', methods=['POST'])
def salvar_sorteio_instagram_ajax(sorteio_id):
    # Salva vencedores no banco
    # Atualiza status do sorteio
    # Retorna resposta JSON
```

### Dados Passados para Frontend
```javascript
const participantes = {{ participantes_json|tojson }};
const sorteioTitulo = {{ sorteio.titulo|tojson }};
const sorteioDescricao = {{ sorteio.descricao|tojson }};
```

## Fluxo de Execução

### 1. Inicialização
1. Usuário clica em "Realizar Sorteio"
2. Validação de dados
3. Criação do modal fullscreen
4. Inicialização do relógio

### 2. Sorteio
1. População da ficha com dados
2. Animação sequencial para cada ganhador
3. Adição de ganhadores à lista direita
4. Efeitos visuais (confetti)

### 3. Finalização
1. Transição do layout (1.2s)
2. Atualização da ficha com resultados
3. Grid responsivo de ganhadores
4. Salvamento no backend
5. Alerta de sucesso

## Arquivos Principais

### Frontend
- `app/templates/admin/instagram_participantes.html` - Template principal
- `app/static/js/script.js` - Lógica JavaScript
- `app/static/css/style.css` - Estilos CSS

### Backend
- `app/routes/admin.py` - Rotas do sorteio
- `app/models.py` - Modelos de dados
- `app/utils.py` - Utilitários

## Considerações para Filmagem

### 1. Layout Otimizado
- Cores contrastantes para câmera
- Textos grandes e legíveis
- Animações suaves e profissionais

### 2. Timing
- Transições de 1.2s para câmera lenta
- Animações sequenciais para suspense
- Pausas estratégicas

### 3. Responsividade
- Funciona em diferentes resoluções
- Adapta-se a telas grandes
- Mantém legibilidade

## Troubleshooting

### Problemas Comuns
1. **Modal não abre**: Verificar se `script.js` está carregado
2. **Dados não aparecem**: Verificar `participantes_json` no backend
3. **Animações travam**: Verificar conflitos de CSS
4. **Layout quebra**: Verificar responsividade

### Debug
- Console do navegador para erros JavaScript
- Network tab para requisições AJAX
- Elements tab para inspecionar CSS

## Melhorias Futuras

### Sugestões
1. **Sons**: Efeitos sonoros para sorteio
2. **Streaming**: Integração com plataformas de streaming
3. **Temas**: Múltiplos temas visuais
4. **Estatísticas**: Gráficos em tempo real
5. **Histórico**: Salvamento de vídeos dos sorteios

---

**Nota**: Este sistema foi projetado especificamente para transmissões ao vivo e filmagens profissionais, com foco em visual impactante e animações fluidas. 