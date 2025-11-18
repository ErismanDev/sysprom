#!/bin/bash

# Script para fazer deploy das alterações de armas particulares e configurações
# Execute no terminal do Cursor: bash deploy_armas_particulares.sh

echo "==============================================================="
echo "🚀 DEPLOY - ARMAS PARTICULARES E CONFIGURAÇÕES"
echo "==============================================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configurações do servidor
SERVER="64.23.185.235"
USER="root"
REMOTE_PATH="/home/seprom/sepromcbmepi"

# Arquivos modificados nesta sessão
FILES=(
    "militares/models.py"
    "militares/forms.py"
    "militares/templates/militares/arma_particular_form.html"
    "militares/templates/militares/arma_particular_list.html"
    "militares/templates/militares/configuracao_arma_form.html"
    "militares/views_material_belico.py"
    "militares/urls.py"
    "militares/migrations/0400_adicionar_campos_raias_arma_particular.py"
)

echo "📋 Arquivos que serão commitados:"
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo -e "${YELLOW}   ⚠ $file (não encontrado)${NC}"
    fi
done
echo ""

# Verificar se há alterações
if git diff --quiet "${FILES[@]}" 2>/dev/null && git diff --cached --quiet "${FILES[@]}" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Nenhuma alteração detectada nos arquivos especificados${NC}"
    read -p "Deseja continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Operação cancelada."
        exit 0
    fi
fi

# Adicionar arquivos ao staging
echo "📦 Adicionando arquivos ao Git..."
git add "${FILES[@]}" 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro ao adicionar arquivos ao Git${NC}"
    exit 1
fi

# Verificar se há algo para commitar
if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  Nenhuma alteração para commitar${NC}"
    read -p "Deseja fazer push e atualizar o servidor mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Operação cancelada."
        exit 0
    fi
else
    # Fazer commit
    echo "💾 Fazendo commit..."
    git commit -m "feat: Adicionar campos de raias em armas particulares e botões para adicionar tipos/calibres em configurações

- Adicionado campos alma_raiada, quantidade_raias e direcao_raias em ArmaParticular
- Adicionado Select2 no campo militar do formulário de armas particulares
- Adicionado posto e CPF na lista de armas particulares
- Adicionado botões para inserir novos tipos e calibres em configurações de armas
- Alterado 'Nº Registro na Polícia Federal' para 'Nº Registro SIGMA'
- Removido campo militar responsável do formulário de armas
- Adicionado carregamento automático de configuração na edição de armas" 2>/dev/null

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro ao fazer commit${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Commit realizado com sucesso!${NC}"
fi

# Fazer push
echo ""
echo "📤 Fazendo push para o repositório..."
BRANCH=$(git branch --show-current)
git push origin "$BRANCH" 2>/dev/null || git push origin main 2>/dev/null || git push origin master 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Não foi possível fazer push automaticamente${NC}"
    echo "   Execute manualmente: git push"
    read -p "Deseja continuar com a atualização do servidor? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Operação cancelada."
        exit 0
    fi
else
    echo -e "${GREEN}✅ Push realizado com sucesso!${NC}"
fi

# Verificar conexão com servidor
echo ""
echo "🔍 Verificando conexão com servidor..."
if ! ssh -o ConnectTimeout=5 ${USER}@${SERVER} "echo 'Conexão OK'" 2>/dev/null; then
    echo -e "${RED}❌ Erro: Não foi possível conectar ao servidor ${SERVER}${NC}"
    echo "   Verifique se:"
    echo "   1. O servidor está online"
    echo "   2. Você tem acesso SSH configurado"
    echo "   3. A chave SSH está correta"
    exit 1
fi

echo -e "${GREEN}✅ Conexão estabelecida!${NC}"
echo ""

# Executar comandos no servidor via SSH
echo "📦 Atualizando servidor..."
ssh ${USER}@${SERVER} << 'ENDSSH'
    set -e
    
    cd /home/seprom/sepromcbmepi
    
    # Fazer backup antes de atualizar
    echo "💾 Criando backup rápido..."
    BACKUP_DIR="/home/seprom/backups/$(date +%Y%m%d_%H%M%S)_armas_particulares"
    mkdir -p "$BACKUP_DIR"
    cp -r militares/models.py militares/forms.py militares/templates/militares/arma_particular*.* militares/templates/militares/configuracao_arma_form.html militares/views_material_belico.py militares/urls.py "$BACKUP_DIR/" 2>/dev/null || true
    echo "✅ Backup salvo em: $BACKUP_DIR"
    
    # Atualizar código do git
    if [ -d ".git" ]; then
        echo "📥 Fazendo pull do repositório..."
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || {
            echo "⚠️  Não foi possível fazer pull do git"
            exit 1
        }
        echo "✅ Código atualizado!"
    else
        echo "❌ Repositório Git não encontrado"
        exit 1
    fi
    
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
    echo -e "${GREEN}✅ DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
    echo "==============================================================="
    echo ""
    echo "🌐 Acesse: http://64.23.185.235/login/"
    echo ""
else
    echo ""
    echo "==============================================================="
    echo -e "${RED}❌ ERRO DURANTE O DEPLOY${NC}"
    echo "==============================================================="
    echo "Verifique os logs acima para mais detalhes."
    exit 1
fi

