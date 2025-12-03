#!/bin/bash
cd /home/seprom/sepromcbmepi
git pull origin master
source venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput
sudo systemctl restart seprom
echo "Deploy concluido com sucesso!"

