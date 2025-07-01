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
            display.innerHTML = `
                <div class="resultado-final">
                    <div class="mb-4 text-center">
                        <div class="data-sorteio mb-3">
                            <i class="bi bi-calendar-check"></i> <strong>${dataHora}</strong>
                        </div>
                        <div class="alert alert-info mb-3" id="statusAlert">
                            <i class="bi bi-gear-fill"></i> Salvando resultados...
                        </div>
                    </div>
                    <div class="text-center mb-4">
                        <h3>🎉 PARABÉNS AOS GANHADORES! 🎉</h3>
                    </div>
                    ${resultados.map(r => `
                        <div class="mb-4 text-center">
                            <h4 class="text-primary">${r.tipo === 'Loja BIG' ? '🏢' : '🏬'} ${r.tipo}</h4>
                            <div class="ganhador-nome ${r.tipo === 'Loja BIG' ? 'ganhador-big' : 'ganhador-ultra'}" style="font-size: 3rem;">
                                ${r.vencedor.nome}
                            </div>
                        </div>
                    `).join('')}
                    <div class="text-center mt-4" id="botoesAcao" style="display: none;">
                        <button type="button" class="btn btn-discreto" onclick="window.location.href='/admin/dashboard'">
                            ← Voltar ao Dashboard
                        </button>
                    </div>
                </div>
            `;

            // SALVA AUTOMATICAMENTE NO BANCO VIA AJAX
            setTimeout(() => {
                this.submitarFormularioAjax(resultados);
            }, 1500);
            
        }, 2000);
    }

    // Exibe resultado dos colaboradores
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
            display.innerHTML = `
                <div class="resultado-final">
                    <div class="mb-4 text-center">
                        <div class="data-sorteio mb-3">
                            <i class="bi bi-calendar-check"></i> <strong>${dataHora}</strong>
                        </div>
                        <div class="alert alert-info mb-3" id="statusAlert">
                            <i class="bi bi-gear-fill"></i> Salvando resultados...
                        </div>
                    </div>
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
                    <div class="text-center mt-4" id="botoesAcao" style="display: none;">
                        <a href="/manager/dashboard" class="btn btn-warning btn-lg">
                            <i class="bi bi-arrow-left"></i> Ir para Dashboard
                        </a>
                    </div>
                </div>
            `;

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

    // Exibe sucesso no sorteio
    exibirSucesso(mensagem) {
        const status = document.getElementById('sorteioStatus');
        const alertDiv = document.getElementById('statusAlert');
        const botoesDiv = document.getElementById('botoesAcao');
        
        if (status) status.textContent = '✅ Sorteio concluído com sucesso!';
        
        if (alertDiv) {
            alertDiv.className = 'alert alert-success mb-3';
            alertDiv.innerHTML = '<i class="bi bi-check-circle-fill"></i> ' + mensagem;
        }
        
        if (botoesDiv) {
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