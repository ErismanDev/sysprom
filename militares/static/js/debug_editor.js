// Script de debug para testar os botões de formatação
console.log('Script de debug carregado');

// Função para testar se o editor está disponível
function testEditor() {
    console.log('Testando editor...');
    console.log('window.editors:', window.editors);
    
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        console.log('Editor encontrado:', editor);
        console.log('Editor tem execute:', typeof editor.execute === 'function');
        
        // Testar comandos básicos
        try {
            editor.execute('bold');
            console.log('Comando bold executado com sucesso');
        } catch (error) {
            console.error('Erro ao executar bold:', error);
        }
        
        try {
            editor.execute('italic');
            console.log('Comando italic executado com sucesso');
        } catch (error) {
            console.error('Erro ao executar italic:', error);
        }
        
    } else {
        console.log('Nenhum editor encontrado');
    }
}

// Função para testar formatação
function testFormatText(format) {
    console.log('Testando formatText com:', format);
    
    if (window.editors && Object.keys(window.editors).length > 0) {
        const editor = Object.values(window.editors)[0];
        
        try {
            switch(format) {
                case 'bold':
                    editor.execute('bold');
                    console.log('Bold aplicado com sucesso');
                    break;
                case 'italic':
                    editor.execute('italic');
                    console.log('Italic aplicado com sucesso');
                    break;
                case 'underline':
                    editor.execute('underline');
                    console.log('Underline aplicado com sucesso');
                    break;
                default:
                    console.log('Formato não testado:', format);
            }
        } catch (error) {
            console.error('Erro ao aplicar formatação:', error);
        }
    } else {
        console.log('Editor não disponível');
    }
}

// Adicionar ao window para acesso global
window.testEditor = testEditor;
window.testFormatText = testFormatText;

// Executar teste após 3 segundos
setTimeout(() => {
    console.log('Executando teste automático do editor...');
    testEditor();
}, 3000); 