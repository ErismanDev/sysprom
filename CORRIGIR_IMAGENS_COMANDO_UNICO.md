# 🔧 Corrigir Imagens - Comando Único

## 🚀 Execute Este Comando no Servidor

```bash
# 1. Criar diretório media se não existir
sudo mkdir -p /home/seprom/sepromcbmepi/media

# 2. Corrigir permissões
sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/media
sudo chmod -R 755 /home/seprom/sepromcbmepi/media

# 3. Atualizar configuração do Nginx para usar TCP
sudo sed -i 's|proxy_pass http://unix:/home/seprom/sepromcbmepi/seprom.sock;|proxy_pass http://127.0.0.1:8000;|g' /etc/nginx/sites-available/seprom

# 4. Atualizar server_name no Nginx
sudo sed -i 's|server_name _;|server_name 64.23.185.235;|g' /etc/nginx/sites-available/seprom

# 5. Garantir que o site está habilitado
sudo ln -sf /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/seprom

# 6. Remover site padrão se existir
sudo rm -f /etc/nginx/sites-enabled/default

# 7. Testar configuração do Nginx
sudo nginx -t

# 8. Recarregar Nginx
sudo systemctl reload nginx

# 9. Verificar status
echo "✅ Verificando status do Nginx:"
sudo systemctl status nginx --no-pager -l | head -10

# 10. Verificar se o diretório media existe
echo ""
echo "✅ Verificando diretório media:"
ls -la /home/seprom/sepromcbmepi/media/ | head -5

# 11. Testar acesso a arquivos de mídia
echo ""
echo "✅ Testando acesso a /media/:"
curl -I http://localhost/media/ 2>&1 | head -5

echo ""
echo "✅ Correção concluída!"
echo ""
echo "💡 Se as imagens ainda não carregarem:"
echo "   1. Verifique se os arquivos de mídia foram enviados via WinSCP"
echo "   2. Verifique os logs: sudo tail -50 /var/log/nginx/seprom_error.log"
echo "   3. Teste uma imagem específica: curl -I http://64.23.185.235/media/nome_arquivo.jpg"
```

---

## 📋 Comando Tudo em Um (Copiar e Colar)

```bash
sudo mkdir -p /home/seprom/sepromcbmepi/media && \
sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/media && \
sudo chmod -R 755 /home/seprom/sepromcbmepi/media && \
sudo sed -i 's|proxy_pass http://unix:/home/seprom/sepromcbmepi/seprom.sock;|proxy_pass http://127.0.0.1:8000;|g' /etc/nginx/sites-available/seprom && \
sudo sed -i 's|server_name _;|server_name 64.23.185.235;|g' /etc/nginx/sites-available/seprom && \
sudo ln -sf /etc/nginx/sites-available/seprom /etc/nginx/sites-enabled/seprom && \
sudo rm -f /etc/nginx/sites-enabled/default && \
sudo nginx -t && \
sudo systemctl reload nginx && \
echo "✅ Correção concluída! Verifique se as imagens estão carregando agora."
```

---

## 🔍 Verificar se Funcionou

```bash
# Verificar configuração do Nginx
cat /etc/nginx/sites-available/seprom | grep -A 2 "location /media/"

# Verificar se está servindo
curl -I http://localhost/media/

# Ver logs de erro
sudo tail -20 /var/log/nginx/seprom_error.log
```

---

## 📤 Enviar Arquivos de Mídia do PC Local

Se os arquivos de mídia não foram enviados, use WinSCP para enviar:

1. Conecte via WinSCP ao servidor
2. Navegue até `/home/seprom/sepromcbmepi/media/` no servidor
3. Envie os arquivos da pasta `media` do PC local para o servidor
4. Verifique permissões após o envio:
   ```bash
   sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/media
   sudo chmod -R 755 /home/seprom/sepromcbmepi/media
   ```

