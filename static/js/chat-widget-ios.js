/**
 * Chat Widget iOS - Flutuante e Sobrepõe a Página
 */

class ChatWidgetIOS {
    constructor() {
        this.panel = document.getElementById('chat-panel');
        this.toggleBtn = document.getElementById('chat-toggle-btn');
        this.isOpen = false;
        this.currentChatId = null;
        this.pollInterval = 2000;
        this.pollTimer = null;
        this.ultimaMensagemId = null;
        this.emojiPickerVisible = false;
        this.chatCalls = null;
        this.chatsCache = null; // Cache de conversas
        this.ultimaTotalNaoLidas = 0; // Para detectar novas mensagens
        this.notificacoesPermitidas = false; // Status da permissão de notificações
        this.pollTimerNotificacoes = null; // Timer para polling de notificações quando chat fechado
        this.init();
    }

    init() {
        // Event listeners
        if (this.toggleBtn) { this.toggleBtn.addEventListener('click', () => this.togglePanel()); }
        var elClose = document.getElementById('btn-close-chat'); if (elClose) { elClose.addEventListener('click', () => this.closePanel()); }
        var elMin = document.getElementById('btn-minimize-chat'); if (elMin) { elMin.addEventListener('click', () => this.minimizePanel()); }
        var elRestore = document.getElementById('btn-restore-chat'); if (elRestore) { elRestore.addEventListener('click', () => this.restorePanel()); }
        var elIndicator = document.getElementById('chat-minimized-indicator'); if (elIndicator) { elIndicator.addEventListener('click', () => this.restorePanel()); }
        var elNova = document.getElementById('btn-nova-conversa'); if (elNova) { elNova.addEventListener('click', () => this.showNovaConversa()); }
        var elBack = document.getElementById('btn-back-conversas'); if (elBack) { elBack.addEventListener('click', () => this.showConversas()); }
        var elBackNova = document.getElementById('btn-back-conversas-nova'); if (elBackNova) { elBackNova.addEventListener('click', () => this.showConversas()); }
        var elFormEnviar = document.getElementById('chat-form-enviar'); if (elFormEnviar) { elFormEnviar.addEventListener('submit', (e) => this.enviarMensagem(e)); }
        var elBuscaUsuarios = document.getElementById('chat-search-usuarios'); if (elBuscaUsuarios) { elBuscaUsuarios.addEventListener('input', (e) => this.buscarUsuarios(e.target.value)); }
        var elOverlay = document.getElementById('chat-overlay'); if (elOverlay) { elOverlay.addEventListener('click', () => this.closePanel()); }
        
        // Fechar emoji picker ao clicar fora
        document.addEventListener('click', (e) => {
            const picker = document.getElementById('emoji-picker');
            const btnEmoji = document.getElementById('btn-emoji-chat');
            if (picker && this.emojiPickerVisible && 
                !picker.contains(e.target) && 
                (!btnEmoji || !btnEmoji.contains(e.target))) {
                this.fecharEmojiPicker();
            }
        });
        
        // Busca de conversas
        var elBusca = document.getElementById('chat-search-input'); if (elBusca) { elBusca.addEventListener('input', (e) => this.buscarConversas(e.target.value)); }
        
        // Emoji picker
        var elEmoji = document.getElementById('btn-emoji-chat'); if (elEmoji) { elEmoji.addEventListener('click', () => this.toggleEmojiPicker()); }
        var elCloseEmoji = document.getElementById('btn-close-emoji'); if (elCloseEmoji) { elCloseEmoji.addEventListener('click', () => this.fecharEmojiPicker()); }
        
        // Carregar conversas
        this.carregarConversas();
        this.carregarUsuarios();
        
        // Inicializar emoji picker
        this.inicializarEmojiPicker();
        
        // Sistema de chamadas desabilitado
        // if (typeof ChatCalls !== 'undefined') {
        //     this.chatCalls = new ChatCalls(this);
        // }
        this.chatCalls = null;
        
        // Inicializar sistema de mensagens de voz
        if (typeof ChatVoiceMessage !== 'undefined') {
            this.chatVoiceMessage = new ChatVoiceMessage(this);
        }
        
        // Solicitar permissão de notificações
        this.solicitarPermissaoNotificacoes();
        
        // Remover/esconder qualquer botão de chamada que possa existir
        this.removerBotoesChamada();
        
        // NÃO iniciar polling automaticamente - só quando houver atividade
        // O polling será iniciado quando:
        // 1. O chat for aberto (openPanel)
        // 2. Houver envio de mensagem
        // 3. Houver recebimento de mensagem
        // Fazer apenas uma verificação inicial para carregar o estado
        setTimeout(() => {
            this.carregarConversas();
        }, 1000);
        
        // NÃO iniciar polling aqui - só inicia quando o chat for aberto
        // O polling será iniciado em openPanel()
    }
    
    removerBotoesChamada() {
        // Remover/esconder botões de chamada
        const btnVideo = document.getElementById('btn-call-video');
        const btnVoice = document.getElementById('btn-call-voice');
        const acoesContato = document.getElementById('chat-acoes-contato');
        const overlayChamada = document.getElementById('chat-call-overlay');
        
        if (btnVideo) {
            btnVideo.remove();
        }
        if (btnVoice) {
            btnVoice.remove();
        }
        if (acoesContato) {
            acoesContato.remove();
        }
        if (overlayChamada) {
            overlayChamada.remove();
        }
        
        // Remover qualquer listener de chamadas que possa existir
        if (typeof ChatCalls !== 'undefined') {
            console.log('⚠️ ChatCalls ainda está definido, mas não será usado');
        }
    }
    
    verificarNovasMensagens() {
        // Verificação imediata de novas mensagens
        // Só verificar se houver atividade recente ou se o chat estiver aberto
        const tempoDesdeUltimaAtividade = Date.now() - (this.ultimaAtividade || 0);
        const estaInativo = tempoDesdeUltimaAtividade > 60000; // 1 minuto sem atividade
        
        // Se estiver inativo e o chat estiver fechado, não verificar
        if (estaInativo && !this.isOpen) {
            return;
        }
        
        if (!this.isOpen) {
            this.carregarConversas();
        } else {
            // Se o chat está aberto, apenas atualizar o badge
            fetch('/militares/api/chat/chats/', {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Response not OK');
            })
            .then(data => {
                if (data.success) {
                    this.atualizarBadge(data.total_nao_lidas || 0);
                    // Se houver novas mensagens não lidas, registrar atividade
                    if (data.total_nao_lidas > 0) {
                        this.registrarAtividade();
                    }
                }
            })
            .catch(error => {
                // Erro silencioso
            });
        }
    }
    
    iniciarPollingNotificacoes() {
        // Polling para verificar novas mensagens e atualizar badge
        // Só inicia se o chat estiver aberto ou se houver atividade recente
        if (this.pollTimerNotificacoes) {
            clearInterval(this.pollTimerNotificacoes);
        }
        
        // Verificar apenas quando necessário (chat aberto ou atividade recente)
        // Intervalo maior quando inativo (30 segundos) e menor quando ativo (5 segundos)
        this.ultimaAtividade = Date.now();
        this.intervaloInativo = 30000; // 30 segundos quando inativo
        this.intervaloAtivo = 5000; // 5 segundos quando ativo
        
        this.pollTimerNotificacoes = setInterval(() => {
            try {
                const tempoDesdeUltimaAtividade = Date.now() - (this.ultimaAtividade || 0);
                const estaInativo = tempoDesdeUltimaAtividade > 60000; // 1 minuto sem atividade
                
                // Se estiver inativo e o chat estiver fechado, parar o polling
                if (estaInativo && !this.isOpen) {
                    this.pararPollingNotificacoes();
                    return;
                }
                
                // Se o chat estiver aberto ou houver atividade recente, verificar
                if (this.isOpen || tempoDesdeUltimaAtividade < 60000) {
                    this.verificarNovasMensagens();
                }
            } catch (error) {
                // Se houver erro, tentar reiniciar o polling após 5 segundos
                console.warn('Erro no polling de notificações, tentando reiniciar...', error);
                setTimeout(() => {
                    if (!this.pollTimerNotificacoes) {
                        this.iniciarPollingNotificacoes();
                    }
                }, 5000);
            }
        }, this.intervaloAtivo); // Usar intervalo ativo por padrão
        
        console.log('✅ Polling de notificações iniciado (modo ativo)');
    }
    
