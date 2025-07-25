let autoSaveTimer;
let startTime = new Date();
let lastSaved = null;
let currentZoom = 100;

// Funções principais do SEI
function saveDocument() {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        const content = editor.getData();
        
        // Simular salvamento
        showNotification('Documento salvo com sucesso!', 'success');
        updateLastSaved();
    }
}

function signDocument() {
    showNotification('Funcionalidade de assinatura será implementada em breve.', 'info');
}

// Funções de formatação SEI
function formatText(format) {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        editor.execute(format);
    }
}

function increaseFontSize() {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        const currentSize = parseInt(editor.getData().match(/font-size:\s*(\d+)px/)?.[1] || '12');
        editor.execute('fontSize', { value: (currentSize + 2).toString() });
    }
}

function decreaseFontSize() {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        const currentSize = parseInt(editor.getData().match(/font-size:\s*(\d+)px/)?.[1] || '12');
        if (currentSize > 8) {
            editor.execute('fontSize', { value: (currentSize - 2).toString() });
        }
    }
}

function changeZoom(value) {
    currentZoom = parseInt(value);
    const editorElement = document.querySelector('.ck-editor__editable');
    if (editorElement) {
        editorElement.style.transform = `scale(${currentZoom / 100})`;
        editorElement.style.transformOrigin = 'top left';
    }
}

// Funções de inserção SEI
function insertTable() {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        editor.execute('insertTable', { rows: 3, columns: 3 });
    }
}

function insertList(type) {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        if (type === 'bulleted') {
            editor.execute('bulletedList');
        } else {
            editor.execute('numberedList');
        }
    }
}

function insertQuote() {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        editor.execute('blockQuote');
    }
}

function insertLink() {
    const url = prompt('Digite a URL:');
    if (url && window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        editor.execute('link', url);
    }
}

function insertImage() {
    const url = prompt('Digite a URL da imagem:');
    if (url && window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        editor.execute('image', { src: url });
    }
}

function insertAutoText() {
    const autoTexts = [
        'Aos [[dia]] dias do mês de [[mês]] do ano de [[ano]], às [[horário]] horas',
        'Compareceram os seguintes membros:',
        'Foi aprovada por unanimidade',
        'Nada mais havendo a tratar',
        'Lavrei a presente ata que vai por todos assinada'
    ];
    
    const selected = prompt('Selecione o texto automático:\n1. Data e hora\n2. Membros presentes\n3. Aprovação\n4. Encerramento\n5. Assinatura');
    
    if (selected && window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        const index = parseInt(selected) - 1;
        if (index >= 0 && index < autoTexts.length) {
            editor.execute('input', { text: autoTexts[index] });
        }
    }
}

function insertJustifiedText() {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        editor.execute('alignment', { value: 'justify' });
    }
}

function indentText() {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        editor.execute('indent');
    }
}

function outdentText() {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        editor.execute('outdent');
    }
}

function insertSpecialCharacters() {
    const chars = ['©', '®', '™', '€', '£', '¥', '¢', '§', '¶', '†', '‡', '•', '◦', '‣', '⁃', '⁌', '⁍'];
    const selected = prompt('Selecione um caractere especial:\n' + chars.map((c, i) => `${i + 1}. ${c}`).join('\n'));
    
    if (selected && window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        const index = parseInt(selected) - 1;
        if (index >= 0 && index < chars.length) {
            editor.execute('input', { text: chars[index] });
        }
    }
}

function insertSymbols() {
    const symbols = ['±', '∞', '≈', '≠', '≤', '≥', '×', '÷', '√', '∑', '∏', '∫', '∂', '∆', '∇', '∈', '∉', '∋', '∌'];
    const selected = prompt('Selecione um símbolo:\n' + symbols.map((s, i) => `${i + 1}. ${s}`).join('\n'));
    
    if (selected && window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        const index = parseInt(selected) - 1;
        if (index >= 0 && index < symbols.length) {
            editor.execute('input', { text: symbols[index] });
        }
    }
}

function insertCurrency() {
    const currencies = ['R$', '$', '€', '£', '¥', '₽', '₹', '₩', '₪', '₦', '₨', '₫', '₭', '₮', '₯', '₰', '₱', '₲', '₳', '₴', '₵'];
    const selected = prompt('Selecione uma moeda:\n' + currencies.map((c, i) => `${i + 1}. ${c}`).join('\n'));
    
    if (selected && window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        const index = parseInt(selected) - 1;
        if (index >= 0 && index < currencies.length) {
            editor.execute('input', { text: currencies[index] });
        }
    }
}

function voiceInput() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'pt-BR';
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            if (window.editors && Object.keys(window.editors).length > 0) {
                const editor = Object.values(window.editors)[0];
                editor.execute('input', { text: transcript });
            }
        };
        
        recognition.start();
        showNotification('Fale agora...', 'info');
    } else {
        showNotification('Reconhecimento de voz não suportado neste navegador.', 'error');
    }
}

