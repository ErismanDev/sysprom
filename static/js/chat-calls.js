/**
 * Sistema de Chamadas de Voz e Vídeo usando WebRTC
 */

class ChatCalls {
    constructor(chatWidget) {
        this.chatWidget = chatWidget;
        this.localStream = null;
        this.remoteStream = null;
        this.peerConnection = null;
        this.isCallActive = false;
        this.isVideoCall = false;
        this.callStartTime = null;
        this.callTimer = null;
        this.currentCallId = null;
        this.isMuted = false;
        this.isVideoEnabled = true;
        this.pollingRespostaTimer = null;
        this.pollingChamadaPendenteTimer = null;
        this.init();
    }

    init() {
        try {
            // Event listeners para botões de chamada
            const btnVideo = document.getElementById('btn-call-video');
            const btnVoice = document.getElementById('btn-call-voice');
            const btnAccept = document.getElementById('btn-call-accept');
            const btnReject = document.getElementById('btn-call-reject');
            const btnEnd = document.getElementById('btn-call-end');
            const btnMute = document.getElementById('btn-call-mute');
            const btnToggleVideo = document.getElementById('btn-call-toggle-video');
            
            if (btnVideo) {
                btnVideo.addEventListener('click', () => {
                    console.log('Botão de vídeo clicado');
                    this.iniciarChamada(true);
                });
            } else {
                console.warn('Botão btn-call-video não encontrado');
            }
            
            if (btnVoice) {
                btnVoice.addEventListener('click', () => {
                    console.log('Botão de voz clicado');
                    this.iniciarChamada(false);
                });
            } else {
                console.warn('Botão btn-call-voice não encontrado');
            }
            
            if (btnAccept) {
                btnAccept.addEventListener('click', () => this.aceitarChamada());
            }
            
            if (btnReject) {
                btnReject.addEventListener('click', () => this.rejeitarChamada());
            }
            
            if (btnEnd) {
                btnEnd.addEventListener('click', () => this.encerrarChamada());
            }
            
            if (btnMute) {
                btnMute.addEventListener('click', () => this.toggleMute());
            }
            
            if (btnToggleVideo) {
                btnToggleVideo.addEventListener('click', () => this.toggleVideo());
            }
            
            // Verificar chamadas pendentes periodicamente
            this.iniciarPollingChamadasPendentes();
        } catch (error) {
            console.error('Erro ao inicializar ChatCalls:', error);
        }
    }

    async iniciarChamada(video = true) {
        console.log('iniciarChamada chamado', { video, currentChatId: this.chatWidget.currentChatId });
        
        if (!this.chatWidget || !this.chatWidget.currentChatId) {
            console.error('Não há chat selecionado');
            alert('Por favor, selecione uma conversa primeiro');
            return;
        }
        
        this.isVideoCall = video;
        this.currentCallId = `call_${Date.now()}_${this.chatWidget.obterUsuarioId()}`;
        
        try {
            // Verificar se getUserMedia está disponível
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('getUserMedia não está disponível. Use HTTPS ou localhost.');
            }
            
            // Solicitar acesso à câmera/microfone
            const constraints = {
                audio: true,
                video: video ? {
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                } : false
            };
            
            this.localStream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Mostrar interface de chamada
            this.mostrarInterfaceChamada('outgoing');
            
            // Exibir vídeo local se for chamada de vídeo
            if (video && this.localStream.getVideoTracks().length > 0) {
                const localVideo = document.getElementById('chat-call-video-local-stream');
                localVideo.srcObject = this.localStream;
                document.getElementById('chat-call-video-local').style.display = 'block';
            }
            
            // Criar peer connection
            await this.criarPeerConnection();
            
            // Adicionar tracks locais
            this.localStream.getTracks().forEach(track => {
                this.peerConnection.addTrack(track, this.localStream);
            });
            
            // Criar oferta
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);
            