    registrarAtividade() {
        // Registrar atividade do usuário (envio de mensagem, abertura de chat, etc)
        this.ultimaAtividade = Date.now();
        
        // Se o polling estava parado, reiniciar
        if (!this.pollTimerNotificacoes && this.isOpen) {
            this.iniciarPollingNotificacoes();
        }
    }
    
    pararPollingNotificacoes() {
        if (this.pollTimerNotificacoes) {
            clearInterval(this.pollTimerNotificacoes);
            this.pollTimerNotificacoes = null;
        }
    }
    
    async solicitarPermissaoNotificacoes() {
        if (!('Notification' in window)) {
            console.log('Este navegador não suporta notificações');
            return;
        }
        
        if (Notification.permission === 'granted') {
            this.notificacoesPermitidas = true;
            console.log('✅ Permissão de notificações já concedida');
        } else if (Notification.permission !== 'denied') {
            // A permissão será solicitada quando o usuário receber a primeira mensagem
            console.log('Permissão de notificações ainda não solicitada');
        }
    }
    
    async mostrarNotificacaoMensagem(mensagem, nomeContato, fotoContato) {
        // Notificações do navegador desabilitadas - apenas o badge pulsante será usado
        return;
        
        /* Código de notificações desabilitado
        // Verificar se o chat está fechado ou minimizado
        if (this.isOpen && this.currentChatId === String(mensagem.chat)) {
            // Chat está aberto e é o chat atual - não mostrar notificação
            return;
        }
        
        // Verificar permissão
        if (!('Notification' in window)) {
            return;
        }
        
        if (Notification.permission === 'default') {
            // Solicitar permissão na primeira vez
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                this.notificacoesPermitidas = true;
            } else {
                return; // Usuário negou permissão
            }
        }
        
        if (Notification.permission === 'granted') {
            const options = {
                body: mensagem.mensagem || 'Nova mensagem',
                icon: fotoContato || '/static/img/default-avatar.png',
                badge: '/static/img/default-avatar.png',
                tag: `chat-${mensagem.chat}`, // Evitar notificações duplicadas do mesmo chat
                requireInteraction: false,
                silent: false
            };
            
            try {
                const notification = new Notification(`${nomeContato || 'Nova mensagem'}`, options);
                
                // Fechar notificação após 5 segundos
                setTimeout(() => {
                    notification.close();
                }, 5000);
                
                // Quando clicar na notificação, abrir o chat
                notification.onclick = () => {
                    window.focus();
                    this.togglePanel();
                    if (mensagem.chat) {
                        setTimeout(() => {
                            this.abrirChat(mensagem.chat);
                        }, 300);
                    }
                    notification.close();
                };
            } catch (error) {
                console.error('Erro ao mostrar notificação:', error);
            }
        }
        */
    }
    
