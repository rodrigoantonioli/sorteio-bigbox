# Funcionalidade de Sorteio do Instagram

## Visão Geral

A funcionalidade de Sorteio do Instagram permite ao administrador realizar sorteios baseados em comentários de posts do Instagram, com uma interface moderna e uma experiência de sorteio "cinematográfica". Esta funcionalidade é **exclusiva para administradores**.

## Características Principais

### 1. Processamento de Comentários
- **Entrada de dados**: O administrador pode colar o texto copiado diretamente do Instagram ou fazer upload de um arquivo .txt contendo os comentários.
- **Validação inteligente**: Reconhece variações da palavra-chave (maiúsculas/minúsculas, com/sem pontuação).
- **Limite de tickets**: Cada participante pode ter no máximo um número configurável de tickets (padrão: 30).

### 2. Sistema de Tickets Ponderado
- Cada comentário válido que contém a palavra-chave conta como 1 ticket para o participante.
- **Sorteio Justo**: O sistema realiza um sorteio ponderado. Participantes com mais tickets (mais comentários válidos) têm proporcionalmente mais chances de ganhar.
- O número máximo de tickets por pessoa é configurável.

### 3. Sorteio Cinematográfico Interativo
- **Visualização em Cards**: Os participantes são exibidos em uma grade de cards, facilitando a visualização.
- **Animação "Chacoalhar"**: Um botão permite embaralhar visualmente os cards dos participantes antes do sorteio.
- **Sorteio em Tela Cheia**: Ao clicar em "Realizar Sorteio", um modal em tela cheia é aberto, exibindo uma animação com os nomes dos participantes passando rapidamente na tela.
- **Seleção de Vencedores**: A animação para nos vencedores, que são exibidos em destaque. O número de vencedores é configurável na tela do sorteio.
- **Resultado Persistente**: Após o sorteio, a tela exibe permanentemente os ganhadores.

## Como Usar

### 1. Acessar a Funcionalidade
- No dashboard do admin, clique em "Sorteios Instagram".
- Ou acesse diretamente: `/admin/instagram`

### 2. Criar Novo Sorteio
1.  Clique em "Novo Sorteio".
2.  Preencha os campos do formulário (título, palavra-chave, etc.).
3.  Cole o conteúdo dos comentários ou faça o upload de um arquivo .txt.
4.  Clique em "Processar Comentários". O sistema irá analisar os comentários e criar a lista de participantes.

### 3. Realizar o Sorteio
1.  Na lista de sorteios, clique em "Ver Participantes" no sorteio desejado.
2.  Você verá os cards de todos os participantes e as estatísticas.
3.  (Opcional) Clique em **"Chacoalhar Participantes"** para embaralhar os cards.
4.  Defina o **número de vencedores** que deseja sortear.
5.  Clique em **"Realizar Sorteio"**.
6.  Assista à animação em tela cheia. Os vencedores serão revelados ao final e salvos automaticamente.
7.  A página será recarregada exibindo os ganhadores.

## Estrutura Técnica
A estrutura de Models e o parser de comentários permanecem os mesmos, porém a interface foi completamente modernizada, utilizando cards e uma animação de sorteio em tela cheia controlada por JavaScript. A lógica de sorteio agora é ponderada, respeitando o número de tickets de cada participante para determinar a probabilidade de vitória. 