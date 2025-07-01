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
    }

    // Inicializa o sorteio de lojas
    iniciarSorteioLojas(lojasBig, lojasUltra) {
        this.criarModal('Sorteio de Lojas', 'Preparando sorteio das lojas...');
        
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
                        <div class="modal-header">
                            <h4 class="modal-title text-white w-100">
                                🎲 ${titulo}
                            </h4>
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
                            <div class="mt-3">
                                <button type="button" class="btn btn-secondary d-none" id="fecharModal" data-bs-dismiss="modal">
                                    Fechar
                                </button>
                                <button type="button" class="btn btn-novo-sorteio d-none" id="novoSorteio">
                                    🎲 Novo Sorteio
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        this.modal = new bootstrap.Modal(document.getElementById('sorteioModal'));
        this.modal.show();

        // Event listeners
        document.getElementById('novoSorteio')?.addEventListener('click', () => {
            this.modal.hide();
            location.reload();
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

    // Atualiza status do sorteio
    atualizarStatus(texto) {
        const status = document.getElementById('sorteioStatus');
        if (status) {
            status.textContent = texto;
        }
    }

    // Exibe resultado final das lojas
    exibirResultadoFinal(resultados) {
        setTimeout(() => {
            this.atualizarStatus('🎉 Sorteio concluído com sucesso!');
            
            const display = document.getElementById('sorteioDisplay');
            display.innerHTML = `
                <div class="resultado-final">
                    ${resultados.map(r => `
                        <div class="mb-3">
                            <h5 class="text-primary">${r.tipo}</h5>
                            <div class="nome-sorteio vencedor" style="font-size: 1.8rem;">
                                ${r.vencedor.nome || r.vencedor.codigo}
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;

            // Mostra botões
            document.getElementById('fecharModal').classList.remove('d-none');
            document.getElementById('novoSorteio').classList.remove('d-none');
            
            // RESULTADO PERMANECE NA TELA - Não submete automaticamente
            // Usuário decide quando fechar ou fazer novo sorteio
            
        }, 2000);
    }

    // Exibe resultado dos colaboradores
    exibirResultadoColaboradores(resultados) {
        setTimeout(() => {
            this.atualizarStatus('🎉 Sorteio de colaboradores concluído!');
            
            const display = document.getElementById('sorteioDisplay');
            display.innerHTML = `
                <div class="resultado-final">
                    <h5 class="text-primary mb-3">
                        ${resultados.length > 1 ? 'Colaboradores Sorteados' : 'Colaborador Sorteado'}
                    </h5>
                    ${resultados.map((colaborador, index) => `
                        <div class="mb-2">
                            <div class="nome-sorteio vencedor" style="font-size: ${resultados.length > 1 ? '1.5rem' : '2rem'};">
                                ${index + 1}. ${colaborador.nome}
                            </div>
                            <small class="text-muted">${colaborador.setor}</small>
                        </div>
                    `).join('')}
                </div>
            `;

            // Mostra botões
            document.getElementById('fecharModal').classList.remove('d-none');
            document.getElementById('novoSorteio').classList.remove('d-none');
            
            // RESULTADO PERMANECE NA TELA - Não submete automaticamente
            // Usuário decide quando fechar ou fazer novo sorteio
            
        }, 2000);
    }

    // Submete formulário de lojas
    submitarFormulario(resultados) {
        // Aqui você implementaria a submissão real do formulário
        // Por enquanto, apenas fecha o modal
        console.log('Resultados do sorteio:', resultados);
        // this.modal.hide();
    }

    // Submete formulário de colaboradores
    submitarFormularioColaboradores(resultados) {
        // Aqui você implementaria a submissão real do formulário
        console.log('Colaboradores sorteados:', resultados);
        // this.modal.hide();
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