    buscarConversas(termo) {
        const itens = document.querySelectorAll('#chat-conversas-list .chat-item-ios');
        itens.forEach(item => {
            const texto = item.textContent.toLowerCase();
            if (texto.includes(termo.toLowerCase())) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    togglePanel() {
        if (this.isOpen) {
            this.closePanel();
        } else {
            this.openPanel();
        }
    }

    openPanel() {
        if (this.panel) { this.panel.classList.add('open'); }
        const overlay = document.getElementById('chat-overlay');
        if (overlay) { overlay.classList.add('active'); }
        this.isOpen = true;
        this.registrarAtividade();
        this.carregarConversas();
        // Iniciar polling apenas quando o chat for aberto
        this.iniciarPolling();
        
        // Iniciar polling de notificações quando o chat for aberto
        if (!this.pollTimerNotificacoes) {
            this.iniciarPollingNotificacoes();
        }
        
        // Iniciar polling da lista de chats se existir
        if (window.chatLista && !window.chatLista.pollTimer) {
            window.chatLista.iniciarPolling();
        }
    }

    closePanel() {
        if (this.panel) { this.panel.classList.remove('open'); }
        const overlay = document.getElementById('chat-overlay');
        if (overlay) { overlay.classList.remove('active'); }
        this.isOpen = false;
        this.pararPolling();
        
        // Parar polling de notificações quando fechar (será reiniciado se houver atividade)
        this.pararPollingNotificacoes();
        
        // Parar polling da lista de chats também
        if (window.chatLista && window.chatLista.pollTimer) {
            clearInterval(window.chatLista.pollTimer);
            window.chatLista.pollTimer = null;
        }
        
        // Fazer uma última verificação ao fechar
        this.carregarConversas();
    }

    minimizePanel() {
        if (this.panel) { this.panel.classList.add('minimized'); }
        const indicator = document.getElementById('chat-minimized-indicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
        // Atualizar badge ao minimizar
        this.carregarConversas();
        // Parar polling quando minimizado (chat não está visível)
        this.pararPolling();
        // Parar polling de notificações quando minimizado
        this.pararPollingNotificacoes();
        if (window.chatLista && window.chatLista.pollTimer) {
            clearInterval(window.chatLista.pollTimer);
            window.chatLista.pollTimer = null;
        }
    }
    
    restorePanel() {
        if (this.panel) { this.panel.classList.remove('minimized'); }
        const indicator = document.getElementById('chat-minimized-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
        // Retomar polling quando restaurar
        if (this.isOpen) {
            this.registrarAtividade();
            this.iniciarPolling();
            // Reiniciar polling de notificações quando restaurar
            if (!this.pollTimerNotificacoes) {
                this.iniciarPollingNotificacoes();
            }
            if (window.chatLista && !window.chatLista.pollTimer) {
                window.chatLista.iniciarPolling();
            }
        }
    }

    showConversas() {
        var vConversas = document.getElementById('chat-conversas-view'); if (vConversas) { vConversas.classList.add('active'); }
        var vMensagens = document.getElementById('chat-mensagens-view'); if (vMensagens) { vMensagens.classList.remove('active'); }
        var vNova = document.getElementById('chat-nova-conversa-view'); if (vNova) { vNova.classList.remove('active'); }
        this.currentChatId = null;
        this.pararPolling();
        
        // Esconder botões de chamada
        const acoesContato = document.getElementById('chat-acoes-contato');
        if (acoesContato) {
            acoesContato.style.display = 'none';
        }
    }
    
    showNovaConversa() {
        var vConversas = document.getElementById('chat-conversas-view'); if (vConversas) { vConversas.classList.remove('active'); }
        var vMensagens = document.getElementById('chat-mensagens-view'); if (vMensagens) { vMensagens.classList.remove('active'); }
        var vNova = document.getElementById('chat-nova-conversa-view'); if (vNova) { vNova.classList.add('active'); }
        this.carregarUsuarios();
    }
    
    async carregarUsuarios() {
        try {
            const response = await fetch('/militares/api/chat/usuarios/', {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            if (!response.ok) return;
            
            const data = await response.json();
            if (data.success) {
                this.renderizarUsuarios(data.usuarios);
            }
        } catch (error) {
            console.error('Erro ao carregar usuários:', error);
        }
    }
    
    renderizarUsuarios(usuarios) {
        const container = document.getElementById('chat-usuarios-list');
        if (!container) return;

        if (usuarios.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px 20px; color: #8E8E93;">
                    <i class="fas fa-users" style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;"></i>
                    <p>Nenhum usuário disponível</p>
                </div>
            `;
            return;
        }

        container.innerHTML = usuarios.map(usuario => {
            const inicial = usuario.nome.charAt(0).toUpperCase();
            const foto = usuario.foto || null;
            return `
            <div class="chat-item-ios" data-usuario-id="${usuario.id}">
                <div class="chat-avatar-item">
                    ${foto ? `<img src="${foto}" alt="${usuario.nome}">` : `<span>${inicial}</span>`}
                    <span class="chat-status-item ${usuario.online ? '' : 'offline'}"></span>
                </div>
                <div class="chat-info-item">
                    <div class="chat-nome-item">${this.escapeHtml(usuario.nome)}</div>
                    <div class="chat-preview-item">${this.escapeHtml(usuario.email || '')}</div>
                </div>
                ${usuario.ja_tem_chat ? `
                <div class="chat-meta-item">
                    <i class="fas fa-comments text-primary"></i>
                </div>
                ` : ''}
            </div>
        `;
        }).join('');

        // Event listeners
        container.querySelectorAll('.chat-item-ios').forEach(item => {
            item.addEventListener('click', () => {
                const usuarioId = item.getAttribute('data-usuario-id');
                this.iniciarConversa(usuarioId);
            });
        });
    }
    
    async iniciarConversa(usuarioId) {
        try {
            // Primeiro, verificar se já existe chat
            try {
                const chatsResponse = await fetch('/militares/api/chat/chats/');
                if (chatsResponse.ok) {
                    const chatsData = await chatsResponse.json();
                    if (chatsData.success) {
                        const chatExistente = chatsData.chats.find(c => c.outro_participante_id == usuarioId);
                        if (chatExistente) {
                            this.abrirChat(chatExistente.id, usuarioId);
                            return;
                        }
                    }
                }
            } catch (error) {
                // Se falhar ao buscar chats, continuar para criar novo
                if (!error.message || !error.message.includes('Failed to fetch')) {
                    console.error('Erro ao verificar chats existentes:', error);
                }
            }
            
            // Se não existe, criar novo chat
            try {
                const response = await fetch(`/militares/chat/iniciar/${usuarioId}/`, {
                    method: 'GET',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                
                if (response.ok || response.redirected) {
                    // Recarregar conversas e encontrar o chat criado
                    await this.carregarConversas();
                    try {
                        const chatsResponse2 = await fetch('/militares/api/chat/chats/');
                        if (chatsResponse2.ok) {
                            const chatsData2 = await chatsResponse2.json();
                            if (chatsData2.success) {
                                const chat = chatsData2.chats.find(c => c.outro_participante_id == usuarioId);
                                if (chat) {
                                    this.abrirChat(chat.id, usuarioId);
                                }
                            }
                        }
                    } catch (error) {
                        // Erro ao buscar chat criado - não crítico
                        if (!error.message || !error.message.includes('Failed to fetch')) {
                            console.error('Erro ao buscar chat criado:', error);
                        }
                    }
                }
            } catch (error) {
                if (!error.message || !error.message.includes('Failed to fetch')) {
                    console.error('Erro ao iniciar conversa:', error);
                }
            }
        } catch (error) {
            // Erro geral - apenas logar se não for erro de conexão
            if (!error.message || !error.message.includes('Failed to fetch')) {
                console.error('Erro ao iniciar conversa:', error);
            }
        }
    }
    
    buscarUsuarios(termo) {
        // Implementar busca de usuários
        const itens = document.querySelectorAll('#chat-usuarios-list .chat-item-ios');
        itens.forEach(item => {
            const texto = item.textContent.toLowerCase();
            if (texto.includes(termo.toLowerCase())) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    async carregarConversas() {
        try {
            const response = await fetch('/militares/api/chat/chats/', {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            if (!response.ok) {
                // Se não for OK, não renderizar nada
                return;
            }
            
            const data = await response.json();
            if (data.success) {
                // Detectar novas mensagens comparando com o estado anterior
                const totalAnterior = this.ultimaTotalNaoLidas || 0;
                const totalAtual = data.total_nao_lidas || 0;
                
                // Se há novas mensagens não lidas e o chat está fechado
                if (totalAtual > totalAnterior && !this.isOpen) {
                    // Registrar atividade quando detectar novas mensagens
                    this.registrarAtividade();
                    
                    // Encontrar chats com novas mensagens
                    const chatsComNovasMensagens = data.chats.filter(chat => chat.nao_lidas > 0);
                    
                    // Mostrar notificação para cada chat com novas mensagens
                    for (const chat of chatsComNovasMensagens) {
                        // Verificar se a mensagem é nova (comparar com cache anterior)
                        const chatAnterior = (this.chatsCache && this.chatsCache.chats) ? this.chatsCache.chats.find(c => c.id === chat.id) : null;
                        const mensagemNova = !chatAnterior || 
                                           chat.ultima_mensagem_id !== chatAnterior.ultima_mensagem_id;
                        
                        // Só mostrar notificação se:
                        // 1. A mensagem é nova (ID diferente)
                        // 2. Há mensagens não lidas (nao_lidas > 0)
                        // 3. O chat anterior tinha menos mensagens não lidas (ou não existia)
                        const tinhaMensagensAnterior = chatAnterior && chatAnterior.nao_lidas ? chatAnterior.nao_lidas : 0;
                        const temMensagensAgora = chat.nao_lidas || 0;
                        const aumentouMensagens = temMensagensAgora > tinhaMensagensAnterior;
                        
                        if (mensagemNova && chat.ultima_mensagem_id && aumentouMensagens) {
                            // Criar objeto de mensagem simulado para a notificação
                            const mensagem = {
                                id: chat.ultima_mensagem_id,
                                chat: chat.id,
                                mensagem: chat.ultima_mensagem || 'Nova mensagem',
                                remetente_id: chat.ultima_mensagem_remetente_id
                            };
                            
                            await this.mostrarNotificacaoMensagem(
                                mensagem,
                                chat.outro_participante,
                                chat.outro_foto
                            );
                        }
                    }
                }
                
                this.chatsCache = data; // Armazenar cache para uso posterior
                this.renderizarConversas(data.chats);
                this.atualizarBadge(data.total_nao_lidas);
                this.ultimaTotalNaoLidas = totalAtual; // Atualizar estado anterior
            }
        } catch (error) {
            // Erro de conexão - não logar se for apenas conexão recusada
            // (servidor pode não estar rodando o chat ou endpoint não disponível)
            if (error.message && !error.message.includes('Failed to fetch')) {
                console.error('Erro ao carregar conversas:', error);
            }
            // Não renderizar nada em caso de erro
        }
    }

    renderizarConversas(chats) {
        const container = document.getElementById('chat-conversas-list');
        if (!container) return;

        if (chats.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px 20px; color: #8E8E93;">
                    <i class="fas fa-comments" style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;"></i>
                    <p>Nenhuma conversa ainda</p>
                </div>
            `;
            return;
        }

        container.innerHTML = chats.map(chat => {
            const inicial = chat.outro_participante.charAt(0).toUpperCase();
            const foto = chat.outro_foto || null;
            return `
            <div class="chat-item-ios" data-chat-id="${chat.id}" data-outro-id="${chat.outro_participante_id}">
                <div class="chat-avatar-item">
                    ${foto ? `<img src="${foto}" alt="${chat.outro_participante}">` : `<span>${inicial}</span>`}
                    <span class="chat-status-item ${chat.outro_online ? '' : 'offline'}"></span>
                </div>
                <div class="chat-info-item">
                    <div class="chat-nome-item">${this.escapeHtml(chat.outro_participante)}</div>
                    <div class="chat-preview-item">${this.escapeHtml(chat.ultima_mensagem || 'Nenhuma mensagem')}</div>
                </div>
                <div class="chat-meta-item">
                    <div class="chat-time-item">${chat.ultima_atualizacao}</div>
                    ${chat.nao_lidas > 0 ? `<span class="chat-badge-item">${chat.nao_lidas}</span>` : ''}
                </div>
                <button class="btn-delete-chat" data-chat-id="${chat.id}" title="Excluir conversa" onclick="event.stopPropagation();">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `;
        }).join('');

        // Event listeners para itens
        container.querySelectorAll('.chat-item-ios').forEach(item => {
            item.addEventListener('click', () => {
                const chatId = item.getAttribute('data-chat-id');
                const outroId = item.getAttribute('data-outro-id');
                this.abrirChat(chatId, outroId);
            });
        });

        // Event listeners para botões de excluir
        container.querySelectorAll('.btn-delete-chat').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const chatId = btn.getAttribute('data-chat-id');
                this.excluirConversa(chatId);
            });
        });
    }

    async abrirChat(chatId, outroId) {
        this.currentChatId = chatId;
        
        // Mostrar view de mensagens
        var vConversas = document.getElementById('chat-conversas-view'); if (vConversas) { vConversas.classList.remove('active'); }
        var vMensagens = document.getElementById('chat-mensagens-view'); if (vMensagens) { vMensagens.classList.add('active'); }
        
        // Adicionar atributo para facilitar acesso ao outro participante
        const header = document.querySelector('.chat-header-conversa');
        if (header && outroId) {
            header.setAttribute('data-outro-participante-id', outroId);
        }
        
        // Carregar mensagens
        await this.carregarMensagens(chatId);
        
        // Iniciar polling
        this.iniciarPolling();
        
        // Sistema de chamadas desabilitado
        // if (this.chatCalls) {
        //     console.log('🔄 Reiniciando polling de chamadas pendentes ao abrir chat:', chatId);
        //     this.chatCalls.iniciarPollingChamadasPendentes();
        // }
        
        // Garantir que botões de chamada sejam removidos
        this.removerBotoesChamada();
        
        // Atualizar header
        this.atualizarHeaderChat(outroId);
    }

    async carregarMensagens(chatId) {
        try {
            const response = await fetch(`/militares/api/chat/${chatId}/mensagens/`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            if (!response.ok) return;
            
            const data = await response.json();
            if (data.success) {
                // Limpar container antes de renderizar
                const container = document.getElementById('chat-mensagens-container');
                if (container) {
                    container.innerHTML = '';
                }
                
                // Renderizar todas as mensagens
                this.renderizarMensagens(data.mensagens);
                
                // Definir última mensagem ID
                if (data.mensagens.length > 0) {
                    this.ultimaMensagemId = data.mensagens[data.mensagens.length - 1].id;
                } else {
                    this.ultimaMensagemId = null;
                }
                
                // Scroll para o final após um pequeno delay para garantir que o DOM foi atualizado
                setTimeout(() => {
                    this.scrollParaFinal();
                }, 100);
            }
        } catch (error) {
            console.error('Erro ao carregar mensagens:', error);
        }
    }

    renderizarMensagens(mensagens) {
        const container = document.getElementById('chat-mensagens-container');
        if (!container) return;

        // Se não houver mensagens, mostrar mensagem vazia
        if (mensagens.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px 20px; color: #8E8E93;">
                    <i class="fas fa-comments" style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;"></i>
                    <p>Nenhuma mensagem ainda</p>
                </div>
            `;
            return;
        }

        // Renderizar todas as mensagens (já vêm ordenadas do mais antigo ao mais recente)
        let ultimaData = null;
        mensagens.forEach((msg, index) => {
            const msgDate = this.parsearData(msg.data_envio);
            if (isNaN(msgDate.getTime())) return; // Pula se não conseguir parsear
            
            const msgData = new Date(msgDate.getFullYear(), msgDate.getMonth(), msgDate.getDate());
            
            // Verificar se precisa adicionar separador de data
            if (!ultimaData || msgData.getTime() !== ultimaData.getTime()) {
                const separadorDiv = document.createElement('div');
                separadorDiv.className = 'chat-data-separador';
                separadorDiv.textContent = this.formatarDataSeparador(msg.data_envio);
                container.appendChild(separadorDiv);
                ultimaData = msgData;
            }
            
            const isSent = msg.remetente_id === this.obterUsuarioId();
            const hora = this.formatarDataHora(msg.data_envio);
            const iconeLeitura = isSent ? (msg.lida ? '<i class="fas fa-check-double" style="font-size: 10px; margin-left: 2px; color: #53BDEB;"></i>' : '<i class="fas fa-check" style="font-size: 10px; margin-left: 2px; color: #667781; opacity: 0.7;"></i>') : '';
            
            // Obter foto do remetente (pode ser do outro ou do usuário logado)
            let remetenteFoto = msg.remetente_foto || null;
            if (!remetenteFoto && !isSent) {
                // Se não tem foto na mensagem e é mensagem recebida, tentar obter do header
                remetenteFoto = this.obterFotoOutroParticipante();
            }
            
            // Obter foto do usuário logado
            let usuarioFoto = this.obterFotoUsuario();
            if (!usuarioFoto && isSent) {
                // Se não tem foto do usuário, tentar obter da primeira mensagem enviada
                const primeiraMsgEnviada = mensagens.find(m => m.remetente_id === this.obterUsuarioId() && m.remetente_foto);
                if (primeiraMsgEnviada) {
                    usuarioFoto = primeiraMsgEnviada.remetente_foto;
                }
            }
            
            const inicialRemetente = (msg.remetente || '?').charAt(0).toUpperCase();
            const inicialUsuario = this.obterInicialUsuario();
            
            const msgDiv = document.createElement('div');
            msgDiv.className = `chat-mensagem-ios ${isSent ? 'sent' : 'received'}`;
            msgDiv.setAttribute('data-msg-id', msg.id);
            msgDiv.setAttribute('data-msg-date', msg.data_envio);
            
            // Verificar se é mensagem de áudio
            const isAudio = msg.audio && msg.audio.trim() !== '';
            const conteudoMensagem = isAudio ? this.renderizarAudioMessage(msg) : `<div style="margin-bottom: 2px;">${this.escapeHtml(msg.texto).replace(/\n/g, '<br>')}</div>`;
            
            msgDiv.innerHTML = `
                ${!isSent ? `
                <div class="chat-avatar-msg">
                    ${remetenteFoto ? `<img src="${remetenteFoto}" alt="${msg.remetente}">` : `<span>${inicialRemetente}</span>`}
                </div>
                ` : ''}
                <div class="chat-bubble-ios ${isSent ? 'sent' : 'received'}" style="position: relative;">
                    ${conteudoMensagem}
                    <div class="chat-time-bubble">${hora}${iconeLeitura}</div>
                    ${isSent ? `
                    <button type="button" class="btn-delete-mensagem" data-mensagem-id="${msg.id}" title="Apagar mensagem">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                    ` : ''}
                </div>
                ${isSent ? `
                <div class="chat-avatar-msg">
                    ${usuarioFoto ? `<img src="${usuarioFoto}" alt="Você">` : `<span>${inicialUsuario}</span>`}
                </div>
                ` : ''}
            `;
            container.appendChild(msgDiv);
            
            // Adicionar evento de clique no botão de apagar (apenas para mensagens enviadas)
            if (isSent) {
                const btnDelete = msgDiv.querySelector('.btn-delete-mensagem');
                if (btnDelete) {
                    btnDelete.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this.apagarMensagem(msg.id);
                    });
                }
            }
            
            // Inicializar player de áudio se for mensagem de áudio
            if (isAudio) {
                this.inicializarAudioPlayer(msgDiv, msg);
            }
        });
    }

    async enviarMensagem(e) {
        e.preventDefault();
        
        if (!this.currentChatId) return;
        
        const input = document.getElementById('chat-input-mensagem');
        const texto = input.value.trim();
        if (!texto) return;

        input.value = '';
        this.fecharEmojiPicker();

        try {
            const formData = new FormData();
            formData.append('mensagem', texto);
            formData.append('csrfmiddlewaretoken', this.obterCSRFToken());

            const response = await fetch(`/militares/chat/${this.currentChatId}/enviar/`, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (!response.ok) throw new Error('Erro ao enviar');

            const data = await response.json();
            if (data.success) {
                this.adicionarMensagem(data.mensagem);
                this.ultimaMensagemId = data.mensagem.id;
                this.registrarAtividade(); // Registrar atividade ao enviar mensagem
            }
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            alert('Erro ao enviar mensagem');
        }
    }

    renderizarAudioMessage(msg) {
        const duracao = msg.duracao_audio || 0;
        const minutos = Math.floor(duracao / 60);
        const segundos = duracao % 60;
        const duracaoFormatada = `${String(minutos).padStart(2, '0')}:${String(segundos).padStart(2, '0')}`;
        
        return `
            <div class="chat-audio-message">
                <div class="chat-audio-player">
                    <button class="chat-audio-play-btn" data-audio-url="${msg.audio}" data-msg-id="${msg.id}">
                        <i class="fas fa-play"></i>
                    </button>
                    <div class="chat-audio-waveform" id="audio-waveform-${msg.id}">
                        ${this.gerarWaveformBars()}
                    </div>
                    <span class="chat-audio-duration">${duracaoFormatada}</span>
                </div>
            </div>
        `;
    }
    
    gerarWaveformBars() {
        let bars = '';
        for (let i = 0; i < 20; i++) {
            const height = Math.random() * 30 + 4;
            bars += `<div class="chat-audio-waveform-bar" style="height: ${height}px;"></div>`;
        }
        return bars;
    }
    
    inicializarAudioPlayer(msgDiv, msg) {
        const playBtn = msgDiv.querySelector('.chat-audio-play-btn');
        if (!playBtn || !msg.audio) return;
        
        let audio = null;
        let isPlaying = false;
        
        playBtn.addEventListener('click', () => {
            if (!audio) {
                audio = new Audio(msg.audio);
                audio.addEventListener('ended', () => {
                    isPlaying = false;
                    playBtn.innerHTML = '<i class="fas fa-play"></i>';
                    playBtn.classList.remove('playing');
                });
            }
            
            if (isPlaying) {
                audio.pause();
                audio.currentTime = 0;
                isPlaying = false;
                playBtn.innerHTML = '<i class="fas fa-play"></i>';
                playBtn.classList.remove('playing');
            } else {
                audio.play();
                isPlaying = true;
                playBtn.innerHTML = '<i class="fas fa-pause"></i>';
                playBtn.classList.add('playing');
            }
        });
    }

    adicionarMensagem(mensagem) {
        const container = document.getElementById('chat-mensagens-container');
        if (!container) return;

        const msgDate = this.parsearData(mensagem.data_envio);
        if (isNaN(msgDate.getTime())) return;
        
        const msgData = new Date(msgDate.getFullYear(), msgDate.getMonth(), msgDate.getDate());
        
        // Verificar se precisa adicionar separador de data
        const ultimaMsg = container.querySelector('.chat-mensagem-ios:last-child');
        let precisaSeparador = false;
        
        if (ultimaMsg) {
            const ultimaDataAttr = ultimaMsg.getAttribute('data-msg-date');
            if (ultimaDataAttr) {
                const ultimaData = this.parsearData(ultimaDataAttr);
                if (!isNaN(ultimaData.getTime())) {
                    const ultimaDataDate = new Date(ultimaData.getFullYear(), ultimaData.getMonth(), ultimaData.getDate());
                    precisaSeparador = msgData.getTime() !== ultimaDataDate.getTime();
                } else {
                    precisaSeparador = true;
                }
            } else {
                precisaSeparador = true;
            }
        } else {
            // Primeira mensagem, adicionar separador
            precisaSeparador = true;
        }
        
        if (precisaSeparador) {
            const separadorDiv = document.createElement('div');
            separadorDiv.className = 'chat-data-separador';
            separadorDiv.textContent = this.formatarDataSeparador(mensagem.data_envio);
            container.appendChild(separadorDiv);
        }

        const isSent = mensagem.remetente_id === this.obterUsuarioId();
        const hora = this.formatarDataHora(mensagem.data_envio);
        const iconeLeitura = isSent ? (mensagem.lida ? '<i class="fas fa-check-double" style="font-size: 10px; margin-left: 2px; color: #53BDEB;"></i>' : '<i class="fas fa-check" style="font-size: 10px; margin-left: 2px; color: #667781; opacity: 0.7;"></i>') : '';
        
        // Obter foto do remetente (pode ser do outro ou do usuário logado)
        let remetenteFoto = mensagem.remetente_foto || null;
        if (!remetenteFoto && !isSent) {
            // Se não tem foto na mensagem e é mensagem recebida, tentar obter do header
            remetenteFoto = this.obterFotoOutroParticipante();
        }
        
        // Obter foto do usuário logado
        let usuarioFoto = this.obterFotoUsuario();
        if (!usuarioFoto && isSent) {
            // Se não tem foto do usuário, usar a foto que vem na mensagem
            usuarioFoto = mensagem.remetente_foto || null;
        }
        
        const inicialRemetente = (mensagem.remetente || '?').charAt(0).toUpperCase();
        const inicialUsuario = this.obterInicialUsuario();

        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-mensagem-ios ${isSent ? 'sent' : 'received'}`;
        msgDiv.setAttribute('data-msg-id', mensagem.id);
        msgDiv.setAttribute('data-msg-date', mensagem.data_envio);
        
        // Verificar se é mensagem de áudio
        const isAudio = mensagem.audio && mensagem.audio.trim() !== '';
        const conteudoMensagem = isAudio ? this.renderizarAudioMessage(mensagem) : `<div style="margin-bottom: 2px;">${this.escapeHtml(mensagem.texto || '').replace(/\n/g, '<br>')}</div>`;
        
        msgDiv.innerHTML = `
            ${!isSent ? `
            <div class="chat-avatar-msg">
                ${remetenteFoto ? `<img src="${remetenteFoto}" alt="${mensagem.remetente}">` : `<span>${inicialRemetente}</span>`}
            </div>
            ` : ''}
            <div class="chat-bubble-ios ${isSent ? 'sent' : 'received'}" style="position: relative;">
                ${conteudoMensagem}
                <div class="chat-time-bubble">${hora}${iconeLeitura}</div>
                ${isSent ? `
                <button type="button" class="btn-delete-mensagem" data-mensagem-id="${mensagem.id}" title="Apagar mensagem">
                    <i class="fas fa-trash-alt"></i>
                </button>
                ` : ''}
            </div>
            ${isSent ? `
            <div class="chat-avatar-msg">
                ${usuarioFoto ? `<img src="${usuarioFoto}" alt="Você">` : `<span>${inicialUsuario}</span>`}
            </div>
            ` : ''}
        `;
        
        // Adicionar evento de clique no botão de apagar (apenas para mensagens enviadas)
        if (isSent) {
            const btnDelete = msgDiv.querySelector('.btn-delete-mensagem');
            if (btnDelete) {
                btnDelete.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.apagarMensagem(mensagem.id);
                });
            }
        }

        container.appendChild(msgDiv);
        
        // Inicializar player de áudio se for mensagem de áudio
        if (isAudio) {
            this.inicializarAudioPlayer(msgDiv, mensagem);
        }
        
        this.scrollParaFinal();
    }
    
    obterFotoUsuario() {
        // Tentar obter da primeira mensagem enviada já renderizada
        const usuarioAvatar = document.querySelector('.chat-mensagem-ios.sent .chat-avatar-msg img');
        if (usuarioAvatar) {
            return usuarioAvatar.src;
        }
        
        // Tentar obter do header do chat
        const headerAvatar = document.querySelector('#chat-avatar-contato img');
        if (headerAvatar) {
            // Se o avatar do header é do outro participante, não usar
            return null;
        }
        
        return null;
    }
    
    obterFotoOutroParticipante() {
        // Tentar obter do header do chat
        const avatarElement = document.getElementById('chat-avatar-contato');
        if (avatarElement) {
            const img = avatarElement.querySelector('img');
            if (img && img.src) {
                return img.src;
            }
        }
        
        // Tentar obter da primeira mensagem recebida já renderizada
        const outroAvatar = document.querySelector('.chat-mensagem-ios.received .chat-avatar-msg img');
        if (outroAvatar) {
            return outroAvatar.src;
        }
        
        return null;
    }

    iniciarPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
        }
        
        this.pollTimer = setInterval(async () => {
            if (this.currentChatId) {
                await this.buscarNovasMensagens();
                await this.verificarStatusLeitura();
                
                // Atualizar status online do contato atual
                const outroId = this.obterOutroParticipanteId();
                if (outroId) {
                    await this.atualizarStatusOnlineContato(outroId);
                }
            }
            this.carregarConversas();
        }, this.pollInterval);
    }
    
    async atualizarStatusOnlineContato(outroId) {
        try {
            const response = await fetch(`/militares/api/chat/status-online/${outroId}/`);
            if (response.ok) {
                const data = await response.json();
                const statusElement = document.getElementById('chat-status-contato');
                if (statusElement) {
                    statusElement.textContent = data.online ? 'Online' : 'Offline';
                }
            }
        } catch (error) {
            // Silenciar erro
        }
    }
    
    obterOutroParticipanteId() {
        // Tentar obter do atributo data-outro-participante-id se existir
        const header = document.querySelector('.chat-header-conversa');
        if (header) {
            const outroId = header.getAttribute('data-outro-participante-id');
            if (outroId) return parseInt(outroId);
        }
        
        // Tentar obter da lista de chats
        if (this.chatsCache && this.chatsCache.success) {
            const chat = this.chatsCache.chats.find(c => c.id == this.currentChatId);
            if (chat) {
                return chat.outro_participante_id;
            }
        }
        
        return null;
    }

    pararPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }

