(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Função para mostrar/ocultar o campo nota_cho
        function toggleNotaCho() {
            var cursoCho = $('#id_curso_cho');
            var notaChoField = $('.field-nota_cho');
            
            if (cursoCho.is(':checked')) {
                notaChoField.show();
            } else {
                notaChoField.hide();
                // Limpar o valor quando ocultar
                $('#id_nota_cho').val('');
            }
        }
        
        // Executar na carga da página
        toggleNotaCho();
        
        // Executar quando o checkbox mudar
        $('#id_curso_cho').on('change', function() {
            toggleNotaCho();
        });
    });
})(django.jQuery); 