// Funções utilitárias
function undoAction() {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        editor.execute('undo');
    }
}

function redoAction() {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        editor.execute('redo');
    }
}

function alignText(alignment) {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        editor.execute('alignment', { value: alignment });
    }
}

function insertVariable(variable) {
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        editor.execute('input', { text: variable });
    }
}

function toggleVariables() {
    const content = document.getElementById('variablesContent');
    const icon = document.querySelector('.btn-toggle i');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.className = 'fas fa-chevron-down';
    } else {
        content.style.display = 'none';
        icon.className = 'fas fa-chevron-up';
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 10px 20px;
        border-radius: 4px;
        color: white;
        font-size: 14px;
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    if (type === 'success') notification.style.backgroundColor = '#28a745';
    else if (type === 'error') notification.style.backgroundColor = '#dc3545';
    else notification.style.backgroundColor = '#17a2b8';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function updateLastSaved() {
    const now = new Date();
    lastSaved = now;
    const timeString = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    console.log(`Documento salvo às ${timeString}`);
}

// Inicializar CKEditor
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        if (window.editors && Object.keys(window.editors).length > 0) {
            const editor = Object.values(window.editors)[0];
            console.log('Editor SEI inicializado com sucesso');
        } else {
            const textarea = document.querySelector('textarea[name="conteudo"]');
            if (textarea) {
                console.log('Inicializando editor SEI...');
                
                if (typeof ClassicEditor === 'undefined') {
                    const script = document.createElement('script');
                    script.src = 'https://cdn.ckeditor.com/ckeditor5/40.0.0/classic/ckeditor.js';
                    script.onload = function() {
                        initializeSEIEditor();
                    };
                    document.head.appendChild(script);
                } else {
                    initializeSEIEditor();
                }
            }
        }
    }, 1000);
});

function initializeSEIEditor() {
    const textarea = document.querySelector('textarea[name="conteudo"]');
    if (textarea && typeof ClassicEditor !== 'undefined') {
        ClassicEditor
            .create(textarea, {
                language: 'pt-br',
                toolbar: {
                    items: [
                        'heading',
                        '|',
                        'bold',
                        'italic',
                        'underline',
                        'strikethrough',
                        'subscript',
                        'superscript',
                        '|',
                        'fontSize',
                        'fontFamily',
                        'fontColor',
                        'fontBackgroundColor',
                        '|',
                        'alignment',
                        '|',
                        'numberedList',
                        'bulletedList',
                        '|',
                        'indent',
                        'outdent',
                        '|',
                        'link',
                        'blockQuote',
                        'insertTable',
                        'mediaEmbed',
                        'imageUpload',
                        '|',
                        'horizontalLine',
                        'pageBreak',
                        '|',
                        'specialCharacters',
                        '|',
                        'findAndReplace',
                        '|',
                        'undo',
                        'redo',
                        '|',
                        'sourceEditing'
                    ]
                },
                heading: {
                    options: [
                        { model: 'paragraph', title: 'Parágrafo', class: 'ck-heading_paragraph' },
                        { model: 'heading1', view: 'h1', title: 'Título 1', class: 'ck-heading_heading1' },
                        { model: 'heading2', view: 'h2', title: 'Título 2', class: 'ck-heading_heading2' },
                        { model: 'heading3', view: 'h3', title: 'Título 3', class: 'ck-heading_heading3' },
                        { model: 'heading4', view: 'h4', title: 'Título 4', class: 'ck-heading_heading4' }
                    ]
                },
                fontSize: {
                    options: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72]
                },
                fontFamily: {
                    options: [
                        'default',
                        'Arial, Helvetica, sans-serif',
                        'Courier New, Courier, monospace',
                        'Georgia, serif',
                        'Lucida Sans Unicode, Lucida Grande, sans-serif',
                        'Tahoma, Geneva, sans-serif',
                        'Times New Roman, Times, serif',
                        'Trebuchet MS, Helvetica, sans-serif',
                        'Verdana, Geneva, sans-serif'
                    ]
                },
                alignment: {
                    options: ['left', 'center', 'right', 'justify']
                },
                table: {
                    contentToolbar: ['tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties']
                }
            })
            .then(editor => {
                window.editors = window.editors || {};
                window.editors['conteudo'] = editor;
                
                editor.model.document.on('change:data', () => {
                    textarea.value = editor.getData();
                });
                
                console.log('Editor SEI inicializado com sucesso');
            })
            .catch(error => {
                console.error('Erro ao inicializar editor SEI:', error);
            });
    }
}

// Adicionar estilos CSS para notificações
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style); 