    async buscarNovasMensagens() {
        if (!this.currentChatId || !this.ultimaMensagemId) return;

        try {
            // Buscar todas as mensagens para verificar se alguma foi deletada
            const response = await fetch(`/militares/api/chat/${this.currentChatId}/mensagens/`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (!response.ok) return;

            const data = await response.json();
            if (data.success && data.mensagens) {
                const container = document.getElementById('chat-mensagens-container');
                if (!container) return;
                
                // Obter IDs de todas as mensagens que existem no servidor
                const idsServidor = new Set(data.mensagens.map(msg => msg.id));
                
                // Remover mensagens que não existem mais no servidor (foram apagadas)
                const mensagensNaTela = container.querySelectorAll('[data-msg-id]');
                mensagensNaTela.forEach(msgElement => {
                    const msgId = parseInt(msgElement.getAttribute('data-msg-id'));
                    if (!idsServidor.has(msgId)) {
                        // Mensagem foi deletada, remover da tela
                        msgElement.style.transition = 'opacity 0.3s ease';
                        msgElement.style.opacity = '0';
                        setTimeout(() => {
                            msgElement.remove();
                        }, 300);
                    }
                });
                
                // Adicionar novas mensagens (apenas as que não estão na tela)
                let novaMensagemRecebida = false;
                data.mensagens.forEach(msg => {
                    const existeNaTela = container.querySelector(`[data-msg-id="${msg.id}"]`);
                    if (!existeNaTela) {
                        this.adicionarMensagem(msg);
                        // Verificar se é mensagem recebida (não enviada pelo usuário atual)
                        const isSent = msg.remetente_id === this.obterUsuarioId();
                        if (!isSent) {
                            novaMensagemRecebida = true;
                        }
                    }
                    // Atualizar última mensagem ID
                    if (msg.id > (this.ultimaMensagemId || 0)) {
                        this.ultimaMensagemId = msg.id;
                    }
                });
                
                // Registrar atividade se recebeu nova mensagem
                if (novaMensagemRecebida) {
                    this.registrarAtividade();
                }
            }
        } catch (error) {
            console.error('Erro ao buscar mensagens:', error);
        }
    }

    async verificarStatusLeitura() {
        if (!this.currentChatId) return;

        try {
            const response = await fetch(`/militares/api/chat/${this.currentChatId}/status-leitura/`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (!response.ok) return;

            const data = await response.json();
            if (data.success && data.mensagens_lidas) {
                // Atualizar ícones de leitura para mensagens enviadas
                data.mensagens_lidas.forEach(msgId => {
                    const msgElement = document.querySelector(`[data-msg-id="${msgId}"]`);
                    if (msgElement) {
                        const timeBubble = msgElement.querySelector('.chat-time-bubble');
                        if (timeBubble) {
                            // Verificar se já tem check-double, se não, atualizar
                            if (!timeBubble.innerHTML.includes('fa-check-double')) {
                                // Extrair o texto da hora (remover HTML de ícones)
                                let horaTexto = timeBubble.textContent.trim();
                                // Se tiver ícone de check simples, remover
                                if (timeBubble.innerHTML.includes('fa-check')) {
                                    horaTexto = horaTexto.replace(/[✓]/g, '').trim();
                                }
                                // Atualizar com check-double azul
                                timeBubble.innerHTML = `${horaTexto}<i class="fas fa-check-double" style="font-size: 10px; margin-left: 2px; color: #53BDEB;"></i>`;
                            }
                        }
                    }
                });
            }
        } catch (error) {
            // Silenciar erro
        }
    }

    async atualizarHeaderChat(outroId) {
        // Buscar informações do outro participante
        try {
            try {
                const response = await fetch(`/militares/api/chat/status-online/${outroId}/`);
                if (response.ok) {
                    const data = await response.json();
                    const statusElement = document.getElementById('chat-status-contato');
                    if (statusElement) {
                        statusElement.textContent = data.online ? 'Online' : 'Offline';
                    }
                }
            } catch (error) {
                // Erro ao buscar status online - não crítico
                if (!error.message || !error.message.includes('Failed to fetch')) {
                    console.error('Erro ao buscar status online:', error);
                }
            }
            
            // Buscar nome e foto do participante
            try {
                const chatsResponse = await fetch('/militares/api/chat/chats/');
                if (chatsResponse.ok) {
                    const chatsData = await chatsResponse.json();
                    if (chatsData.success) {
                        const chat = chatsData.chats.find(c => c.outro_participante_id == outroId);
                        if (chat) {
                            const nomeElement = document.getElementById('chat-nome-contato');
                            const avatarElement = document.getElementById('chat-avatar-contato');
                            const inicialElement = document.getElementById('chat-inicial-contato');
                            const acoesContato = document.getElementById('chat-acoes-contato');
                            
                            if (nomeElement) nomeElement.textContent = chat.outro_participante;
                            if (chat.outro_foto && avatarElement) {
                                avatarElement.innerHTML = `<img src="${chat.outro_foto}" alt="${chat.outro_participante}" style="width: 100%; height: 100%; border-radius: 20px; object-fit: cover;">`;
                            } else if (inicialElement) {
                                inicialElement.textContent = chat.outro_participante.charAt(0).toUpperCase();
                            }
                            
                            // Botões de chamada removidos
                            // if (acoesContato) {
                            //     acoesContato.style.display = 'flex';
                            // }
                            if (acoesContato) {
                                acoesContato.style.display = 'none';
                            }
                        }
                    }
                }
            } catch (error) {
                // Erro ao buscar informações do chat - não crítico
                if (!error.message || !error.message.includes('Failed to fetch')) {
                    console.error('Erro ao buscar informações do chat:', error);
                }
            }
        } catch (error) {
            // Erro geral - silenciar se for apenas conexão recusada
            if (!error.message || !error.message.includes('Failed to fetch')) {
                console.error('Erro ao atualizar header do chat:', error);
            }
        }
    }

    scrollParaFinal() {
        const area = document.getElementById('chat-mensagens-area');
        if (area) {
            // Usar múltiplas tentativas para garantir que o scroll funcione
            const scroll = () => {
                area.scrollTop = area.scrollHeight;
            };
            
            // Tentar imediatamente
            scroll();
            
            // Tentar após um frame
            requestAnimationFrame(scroll);
            
            // Tentar após um pequeno delay (para garantir que todas as mensagens foram renderizadas)
            setTimeout(scroll, 50);
            setTimeout(scroll, 150);
        }
    }

    atualizarBadge(count) {
        // Badge do botão flutuante
        const badge = document.getElementById('chat-badge-notificacao');
        if (badge) {
            const countAnterior = parseInt(badge.textContent) || 0;
            const temNovaMensagem = count > countAnterior && countAnterior >= 0;
            
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'flex';
                
                // Adicionar animação pulsante quando houver nova mensagem
                if (temNovaMensagem) {
                    badge.classList.add('new-message');
                    // Manter a animação pulsante enquanto houver mensagens não lidas
                } else if (count > 0 && !badge.classList.contains('new-message')) {
                    // Se já havia mensagens mas não estava pulsando, adicionar animação
                    badge.classList.add('new-message');
                }
            } else {
                badge.style.display = 'none';
                badge.classList.remove('new-message');
            }
        }
        
        // Badge do header
        const badgeHeader = document.getElementById('chat-badge-header');
        if (badgeHeader) {
            if (count > 0) {
                badgeHeader.textContent = count;
                badgeHeader.style.display = 'inline-block';
            } else {
                badgeHeader.style.display = 'none';
            }
        }
        
        // Badge quando minimizado
        const badgeMinimized = document.getElementById('chat-badge-minimized');
        const indicator = document.getElementById('chat-minimized-indicator');
        if (badgeMinimized && indicator) {
            if (count > 0) {
                badgeMinimized.textContent = count;
                badgeMinimized.style.display = 'inline-block';
                indicator.classList.add('has-unread');
            } else {
                badgeMinimized.style.display = 'none';
                indicator.classList.remove('has-unread');
            }
        }
    }

    parsearData(dataHora) {
        // Tenta parsear a data que vem do backend (formato: "dd/mm/yyyy HH:mm:ss")
        if (typeof dataHora === 'string') {
            // Formato do backend: "15/11/2024 14:30:00"
            const match = dataHora.match(/(\d{2})\/(\d{2})\/(\d{4}) (\d{2}):(\d{2}):(\d{2})/);
            if (match) {
                const [, dia, mes, ano, hora, minuto, segundo] = match;
                return new Date(parseInt(ano), parseInt(mes) - 1, parseInt(dia), parseInt(hora), parseInt(minuto), parseInt(segundo));
            }
            // Tenta parsear como ISO ou formato padrão
            const date = new Date(dataHora);
            if (!isNaN(date.getTime())) {
                return date;
            }
        }
        // Se já for um objeto Date
        if (dataHora instanceof Date) {
            return dataHora;
        }
        // Fallback: retorna data atual
        return new Date();
    }

    formatarHora(dataHora) {
        const date = this.parsearData(dataHora);
        if (isNaN(date.getTime())) return '';
        const horas = String(date.getHours()).padStart(2, '0');
        const minutos = String(date.getMinutes()).padStart(2, '0');
        return `${horas}:${minutos}`;
    }

    formatarDataHora(dataHora) {
        const date = this.parsearData(dataHora);
        if (isNaN(date.getTime())) return '';
        
        const agora = new Date();
        const hoje = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());
        const ontem = new Date(hoje);
        ontem.setDate(ontem.getDate() - 1);
        const dataMsg = new Date(date.getFullYear(), date.getMonth(), date.getDate());
        
        const horas = String(date.getHours()).padStart(2, '0');
        const minutos = String(date.getMinutes()).padStart(2, '0');
        const horaFormatada = `${horas}:${minutos}`;
        
        // Se for hoje, mostra apenas a hora
        if (dataMsg.getTime() === hoje.getTime()) {
            return horaFormatada;
        }
        
        // Se for ontem, mostra "Ontem" + hora
        if (dataMsg.getTime() === ontem.getTime()) {
            return `Ontem ${horaFormatada}`;
        }
        
        // Se for deste ano, mostra dia/mês + hora
        if (date.getFullYear() === agora.getFullYear()) {
            const dia = String(date.getDate()).padStart(2, '0');
            const mes = String(date.getMonth() + 1).padStart(2, '0');
            return `${dia}/${mes} ${horaFormatada}`;
        }
        
        // Se for de outro ano, mostra data completa
        const dia = String(date.getDate()).padStart(2, '0');
        const mes = String(date.getMonth() + 1).padStart(2, '0');
        const ano = date.getFullYear();
        return `${dia}/${mes}/${ano} ${horaFormatada}`;
    }

