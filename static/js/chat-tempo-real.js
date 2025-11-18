/**
 * Sistema de Chat em Tempo Real
 * Atualização automática de mensagens tipo WhatsApp
 */

class ChatTempoReal {
    constructor(chatId) {
        this.chatId = chatId;
        this.pollInterval = 2000; // 2 segundos
        this.pollTimer = null;
        this.ultimaMensagemId = null;
        this.chatMensagens = document.getElementById('chat-mensagens');
        this.formEnviar = document.getElementById('form-enviar-mensagem');
        this.inputMensagem = document.getElementById('input-mensagem');
    }

    init() {
        // Obter última mensagem ID
        this.obterUltimaMensagemId();
        
        // Configurar formulário de envio
        if (this.formEnviar) {
            this.formEnviar.addEventListener('submit', (e) => this.enviarMensagem(e));
        }
        
        // Iniciar polling
        this.iniciarPolling();
        
        // Verificar quando a página ganha foco
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.buscarNovasMensagens();
            }
        });
        
        // Scroll automático
        this.scrollParaFinal();
    }

    obterUltimaMensagemId() {
        const mensagens = this.chatMensagens.querySelectorAll('[data-mensagem-id]');
        if (mensagens.length > 0) {
            const ultima = mensagens[mensagens.length - 1];
            this.ultimaMensagemId = parseInt(ultima.getAttribute('data-mensagem-id'));
        }
    }

    iniciarPolling() {
        this.pollTimer = setInterval(() => {
            this.buscarNovasMensagens();
            this.verificarStatusOnline();
        }, this.pollInterval);
    }
    
    async verificarStatusOnline() {
        // Verificar status online do outro participante
        const outroParticipanteId = this.obterOutroParticipanteId();
        if (!outroParticipanteId) return;
        
        try {
            const response = await fetch(`/militares/api/chat/status-online/${outroParticipanteId}/`);
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.atualizarStatusOnline(data.online);
                }
            }
        } catch (error) {
            // Silenciar erro
        }
    }
    
    obterOutroParticipanteId() {
        // Tentar obter do contexto da página
        const chatHeader = document.querySelector('.chat-header-modern');
        if (chatHeader) {
            const outroId = chatHeader.getAttribute('data-outro-participante-id');
            return outroId ? parseInt(outroId) : null;
        }
        return null;
    }
    
    atualizarStatusOnline(online) {
        const statusElement = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        if (statusElement) {
            if (online) {
                statusElement.className = 'status-online';
                if (statusText) {
                    statusText.textContent = 'Online';
                }
            } else {
                statusElement.className = 'status-offline';
                if (statusText) {
                    statusText.textContent = 'Offline';
                }
            }
        }
    }

    pararPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }

    async buscarNovasMensagens() {
        try {
            const url = `/militares/api/chat/${this.chatId}/mensagens/`;
            const params = this.ultimaMensagemId ? `?ultima_id=${this.ultimaMensagemId}` : '';
            
            const response = await fetch(url + params, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            if (!response.ok) {
                throw new Error('Erro ao buscar mensagens');
            }

            const data = await response.json();
            
            if (data.success && data.mensagens && data.mensagens.length > 0) {
                data.mensagens.forEach(mensagem => {
                    this.adicionarMensagem(mensagem);
                    this.ultimaMensagemId = mensagem.id;
                });
                this.scrollParaFinal();
            }
        } catch (error) {
            console.error('Erro ao buscar mensagens:', error);
        }
    }

    adicionarMensagem(mensagem) {
        // Verificar se a mensagem já existe
        const existe = this.chatMensagens.querySelector(`[data-mensagem-id="${mensagem.id}"]`);
        if (existe) {
            return;
        }

        const mensagemDiv = document.createElement('div');
        mensagemDiv.className = 'd-flex';
        mensagemDiv.setAttribute('data-mensagem-id', mensagem.id);
        
        const isEnviada = mensagem.remetente_id === this.obterUsuarioId();
        mensagemDiv.classList.add(isEnviada ? 'message-sent justify-content-end' : 'message-received justify-content-start');
        
        const hora = this.formatarHora(mensagem.data_envio);
        const iconeLeitura = isEnviada ? (mensagem.lida ? '<i class="fas fa-check-double ms-1"></i>' : '<i class="fas fa-check ms-1"></i>') : '';
        const inicialRemetente = mensagem.remetente ? mensagem.remetente.charAt(0).toUpperCase() : '?';
        
        // Obter foto do remetente (pode ser do outro ou do usuário logado)
        let remetenteFoto = mensagem.remetente_foto || null;
        if (!remetenteFoto && !isEnviada) {
            // Se não tem foto na mensagem e é mensagem recebida, tentar obter de mensagens anteriores
            const outraMsg = document.querySelector('.message-received .message-avatar.avatar-received img');
            if (outraMsg) {
                remetenteFoto = outraMsg.src;
            }
        }
        
        // Obter foto do usuário logado
        let usuarioFoto = this.obterFotoUsuario();
        if (!usuarioFoto && isEnviada) {
            // Se não tem foto do usuário, usar a foto que vem na mensagem
            usuarioFoto = mensagem.remetente_foto || null;
        }
        
        mensagemDiv.innerHTML = `
            <div class="message-bubble d-flex align-items-end">
                ${!isEnviada ? `
                ${remetenteFoto ? `
                <img src="${remetenteFoto}" alt="${mensagem.remetente}" class="message-avatar avatar-received" style="object-fit: cover;">
                ` : `
                <div class="message-avatar avatar-received">
                    ${inicialRemetente}
                </div>
                `}
                ` : ''}
                <div class="bubble-content ${isEnviada ? 'bubble-sent' : 'bubble-received'}">
                    <div>${this.escapeHtml(mensagem.texto).replace(/\n/g, '<br>')}</div>
                    <div class="message-time">
                        ${hora}${iconeLeitura}
                    </div>
                </div>
                ${isEnviada ? `
                ${usuarioFoto ? `
                <img src="${usuarioFoto}" alt="Você" class="message-avatar avatar-sent" style="object-fit: cover;">
                ` : `
                <div class="message-avatar avatar-sent">
                    ${this.obterInicialUsuario()}
                </div>
                `}
                ` : ''}
            </div>
        `;
        
        const container = this.chatMensagens.querySelector('#mensagens-container');
        if (container) {
            container.appendChild(mensagemDiv);
        } else {
            // Se não existe container, criar
            const novoContainer = document.createElement('div');
            novoContainer.id = 'mensagens-container';
            this.chatMensagens.appendChild(novoContainer);
            novoContainer.appendChild(mensagemDiv);
        }
    }
    
    obterInicialUsuario() {
        // Tentar obter do nome do usuário logado
        const usuarioNome = document.querySelector('.chat-header-modern h6')?.textContent || 'U';
        return usuarioNome.charAt(0).toUpperCase();
    }
    
    obterFotoUsuario() {
        // Tentar obter foto do usuário logado das mensagens existentes
        const usuarioAvatar = document.querySelector('.message-avatar.avatar-sent img');
        if (usuarioAvatar) {
            return usuarioAvatar.src;
        }
        return null;
    }

    async enviarMensagem(e) {
        e.preventDefault();
        
        const mensagemTexto = this.inputMensagem.value.trim();
        if (!mensagemTexto) {
            return;
        }
        
        // Limpar input
        this.inputMensagem.value = '';
        
        try {
            const formData = new FormData();
            formData.append('mensagem', mensagemTexto);
            formData.append('csrfmiddlewaretoken', this.obterCSRFToken());
            
            const response = await fetch(`/militares/chat/${this.chatId}/enviar/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            if (!response.ok) {
                throw new Error('Erro ao enviar mensagem');
            }

            const data = await response.json();
            
            if (data.success) {
                // Adicionar mensagem imediatamente
                this.adicionarMensagem(data.mensagem);
                this.ultimaMensagemId = data.mensagem.id;
                this.scrollParaFinal();
            }
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            alert('Erro ao enviar mensagem. Tente novamente.');
            this.inputMensagem.value = mensagemTexto; // Restaurar texto
        }
    }

    scrollParaFinal() {
        if (this.chatMensagens) {
            this.chatMensagens.scrollTop = this.chatMensagens.scrollHeight;
        }
    }

    formatarHora(dataHora) {
        const date = new Date(dataHora);
        const horas = String(date.getHours()).padStart(2, '0');
        const minutos = String(date.getMinutes()).padStart(2, '0');
        return `${horas}:${minutos}`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    obterCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    obterUsuarioId() {
        // Tentar obter do contexto ou de um atributo data
        const usuarioId = document.body.getAttribute('data-usuario-id');
        return usuarioId ? parseInt(usuarioId) : null;
    }
}

// Classe para atualizar lista de chats
class ChatListaTempoReal {
    constructor() {
        this.pollInterval = 5000; // 5 segundos
        this.pollTimer = null;
    }

    init() {
        // NÃO iniciar automaticamente - só quando o chat widget for aberto
        // this.iniciarPolling();
    }

    iniciarPolling() {
        // Se já estiver rodando, não iniciar novamente
        if (this.pollTimer) {
            return;
        }
        this.pollTimer = setInterval(() => {
            this.atualizarLista();
        }, this.pollInterval);
    }
    
    pararPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }

    async atualizarLista() {
        try {
            const response = await fetch('/militares/api/chat/chats/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            if (!response.ok) {
                // Se não for OK, parar o polling silenciosamente
                if (this.pollTimer) {
                    clearInterval(this.pollTimer);
                    this.pollTimer = null;
                }
                return;
            }

            const data = await response.json();
            
            if (data.success) {
                // Atualizar badge de mensagens não lidas
                this.atualizarBadge(data.total_nao_lidas);
            }
        } catch (error) {
            // Erro de conexão - parar o polling silenciosamente
            // Não logar erro se for apenas conexão recusada (servidor pode não estar rodando o chat)
            if (error.message && error.message.includes('Failed to fetch')) {
                if (this.pollTimer) {
                    clearInterval(this.pollTimer);
                    this.pollTimer = null;
                }
                return;
            }
            // Logar apenas erros inesperados
            console.error('Erro ao atualizar lista de chats:', error);
        }
    }

    atualizarBadge(count) {
        const badge = document.getElementById('chat-badge-nav');
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    }
}

// Inicializar quando o DOM estiver pronto
// NÃO inicializar automaticamente - só quando o chat widget for aberto
document.addEventListener('DOMContentLoaded', () => {
    // Criar instância global mas não iniciar polling ainda
    // O polling será iniciado quando o chat widget for aberto
    if (document.getElementById('chat-mensagens') === null) {
        window.chatLista = new ChatListaTempoReal();
        // NÃO chamar init() aqui - será chamado quando o chat for aberto
    }
});

