/**
 * Sistema de Visualização de Senha
 * Adiciona botão de "olho" para mostrar/ocultar senha em todos os campos de senha
 */

class PasswordToggle {
    constructor() {
        this.init();
    }

    init() {
        this.addPasswordToggles();
        this.setupGlobalFunctions();
    }

    addPasswordToggles() {
        // Selecionar todos os campos de senha
        const passwordFields = document.querySelectorAll('input[type="password"]');
        
        passwordFields.forEach(field => {
            // Verificar se já tem toggle (evitar duplicação)
            if (field.parentNode.querySelector('.password-toggle-btn')) {
                return;
            }

            this.createPasswordToggle(field);
        });
    }

    createPasswordToggle(passwordField) {
        // Criar wrapper para o campo de senha
        const wrapper = document.createElement('div');
        wrapper.className = 'password-field-wrapper position-relative';
        wrapper.style.display = 'flex';
        wrapper.style.alignItems = 'center';

        // Mover o campo de senha para o wrapper
        passwordField.parentNode.insertBefore(wrapper, passwordField);
        wrapper.appendChild(passwordField);

        // Criar botão de toggle
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle-btn btn btn-outline-secondary position-absolute end-0 me-2';
        toggleBtn.style.zIndex = '10';
        toggleBtn.style.border = 'none';
        toggleBtn.style.background = 'transparent';
        toggleBtn.style.color = '#6c757d';
        toggleBtn.style.fontSize = '14px';
        toggleBtn.style.padding = '6px 8px';
        toggleBtn.style.borderRadius = '4px';
        toggleBtn.style.transition = 'all 0.2s ease';

        // Ícone inicial (olho fechado)
        toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
        toggleBtn.title = 'Mostrar senha';

        // Adicionar padding direito ao campo de senha para o botão
        passwordField.style.paddingRight = '40px';

        // Adicionar botão ao wrapper
        wrapper.appendChild(toggleBtn);

        // Adicionar eventos
        this.addToggleEvents(toggleBtn, passwordField);
    }

    addToggleEvents(toggleBtn, passwordField) {
        let isVisible = false;

        toggleBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            if (isVisible) {
                // Ocultar senha
                passwordField.type = 'password';
                toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
                toggleBtn.title = 'Mostrar senha';
                toggleBtn.style.color = '#6c757d';
                isVisible = false;
            } else {
                // Mostrar senha
                passwordField.type = 'text';
                toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
                toggleBtn.title = 'Ocultar senha';
                toggleBtn.style.color = '#dc3545';
                isVisible = true;

                // Auto-ocultar após 3 segundos
                setTimeout(() => {
                    if (isVisible) {
                        passwordField.type = 'password';
                        toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
                        toggleBtn.title = 'Mostrar senha';
                        toggleBtn.style.color = '#6c757d';
                        isVisible = false;
                    }
                }, 3000);
            }
        });

        // Hover effects
        toggleBtn.addEventListener('mouseenter', () => {
            toggleBtn.style.backgroundColor = '#f8f9fa';
            toggleBtn.style.color = isVisible ? '#c82333' : '#495057';
        });

        toggleBtn.addEventListener('mouseleave', () => {
            toggleBtn.style.backgroundColor = 'transparent';
            toggleBtn.style.color = isVisible ? '#dc3545' : '#6c757d';
        });

        // Foco no campo de senha
        passwordField.addEventListener('focus', () => {
            toggleBtn.style.backgroundColor = '#e9ecef';
        });

        passwordField.addEventListener('blur', () => {
            toggleBtn.style.backgroundColor = 'transparent';
        });
    }

    setupGlobalFunctions() {
        // Disponibilizar funções globalmente
        window.addPasswordToggle = (fieldId) => {
            const field = document.getElementById(fieldId);
            if (field && field.type === 'password') {
                this.createPasswordToggle(field);
            }
        };

        window.addPasswordTogglesToPage = () => {
            this.addPasswordToggles();
        };
    }

    // Método para adicionar toggle a um campo específico
    addToggleToField(fieldId) {
        const field = document.getElementById(fieldId);
        if (field && field.type === 'password') {
            this.createPasswordToggle(field);
        }
    }

    // Método para remover todos os toggles
    removeAllToggles() {
        const toggles = document.querySelectorAll('.password-toggle-btn');
        toggles.forEach(toggle => {
            toggle.remove();
        });

        const wrappers = document.querySelectorAll('.password-field-wrapper');
        wrappers.forEach(wrapper => {
            const passwordField = wrapper.querySelector('input[type="password"]');
            if (passwordField) {
                wrapper.parentNode.insertBefore(passwordField, wrapper);
                wrapper.remove();
            }
        });
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    window.passwordToggle = new PasswordToggle();
});

// Função global para compatibilidade
function addPasswordToggle(fieldId) {
    if (window.passwordToggle) {
        return window.passwordToggle.addToggleToField(fieldId);
    }
    // Fallback se o sistema ainda não estiver inicializado
    setTimeout(() => addPasswordToggle(fieldId), 100);
}

// Função para adicionar toggles a todos os campos de senha da página
function addPasswordTogglesToPage() {
    if (window.passwordToggle) {
        return window.passwordToggle.addPasswordToggles();
    }
    // Fallback se o sistema ainda não estiver inicializado
    setTimeout(() => addPasswordTogglesToPage(), 100);
}
