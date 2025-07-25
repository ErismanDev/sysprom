// Configuração específica do CKEditor 5 para Voto Proferido
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar o CKEditor 5 carregar
    if (typeof ClassicEditor !== 'undefined') {
        // Configuração para o campo voto_proferido
        const votoEditor = document.querySelector('textarea[data-config-name="voto_proferido_config"]');
        if (votoEditor) {
            ClassicEditor
                .create(votoEditor, {
                    // Configuração da barra de ferramentas
                    toolbar: {
                        items: [
                            'heading',
                            '|',
                            'bold',
                            'italic',
                            'underline',
                            'strikethrough',
                            '|',
                            'bulletedList',
                            'numberedList',
                            '|',
                            'indent',
                            'outdent',
                            '|',
                            'link',
                            'blockQuote',
                            'insertTable',
                            '|',
                            'undo',
                            'redo'
                        ]
                    },
                    // Configuração do cabeçalho
                    heading: {
                        options: [
                            { model: 'paragraph', title: 'Parágrafo', class: 'ck-heading_paragraph' },
                            { model: 'heading1', view: 'h1', title: 'Título 1', class: 'ck-heading_heading1' },
                            { model: 'heading2', view: 'h2', title: 'Título 2', class: 'ck-heading_heading2' },
                            { model: 'heading3', view: 'h3', title: 'Título 3', class: 'ck-heading_heading3' }
                        ]
                    },
                    // Configuração da tabela
                    table: {
                        contentToolbar: [
                            'tableColumn',
                            'tableRow',
                            'mergeTableCells'
                        ]
                    },
                    // Configuração do link
                    link: {
                        decorators: {
                            addTargetToExternalLinks: true,
                            defaultProtocol: 'https://'
                        }
                    },
                    // Configuração do placeholder
                    placeholder: 'Digite aqui o texto do voto que você proferiu durante a sessão...',
                    // Configuração da altura mínima
                    height: '400px',
                    // Configuração do idioma
                    language: 'pt-br',
                    // Configuração de atalhos de teclado
                    keystrokes: {
                        'Ctrl+B': 'bold',
                        'Ctrl+I': 'italic',
                        'Ctrl+U': 'underline',
                        'Ctrl+Z': 'undo',
                        'Ctrl+Y': 'redo',
                        'Tab': 'indent',
                        'Shift+Tab': 'outdent'
                    }
                })
                .then(editor => {
                    console.log('Editor CKEditor 5 para Voto Proferido inicializado com sucesso!');
                    
                    // Configurar estatísticas em tempo real
                    const wordCountElement = document.getElementById('wordCount');
                    const charCountElement = document.getElementById('charCount');
                    
                    if (wordCountElement && charCountElement) {
                        editor.model.document.on('change:data', () => {
                            const data = editor.getData();
                            const textContent = editor.getData().replace(/<[^>]*>/g, '');
                            
                            // Contar palavras
                            const words = textContent.trim() ? textContent.trim().split(/\s+/).length : 0;
                            wordCountElement.textContent = `${words} palavras`;
                            
                            // Contar caracteres
                            charCountElement.textContent = `${textContent.length} caracteres`;
                        });
                    }
                    
                    // Configurar auto-save
                    let autoSaveInterval = setInterval(() => {
                        const data = editor.getData();
                        if (data.trim()) {
                            const lastSaveElement = document.getElementById('lastSave');
                            if (lastSaveElement) {
                                const now = new Date();
                                const timeString = now.toLocaleTimeString('pt-BR', { 
                                    hour: '2-digit', 
                                    minute: '2-digit' 
                                });
                                lastSaveElement.textContent = `Último save: ${timeString}`;
                            }
                        }
                    }, 30000); // Auto-save a cada 30 segundos
                    
                    // Configurar tempo gasto
                    let startTime = new Date();
                    const timeSpentElement = document.getElementById('timeSpent');
                    
                    if (timeSpentElement) {
                        setInterval(() => {
                            const agora = new Date();
                            const diff = Math.floor((agora - startTime) / 1000);
                            const minutos = Math.floor(diff / 60);
                            const segundos = diff % 60;
                            timeSpentElement.textContent = `Tempo: ${minutos.toString().padStart(2, '0')}:${segundos.toString().padStart(2, '0')}`;
                        }, 1000);
                    }
                })
                .catch(error => {
                    console.error('Erro ao inicializar o CKEditor 5:', error);
                });
        }
    } else {
        console.log('CKEditor 5 não encontrado. Aguardando...');
        // Tentar novamente após um delay
        setTimeout(() => {
            if (typeof ClassicEditor !== 'undefined') {
                location.reload();
            }
        }, 1000);
    }
}); 