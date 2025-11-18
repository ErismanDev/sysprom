/**
 * Sistema de Mensagens de Voz
 */

class ChatVoiceMessage {
    constructor(chatWidget) {
        this.chatWidget = chatWidget;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordingStartTime = null;
        this.recordingTimer = null;
        this.startX = 0;
        this.currentX = 0;
        this.isDragging = false;
        this.init();
    }

    init() {
        const btnVoice = document.getElementById('btn-voice-chat');
        const btnCancel = document.getElementById('btn-cancel-recording');
        const voiceUI = document.getElementById('voice-recording-ui');
        
        if (!btnVoice) return;
        
        // Event listeners
        btnVoice.addEventListener('mousedown', (e) => this.iniciarGravacao(e));
        btnVoice.addEventListener('touchstart', (e) => this.iniciarGravacao(e));
        
        document.addEventListener('mouseup', (e) => this.pararGravacao(e));
        document.addEventListener('touchend', (e) => this.pararGravacao(e));
        
        btnCancel?.addEventListener('click', () => this.cancelarGravacao());
        
        // Drag para cancelar
        if (voiceUI) {
            voiceUI.addEventListener('touchmove', (e) => this.handleDrag(e));
            voiceUI.addEventListener('mousemove', (e) => this.handleDrag(e));
        }
    }

    async iniciarGravacao(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (this.isRecording) return;
        
        try {
            // Verificar se getUserMedia está disponível
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('getUserMedia não está disponível. Use HTTPS ou localhost.');
            }
            
            // Verificar se está em HTTPS (obrigatório em mobile)
            if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
                throw new Error('HTTPS_REQUIRED');
            }
            
