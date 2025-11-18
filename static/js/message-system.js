/**
 * Sistema de Mensagens Flutuantes (Toasts)
 * Mostra apenas mensagens de ERRO como toasts flutuantes
 * Outras mensagens permanecem como alertas estáticos
 */

class MessageSystem {
    constructor() {
        this.container = null;
        this.messageQueue = [];
        this.isProcessing = false;
        this.init();
    }

    init() {
        // Sistema de toast desabilitado - usando modais modernos em todo o sistema
        return;
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        this.container.className = 'toast-container position-fixed top-0 end-0 p-3';
        this.container.style.zIndex = '9999';
        document.body.appendChild(this.container);
    }

    showToast(message, type = 'error', duration = 8000) {
        // Sistema de toast desabilitado - usando modais modernos
        return null;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    processDjangoMessages() {
        // Sistema de toast desabilitado - mensagens de erro serão tratadas por modais modernos
        return;
    }

    setupGlobalFunctions() {
        // Sistema de toast desabilitado - funções não disponibilizadas
        return;
    }

    // Método apenas para erros
    error(message, duration = 8000) {
        // Sistema de toast desabilitado - usando modais modernos
        return null;
    }
}

// Inicializar o sistema de mensagens quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    window.messageSystem = new MessageSystem();
});

// Função global para compatibilidade (apenas erros)
function showErrorToast(message, duration = 8000) {
    // Sistema de toast desabilitado - usando modais modernos
    return null;
}
