# 🔧 Corrigir Exibição de Imagens no Chat

## ⚠️ Problema

O chat estava exibindo apenas a imagem local (do usuário logado), mas não mostrava a imagem do outro interlocutor nas mensagens recebidas.

---

## ✅ Correções Implementadas

### 1. Função `obterFotoOutroParticipante()` (chat-widget-ios.js)

**Nova função criada** para obter a foto do outro participante:

```javascript
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
```

### 2. Função `obterFotoUsuario()` (chat-widget-ios.js)

**Melhorada** para buscar a foto do usuário logado de forma mais precisa:

```javascript
obterFotoUsuario() {
    // Tentar obter da primeira mensagem enviada já renderizada
    const usuarioAvatar = document.querySelector('.chat-mensagem-ios.sent .chat-avatar-msg img');
    if (usuarioAvatar) {
        return usuarioAvatar.src;
    }
    
    return null;
}
```

### 3. Função `renderizarMensagens()` (chat-widget-ios.js)

**Corrigida** para usar a foto do remetente corretamente:

```javascript
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
```

### 4. Função `adicionarMensagem()` (chat-widget-ios.js e chat-tempo-real.js)

**Corrigida** para usar a foto do remetente quando novas mensagens chegam:

```javascript
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
```

---

## 📋 Comportamento Após Correção

### Mensagens Recebidas
- ✅ Exibem a foto do remetente (outro participante)
- ✅ Se não houver foto na mensagem, tenta obter do header do chat
- ✅ Se não houver no header, tenta obter de mensagens anteriores já renderizadas
- ✅ Se não houver foto, exibe inicial do nome

### Mensagens Enviadas
- ✅ Exibem a foto do usuário logado
- ✅ Se não houver foto, tenta obter de mensagens anteriores já renderizadas
- ✅ Se não houver foto, exibe inicial do nome

---

## 🔍 Arquivos Modificados

1. `static/js/chat-widget-ios.js`
   - Adicionada função `obterFotoOutroParticipante()`
   - Melhorada função `obterFotoUsuario()`
   - Corrigida função `renderizarMensagens()`
   - Corrigida função `adicionarMensagem()`

2. `static/js/chat-tempo-real.js`
   - Corrigida função `adicionarMensagem()`

---

## ✅ Testes

Após as correções, teste:

1. **Abrir um chat existente:**
   - As mensagens recebidas devem mostrar a foto do outro participante
   - As mensagens enviadas devem mostrar sua foto

2. **Receber nova mensagem:**
   - A nova mensagem recebida deve mostrar a foto do remetente
   - Se não houver foto na mensagem, deve tentar obter do header ou mensagens anteriores

3. **Enviar nova mensagem:**
   - A nova mensagem enviada deve mostrar sua foto
   - Se não houver foto, deve tentar obter de mensagens anteriores

---

---

## 📹 Correções para Chamadas de Vídeo

### 1. Função `mostrarInterfaceChamada()` (chat-calls.js)

**Melhorada** para obter a foto do contato de múltiplas fontes:

```javascript
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
    
    // Usar inicial do nome do contato
    if (nomeContato && nomeContato !== 'Selecione uma conversa') {
        return { foto: null, inicial: nomeContato.charAt(0).toUpperCase() };
    }
    
    return { foto: null, inicial: '?' };
};
```

### 2. Handler `ontrack` (chat-calls.js)

**Corrigido** para exibir avatar quando o vídeo remoto não estiver disponível:

```javascript
if (this.isVideoCall && this.remoteStream.getVideoTracks().length > 0) {
    // Chamada de vídeo - mostrar vídeo
    remoteVideo.srcObject = this.remoteStream;
    remoteVideo.style.display = 'block';
    if (avatarVoice) avatarVoice.style.display = 'none';
} else {
    // Chamada de voz ou vídeo sem stream de vídeo - mostrar avatar
    if (avatarVoice) {
        avatarVoice.style.display = 'flex';
        // Configurar foto/inicial do contato
    }
}
```

### 3. Estado 'active' da chamada (chat-calls.js)

**Adicionado** suporte para exibir avatar em chamadas de vídeo quando o vídeo remoto não estiver disponível:

```javascript
// Se for chamada de vídeo mas não houver stream de vídeo remoto, mostrar avatar
if (this.isVideoCall && avatarVoice) {
    const remoteVideo = document.getElementById('chat-call-video-remote-stream');
    if (!remoteVideo || !remoteVideo.srcObject || remoteVideo.style.display === 'none') {
        avatarVoice.style.display = 'flex';
        // Configurar foto/inicial do contato
    }
}
```

---

## 📋 Comportamento Após Correção - Chamadas

### Chamadas de Voz
- ✅ Exibem avatar do contato (foto ou inicial)
- ✅ Busca foto de múltiplas fontes (header, mensagens)
- ✅ Fallback para inicial do nome se não houver foto

### Chamadas de Vídeo
- ✅ Exibem vídeo remoto quando disponível
- ✅ Exibem avatar quando vídeo remoto não está disponível
- ✅ Busca foto de múltiplas fontes para o avatar
- ✅ Fallback para inicial do nome se não houver foto

---

**Última atualização**: 2024-11-16

