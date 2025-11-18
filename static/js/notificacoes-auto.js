/**
 * Atualização automática de notificações
 * Atualiza o badge de notificações no navbar periodicamente
 */

(function() {
    'use strict';
    
    const NOTIFICACOES_API_URL = '/militares/api/notificacoes/nao-lidas/';
    const UPDATE_INTERVAL = 30000; // 30 segundos
    
    let notificacoesInterval = null;
    
    /**
     * Atualiza o badge de notificações
     */
    function atualizarBadgeNotificacoes() {
        fetch(NOTIFICACOES_API_URL, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao buscar notificações');
            }
            return response.json();
        })
        .then(data => {
            const badge = document.querySelector('.nav-link[href*="notificacoes"] .notification-badge');
            const navIconWrapper = document.querySelector('.nav-link[href*="notificacoes"] .nav-icon-wrapper');
            
            if (data.total > 0) {
                // Se já existe badge, atualiza o número
                if (badge) {
                    badge.textContent = data.total;
                } else {
                    // Cria novo badge se não existir
                    if (navIconWrapper) {
                        const newBadge = document.createElement('span');
                        newBadge.className = 'notification-badge';
                        newBadge.textContent = data.total;
                        navIconWrapper.appendChild(newBadge);
                    }
                }
            } else {
                // Remove badge se não houver notificações
                if (badge) {
                    badge.remove();
                }
            }
        })
        .catch(error => {
            console.error('Erro ao atualizar notificações:', error);
        });
    }
    
    /**
     * Inicia a atualização automática
     */
    function iniciarAtualizacao() {
        // Atualiza imediatamente
        atualizarBadgeNotificacoes();
        
        // Configura atualização periódica
        notificacoesInterval = setInterval(atualizarBadgeNotificacoes, UPDATE_INTERVAL);
    }
    
    /**
     * Para a atualização automática
     */
    function pararAtualizacao() {
        if (notificacoesInterval) {
            clearInterval(notificacoesInterval);
            notificacoesInterval = null;
        }
    }
    
    // Inicia quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', iniciarAtualizacao);
    } else {
        iniciarAtualizacao();
    }
    
    // Para a atualização quando a página estiver sendo descarregada
    window.addEventListener('beforeunload', pararAtualizacao);
    
    // Expõe funções para uso externo se necessário
    window.NotificacoesAuto = {
        atualizar: atualizarBadgeNotificacoes,
        iniciar: iniciarAtualizacao,
        parar: pararAtualizacao
    };
    
})();

