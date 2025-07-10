// Script principal do Sistema de Sorteios

document.addEventListener('DOMContentLoaded', function() {
    // Adiciona classe fade-in aos cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
    
    // Confirmação para ações críticas
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja realizar esta ação?')) {
                e.preventDefault();
            }
        });
    });
    
    // Tooltips do Bootstrap
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
});

// ========================================
//    SISTEMA DE SORTEIO ANIMADO
// ========================================

class SorteioAnimado {
    constructor() {
        this.isRunning = false;
        this.modal = null;
        this.intervalId = null;
        this.timeoutIds = [];
        this.ultimoVencedor = null; // Para armazenar o último item mostrado
        this.sorteioLojasComSucesso = false; // Flag para controlar reload
    }

    // Inicializa o sorteio de lojas
    iniciarSorteioLojas(lojasBig, lojasUltra) {
        this.criarModal('Sortear Lojas Ganhadoras', 'Preparando sorteio das lojas...');
        
        setTimeout(() => {
            this.executarSorteioSequencial([
                { nome: 'Loja BIG', items: lojasBig, cor: 'bandeira-big' },
                { nome: 'Loja ULTRA', items: lojasUltra, cor: 'bandeira-ultra' }
            ]);
        }, 1000);
    }

    // Inicializa o sorteio de colaboradores
    iniciarSorteioColaboradores(colaboradores, quantidade = 1) {
        this.criarModal('Sorteio de Colaboradores', 'Preparando sorteio dos colaboradores...');
        
        setTimeout(() => {
            this.executarSorteioColaboradores(colaboradores, quantidade);
        }, 1000);
    }

    // Inicializa o sorteio do Instagram
    iniciarSorteioInstagram(participantes, quantidadeVencedores, sorteioTitulo, sorteioDescricao) {
        this.criarModal('Sorteio Instagram', 'Preparando sorteio...');
        this.sorteioTitulo = sorteioTitulo;
        this.sorteioDescricao = sorteioDescricao;
        
        setTimeout(() => {
             this.executarSorteioInstagram(participantes, quantidadeVencedores);
        }, 1000);
    }