    formatarDataSeparador(dataHora) {
        const date = this.parsearData(dataHora);
        if (isNaN(date.getTime())) return '';
        
        const agora = new Date();
        const hoje = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());
        const ontem = new Date(hoje);
        ontem.setDate(ontem.getDate() - 1);
        const dataMsg = new Date(date.getFullYear(), date.getMonth(), date.getDate());
        
        // Se for hoje, mostra "Hoje"
        if (dataMsg.getTime() === hoje.getTime()) {
            return 'Hoje';
        }
        
        // Se for ontem, mostra "Ontem"
        if (dataMsg.getTime() === ontem.getTime()) {
            return 'Ontem';
        }
        
        // Se for deste ano, mostra dia/mês
        if (date.getFullYear() === agora.getFullYear()) {
            const dia = String(date.getDate()).padStart(2, '0');
            const meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 
                          'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
            return `${dia} de ${meses[date.getMonth()]}`;
        }
        
        // Se for de outro ano, mostra data completa
        const dia = String(date.getDate()).padStart(2, '0');
        const ano = date.getFullYear();
        const meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 
                      'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
        return `${dia} de ${meses[date.getMonth()]} de ${ano}`;
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
        return parseInt(document.body.getAttribute('data-usuario-id') || '0');
    }

    obterInicialUsuario() {
        // Tentar obter do nome do usuário no navbar ou usar inicial padrão
        var elNomeNavbar = document.querySelector('.navbar-brand .text-white');
        var nomeNavbar = elNomeNavbar && elNomeNavbar.textContent ? elNomeNavbar.textContent.trim() : '';
        var elUsuarioNome = document.querySelector('[data-usuario-nome]');
        var attrUsuarioNome = elUsuarioNome ? elUsuarioNome.getAttribute('data-usuario-nome') : '';
        const usuarioNome = nomeNavbar || attrUsuarioNome || 'U';
        const inicial = usuarioNome.charAt(0).toUpperCase();
        return inicial || 'U';
    }

    inicializarEmojiPicker() {
        const emojis = [
            '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂',
            '🙂', '🙃', '😉', '😊', '😇', '🥰', '😍', '🤩',
            '😘', '😗', '☺️', '😚', '😙', '😋', '😛', '😜',
            '🤪', '😝', '🤑', '🤗', '🤭', '🤫', '🤔', '🤐',
            '🤨', '😐', '😑', '😶', '😏', '😒', '🙄', '😬',
            '🤥', '😌', '😔', '😪', '🤤', '😴', '😷', '🤒',
            '🤕', '🤢', '🤮', '🤧', '🥵', '🥶', '😶‍🌫️', '😵',
            '😵‍💫', '🤯', '🤠', '🥳', '😎', '🤓', '🧐', '😕',
            '😟', '🙁', '☹️', '😮', '😯', '😲', '😳', '🥺',
            '😦', '😧', '😨', '😰', '😥', '😢', '😭', '😱',
            '😖', '😣', '😞', '😓', '😩', '😫', '🥱', '😤',
            '😡', '😠', '🤬', '😈', '👿', '💀', '☠️', '💩',
            '👍', '👎', '👊', '✊', '🤛', '🤜', '🤞', '✌️',
            '🤟', '🤘', '👌', '🤌', '🤏', '👈', '👉', '👆',
            '👇', '☝️', '👋', '🤚', '🖐️', '✋', '🖖', '👏',
            '🙌', '🤲', '🤝', '🙏', '✍️', '💪', '🦾', '🦿',
            '🦵', '🦶', '👂', '🦻', '👃', '👶', '👧', '🧒',
            '👦', '👩', '🧑', '👨', '👩‍🦱', '👨‍🦱', '👩‍🦰', '👨‍🦰',
            '👱‍♀️', '👱', '👱‍♂️', '👩‍🦳', '👨‍🦳', '👩‍🦲', '👨‍🦲', '🧔',
            '👵', '🧓', '👴', '👲', '👳‍♀️', '👳', '👳‍♂️', '🧕',
            '👮‍♀️', '👮', '👮‍♂️', '👷‍♀️', '👷', '👷‍♂️', '💂‍♀️', '💂',
            '💂‍♂️', '🕵️‍♀️', '🕵️', '🕵️‍♂️', '👩‍⚕️', '👨‍⚕️', '👩‍🌾', '👨‍🌾',
            '👩‍🍳', '👨‍🍳', '👩‍🎓', '👨‍🎓', '👩‍🎤', '👨‍🎤', '👩‍🏫', '👨‍🏫',
            '👩‍🏭', '👨‍🏭', '👩‍💻', '👨‍💻', '👩‍💼', '👨‍💼', '👩‍🔧', '👨‍🔧',
            '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍',
            '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖',
            '💘', '💝', '💟', '☮️', '✝️', '☪️', '🕉️', '☸️',
            '✡️', '🔯', '🕎', '☯️', '☦️', '🛐', '⛎', '♈',
            '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐',
            '♑', '♒', '♓', '🆔', '⚛️', '🉑', '☢️', '☣️'
        ];

        const container = document.getElementById('emoji-picker-content');
        if (!container) return;

        container.innerHTML = emojis.map(emoji => 
            `<div class="emoji-item" data-emoji="${emoji}">${emoji}</div>`
        ).join('');

        // Event listeners para emojis
        container.querySelectorAll('.emoji-item').forEach(item => {
            item.addEventListener('click', () => {
                const emoji = item.getAttribute('data-emoji');
                this.inserirEmoji(emoji);
            });
        });
    }

    toggleEmojiPicker() {
        const picker = document.getElementById('emoji-picker');
        if (!picker) return;

        if (this.emojiPickerVisible) {
            this.fecharEmojiPicker();
        } else {
            this.abrirEmojiPicker();
        }
    }

    abrirEmojiPicker() {
        const picker = document.getElementById('emoji-picker');
        if (picker) {
            picker.classList.add('show');
            this.emojiPickerVisible = true;
        }
    }

    fecharEmojiPicker() {
        const picker = document.getElementById('emoji-picker');
        if (picker) {
            picker.classList.remove('show');
            this.emojiPickerVisible = false;
        }
    }

    inserirEmoji(emoji) {
        const input = document.getElementById('chat-input-mensagem');
        if (input) {
            const start = input.selectionStart || 0;
            const end = input.selectionEnd || 0;
            const text = input.value;
            const newText = text.substring(0, start) + emoji + text.substring(end);
            input.value = newText;
            input.focus();
            // Reposicionar cursor após o emoji
            input.setSelectionRange(start + emoji.length, start + emoji.length);
        }
    }

    async excluirConversa(chatId) {
        if (!confirm('Tem certeza que deseja excluir esta conversa?')) {
            return;
        }

        try {
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', this.obterCSRFToken());

            const response = await fetch(`/militares/chat/${chatId}/excluir/`, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (!response.ok) throw new Error('Erro ao excluir conversa');

            const data = await response.json();
            if (data.success) {
                // Se a conversa excluída é a atual, voltar para lista
                if (this.currentChatId == chatId) {
                    this.showConversas();
                }
                // Recarregar lista de conversas
                this.carregarConversas();
            } else {
                alert(data.error || 'Erro ao excluir conversa');
            }
        } catch (error) {
            console.error('Erro ao excluir conversa:', error);
            alert('Erro ao excluir conversa');
        }
    }
    
    async apagarMensagem(mensagemId) {
        if (!this.currentChatId) {
            alert('Erro: Chat não encontrado');
            return;
        }
        
        if (!confirm('Tem certeza que deseja apagar esta mensagem?\n\nA mensagem será removida da conversa para você e para o outro participante.')) {
            return;
        }
        
        try {
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', this.obterCSRFToken());
            
            // Encontrar elemento antes de deletar para animação
            const msgElement = document.querySelector(`[data-msg-id="${mensagemId}"]`);
            
            const response = await fetch(`/militares/chat/${this.currentChatId}/mensagem/${mensagemId}/deletar/`, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            if (!response.ok) throw new Error('Erro ao apagar mensagem');
            
            const data = await response.json();
            if (data.success) {
                // Remover mensagem da interface com animação
                if (msgElement) {
                    msgElement.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    msgElement.style.opacity = '0';
                    msgElement.style.transform = 'translateX(20px)';
                    setTimeout(() => {
                        msgElement.remove();
                        
                        // Verificar se não há mais mensagens e mostrar mensagem vazia
                        const container = document.getElementById('chat-mensagens-container');
                        if (container && container.children.length === 0) {
                            container.innerHTML = `
                                <div style="text-align: center; padding: 40px 20px; color: #8E8E93;">
                                    <i class="fas fa-comments" style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;"></i>
                                    <p>Nenhuma mensagem ainda</p>
                                </div>
                            `;
                        }
                    }, 300);
                }
                
                // A mensagem já foi deletada do banco, então quando o outro participante
                // atualizar as mensagens (via polling), ela não aparecerá mais
                console.log('Mensagem apagada com sucesso. O outro participante verá a atualização na próxima sincronização.');
            } else {
                alert(data.error || 'Erro ao apagar mensagem');
            }
        } catch (error) {
            console.error('Erro ao apagar mensagem:', error);
            alert('Erro ao apagar mensagem: ' + error.message);
        }
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.chatWidget = new ChatWidgetIOS();
});