            // Enviar oferta para o servidor (simulado - em produção usar WebSocket)
            this.enviarOfertaChamada(offer);
            
        } catch (error) {
            console.error('Erro ao iniciar chamada:', error);
            this.tratarErroPermissao(error, video);
            this.encerrarChamada();
        }
    }
    
    tratarErroPermissao(error, video) {
        let mensagem = 'Erro ao acessar ';
        mensagem += video ? 'câmera e microfone' : 'microfone';
        mensagem += '. ';
        
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            mensagem += '\n\nPermissão negada. Por favor:\n';
            mensagem += '1. Clique no ícone de cadeado na barra de endereço\n';
            mensagem += '2. Permita o acesso à ' + (video ? 'câmera e microfone' : 'microfone') + '\n';
            mensagem += '3. Recarregue a página e tente novamente';
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            mensagem += '\n\nNenhum dispositivo encontrado. Verifique se há ';
            mensagem += video ? 'câmera e microfone' : 'microfone';
            mensagem += ' conectados ao dispositivo.';
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
            mensagem += '\n\nO dispositivo está sendo usado por outro aplicativo. ';
            mensagem += 'Feche outros aplicativos que possam estar usando o dispositivo.';
        } else if (error.name === 'OverconstrainedError') {
            mensagem += '\n\nO dispositivo não suporta as configurações solicitadas.';
        } else if (error.message && error.message.includes('HTTPS')) {
            mensagem += '\n\nAcesso à mídia requer HTTPS. O site precisa ser servido via HTTPS.';
        } else {
            mensagem += '\n\nErro: ' + (error.message || error.name);
        }
        
        alert(mensagem);
    }

    async criarPeerConnection() {
        const configuration = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ]
        };
        
        this.peerConnection = new RTCPeerConnection(configuration);
        
        // Quando receber stream remoto
        this.peerConnection.ontrack = (event) => {
            console.log('🎯 EVENTO ONTRACK DISPARADO!');
            console.log('Event:', event);
            console.log('Streams:', event.streams);
            console.log('Track:', event.track);
            console.log('Track kind:', event.track?.kind);
            console.log('Track enabled:', event.track?.enabled);
            console.log('Track readyState:', event.track?.readyState);
            
            // IMPORTANTE: Verificar se não é o stream local
            // O ontrack pode ser disparado com o stream local em alguns casos
            if (this.localStream) {
                const isLocalStream = event.streams && event.streams.some(stream => {
                    return stream.id === this.localStream.id || 
                           stream.getTracks().some(track => 
                               this.localStream.getTracks().some(localTrack => localTrack.id === track.id)
                           );
                });
                
                if (isLocalStream) {
                    console.warn('⚠️ Evento ontrack recebido com stream LOCAL, ignorando...');
                    return;
                }
            }
            
            // Verificar se o evento tem um stream válido
            if (!event.streams || event.streams.length === 0) {
                console.warn('⚠️ Evento ontrack sem streams, tentando usar event.stream...');
                if (!event.stream) {
                    console.error('❌ Nenhum stream encontrado no evento ontrack!');
                    return;
                }
            }
            
            // Obter o stream correto
            let streamRecebido = null;
            if (event.streams && event.streams.length > 0) {
                streamRecebido = event.streams[0];
            } else if (event.stream) {
                streamRecebido = event.stream;
            } else {
                console.error('❌ Nenhum stream encontrado no evento ontrack!');
                return;
            }
            
            // Verificar se o stream tem tracks válidos
            if (!streamRecebido || streamRecebido.getTracks().length === 0) {
                console.warn('⚠️ Stream recebido sem tracks válidos');
                return;
            }
            
            // Se já temos um remoteStream diferente, usar o novo stream
            // (cada evento ontrack pode trazer um stream diferente, mas geralmente é o mesmo)
            if (this.remoteStream && this.remoteStream.id !== streamRecebido.id) {
                console.log('🔄 Novo stream recebido, substituindo stream anterior');
                console.log('  Stream anterior ID:', this.remoteStream.id);
                console.log('  Novo stream ID:', streamRecebido.id);
                // Parar tracks do stream anterior
                this.remoteStream.getTracks().forEach(track => track.stop());
            }
            
            // Usar o stream recebido
            this.remoteStream = streamRecebido;
            
            console.log('Remote stream atribuído:', this.remoteStream);
            console.log('Stream ID:', this.remoteStream.id);
            console.log('Tracks no stream:', this.remoteStream.getTracks().length);
            console.log('Video tracks:', this.remoteStream.getVideoTracks().length);
            console.log('Audio tracks:', this.remoteStream.getAudioTracks().length);
            console.log('All tracks:', this.remoteStream.getTracks().map(t => ({
                kind: t.kind,
                enabled: t.enabled,
                readyState: t.readyState,
                id: t.id
            })));
            
            const remoteVideo = document.getElementById('chat-call-video-remote-stream');
            console.log('Remote video element:', remoteVideo);
            const avatarVoice = document.getElementById('chat-call-avatar-voice');
            const avatarImg = document.getElementById('chat-call-avatar-img');
            const avatarInicial = document.getElementById('chat-call-avatar-inicial');
            
            // Função auxiliar para obter foto do contato
            const obterFotoContato = () => {
                const avatarContato = document.getElementById('chat-avatar-contato');
                if (avatarContato) {
                    const img = avatarContato.querySelector('img');
                    if (img && img.src) {
                        return { foto: img.src, inicial: null };
                    }
                    const inicial = avatarContato.querySelector('span');
                    if (inicial && inicial.textContent) {
                        return { foto: null, inicial: inicial.textContent };
                    }
                }
                
                const msgAvatar = document.querySelector('.chat-mensagem-ios.received .chat-avatar-msg img, .message-received .message-avatar.avatar-received img');
                if (msgAvatar && msgAvatar.src) {
                    return { foto: msgAvatar.src, inicial: null };
                }
                
                const nomeContato = document.getElementById('chat-nome-contato')?.textContent;
                if (nomeContato && nomeContato !== 'Selecione uma conversa') {
                    return { foto: null, inicial: nomeContato.charAt(0).toUpperCase() };
                }
                
                return { foto: null, inicial: '?' };
            };
            
            const infoContato = obterFotoContato();
            
            // Verificar se há stream de vídeo remoto
            const hasVideoTracks = this.remoteStream.getVideoTracks().length > 0;
            const hasAudioTracks = this.remoteStream.getAudioTracks().length > 0;
            
            console.log('═══════════════════════════════════════');
            console.log('📹 STREAM REMOTO RECEBIDO (ONTRACK)');
            console.log('═══════════════════════════════════════');
            console.log('Track kind:', event.track?.kind);
            console.log('Track enabled:', event.track?.enabled);
            console.log('Track readyState:', event.track?.readyState);
            console.log('isVideoCall:', this.isVideoCall);
            console.log('hasVideoTracks:', hasVideoTracks);
            console.log('hasAudioTracks:', hasAudioTracks);
            console.log('Video tracks:', this.remoteStream.getVideoTracks().length);
            console.log('Audio tracks:', this.remoteStream.getAudioTracks().length);
            console.log('All tracks:', this.remoteStream.getTracks().map(t => ({kind: t.kind, enabled: t.enabled, readyState: t.readyState})));
            console.log('Remote stream:', this.remoteStream);
            console.log('Connection state:', this.peerConnection.connectionState);
            console.log('ICE connection state:', this.peerConnection.iceConnectionState);
            console.log('═══════════════════════════════════════');
            
            // Se for track de áudio e não houver tracks de vídeo ainda, aguardar
            if (event.track && event.track.kind === 'audio' && !hasVideoTracks && this.isVideoCall) {
                console.log('📞 Track de áudio recebido, aguardando track de vídeo...');
                // Não retornar, apenas não exibir vídeo ainda
            }
            
            // Exibir vídeo se:
            // 1. For chamada de vídeo
            // 2. Houver tracks de vídeo no stream remoto
            // (Não precisamos esperar a conexão estar completamente estabelecida - o stream já está disponível)
            // A conexão será estabelecida automaticamente pelo WebRTC
            
            // Verificar estado da conexão (apenas para log)
            const conexaoEstabelecida = this.peerConnection.connectionState === 'connected' || 
                                       this.peerConnection.connectionState === 'connecting' ||
                                       this.peerConnection.iceConnectionState === 'connected' ||
                                       this.peerConnection.iceConnectionState === 'completed' ||
                                       this.peerConnection.iceConnectionState === 'checking';
            
            console.log('🔍 Estado da conexão:', {
                connectionState: this.peerConnection.connectionState,
                iceConnectionState: this.peerConnection.iceConnectionState,
                conexaoEstabelecida: conexaoEstabelecida
            });
            
            // Exibir vídeo se houver tracks de vídeo (independente do estado da conexão)
            console.log('🔍 Verificando condições para exibir vídeo:', {
                isVideoCall: this.isVideoCall,
                hasVideoTracks: hasVideoTracks,
                trackKind: event.track?.kind
            });
            
            if (this.isVideoCall && hasVideoTracks) {
                // Chamada de vídeo com stream de vídeo - mostrar vídeo remoto
                console.log('✅ Exibindo vídeo remoto (condições atendidas)');
                console.log('🔍 Estado ANTES de configurar:', {
                    remoteVideoExiste: !!remoteVideo,
                    remoteVideoDisplay: remoteVideo?.style.display,
                    remoteVideoSrcObject: !!remoteVideo?.srcObject,
                    remoteStreamExiste: !!this.remoteStream,
                    videoTracks: this.remoteStream?.getVideoTracks().length
                });
                
                if (remoteVideo) {
                    // Limpar qualquer stream anterior
                    if (remoteVideo.srcObject) {
                        console.log('🧹 Limpando stream anterior');
                        remoteVideo.srcObject.getTracks().forEach(track => track.stop());
                    }
                    
                    // Atribuir stream
                    console.log('📹 Atribuindo stream remoto ao elemento de vídeo');
                    remoteVideo.srcObject = this.remoteStream;
                    
                    // Garantir que o vídeo está visível
                    console.log('👁️ Tornando vídeo visível');
                    remoteVideo.style.display = 'block';
                    remoteVideo.style.visibility = 'visible';
                    remoteVideo.style.opacity = '1';
                    
                    // Garantir que o container também está visível
                    const remoteContainer = document.getElementById('chat-call-video-remote');
                    if (remoteContainer) {
                        remoteContainer.style.display = 'flex';
                        console.log('✅ Container de vídeo remoto visível');
                    }
                    
                    // Esconder avatar e status
                    if (avatarVoice) {
                        avatarVoice.style.display = 'none';
                        console.log('👤 Avatar escondido');
                    }
                    const statusDiv = document.getElementById('chat-call-status');
                    if (statusDiv) {
                        statusDiv.style.display = 'none';
                        console.log('📊 Status escondido');
                    }
                    
                    // Forçar reprodução (aguardar um pouco para o stream estar pronto)
                    const tentarReproduzir = (tentativa = 1) => {
                        console.log(`▶️ Tentando reproduzir vídeo remoto (tentativa ${tentativa})...`);
                        console.log('🔍 Estado do vídeo antes de reproduzir:', {
                            paused: remoteVideo.paused,
                            ended: remoteVideo.ended,
                            readyState: remoteVideo.readyState,
                            networkState: remoteVideo.networkState,
                            videoWidth: remoteVideo.videoWidth,
                            videoHeight: remoteVideo.videoHeight,
                            srcObject: !!remoteVideo.srcObject
                        });
                        
                        // Sempre tentar reproduzir, mesmo se não estiver pausado
                        remoteVideo.play().then(() => {
                            console.log('✅ Vídeo remoto reproduzindo com sucesso!');
                            console.log('📐 Dimensões do vídeo:', {
                                videoWidth: remoteVideo.videoWidth,
                                videoHeight: remoteVideo.videoHeight,
                                clientWidth: remoteVideo.clientWidth,
                                clientHeight: remoteVideo.clientHeight
                            });
                            
                            // Se as dimensões ainda são muito pequenas, tentar novamente
                            if (remoteVideo.videoWidth <= 2 && remoteVideo.videoHeight <= 2 && tentativa < 5) {
                                console.warn('⚠️ Vídeo tem dimensões muito pequenas, tentando novamente...');
                                setTimeout(() => tentarReproduzir(tentativa + 1), 1000);
                            }
                        }).catch(e => {
                            // Ignorar AbortError (pode acontecer quando há múltiplas tentativas)
                            if (e.name !== 'AbortError') {
                                console.error('❌ Erro ao reproduzir vídeo remoto:', e);
                                console.error('❌ Detalhes do erro:', {
                                    name: e.name,
                                    message: e.message,
                                    code: e.code
                                });
                                
                                // Tentar novamente se não for um erro crítico
                                if (tentativa < 5 && e.name !== 'NotAllowedError' && e.name !== 'NotSupportedError') {
                                    setTimeout(() => tentarReproduzir(tentativa + 1), 1000);
                                }
                            } else {
                                // Mesmo com AbortError, tentar novamente se as dimensões são pequenas
                                if (remoteVideo.videoWidth <= 2 && remoteVideo.videoHeight <= 2 && tentativa < 5) {
                                    setTimeout(() => tentarReproduzir(tentativa + 1), 1000);
                                }
                            }
                        });
                    };
                    
                    // Tentar reproduzir várias vezes com delays crescentes
                    setTimeout(() => tentarReproduzir(1), 100);
                    setTimeout(() => tentarReproduzir(2), 500);
                    setTimeout(() => tentarReproduzir(3), 1000);
                    setTimeout(() => tentarReproduzir(4), 2000);
                    
                    // Adicionar event listeners para debug
                    remoteVideo.onloadedmetadata = () => {
                        console.log('✅ Metadata do vídeo remoto carregado');
                        console.log('📐 Dimensões após metadata:', {
                            videoWidth: remoteVideo.videoWidth,
                            videoHeight: remoteVideo.videoHeight
                        });
                    };
                    remoteVideo.onplay = () => {
                        console.log('✅ Vídeo remoto começou a reproduzir');
                        console.log('📐 Dimensões durante reprodução:', {
                            videoWidth: remoteVideo.videoWidth,
                            videoHeight: remoteVideo.videoHeight,
                            clientWidth: remoteVideo.clientWidth,
                            clientHeight: remoteVideo.clientHeight
                        });
                    };
                    remoteVideo.onpause = () => {
                        console.warn('⚠️ Vídeo remoto pausado');
                    };
                    remoteVideo.onstalled = () => {
                        console.warn('⚠️ Vídeo remoto travado');
                    };
                    remoteVideo.onwaiting = () => {
                        console.warn('⚠️ Vídeo remoto aguardando dados');
                    };
                    remoteVideo.onerror = (e) => {
                        console.error('❌ Erro no elemento de vídeo remoto:', e);
                        console.error('❌ Erro detalhado:', {
                            error: remoteVideo.error,
                            networkState: remoteVideo.networkState,
                            readyState: remoteVideo.readyState
                        });
                    };
                    
                    // Função para verificar e forçar reprodução quando conexão estiver estabelecida
                    const verificarConexaoEForcarReproducao = () => {
                        const connectionState = this.peerConnection.connectionState;
                        const iceConnectionState = this.peerConnection.iceConnectionState;
                        
                        if ((connectionState === 'connected' || iceConnectionState === 'connected' || iceConnectionState === 'completed') && 
                            remoteVideo && remoteVideo.srcObject && 
                            (remoteVideo.videoWidth <= 2 || remoteVideo.videoHeight <= 2 || remoteVideo.paused)) {
                            console.log('🔗 Conexão estabelecida, forçando reprodução do vídeo...');
                            tentarReproduzir(5);
                        }
                    };
                    
                    // Armazenar referência para usar nos listeners existentes
                    this._forcarReproducaoRemota = verificarConexaoEForcarReproducao;
                    
                    // Verificar estado após um delay
                    setTimeout(() => {
                        console.log('🔍 Estado APÓS configurar (500ms):', {
                            srcObject: !!remoteVideo.srcObject,
                            display: remoteVideo.style.display,
                            visibility: remoteVideo.style.visibility,
                            opacity: remoteVideo.style.opacity,
                            videoWidth: remoteVideo.videoWidth,
                            videoHeight: remoteVideo.videoHeight,
                            paused: remoteVideo.paused,
                            ended: remoteVideo.ended,
                            readyState: remoteVideo.readyState,
                            networkState: remoteVideo.networkState,
                            error: remoteVideo.error,
                            connectionState: this.peerConnection.connectionState,
                            iceConnectionState: this.peerConnection.iceConnectionState
                        });
                        
                        // Se o vídeo ainda não tem dimensões válidas, tentar novamente
                        if (remoteVideo.srcObject && (remoteVideo.videoWidth <= 2 || remoteVideo.videoHeight <= 2)) {
                            console.warn('⚠️ Vídeo ainda não tem dimensões válidas após 500ms, tentando novamente...');
                            if (this._forcarReproducaoRemota) {
                                this._forcarReproducaoRemota();
                            }
                        }
                    }, 500);
                    
                    console.log('✅ Vídeo remoto configurado:', {
                        srcObject: !!remoteVideo.srcObject,
                        display: remoteVideo.style.display,
                        videoWidth: remoteVideo.videoWidth,
                        videoHeight: remoteVideo.videoHeight
                    });
                    
                    // Forçar atualização da interface após configurar o vídeo
                    // Isso garante que o avatar seja escondido e o vídeo seja exibido
                    setTimeout(() => {
                        console.log('🔄 Forçando atualização da interface após configurar vídeo remoto');
                        this.mostrarInterfaceChamada('active');
                    }, 100);
                } else {
                    console.error('❌ Elemento remoteVideo não encontrado!');
                }
                
                // Garantir que o vídeo local está visível (PIP)
                const videoLocalContainer = document.getElementById('chat-call-video-local');
                if (videoLocalContainer && this.localStream) {
                    videoLocalContainer.style.display = 'block';
                    console.log('✅ Vídeo local (PIP) exibido');
                }
            } else if (this.isVideoCall && !hasVideoTracks && hasAudioTracks) {
                // Chamada de vídeo mas sem stream de vídeo (só áudio) - mostrar avatar
                console.log('⚠️ Vídeo remoto não disponível, mostrando avatar');
                if (avatarVoice) {
                    avatarVoice.style.display = 'flex';
                    if (infoContato.foto && avatarImg) {
                        avatarImg.src = infoContato.foto;
                        avatarImg.style.display = 'block';
                        if (avatarInicial) avatarInicial.style.display = 'none';
                    } else if (infoContato.inicial && avatarInicial) {
                        avatarInicial.textContent = infoContato.inicial;
                        avatarInicial.style.display = 'block';
                        if (avatarImg) avatarImg.style.display = 'none';
                    }
                }
                if (remoteVideo) remoteVideo.style.display = 'none';
            } else {
                // Chamada de voz - mostrar avatar
                console.log('📞 Chamada de voz - mostrando avatar');
                if (avatarVoice) {
                    avatarVoice.style.display = 'flex';
                    if (infoContato.foto && avatarImg) {
                        avatarImg.src = infoContato.foto;
                        avatarImg.style.display = 'block';
                        if (avatarInicial) avatarInicial.style.display = 'none';
                    } else if (infoContato.inicial && avatarInicial) {
                        avatarInicial.textContent = infoContato.inicial;
                        avatarInicial.style.display = 'block';
                        if (avatarImg) avatarImg.style.display = 'none';
                    }
                }
                if (remoteVideo) remoteVideo.style.display = 'none';
            }
            
            document.getElementById('chat-call-status').style.display = 'none';
            this.isCallActive = true;
            this.iniciarTimer();
            
            // Forçar atualização da interface após receber stream
            console.log('🔄 Atualizando interface após receber stream remoto');
            setTimeout(() => {
                this.mostrarInterfaceChamada('active');
            }, 100);
        };
        
        // Quando receber ICE candidate
        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                // Enviar ICE candidate (simulado)
                this.enviarIceCandidate(event.candidate);
            }
        };
        
        // Quando conexão mudar de estado
        this.peerConnection.onconnectionstatechange = () => {
            console.log('🔄 Estado da conexão WebRTC:', this.peerConnection.connectionState);
            
            if (this.peerConnection.connectionState === 'connected') {
                console.log('✅ Conexão WebRTC estabelecida!');
                // Atualizar interface quando conexão for estabelecida
                setTimeout(() => {
                    this.mostrarInterfaceChamada('active');
                    // Forçar reprodução do vídeo remoto se necessário
                    if (this._forcarReproducaoRemota) {
                        this._forcarReproducaoRemota();
                    }
                }, 100);
            } else if (this.peerConnection.connectionState === 'disconnected' || 
                this.peerConnection.connectionState === 'failed') {
                console.error('❌ Conexão WebRTC perdida ou falhou');
                this.encerrarChamada();
            }
        };
        
        // Monitorar ICE connection state
        this.peerConnection.oniceconnectionstatechange = () => {
            console.log('🧊 Estado ICE:', this.peerConnection.iceConnectionState);
            
            if (this.peerConnection.iceConnectionState === 'connected' || 
                this.peerConnection.iceConnectionState === 'completed') {
                console.log('✅ Conexão ICE estabelecida!');
                // Forçar reprodução do vídeo remoto se necessário
                if (this._forcarReproducaoRemota) {
                    setTimeout(() => {
                        this._forcarReproducaoRemota();
                    }, 100);
                }
            }
        };
    }

    mostrarInterfaceChamada(tipo) {
        console.log('📞 mostrarInterfaceChamada chamado com tipo:', tipo);
        console.log('📞 isVideoCall:', this.isVideoCall);
        
        const overlay = document.getElementById('chat-call-overlay');
        if (!overlay) {
            console.error('❌ Elemento chat-call-overlay não encontrado!');
            console.error('❌ Verifique se o HTML da interface de chamada está presente na página.');
            return;
        }
        
        console.log('✅ Overlay encontrado, adicionando classe active...');
        overlay.classList.add('active');
        
        const statusTitle = document.getElementById('chat-call-status-title');
        const statusSubtitle = document.getElementById('chat-call-status-subtitle');
        const nomeInfo = document.getElementById('chat-call-nome-info');
        const nomeContatoEl = document.getElementById('chat-nome-contato');
        const nomeContato = nomeContatoEl ? nomeContatoEl.textContent : 'Contato';
        const videoLocal = document.getElementById('chat-call-video-local');
        const videoRemote = document.getElementById('chat-call-video-remote-stream');
        
        // Configurar interface baseada no tipo de chamada
        const avatarVoice = document.getElementById('chat-call-avatar-voice');
        const avatarInicial = document.getElementById('chat-call-avatar-inicial');
        const avatarImg = document.getElementById('chat-call-avatar-img');
        
        // Função auxiliar para obter foto do contato
        const obterFotoContato = () => {
            // Tentar obter do header do chat
            const avatarContato = document.getElementById('chat-avatar-contato');
            if (avatarContato) {
                const img = avatarContato.querySelector('img');
                if (img && img.src) {
                    return { foto: img.src, inicial: null };
                }
                const inicial = avatarContato.querySelector('span');
                if (inicial && inicial.textContent) {
                    return { foto: null, inicial: inicial.textContent };
                }
            }
            
            // Tentar obter de mensagens recebidas
            const msgAvatar = document.querySelector('.chat-mensagem-ios.received .chat-avatar-msg img, .message-received .message-avatar.avatar-received img');
            if (msgAvatar && msgAvatar.src) {
                return { foto: msgAvatar.src, inicial: null };
            }
            
            // Tentar obter inicial de mensagens
            const msgInicial = document.querySelector('.chat-mensagem-ios.received .chat-avatar-msg span, .message-received .message-avatar.avatar-received');
            if (msgInicial && msgInicial.textContent) {
                return { foto: null, inicial: msgInicial.textContent.trim().charAt(0) };
            }
            
            // Usar inicial do nome do contato
            if (nomeContato && nomeContato !== 'Selecione uma conversa') {
                return { foto: null, inicial: nomeContato.charAt(0).toUpperCase() };
            }
            
            return { foto: null, inicial: '?' };
        };
        
        const infoContato = obterFotoContato();
        
        if (!this.isVideoCall) {
            // Chamada de voz - mostrar avatar
            if (videoLocal) videoLocal.style.display = 'none';
            if (videoRemote) videoRemote.style.display = 'none';
            if (avatarVoice) {
                avatarVoice.style.display = 'flex';
                if (infoContato.foto && avatarImg) {
                    avatarImg.src = infoContato.foto;
                    avatarImg.style.display = 'block';
                    if (avatarInicial) avatarInicial.style.display = 'none';
                } else if (infoContato.inicial && avatarInicial) {
                    avatarInicial.textContent = infoContato.inicial;
                    avatarInicial.style.display = 'block';
                    if (avatarImg) avatarImg.style.display = 'none';
                }
            }
        } else {
            // Chamada de vídeo - mostrar vídeo local e preparar para vídeo remoto
            if (avatarVoice) avatarVoice.style.display = 'none';
            // Mostrar vídeo local se já estiver disponível
            if (this.localStream && videoLocal) {
                videoLocal.style.display = 'block';
            }
            // Configurar avatar caso o vídeo remoto não esteja disponível
            if (infoContato.foto && avatarImg) {
                avatarImg.src = infoContato.foto;
            } else if (infoContato.inicial && avatarInicial) {
                avatarInicial.textContent = infoContato.inicial;
            }
        }
        
        if (tipo === 'outgoing') {
            if (statusTitle) statusTitle.textContent = this.isVideoCall ? 'Chamando...' : 'Ligando...';
            if (statusSubtitle) statusSubtitle.textContent = nomeContato;
            const btnEnd = document.getElementById('btn-call-end');
            const btnAccept = document.getElementById('btn-call-accept');
            const btnReject = document.getElementById('btn-call-reject');
            const btnMute = document.getElementById('btn-call-mute');
            const btnToggleVideo = document.getElementById('btn-call-toggle-video');
            if (btnEnd) btnEnd.style.display = 'flex';
            if (btnAccept) btnAccept.style.display = 'none';
            if (btnReject) btnReject.style.display = 'none';
            if (btnMute) btnMute.style.display = 'none';
            if (btnToggleVideo) btnToggleVideo.style.display = 'none';
        } else if (tipo === 'incoming') {
            if (statusTitle) statusTitle.textContent = this.isVideoCall ? 'Chamada de Vídeo' : 'Chamada de Voz';
            if (statusSubtitle) statusSubtitle.textContent = nomeContato;
            const btnEnd = document.getElementById('btn-call-end');
            const btnAccept = document.getElementById('btn-call-accept');
            const btnReject = document.getElementById('btn-call-reject');
            if (btnEnd) btnEnd.style.display = 'none';
            if (btnAccept) btnAccept.style.display = 'flex';
            if (btnReject) btnReject.style.display = 'flex';
            const btnMute2 = document.getElementById('btn-call-mute');
            const btnToggleVideo2 = document.getElementById('btn-call-toggle-video');
            if (btnMute2) btnMute2.style.display = 'none';
            if (btnToggleVideo2) btnToggleVideo2.style.display = 'none';
        } else if (tipo === 'active') {
            const statusDiv = document.getElementById('chat-call-status');
            const infoDiv = document.getElementById('chat-call-info');
            if (statusDiv) statusDiv.style.display = 'none';
            if (infoDiv) infoDiv.style.display = 'block';
            if (nomeInfo) nomeInfo.textContent = nomeContato;
            const btnMute3 = document.getElementById('btn-call-mute');
            const btnToggleVideo3 = document.getElementById('btn-call-toggle-video');
            const btnEnd3 = document.getElementById('btn-call-end');
            const btnAccept3 = document.getElementById('btn-call-accept');
            const btnReject3 = document.getElementById('btn-call-reject');
            if (btnMute3) btnMute3.style.display = 'flex';
            if (btnToggleVideo3) btnToggleVideo3.style.display = this.isVideoCall ? 'flex' : 'none';
            if (btnEnd3) btnEnd3.style.display = 'flex';
            if (btnAccept3) btnAccept3.style.display = 'none';
            if (btnReject3) btnReject3.style.display = 'none';
            
            // Se for chamada de voz e não houver vídeo remoto, mostrar avatar
            if (!this.isVideoCall && avatarVoice) {
                avatarVoice.style.display = 'flex';
                // Garantir que o avatar está configurado
                const avatarImg = document.getElementById('chat-call-avatar-img');
                const avatarInicial = document.getElementById('chat-call-avatar-inicial');
                const avatarContato = document.getElementById('chat-avatar-contato');
                
                if (avatarContato) {
                    const img = avatarContato.querySelector('img');
                    const inicial = avatarContato.querySelector('span');
                    if (img && img.src && avatarImg) {
                        avatarImg.src = img.src;
                        avatarImg.style.display = 'block';
                        if (avatarInicial) avatarInicial.style.display = 'none';
                    } else if (inicial && inicial.textContent && avatarInicial) {
                        avatarInicial.textContent = inicial.textContent;
                        avatarInicial.style.display = 'block';
                        if (avatarImg) avatarImg.style.display = 'none';
                    }
                }
            }
            
            // Se for chamada de vídeo, verificar se o vídeo remoto está sendo exibido
            if (this.isVideoCall) {
                const remoteVideo = document.getElementById('chat-call-video-remote-stream');
                const videoLocalContainer = document.getElementById('chat-call-video-local');
                
                console.log('🔍 Verificando vídeo remoto no estado active:');
                console.log('  - remoteVideo existe:', !!remoteVideo);
                console.log('  - remoteVideo.srcObject:', !!remoteVideo?.srcObject);
                console.log('  - remoteVideo.style.display:', remoteVideo?.style.display);
                console.log('  - this.remoteStream existe:', !!this.remoteStream);
                console.log('  - hasVideoTracks:', this.remoteStream?.getVideoTracks().length > 0);
                
                // Verificar se há stream remoto com tracks de vídeo
                const hasVideoTracks = this.remoteStream && this.remoteStream.getVideoTracks().length > 0;
                
                // Se houver vídeo remoto com tracks de vídeo, SEMPRE exibir
                // Verificar tanto srcObject quanto remoteStream (pode estar configurado mas não atribuído ainda)
                const videoDisponivel = (remoteVideo && remoteVideo.srcObject) || (remoteVideo && this.remoteStream && hasVideoTracks);
                
                if (videoDisponivel && hasVideoTracks) {
                    console.log('✅ Vídeo remoto disponível, FORÇANDO exibição...');
                    
                    // Se o srcObject não estiver configurado, configurar agora
                    if (remoteVideo && !remoteVideo.srcObject && this.remoteStream) {
                        console.log('📹 Configurando srcObject do vídeo remoto...');
                        remoteVideo.srcObject = this.remoteStream;
                    }
                    
                    // Garantir que o vídeo está visível
                    remoteVideo.style.display = 'block';
                    remoteVideo.style.visibility = 'visible';
                    remoteVideo.style.opacity = '1';
                    
                    // Garantir que o container está visível
                    const remoteContainer = document.getElementById('chat-call-video-remote');
                    if (remoteContainer) {
                        remoteContainer.style.display = 'flex';
                    }
                    
                    // Esconder avatar e status
                    if (avatarVoice) avatarVoice.style.display = 'none';
                    const statusDiv = document.getElementById('chat-call-status');
                    if (statusDiv) statusDiv.style.display = 'none';
                    
                    // Tentar reproduzir se não estiver reproduzindo
                    if (remoteVideo.paused) {
                        console.log('▶️ Vídeo pausado, tentando reproduzir...');
                        remoteVideo.play().catch(e => {
                            console.error('❌ Erro ao reproduzir:', e);
                        });
                    }
                    
                    // Garantir que o vídeo local está visível
                    if (videoLocalContainer && this.localStream) {
                        videoLocalContainer.style.display = 'block';
                    }
                } else {
                    // Se não houver vídeo remoto ou não estiver visível, mostrar avatar
                    console.log('⚠️ Vídeo remoto não disponível ainda, mostrando avatar');
                    if (avatarVoice) {
                        avatarVoice.style.display = 'flex';
                        const avatarImg = document.getElementById('chat-call-avatar-img');
                        const avatarInicial = document.getElementById('chat-call-avatar-inicial');
                        const avatarContato = document.getElementById('chat-avatar-contato');
                        
                        if (avatarContato) {
                            const img = avatarContato.querySelector('img');
                            const inicial = avatarContato.querySelector('span');
                            if (img && img.src && avatarImg) {
                                avatarImg.src = img.src;
                                avatarImg.style.display = 'block';
                                if (avatarInicial) avatarInicial.style.display = 'none';
                            } else if (inicial && inicial.textContent && avatarInicial) {
                                avatarInicial.textContent = inicial.textContent;
                                avatarInicial.style.display = 'block';
                                if (avatarImg) avatarImg.style.display = 'none';
                            }
                        }
                    }
                    
                    // Mostrar status "Aguardando resposta..." apenas se não houver stream
                    if (!this.remoteStream) {
                        const statusDiv = document.getElementById('chat-call-status');
                        if (statusDiv) {
                            statusDiv.style.display = 'block';
                            const statusTitle = document.getElementById('chat-call-status-title');
                            if (statusTitle) statusTitle.textContent = 'Aguardando resposta...';
                        }
                    }
                }
            }
        }
        
        console.log('✅ mostrarInterfaceChamada concluído com sucesso!');
    }

    async aceitarChamada() {
        try {
            // Buscar dados da chamada pendente
            const response = await fetch(`/militares/api/chat/${this.chatWidget.currentChatId}/chamada/pendente/`);
            if (!response.ok) {
                throw new Error('Erro ao buscar chamada');
            }
            
            const data = await response.json();
            if (!data.success || !data.chamada_pendente) {
                throw new Error('Chamada não encontrada');
            }
            
            const chamada = data.chamada_pendente;
            this.currentCallId = chamada.id;
            this.isVideoCall = chamada.tipo === 'video';
            
            // Verificar se getUserMedia está disponível
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('getUserMedia não está disponível. Use HTTPS ou localhost.');
            }
            
            // Solicitar acesso à câmera/microfone
            const constraints = {
                audio: true,
                video: this.isVideoCall ? {
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                } : false
            };
            
            this.localStream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Exibir vídeo local se for chamada de vídeo
            if (this.isVideoCall && this.localStream.getVideoTracks().length > 0) {
                const localVideo = document.getElementById('chat-call-video-local-stream');
                localVideo.srcObject = this.localStream;
                document.getElementById('chat-call-video-local').style.display = 'block';
            }
            
            // Criar peer connection
            await this.criarPeerConnection();
            
            // Adicionar tracks locais
            this.localStream.getTracks().forEach(track => {
                this.peerConnection.addTrack(track, this.localStream);
            });
            
            // Processar oferta recebida
            if (chamada.oferta) {
                await this.processarOfertaAoAceitar(chamada.oferta);
            }
            
            // Criar resposta
            const answer = await this.peerConnection.createAnswer();
            await this.peerConnection.setLocalDescription(answer);
            
            // Enviar resposta
            await this.enviarRespostaChamada(answer);
            
            this.mostrarInterfaceChamada('active');
            
        } catch (error) {
            console.error('Erro ao aceitar chamada:', error);
            this.tratarErroPermissao(error, this.isVideoCall);
            this.encerrarChamada();
        }
    }

    async rejeitarChamada() {
        if (this.currentCallId && this.chatWidget.currentChatId) {
            try {
                const csrftoken = this.obterCSRFToken();
                await fetch(`/militares/api/chat/${this.chatWidget.currentChatId}/chamada/${this.currentCallId}/rejeitar/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrftoken
                    },
                    credentials: 'same-origin'
                });
            } catch (error) {
                console.error('Erro ao rejeitar chamada:', error);
            }
        }
        this.encerrarChamada();
    }

    async encerrarChamada() {
        // Notificar servidor se necessário
        if (this.currentCallId && this.chatWidget.currentChatId && this.isCallActive) {
            try {
                const csrftoken = this.obterCSRFToken();
                const duracao = this.callStartTime ? Math.floor((Date.now() - this.callStartTime) / 1000) : null;
                await fetch(`/militares/api/chat/${this.chatWidget.currentChatId}/chamada/${this.currentCallId}/finalizar/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrftoken
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({ duracao: duracao })
                });
            } catch (error) {
                console.error('Erro ao finalizar chamada:', error);
            }
        } else if (this.currentCallId && this.chatWidget.currentChatId) {
            // Se não estava ativa, pode ser cancelamento
            try {
                const csrftoken = this.obterCSRFToken();
                await fetch(`/militares/api/chat/${this.chatWidget.currentChatId}/chamada/${this.currentCallId}/cancelar/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrftoken
                    },
                    credentials: 'same-origin'
                });
            } catch (error) {
                console.error('Erro ao cancelar chamada:', error);
            }
        }
        
        // Parar polling
        if (this.pollingRespostaTimer) {
            clearInterval(this.pollingRespostaTimer);
            this.pollingRespostaTimer = null;
        }
        
        // Parar streams
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }
        
        if (this.remoteStream) {
            this.remoteStream.getTracks().forEach(track => track.stop());
            this.remoteStream = null;
        }
        
        // Fechar peer connection
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }
        
        // Limpar vídeos
        const localVideo = document.getElementById('chat-call-video-local-stream');
        const remoteVideo = document.getElementById('chat-call-video-remote-stream');
        if (localVideo) {
            localVideo.srcObject = null;
            document.getElementById('chat-call-video-local').style.display = 'none';
        }
        if (remoteVideo) {
            remoteVideo.srcObject = null;
            remoteVideo.style.display = 'none';
        }
        
        // Esconder overlay
        const overlay = document.getElementById('chat-call-overlay');
        overlay.classList.remove('active');
        
        // Resetar estados
        this.isCallActive = false;
        this.currentCallId = null;
        this.pararTimer();
        document.getElementById('chat-call-info').style.display = 'none';
        document.getElementById('chat-call-status').style.display = 'block';
        
        // Reiniciar polling de chamadas pendentes
        this.iniciarPollingChamadasPendentes();
    }

    toggleMute() {
        if (this.localStream) {
            this.isMuted = !this.isMuted;
            this.localStream.getAudioTracks().forEach(track => {
                track.enabled = !this.isMuted;
            });
            const btn = document.getElementById('btn-call-mute');
            btn.classList.toggle('active', this.isMuted);
        }
    }

    toggleVideo() {
        if (this.localStream && this.isVideoCall) {
            this.isVideoEnabled = !this.isVideoEnabled;
            this.localStream.getVideoTracks().forEach(track => {
                track.enabled = this.isVideoEnabled;
            });
            const btn = document.getElementById('btn-call-toggle-video');
            btn.classList.toggle('active', !this.isVideoEnabled);
        }
    }

    iniciarTimer() {
        this.callStartTime = Date.now();
        this.callTimer = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.callStartTime) / 1000);
            const minutos = Math.floor(elapsed / 60);
            const segundos = elapsed % 60;
            const tempo = `${String(minutos).padStart(2, '0')}:${String(segundos).padStart(2, '0')}`;
            document.getElementById('chat-call-tempo').textContent = tempo;
        }, 1000);
    }

    pararTimer() {
        if (this.callTimer) {
            clearInterval(this.callTimer);
            this.callTimer = null;
        }
        this.callStartTime = null;
        document.getElementById('chat-call-tempo').textContent = '00:00';
    }

    // Métodos para comunicação via polling
    async enviarOfertaChamada(offer) {
        try {
            const csrftoken = this.obterCSRFToken();
            
            if (!csrftoken) {
                console.error('CSRF token não encontrado');
                alert('Erro: Token de segurança não encontrado. Recarregue a página.');
                return;
            }
            
            // Converter a oferta SDP para objeto simples
            const ofertaData = {
                type: offer.type,
                sdp: offer.sdp
            };
            
            const requestBody = {
                tipo: this.isVideoCall ? 'video' : 'voz',
                oferta: ofertaData  // Enviar como objeto, não string dupla
            };
            
            console.log('Enviando chamada:', {
                chatId: this.chatWidget.currentChatId,
                tipo: requestBody.tipo,
                ofertaType: ofertaData.type,
                csrfToken: csrftoken ? csrftoken.substring(0, 10) + '...' : 'NÃO ENCONTRADO'
            });
            
            console.log('Request body:', JSON.stringify(requestBody, null, 2));
            console.log('URL:', `/militares/api/chat/${this.chatWidget.currentChatId}/chamada/iniciar/`);
            
            const response = await fetch(`/militares/api/chat/${this.chatWidget.currentChatId}/chamada/iniciar/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                },
                credentials: 'same-origin',
                body: JSON.stringify(requestBody)
            });
            
            // IMPORTANTE: Ler a resposta como texto primeiro
            const responseText = await response.text();
            
            console.log('═══════════════════════════════════════');
            console.log('🔴 ERRO 400 - DETALHES DA RESPOSTA');
            console.log('═══════════════════════════════════════');
            console.log('Status:', response.status);
            console.log('Status Text:', response.statusText);
            console.log('Response Text (COMPLETO):', responseText);
            console.log('═══════════════════════════════════════');
            
            let responseData;
            try {
                responseData = JSON.parse(responseText);
                console.log('Response Data (parseado):', responseData);
            } catch (e) {
                console.error('❌ Erro ao fazer parse JSON:', e);
                console.error('❌ Texto que causou erro:', responseText);
                responseData = { 
                    error: 'Erro ao processar resposta do servidor', 
                    raw: responseText,
                    parseError: e.message
                };
            }
            
            if (!response.ok) {
                console.error('═══════════════════════════════════════');
                console.error('❌ ERRO NA RESPOSTA DA API');
                console.error('═══════════════════════════════════════');
                console.error('Status:', response.status);
                console.error('Status Text:', response.statusText);
                console.error('Data:', responseData);
                
                if (responseData.details) {
                    console.error('═══════════════════════════════════════');
                    console.error('📋 DETALHES DO ERRO (TRACEBACK):');
                    console.error('═══════════════════════════════════════');
                    console.error(responseData.details);
                }
                
                let errorMessage = responseData.error || 'Erro desconhecido';
                alert(`❌ Erro ao iniciar chamada (${response.status})\n\n${errorMessage}\n\nVerifique o console (F12) para mais detalhes.`);
                this.encerrarChamada();
                return;
            }
            
            if (responseData.success) {
                console.log('Chamada iniciada com sucesso:', responseData.chamada_id);
                this.currentCallId = responseData.chamada_id;
                // Iniciar polling para verificar resposta
                this.iniciarPollingResposta();
            } else {
                console.error('Chamada não foi iniciada:', responseData);
                alert(`Erro: ${responseData.error || 'Não foi possível iniciar a chamada'}`);
                this.encerrarChamada();
            }
        } catch (error) {
            console.error('Erro ao enviar oferta:', error);
            alert('Erro ao iniciar chamada. Verifique o console para mais detalhes.');
            this.encerrarChamada();
        }
    }
    
    iniciarPollingResposta() {
        if (this.pollingRespostaTimer) {
            clearInterval(this.pollingRespostaTimer);
        }
        
        console.log('🔄 Iniciando polling de resposta para chamada:', this.currentCallId);
        
        this.pollingRespostaTimer = setInterval(async () => {
            if (!this.currentCallId || !this.chatWidget.currentChatId) {
                console.log('⚠️ Sem currentCallId ou chatId, parando polling');
                clearInterval(this.pollingRespostaTimer);
                return;
            }
            
            try {
                console.log('🔍 Verificando status da chamada:', this.currentCallId);
                const response = await fetch(`/militares/api/chat/${this.chatWidget.currentChatId}/chamada/${this.currentCallId}/status/`);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('📊 Status da chamada:', {
                        status: data.chamada?.status,
                        temResposta: !!data.chamada?.resposta,
                        resposta: data.chamada?.resposta
                    });
                    
                    if (data.success && data.chamada) {
                        if (data.chamada.status === 'EM_ANDAMENTO' && data.chamada.resposta) {
                            console.log('✅ Resposta recebida! Processando...');
                            await this.processarResposta(data.chamada.resposta);
                            clearInterval(this.pollingRespostaTimer);
                            this.pollingRespostaTimer = null;
                        } else if (data.chamada.status === 'REJEITADA' || data.chamada.status === 'CANCELADA') {
                            console.log('❌ Chamada rejeitada ou cancelada');
                            this.encerrarChamada();
                            clearInterval(this.pollingRespostaTimer);
                            this.pollingRespostaTimer = null;
                        } else {
                            console.log('⏳ Aguardando resposta... Status:', data.chamada.status);
                        }
                    }
                } else {
                    console.warn('⚠️ Erro ao verificar status:', response.status);
                }
            } catch (error) {
                console.error('❌ Erro ao verificar status:', error);
            }
        }, 1000); // Polling a cada 1 segundo
    }
    
    async processarResposta(resposta) {
        console.log('═══════════════════════════════════════');
        console.log('📥 PROCESSANDO RESPOSTA SDP');
        console.log('═══════════════════════════════════════');
        console.log('Resposta recebida:', resposta);
        console.log('PeerConnection existe:', !!this.peerConnection);
        
        if (!this.peerConnection) {
            console.error('❌ PeerConnection não existe!');
            return;
        }
        
        if (!resposta || !resposta.type || !resposta.sdp) {
            console.error('❌ Resposta inválida:', resposta);
            return;
        }
        
        try {
            console.log('✅ Configurando remote description (answer recebido)...');
            console.log('Estado atual do PeerConnection:', this.peerConnection.signalingState);
            
            // Verificar o estado atual
            const currentState = this.peerConnection.signalingState;
            if (currentState === 'have-local-offer') {
                // Temos um offer local, recebemos um answer - apenas configurar remote description
                await this.peerConnection.setRemoteDescription(new RTCSessionDescription(resposta));
                console.log('✅ Remote description (answer) configurado com sucesso!');
                console.log('Novo estado:', this.peerConnection.signalingState);
            } else {
                console.warn('⚠️ Estado inesperado:', currentState);
                // Tentar configurar mesmo assim
                await this.peerConnection.setRemoteDescription(new RTCSessionDescription(resposta));
                console.log('✅ Remote description configurado (forçado)');
            }
            
            // NÃO criar answer aqui - já temos o answer do outro lado
            // A conexão WebRTC deve ser estabelecida agora
        } catch (error) {
            console.error('❌ Erro ao processar resposta:', error);
            console.error('Stack:', error.stack);
        }
    }

    async enviarRespostaChamada(answer) {
        try {
            console.log('📤 Enviando resposta (answer) para o servidor...');
            const csrftoken = this.obterCSRFToken();
            
            const answerData = {
                type: answer.type,
                sdp: answer.sdp
            };
            
            const response = await fetch(`/militares/api/chat/${this.chatWidget.currentChatId}/chamada/aceitar/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    chamada_id: this.currentCallId,
                    resposta: answerData  // Enviar como objeto, não string
                })
            });
            
            console.log('📥 Resposta do servidor:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('📥 Dados recebidos:', data);
                
                if (data.success && data.oferta) {
                    console.log('✅ Oferta recebida, processando...');
                    // Processar oferta recebida (caso o outro lado também tenha enviado)
                    await this.processarOferta(data.oferta);
                }
            } else {
                const errorText = await response.text();
                console.error('❌ Erro ao enviar resposta:', response.status, errorText);
            }
        } catch (error) {
            console.error('❌ Erro ao enviar resposta:', error);
            this.encerrarChamada();
        }
    }
    
    async processarOferta(oferta) {
        console.log('═══════════════════════════════════════');
        console.log('📥 PROCESSANDO OFERTA');
        console.log('═══════════════════════════════════════');
        console.log('Oferta recebida:', oferta);
        console.log('PeerConnection existe:', !!this.peerConnection);
        
        if (!this.peerConnection) {
            console.error('❌ PeerConnection não existe!');
            return;
        }
        
        if (!oferta || !oferta.type || !oferta.sdp) {
            console.error('❌ Oferta inválida:', oferta);
            return;
        }
        
        try {
            console.log('✅ Configurando remote description (oferta)...');
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(oferta));
            console.log('✅ Remote description configurado com sucesso!');
            
            // Após configurar remote description, criar answer
            console.log('✅ Criando answer...');
            const answer = await this.peerConnection.createAnswer();
            await this.peerConnection.setLocalDescription(answer);
            console.log('✅ Answer criado:', answer.type);
            
            // Enviar answer
            console.log('✅ Enviando answer...');
            await this.enviarRespostaChamada(answer);
        } catch (error) {
            console.error('❌ Erro ao processar oferta:', error);
            console.error('Stack:', error.stack);
        }
    }

    enviarIceCandidate(candidate) {
        // Em produção, enviar via WebSocket
        console.log('ICE candidate:', candidate);
    }

    async verificarChamadasPendentes() {
        if (this.isCallActive) {
            console.log('⚠️ Verificação de chamadas pendentes: chamada já ativa');
            return;
        }
        
        try {
            let url;
            if (this.chatWidget && this.chatWidget.currentChatId) {
                // Se há um chat aberto, verificar apenas esse chat
                console.log('🔍 Verificando chamadas pendentes para chat:', this.chatWidget.currentChatId);
                url = `/militares/api/chat/${this.chatWidget.currentChatId}/chamada/pendente/`;
            } else {
                // Se não há chat aberto, verificar todos os chats
                console.log('🔍 Verificando chamadas pendentes em todos os chats...');
                url = `/militares/api/chat/chamada/pendente/todas/`;
            }
            
            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('📊 Resposta de chamadas pendentes:', {
                    success: data.success,
                    temChamadaPendente: !!data.chamada_pendente,
                    chamadaId: data.chamada_pendente?.id,
                    chatId: data.chamada_pendente?.chat_id,
                    tipo: data.chamada_pendente?.tipo
                });
                
                if (data.success && data.chamada_pendente) {
                    console.log('📞 Chamada pendente encontrada! Exibindo interface...');
                    // Se a chamada é de outro chat, abrir esse chat primeiro
                    if (data.chamada_pendente.chat_id && this.chatWidget) {
                        const chatIdAtual = this.chatWidget.currentChatId;
                        if (!chatIdAtual || chatIdAtual !== String(data.chamada_pendente.chat_id)) {
                            console.log(`📂 Abrindo chat ${data.chamada_pendente.chat_id} para exibir chamada pendente...`);
                            // Abrir o chat se o widget tiver essa funcionalidade
                            if (this.chatWidget.abrirChat) {
                                await this.chatWidget.abrirChat(data.chamada_pendente.chat_id);
                            }
                        }
                    }
                    this.mostrarChamadaEntrante(data.chamada_pendente);
                }
            } else {
                console.warn('⚠️ Erro ao verificar chamadas pendentes:', response.status);
            }
        } catch (error) {
            console.error('❌ Erro ao verificar chamadas pendentes:', error);
        }
    }
    
    iniciarPollingChamadasPendentes() {
        if (this.pollingChamadaPendenteTimer) {
            clearInterval(this.pollingChamadaPendenteTimer);
        }
        
        console.log('🔄 Iniciando polling de chamadas pendentes...');
        this.pollingChamadaPendenteTimer = setInterval(() => {
            this.verificarChamadasPendentes();
        }, 2000); // Verificar a cada 2 segundos
        
        // Verificar imediatamente também
        this.verificarChamadasPendentes();
    }
    
    pararPollingChamadasPendentes() {
        if (this.pollingChamadaPendenteTimer) {
            clearInterval(this.pollingChamadaPendenteTimer);
            this.pollingChamadaPendenteTimer = null;
        }
    }

    async mostrarChamadaEntrante(chamada) {
        this.isVideoCall = chamada.tipo === 'video';
        this.currentCallId = chamada.id;
        this.mostrarInterfaceChamada('incoming');
        
        // Processar oferta recebida
        if (chamada.oferta) {
            // A oferta será processada quando o usuário aceitar
        }
    }
    
    async processarOfertaAoAceitar(oferta) {
        console.log('═══════════════════════════════════════');
        console.log('📥 PROCESSANDO OFERTA AO ACEITAR');
        console.log('═══════════════════════════════════════');
        console.log('Oferta recebida:', oferta);
        console.log('PeerConnection existe:', !!this.peerConnection);
        
        if (!this.peerConnection) {
            console.error('❌ PeerConnection não existe!');
            return;
        }
        
        if (!oferta || !oferta.type || !oferta.sdp) {
            console.error('❌ Oferta inválida:', oferta);
            return;
        }
        
        try {
            console.log('✅ Configurando remote description (oferta)...');
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(oferta));
            console.log('✅ Remote description configurado com sucesso!');
        } catch (error) {
            console.error('❌ Erro ao processar oferta:', error);
            console.error('Stack:', error.stack);
        }
    }

    obterCSRFToken() {
        // Tentar usar token global primeiro
        if (typeof window.csrfToken !== 'undefined') {
            return window.csrfToken;
        }
        // Fallback para buscar do formulário
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

