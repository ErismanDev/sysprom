#!/bin/bash
# Script para limpar cache e verificar permissões no servidor

echo "==============================================================="
echo "🔍 VERIFICANDO E CORRIGINDO PERMISSÕES"
echo "==============================================================="
echo ""

ssh root@64.23.185.235 << 'ENDSSH'
    cd /home/seprom/sepromcbmepi
    source venv/bin/activate
    
    echo "🗑️  Limpando cache do Django..."
    python manage.py shell << PYTHON
from django.core.cache import cache
cache.clear()
print("✅ Cache limpo!")
PYTHON
    
    echo ""
    echo "🔄 Reiniciando serviço..."
    sudo systemctl restart seprom
    sleep 3
    
    echo ""
    echo "📊 Status do serviço:"
    sudo systemctl status seprom --no-pager -l | head -15
    
    echo ""
    echo "✅ Verificação concluída!"
    echo ""
    echo "📝 Próximos passos:"
    echo "   1. Acesse: http://64.23.185.235/login/"
    echo "   2. Vá em: Funções Militares"
    echo "   3. Edite a função desejada"
    echo "   4. Em 'Permissões Granulares', selecione:"
    echo "      - MENU_CONFIGURACOES (VISUALIZAR)"
    echo "      - SUBMENU_USUARIOS (VISUALIZAR)"
    echo "      - SUBMENU_PERMISSOES (VISUALIZAR)"
    echo "      - SUBMENU_LOGS (VISUALIZAR)"
    echo "      - SUBMENU_ADMINISTRACAO (VISUALIZAR)"
    echo "      - SUBMENU_TITULOS_PUBLICACAO (VISUALIZAR)"
    echo "   5. Salve e teste novamente"
ENDSSH

echo ""
echo "✅ Processo concluído!"

