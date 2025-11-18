#!/bin/bash

echo "==============================================================="
echo "🚀 FINALIZANDO DEPLOY - ARMAS PARTICULARES"
echo "==============================================================="
echo ""

cd /home/seprom/sepromcbmepi

echo "📦 Ativando ambiente virtual..."
source venv/bin/activate

echo ""
echo "🗄️  Adicionando campos no banco de dados..."
sudo -u postgres psql -d sepromcbmepi << EOF
ALTER TABLE militares_armaparticular ADD COLUMN IF NOT EXISTS alma_raiada BOOLEAN DEFAULT FALSE;
ALTER TABLE militares_armaparticular ADD COLUMN IF NOT EXISTS quantidade_raias INTEGER NULL;
ALTER TABLE militares_armaparticular ADD COLUMN IF NOT EXISTS direcao_raias VARCHAR(10) NULL;
EOF

echo ""
echo "✅ Campos adicionados ao banco!"

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
    echo "⚠️  Verificando logs..."
    sudo systemctl status seprom --no-pager -l | head -20
fi

echo ""
echo "==============================================================="
echo "✅ DEPLOY CONCLUÍDO!"
echo "==============================================================="
echo ""
echo "🌐 Acesse: http://64.23.185.235/login/"
echo ""