            // Verificar permissões antes de solicitar
            if (navigator.permissions) {
                try {
                    const permissionStatus = await navigator.permissions.query({ name: 'microphone' });
                    if (permissionStatus.state === 'denied') {
                        throw new Error('PERMISSION_DENIED');
                    }
                } catch (permError) {
                    // Alguns navegadores não suportam permissions.query, continuar normalmente
                    console.log('Não foi possível verificar permissão:', permError);
                }
            }
            
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) {
                    this.audioChunks.push(event.data);
                    console.log('Chunk recebido:', event.data.size, 'bytes');
                }
            };
            
            this.mediaRecorder.onstop = () => {
                console.log('Gravação parada. Total de chunks:', this.audioChunks.length);
                stream.getTracks().forEach(track => track.stop());
            };
            
            this.mediaRecorder.onerror = (event) => {
                console.error('Erro no MediaRecorder:', event.error);
                this.cancelarGravacao();
            };
            
            // Iniciar gravação com timeslice para garantir que os chunks sejam coletados
            this.mediaRecorder.start(100); // Coletar chunks a cada 100ms
            this.isRecording = true;
            this.recordingStartTime = Date.now();
            console.log('Gravação iniciada');
            
            // Atualizar UI
            const btnVoice = document.getElementById('btn-voice-chat');
            const voiceUI = document.getElementById('voice-recording-ui');
            const inputMensagem = document.getElementById('chat-input-mensagem');
            const btnSend = document.getElementById('btn-send-chat');
            
            if (btnVoice) {
                btnVoice.setAttribute('data-recording', 'true');
            }
            if (voiceUI) {
                voiceUI.style.display = 'block';
            }
            if (inputMensagem) {
                inputMensagem.style.display = 'none';
            }
            if (btnSend) {
                btnSend.style.display = 'none';
            }
            
            // Iniciar timer
            this.iniciarTimer();
            
            // Capturar posição inicial para drag
            if (e.touches) {
                this.startX = e.touches[0].clientX;
            } else {
                this.startX = e.clientX;
            }
            this.isDragging = false;
            
        } catch (error) {
            console.error('Erro ao iniciar gravação:', error);
            this.tratarErroPermissaoMicrofone(error);
        }
    }
    
    tratarErroPermissaoMicrofone(error) {
        let mensagem = '';
        let titulo = 'Erro ao Acessar Microfone';
        
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError' || error.message === 'PERMISSION_DENIED') {
            titulo = 'Permissão Negada';
            mensagem = 'O acesso ao microfone foi negado.\n\n';
            
            // Detectar se é mobile
            const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            
            if (isMobile) {
                mensagem += '📱 Para permitir o microfone no smartphone:\n\n';
                mensagem += '1. Toque no ícone de cadeado 🔒 na barra de endereço\n';
                mensagem += '2. Ou vá em Configurações do navegador\n';
                mensagem += '3. Procure por "Permissões" ou "Microfone"\n';
                mensagem += '4. Permita o acesso ao microfone para este site\n';
                mensagem += '5. Recarregue a página (puxe para baixo)\n';
                mensagem += '6. Tente gravar novamente';
            } else {
                mensagem += '🖥️ Para permitir o microfone:\n\n';
                mensagem += '1. Clique no ícone de cadeado 🔒 na barra de endereço\n';
                mensagem += '2. Procure por "Microfone" ou "Microphone"\n';
                mensagem += '3. Altere para "Permitir"\n';
                mensagem += '4. Recarregue a página (F5)\n';
                mensagem += '5. Tente gravar novamente';
            }
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            titulo = 'Microfone Não Encontrado';
            mensagem = 'Nenhum microfone foi detectado no dispositivo.\n\n';
            mensagem += 'Verifique se:\n';
            mensagem += '• Há um microfone conectado ao dispositivo\n';
            mensagem += '• O microfone está funcionando\n';
            mensagem += '• Outros aplicativos conseguem usar o microfone';
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
            titulo = 'Microfone em Uso';
            mensagem = 'O microfone está sendo usado por outro aplicativo.\n\n';
            mensagem += 'Por favor:\n';
            mensagem += '• Feche outros aplicativos que possam estar usando o microfone\n';
            mensagem += '• Aguarde alguns segundos\n';
            mensagem += '• Tente gravar novamente';
        } else if (error.message === 'HTTPS_REQUIRED' || (error.message && error.message.includes('HTTPS'))) {
            titulo = 'HTTPS Necessário';
            mensagem = 'O acesso ao microfone requer conexão segura (HTTPS).\n\n';
            mensagem += 'O site precisa ser acessado via HTTPS para usar o microfone.\n';
            mensagem += 'Entre em contato com o administrador do sistema.';
        } else {
            titulo = 'Erro ao Acessar Microfone';
            mensagem = 'Ocorreu um erro ao tentar acessar o microfone.\n\n';
            mensagem += 'Erro: ' + (error.message || error.name || 'Desconhecido') + '\n\n';
            mensagem += 'Tente:\n';
            mensagem += '• Recarregar a página\n';
            mensagem += '• Verificar as permissões do navegador\n';
            mensagem += '• Usar outro navegador';
        }
        
        // Mostrar mensagem mais amigável
        alert(titulo + '\n\n' + mensagem);
        
        // Log para debug
        console.error('Erro de permissão do microfone:', {
            error: error,
            name: error.name,
            message: error.message,
            userAgent: navigator.userAgent,
            protocol: location.protocol,
            hostname: location.hostname
        });
    }

    pararGravacao(e) {
        if (!this.isRecording) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        // Verificar se foi arrastado para cancelar
        if (this.isDragging && Math.abs(this.currentX - this.startX) > 50) {
            this.cancelarGravacao();
            return;
        }
        
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        this.isRecording = false;
        this.pararTimer();
        
        // Processar áudio
        this.processarAudio();
    }

    cancelarGravacao() {
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        this.isRecording = false;
        this.audioChunks = [];
        this.pararTimer();
        this.esconderUI();
    }

    processarAudio() {
        // Aguardar um pouco para garantir que todos os chunks foram coletados
        setTimeout(() => {
            if (this.audioChunks.length === 0) {
                console.error('Nenhum chunk de áudio foi coletado');
                this.esconderUI();
                return;
            }
            
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
            const duracao = Math.floor((Date.now() - this.recordingStartTime) / 1000);
            
            console.log('Processando áudio:', {
                chunks: this.audioChunks.length,
                tamanho: audioBlob.size,
                duracao: duracao
            });
            
            // Enviar áudio
            this.enviarAudio(audioBlob, duracao);
            
            this.esconderUI();
        }, 100);
    }

    async enviarAudio(audioBlob, duracao) {
        if (!this.chatWidget.currentChatId) {
            console.error('Chat ID não encontrado');
            alert('Erro: Chat não encontrado');
            return;
        }
        
        if (!audioBlob || audioBlob.size === 0) {
            console.error('Áudio vazio ou inválido');
            alert('Erro: Áudio vazio. Tente gravar novamente.');
            return;
        }
        
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'voice-message.webm');
            formData.append('duracao', duracao);
            
            const csrfToken = this.chatWidget.obterCSRFToken();
            if (csrfToken) {
                formData.append('csrfmiddlewaretoken', csrfToken);
            }
            
            console.log('Enviando áudio:', {
                tamanho: audioBlob.size,
                duracao: duracao,
                chatId: this.chatWidget.currentChatId
            });
            
            const response = await fetch(`/militares/chat/${this.chatWidget.currentChatId}/enviar-audio/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const responseText = await response.text();
            console.log('Resposta do servidor:', response.status, responseText);
            
            if (response.ok) {
                try {
                    const data = JSON.parse(responseText);
                    if (data.success) {
                        console.log('Áudio enviado com sucesso:', data);
                        // Recarregar mensagens
                        await this.chatWidget.carregarMensagens(this.chatWidget.currentChatId);
                        this.chatWidget.scrollParaFinal();
                    } else {
                        alert('Erro ao enviar mensagem de voz: ' + (data.error || 'Erro desconhecido'));
                    }
                } catch (parseError) {
                    console.error('Erro ao parsear resposta JSON:', parseError);
                    alert('Erro ao processar resposta do servidor');
                }
            } else {
                try {
                    const errorData = JSON.parse(responseText);
                    alert('Erro ao enviar mensagem de voz: ' + (errorData.error || 'Erro desconhecido'));
                } catch {
                    alert('Erro ao enviar mensagem de voz (Status: ' + response.status + ')');
                }
            }
        } catch (error) {
            console.error('Erro ao enviar áudio:', error);
            alert('Erro ao enviar mensagem de voz: ' + error.message);
        }
    }

    iniciarTimer() {
        const timeElement = document.getElementById('voice-recording-time');
        if (!timeElement) return;
        
        this.recordingTimer = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
            const minutos = Math.floor(elapsed / 60);
            const segundos = elapsed % 60;
            timeElement.textContent = `${String(minutos).padStart(2, '0')}:${String(segundos).padStart(2, '0')}`;
        }, 100);
    }

    pararTimer() {
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
        const timeElement = document.getElementById('voice-recording-time');
        if (timeElement) {
            timeElement.textContent = '00:00';
        }
    }

    esconderUI() {
        const btnVoice = document.getElementById('btn-voice-chat');
        const voiceUI = document.getElementById('voice-recording-ui');
        const inputMensagem = document.getElementById('chat-input-mensagem');
        const btnSend = document.getElementById('btn-send-chat');
        
        if (btnVoice) {
            btnVoice.setAttribute('data-recording', 'false');
        }
        if (voiceUI) {
            voiceUI.style.display = 'none';
        }
        if (inputMensagem) {
            inputMensagem.style.display = 'block';
        }
        if (btnSend) {
            btnSend.style.display = 'flex';
        }
    }

    handleDrag(e) {
        if (!this.isRecording) return;
        
        if (e.touches) {
            this.currentX = e.touches[0].clientX;
        } else {
            this.currentX = e.clientX;
        }
        
        const diff = this.currentX - this.startX;
        if (Math.abs(diff) > 10) {
            this.isDragging = true;
            const voiceUI = document.getElementById('voice-recording-ui');
            if (voiceUI) {
                if (diff < -50) {
                    voiceUI.style.opacity = '0.5';
                    voiceUI.style.transform = `translateX(${diff}px)`;
                } else {
                    voiceUI.style.opacity = '1';
                    voiceUI.style.transform = 'translateX(0)';
                }
            }
        }
    }
}

