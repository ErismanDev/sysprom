#!/bin/bash

echo "==============================================================="
echo "🚀 DEPLOY - ARMAS PARTICULARES E CONFIGURAÇÕES"
echo "==============================================================="
echo ""

# Adicionar arquivos
echo "📦 Adicionando arquivos ao Git..."
git add militares/models.py \
        militares/forms.py \
        militares/templates/militares/arma_particular_form.html \
        militares/templates/militares/arma_particular_list.html \
        militares/templates/militares/configuracao_arma_form.html \
        militares/views_material_belico.py \
        militares/urls.py \
        militares/migrations/0400_adicionar_campos_raias_arma_particular.py

# Verificar se há alterações para commitar
if git diff --cached --quiet; then
    echo "⚠️  Nenhuma alteração para commitar"
    read -p "Deseja fazer push e atualizar o servidor mesmo assim? (s/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Operação cancelada."
        exit 0
    fi
else
    # Fazer commit
    echo "💾 Fazendo commit..."
    git commit -m "feat: Adicionar campos de raias em armas particulares e botões para adicionar tipos/calibres"
    
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao fazer commit"
        exit 1
    fi
    echo "✅ Commit realizado com sucesso!"
fi

# Fazer push
echo ""
echo "📤 Fazendo push para o repositório..."
BRANCH=$(git branch --show-current)
git push origin $BRANCH

if [ $? -ne 0 ]; then
    echo "⚠️  Erro ao fazer push"
    read -p "Deseja continuar com a atualização do servidor? (s/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Operação cancelada."
        exit 0
    fi
else
    echo "✅ Push realizado com sucesso!"
fi

# Atualizar servidor
echo ""
echo "📦 Atualizando servidor Digital Ocean..."
echo ""

ssh root@64.23.185.235 << 'ENDSSH'
cd /home/seprom/sepromcbmepi

echo "💾 Criando backup rápido..."
BACKUP_DIR="/home/seprom/backups/$(date +%Y%m%d_%H%M%S)_armas_particulares"
mkdir -p "$BACKUP_DIR"
cp -r militares/models.py militares/forms.py militares/templates/militares/arma_particular*.* militares/templates/militares/configuracao_arma_form.html militares/views_material_belico.py militares/urls.py "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ Backup salvo em: $BACKUP_DIR"

echo ""
echo "📥 Fazendo pull do repositório..."
git pull origin master || git pull origin main || {
    echo "❌ Erro ao fazer pull do git"
    exit 1
}
echo "✅ Código atualizado!"

echo ""
echo "🐍 Ativando ambiente virtual..."
source venv/bin/activate || {
    echo "❌ Erro ao ativar venv"
    exit 1
}

echo ""
echo "🗄️  Executando migrations..."
python manage.py migrate --noinput

echo ""
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo ""
echo "🔄 Reiniciando serviço Gunicorn..."
sudo systemctl restart seprom
sleep 3

echo ""
echo "📊 Verificando status do serviço..."
if sudo systemctl is-active --quiet seprom; then
    echo "✅ Serviço está rodando corretamente!"
else
    echo "⚠️  Serviço pode ter problemas. Verificando logs..."
    sudo systemctl status seprom --no-pager -l | head -30
fi

echo ""
echo "✅ ATUALIZAÇÃO CONCLUÍDA!"
echo "🌐 Acesse: http://64.23.185.235/login/"
echo ""
echo "📝 Alterações aplicadas:"
echo "   - Campos de raias em armas particulares"
echo "   - Select2 no campo militar"
echo "   - Posto e CPF na lista de armas particulares"
echo "   - Botões para adicionar tipos/calibres em configurações"
echo "   - Alteração de 'Nº Registro PF' para 'Nº Registro SIGMA'"
echo "   - Remoção do campo militar responsável"
echo "   - Carregamento automático de configuração na edição"
ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "==============================================================="
    echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
    echo "==============================================================="
    echo ""
    echo "🌐 Acesse: http://64.23.185.235/login/"
    echo ""
else
    echo ""
    echo "==============================================================="
    echo "❌ ERRO DURANTE O DEPLOY"
    echo "==============================================================="
    echo "Verifique os logs acima para mais detalhes."
    exit 1
fi