    // Cria o modal do sorteio
    criarModal(titulo, statusInicial) {
        // Remove modal existente se houver
        const existingModal = document.getElementById('sorteioModal');
        if (existingModal) {
            existingModal.remove();
        }

        const modalHtml = `
            <div class="modal fade" id="sorteioModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-fullscreen">
                    <div class="modal-content sorteio-modal">
                        <div class="modal-header border-0 position-relative">
                            <h4 class="modal-title text-white w-100 text-center">
                                🎲 ${titulo}
                            </h4>
                            <button type="button" id="fecharModalBtn" class="btn-close-custom d-none" data-bs-dismiss="modal" title="Fechar">
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                        <div class="modal-body p-0">
                            <div class="row g-0 h-100">
                                <!-- Coluna da Animação (Esquerda) -->
                                <div class="col-md-9 d-flex flex-column justify-content-center align-items-center sorteio-col-animacao">
                                    <div class="sorteio-status mb-3" id="sorteioStatus">${statusInicial}</div>
                                    <div class="sorteio-display" id="sorteioDisplay">
                                        <div class="nome-sorteio" id="nomeSorteio">Aguarde...</div>
                                        <div class="confetti-container" id="confettiContainer"></div>
                                    </div>
                                </div>
                                <!-- Coluna dos Ganhadores (Direita) -->
                                <div class="col-md-3 sorteio-col-ganhadores">
                                    <h5 class="text-center py-3">🏆 Ganhadores</h5>
                                    <ul class="list-group list-group-flush" id="listaGanhadores"></ul>
                                    <div class="p-3 mt-auto d-none" id="finalActions">
                                         <div class="alert alert-success"><i class="bi bi-check-circle-fill"></i> Sorteio salvo!</div>
                                         <button class="btn btn-primary w-100" id="fecharEAtualizarBtn">Fechar e Atualizar</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        this.modal = new bootstrap.Modal(document.getElementById('sorteioModal'));
        this.modal.show();

        document.getElementById('fecharModalBtn')?.addEventListener('click', () => this.modal.hide());
        document.getElementById('fecharEAtualizarBtn')?.addEventListener('click', () => window.location.reload());

        document.getElementById('sorteioModal').addEventListener('hidden.bs.modal', () => {
            if (this.sorteioConcluidoComSucesso) {
                window.location.reload();
            }
        });
    }

    // Executa sorteio sequencial (lojas)
    async executarSorteioSequencial(grupos) {
        const resultados = [];

        for (let i = 0; i < grupos.length; i++) {
            const grupo = grupos[i];
            this.atualizarStatus(`Sorteando ${grupo.nome}...`);
            
            // Adiciona indicador de bandeira
            this.adicionarIndicadorBandeira(grupo.cor);
            
            const vencedor = await this.executarAnimacaoSorteio(grupo.items);
            resultados.push({ tipo: grupo.nome, vencedor: vencedor });
            
            if (i < grupos.length - 1) {
                await this.delay(2000); // Pausa entre sorteios
            }
        }

        this.exibirResultadoFinal(resultados);
    }

    // Executa sorteio de colaboradores
    async executarSorteioColaboradores(colaboradores, quantidade) {
        const resultados = [];
        
        for (let i = 0; i < quantidade; i++) {
            this.atualizarStatus(`Sorteando ${i + 1}º colaborador${quantidade > 1 ? ` de ${quantidade}` : ''}...`);
            
            const vencedor = await this.executarAnimacaoSorteio(colaboradores);
            resultados.push(vencedor);
            
            // Remove o vencedor da lista para próximos sorteios
            const index = colaboradores.findIndex(c => c.nome === vencedor.nome);
            if (index > -1) {
                colaboradores.splice(index, 1);
            }
            
            if (i < quantidade - 1 && colaboradores.length > 0) {
                await this.delay(2000);
            }
        }

        this.exibirResultadoColaboradores(resultados);
    }

    // Executa sorteio do Instagram de forma sequencial e interativa
    async executarSorteioInstagram(ticketsPonderados, quantidade) {
        this.sorteioConcluidoComSucesso = false;
        const todosOsGanhadores = [];
        let ticketsDisponiveis = [...ticketsPonderados];

        for (let i = 0; i < quantidade; i++) {
            this.atualizarStatus(`Sorteando ${i + 1}º de ${quantidade} ganhador${quantidade > 1 ? 'es' : ''}...`);

            if (ticketsDisponiveis.length === 0) {
                this.atualizarStatus("Não há mais participantes elegíveis para sortear.");
                break;
            }

            const vencedor = await this.executarAnimacaoSorteio(ticketsDisponiveis);
            todosOsGanhadores.push(vencedor);

            // Adiciona o vencedor à lista da direita imediatamente
            this.adicionarGanhadorNaLista(vencedor, todosOsGanhadores.length);

            // Remove todos os tickets do vencedor para o próximo sorteio
            const usernameVencedor = vencedor.username;
            ticketsDisponiveis = ticketsDisponiveis.filter(p => p.username !== usernameVencedor);

            // Pausa antes do próximo sorteio, se houver
            if (i < quantidade - 1) {
                await this.delay(2500);
            }
        }

        // Finaliza o sorteio
        this.finalizarSorteio(todosOsGanhadores);
    }

    // Executa a animação do sorteio com efeito "Slot Machine" aprimorado
    executarAnimacaoSorteio(items) {
        return new Promise((resolve) => {
            const display = document.getElementById('nomeSorteio');
            const container = document.getElementById('sorteioDisplay');
            
            let speed = 50; // Velocidade inicial (ms)
            let iterations = 0;
            const minIterations = 50; // Mínimo de iterações para garantir um tempo de rolagem
            const maxSpeed = 200; // Velocidade máxima (mais lenta)
            const accelerationSteps = 20; // Quantidade de passos para acelerar/desacelerar

            display.className = 'nome-sorteio';
            container.className = 'sorteio-display';

            const interval = setInterval(() => {
                // Acelera no início
                if (iterations < accelerationSteps) {
                    speed = Math.max(10, speed - 2); // Acelera até 10ms
                }

                // Escolhe um item aleatório para exibir a cada tick
                const randomIndex = Math.floor(Math.random() * items.length);
                const item = items[randomIndex];
                display.textContent = item.nome || item.username || item.codigo || item;
                
                display.classList.add('animando');
                setTimeout(() => display.classList.remove('animando'), speed / 2); // Remove a classe mais rápido

                iterations++;

                // Lógica para parar a animação
                if (iterations >= minIterations && Math.random() < 0.05) { // Chance de parar após minIterations
                    clearInterval(interval);
                    
                    // Garante que o último item exibido seja o vencedor
                    const vencedor = item; 
                    
                    setTimeout(() => {
                        display.textContent = vencedor.nome || vencedor.username || vencedor.codigo || vencedor;
                        display.classList.add('vencedor');
                        container.classList.add('vencedor');
                        
                        this.criarConfetti();
                        resolve(vencedor);
                    }, 500); // Pequeno delay para o efeito final
                }
            }, speed);
        });
    }

    // Adiciona indicador de bandeira
    adicionarIndicadorBandeira(cor) {
        const container = document.getElementById('sorteioDisplay');
        const existing = container.querySelector('.bandeira-indicator');
        if (existing) existing.remove();

        const indicator = document.createElement('div');
        indicator.className = `bandeira-indicator ${cor}`;
        indicator.textContent = cor.includes('big') ? 'BIG' : 'ULTRA';
        container.appendChild(indicator);
    }

    // Cria efeito confetti
    criarConfetti() {
        const container = document.getElementById('confettiContainer');
        container.innerHTML = '';

        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.animationDelay = Math.random() * 3 + 's';
            confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
            container.appendChild(confetti);
        }

        // Remove confetti após animação
        setTimeout(() => {
            container.innerHTML = '';
        }, 5000);
    }

    // Cria confetti de celebração mais dinâmico
    criarConfettiCelebracao() {
        const container = document.getElementById('confettiCelebration');
        if (!container) return;
        
        container.innerHTML = '';

        // Cria múltiplas ondas de confetti
        for (let onda = 0; onda < 3; onda++) {
            setTimeout(() => {
                for (let i = 0; i < 80; i++) {
                    const confetti = document.createElement('div');
                    confetti.className = 'confetti-celebration-piece';
                    
                    // Cores variadas
                    const cores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9CA24', '#6C5CE7', '#FD79A8', '#00B894', '#FDCB6E'];
                    confetti.style.backgroundColor = cores[Math.floor(Math.random() * cores.length)];
                    
                    // Posição e tamanho aleatórios
                    confetti.style.left = Math.random() * 100 + '%';
                    confetti.style.width = (Math.random() * 8 + 4) + 'px';
                    confetti.style.height = confetti.style.width;
                    
                    // Animação personalizada
                    confetti.style.animationDelay = Math.random() * 2 + 's';
                    confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
                    
                    container.appendChild(confetti);
                }
            }, onda * 1000);
        }

        // Remove confetti após todas as ondas
        setTimeout(() => {
            if (container) container.innerHTML = '';
        }, 8000);
    }

    // Atualiza status do sorteio
    atualizarStatus(texto) {
        const status = document.getElementById('sorteioStatus');
        if (status) {
            status.textContent = texto;
        }
    }

    // Exibe resultado final das lojas - VERSÃO COMPACTA E ELEGANTE
    exibirResultadoFinal(resultados) {
        setTimeout(() => {
            // Gera data e hora atual
            const agora = new Date();
            const dataHora = agora.toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit', 
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            
            this.atualizarStatus('');
            
            const display = document.getElementById('sorteioDisplay');
            
            // Container compacto e harmonioso
            display.style.minHeight = '280px';
            display.className = 'sorteio-display resultado-final-compacto';
            
            display.innerHTML = `
                <div class="resultado-lojas-elegante">
                    <!-- Confetes dinâmicos -->
                    <div class="confetti-celebration" id="confettiCelebration"></div>
                    
                    <!-- Título Compacto -->
                    <div class="titulo-resultado-compacto mb-3">
                        🏆 Lojas Ganhadoras
                    </div>
                    
                    <!-- Data Discreta -->
                    <div class="data-discreta mb-4">
                        ${dataHora}
                    </div>
                    
                    <!-- Lojas Ganhadoras - Design Compacto -->
                    <div class="lojas-ganhadoras-compacto">
                        ${resultados.map((r, index) => `
                            <div class="loja-ganhadora-compacta ${r.tipo === 'Loja BIG' ? 'loja-big-elegante' : 'loja-ultra-elegante'}">
                                <div class="loja-badge-compacto">
                                    ${r.tipo === 'Loja BIG' ? 'BIG' : 'ULTRA'}
                                </div>
                                <div class="loja-icone-compacto">
                                    ${r.tipo === 'Loja BIG' ? '🏢' : '🏬'}
                                </div>
                                <div class="loja-nome-compacto">
                                    ${r.vencedor.nome}
                                </div>
                                <div class="loja-codigo-compacto">
                                    ${r.vencedor.codigo || ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;

            // Ativa confetes dinâmicos imediatamente
            this.criarConfettiCelebracao();
            
            // SALVA AUTOMATICAMENTE NO BANCO VIA AJAX (sem loading)
            setTimeout(() => {
                this.submitarFormularioAjax(resultados);
            }, 1000);
            
        }, 1500);
    }

    // Exibe resultado dos colaboradores (SEM BOTÃO DASHBOARD - como o sorteio das lojas)
    exibirResultadoColaboradores(resultados) {
        setTimeout(() => {
            // Gera data e hora atual
            const agora = new Date();
            const dataHora = agora.toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit', 
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            
            this.atualizarStatus('💾 Salvando sorteio no banco de dados...');
            
            const display = document.getElementById('sorteioDisplay');
            
            // Manter tamanho do container durante o sorteio (igual ao sorteio das lojas)
            display.style.minHeight = '350px';
            display.className = 'sorteio-display resultado-final-container';
            
            display.innerHTML = `
                <div class="resultado-final-completo">
                    <!-- Confetes dinâmicos -->
                    <div class="confetti-celebration" id="confettiCelebration"></div>
                    
                    <!-- Data e hora elegante -->
                    <div class="data-sorteio-elegante mb-4 text-center">
                        <i class="bi bi-calendar-check"></i> <strong>${dataHora}</strong>
                    </div>
                    
                    <!-- Status de salvamento -->
                    <div class="alert alert-info mb-4 status-salvamento" id="statusAlert">
                        <i class="bi bi-gear-fill animate-spin"></i> Salvando resultados no sistema...
                    </div>
                    
                    <!-- Resultado será inserido pelo template via AJAX -->
                    <div id="resultadoColaboradorContainer">
                        <!-- Conteúdo será preenchido pela função AJAX customizada -->
                    </div>
                </div>
            `;

            // Ativa confetes dinâmicos imediatamente
            this.criarConfettiCelebracao();
            
            // SALVA AUTOMATICAMENTE NO BANCO VIA AJAX
            setTimeout(() => {
                this.submitarFormularioColaboradoresAjax(resultados);
            }, 1500);
            
        }, 2000);
    }

    // Adiciona um ganhador à lista visual na coluna da direita
    adicionarGanhadorNaLista(ganhador, numero) {
        const listaGanhadores = document.getElementById('listaGanhadores');
        const item = document.createElement('li');
        item.className = 'list-group-item animate__animated animate__fadeInRight';
        item.innerHTML = `
            <span class="badge bg-primary me-2">#${numero}</span>
            @${ganhador.username}
        `;
        listaGanhadores.appendChild(item);
    }

    // Finaliza o sorteio, salva os dados e prepara para fechar
    finalizarSorteio(ganhadores) {
        this.atualizarStatus('Sorteio Concluído!');
        
        const sorteioDisplay = document.getElementById('sorteioDisplay');
        sorteioDisplay.innerHTML = `
            <div class="text-center w-100">
                <h3 class="text-white mb-3">🎉 Sorteio Finalizado! 🎉</h3>
                <p class="text-muted">${this.sorteioTitulo}</p>
                <p class="text-muted small">${this.sorteioDescricao}</p>
            </div>
        `;
        sorteioDisplay.classList.remove('vencedor'); // Remove a classe de vencedor do display principal

        // Salva os resultados e, no sucesso, mostra os botões finais
        this.submitarSorteioInstagramAjax(ganhadores, () => {
            this.sorteioConcluidoComSucesso = true;
            document.getElementById('finalActions').classList.remove('d-none');
            document.getElementById('fecharModalBtn').classList.remove('d-none'); // Mostra o X principal
        });
    }

    // Exibe resultado do Instagram (LEGADO - substituído pela nova lógica)
    exibirResultadoInstagram(resultados) {
        // Esta função foi substituída pela lógica em finalizarSorteio
        // e adicionarGanhadorNaLista. Mantida para evitar quebras em outras partes.
    }

    // Submete formulário de lojas via AJAX
    submitarFormularioAjax(resultados) {
        // Esta função será sobrescrita pelo template que a utiliza
        // Implementação padrão para fallback
        console.log('Resultados do sorteio:', resultados);
        this.exibirErro('Função de salvamento não configurada');
    }

    // Submete formulário de colaboradores via AJAX
    submitarFormularioColaboradoresAjax(resultados) {
        // Esta função será sobrescrita pelo template que a utiliza
        // Implementação padrão para fallback
        console.log('Colaboradores sorteados:', resultados);
        this.exibirErro('Função de salvamento não configurada');
    }

    // Submete formulário de Instagram via AJAX
    submitarSorteioInstagramAjax(resultados, successCallback) {
        console.log("Enviando vencedores para o servidor:", resultados);
        const url = `/admin/instagram/sorteio/${this.sorteioId}/salvar`; // Usa o ID do sorteio armazenado
        const vencedores = resultados.map(r => ({ username: r.username }));

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken // Usa o token CSRF armazenado
            },
            body: JSON.stringify({ vencedores: vencedores })
        })
        .then(response => {
            if (!response.ok) {
                // Tenta extrair uma mensagem de erro do corpo da resposta
                return response.json().then(err => { 
                    throw new Error(err.message || `Erro na rede: ${response.statusText}`); 
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log("Sorteio salvo com sucesso.");
                if (successCallback) successCallback(); // Executa o callback de sucesso
            } else {
                console.error("Erro ao salvar o sorteio:", data.message);
                this.exibirErro(data.message || 'Ocorreu um erro ao salvar o sorteio.');
            }
        })
        .catch(error => {
            console.error('Erro fatal na requisição AJAX:', error);
            this.exibirErro(error.message || 'Erro de comunicação com o servidor.');
        });
    }

    // Submete formulário de lojas (legado - será removido)
    submitarFormulario(resultados) {
        // Redireciona para função AJAX
        this.submitarFormularioAjax(resultados);
    }

    // Submete formulário de colaboradores (legado - será removido)
    submitarFormularioColaboradores(resultados) {
        // Redireciona para função AJAX
        this.submitarFormularioColaboradoresAjax(resultados);
    }

    // Exibe sucesso no sorteio - VERSÃO SILENCIOSA COM RELOAD
    exibirSucesso(mensagem) {
        const status = document.getElementById('sorteioStatus');
        const alertDiv = document.getElementById('statusAlert');
        const botoesDiv = document.getElementById('botoesAcao');
        const colaboradorContainer = document.getElementById('resultadoColaboradorContainer');
        const instagramContainer = document.getElementById('resultadoInstagramContainer');
        
        // Para sorteio de lojas: marca sucesso para reload automático SILENCIOSO 
        if (status && !colaboradorContainer && !instagramContainer) {
            this.sorteioLojasComSucesso = true; // Marca para reload quando fechar modal
            status.style.display = 'none'; // Mantém silencioso como antes (melhor para filmagem)
            console.log('✅ Sorteio de lojas salvo com sucesso - página será recarregada ao fechar (silencioso)');

            // Mostra mensagem de sucesso discreta no canto superior direito
            this.mostrarMensagemSucessoDiscreta();

            // Mostra o X para fechar após sucesso (mas sem mensagem)
            const fecharBtn = document.getElementById('fecharModalX');
            if (fecharBtn) {
                fecharBtn.classList.remove('d-none');
            }
        }
        
        // Remove alert de salvamento (não precisamos mostrar)
        if (alertDiv && !colaboradorContainer && !instagramContainer) {
            alertDiv.style.display = 'none';
        }
        
        // Se for sorteio de colaboradores, insere o resultado no container específico
        if (colaboradorContainer) {
            colaboradorContainer.innerHTML = mensagem;
            if (status) status.style.display = 'none';
            if (alertDiv) {
                alertDiv.className = 'alert alert-success mb-4';
                alertDiv.innerHTML = '<i class="bi bi-check-circle-fill"></i> Resultado salvo com sucesso!';
            }
        }

        // Se for sorteio de instagram, insere o resultado no container específico
        if (instagramContainer) {
            instagramContainer.innerHTML = mensagem;
            if (status) status.style.display = 'none';
            if (alertDiv) {
                alertDiv.className = 'alert alert-success mb-4';
                alertDiv.innerHTML = '<i class="bi bi-check-circle-fill"></i> Resultado salvo com sucesso!';
            }
        }
        
        // Para compatibilidade com sorteio de lojas (sem mostrar botões)
        if (botoesDiv && (colaboradorContainer || instagramContainer)) {
            botoesDiv.style.display = 'block';
        }
    }

    // Exibe erro no sorteio
    exibirErro(mensagem) {
        const status = document.getElementById('sorteioStatus');
        if (status) {
            status.innerHTML = `<div class="alert alert-danger">${mensagem}</div>`;
        }
        const alertDiv = document.getElementById('statusAlert');
        if (alertDiv) {
            alertDiv.className = 'alert alert-danger';
            alertDiv.innerHTML = `<i class="bi bi-exclamation-triangle-fill"></i> ${mensagem}`;
        }
        console.error('Erro no sorteio:', mensagem);
    }

    // Função utilitária para delay
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Mostra mensagem de sucesso discreta no canto superior direito
    mostrarMensagemSucessoDiscreta() {
        // Cria elemento se não existir
        let mensagemSucesso = document.getElementById('mensagem-sucesso-global');
        if (!mensagemSucesso) {
            mensagemSucesso = document.createElement('div');
            mensagemSucesso.id = 'mensagem-sucesso-global';
            mensagemSucesso.className = 'mensagem-sucesso-discreta';
            mensagemSucesso.innerHTML = '<i class="fas fa-check-circle me-2"></i>Resultado salvo!';
            document.body.appendChild(mensagemSucesso);
        }

        // Mostra a mensagem
        mensagemSucesso.style.display = 'block';
        
        // Remove a mensagem após 4 segundos
        setTimeout(() => {
            mensagemSucesso.style.display = 'none';
        }, 4000);
    }
}

// Instância global do sorteio
window.sorteioAnimado = new SorteioAnimado();

// Funções globais para uso nos templates
window.iniciarSorteioLojas = function(lojasBig, lojasUltra) {
    window.sorteioAnimado.iniciarSorteioLojas(lojasBig, lojasUltra);
};

window.iniciarSorteioColaboradores = function(colaboradores, quantidade = 1) {
    window.sorteioAnimado.iniciarSorteioColaboradores(colaboradores, quantidade);
};

window.iniciarSorteioInstagram = function(participantes, quantidadeVencedores = 1) {
    window.sorteioAnimado.iniciarSorteioInstagram(participantes, quantidadeVencedores);
};