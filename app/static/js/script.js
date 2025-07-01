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
    
    // Auto-hide alerts após 10 segundos (aumentado de 5 para 10 segundos)
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 10000); // Aumentado para 10 segundos
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

    // Cria o modal do sorteio
    criarModal(titulo, statusInicial) {
        // Remove modal existente se houver
        const existingModal = document.getElementById('sorteioModal');
        if (existingModal) {
            existingModal.remove();
        }

        const modalHtml = `
            <div class="modal fade" id="sorteioModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content sorteio-modal">
                        <div class="modal-header border-0 position-relative">
                            <h4 class="modal-title text-white w-100 text-center">
                                🎲 ${titulo}
                            </h4>
                            <button type="button" id="fecharModalX" class="btn-close-custom d-none" data-bs-dismiss="modal" title="Fechar">
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                        <div class="modal-body">
                            <div class="sorteio-status" id="sorteioStatus">
                                ${statusInicial}
                            </div>
                            <div class="sorteio-display" id="sorteioDisplay">
                                <div class="nome-sorteio" id="nomeSorteio">
                                    Aguarde...
                                </div>
                                <div class="confetti-container" id="confettiContainer"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        this.modal = new bootstrap.Modal(document.getElementById('sorteioModal'));
        this.modal.show();

        // Event listeners para o X
        document.getElementById('fecharModalX')?.addEventListener('click', () => {
            this.modal.hide();
        });

        // Event listener para quando o modal é fechado - RELOAD APÓS SORTEIO DE LOJAS
        document.getElementById('sorteioModal').addEventListener('hidden.bs.modal', () => {
            // Se houve sucesso no sorteio de lojas, recarrega a página para mostrar resultado
            if (this.sorteioLojasComSucesso) {
                console.log('🔄 Recarregando página após sorteio de lojas bem-sucedido...');
                // Reset da flag para próximos sorteios
                this.sorteioLojasComSucesso = false;
                setTimeout(() => {
                    window.location.reload();
                }, 300);
            }
        });

        // Permite fechar clicando no backdrop após sucesso
        document.getElementById('sorteioModal').addEventListener('click', (e) => {
            if (e.target.id === 'sorteioModal' && this.sorteioLojasComSucesso) {
                this.modal.hide();
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

    // Executa a animação do sorteio
    executarAnimacaoSorteio(items) {
        return new Promise((resolve) => {
            const display = document.getElementById('nomeSorteio');
            const container = document.getElementById('sorteioDisplay');
            
            let currentIndex = 0;
            let speed = 100; // Velocidade inicial (ms)
            let iterations = 0;
            const maxIterations = Math.random() * 30 + 50; // Entre 50-80 iterações
            this.ultimoVencedor = null; // Reset do último vencedor
            
            // Remove classes anteriores
            display.className = 'nome-sorteio';
            container.className = 'sorteio-display';

            const interval = setInterval(() => {
                // Aumenta a velocidade gradualmente
                iterations++;
                if (iterations > maxIterations * 0.7) {
                    speed += 20; // Desacelera no final
                }

                // Mostra item atual
                const item = items[currentIndex];
                this.ultimoVencedor = item; // Armazena o item atual
                display.textContent = item.nome || item.codigo || item;
                display.classList.add('animando');
                
                // Remove animação após um tempo
                setTimeout(() => {
                    display.classList.remove('animando');
                }, 200);

                currentIndex = (currentIndex + 1) % items.length;

                // Para o sorteio
                if (iterations >= maxIterations) {
                    clearInterval(interval);
                    
                    // USA O ÚLTIMO ITEM MOSTRADO NA TELA (correção do bug!)
                    const vencedor = this.ultimoVencedor;
                    
                    // Animação final
                    setTimeout(() => {
                        display.textContent = vencedor.nome || vencedor.codigo || vencedor;
                        display.classList.add('vencedor');
                        container.classList.add('vencedor');
                        
                        // Efeito confetti
                        this.criarConfetti();
                        
                        resolve(vencedor);
                    }, 500);
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
        
        // Para sorteio de lojas: marca sucesso para reload automático
        if (status && !colaboradorContainer) {
            this.sorteioLojasComSucesso = true; // Marca para reload quando fechar modal
            status.textContent = '✅ Sorteio salvo! Feche para ver o resultado na página.';
            status.style.display = 'block';
            status.className = 'sorteio-status sucesso-discreto';
            console.log('✅ Sorteio de lojas salvo com sucesso - página será recarregada ao fechar');
            
            // Mostra o X para fechar após sucesso
            const fecharBtn = document.getElementById('fecharModalX');
            if (fecharBtn) {
                fecharBtn.classList.remove('d-none');
            }
        }
        
        // Remove alert de salvamento (não precisamos mostrar)
        if (alertDiv && !colaboradorContainer) {
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
        
        // Para compatibilidade com sorteio de lojas (sem mostrar botões)
        if (botoesDiv && colaboradorContainer) {
            botoesDiv.style.display = 'block';
        }
    }

    // Exibe erro no sorteio
    exibirErro(mensagem) {
        const status = document.getElementById('sorteioStatus');
        const alertDiv = document.getElementById('statusAlert');
        const botoesDiv = document.getElementById('botoesAcao');
        
        if (status) status.textContent = '❌ Erro ao salvar sorteio';
        
        if (alertDiv) {
            alertDiv.className = 'alert alert-danger mb-3';
            alertDiv.innerHTML = '<i class="bi bi-x-circle-fill"></i> ' + mensagem;
        }
        
        if (botoesDiv) {
            botoesDiv.style.display = 'block';
        }
    }

    // Função utilitária para delay
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
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