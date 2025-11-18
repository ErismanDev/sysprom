# 🔧 Corrigir Erro 403 Forbidden do Nginx

## 🚨 Problema
O Nginx não tem permissão para ler os arquivos estáticos. O usuário `www-data` (Nginx) precisa ter acesso de leitura.

---

## 🚀 Solução Completa

### Comando Único (Copiar e Colar)

```bash
# 1. Corrigir permissões do diretório staticfiles
sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/staticfiles && \
sudo chmod -R 755 /home/seprom/sepromcbmepi/staticfiles && \
sudo find /home/seprom/sepromcbmepi/staticfiles -type f -exec chmod 644 {} \; && \
sudo find /home/seprom/sepromcbmepi/staticfiles -type d -exec chmod 755 {} \; && \

# 2. Corrigir permissões do diretório static (se existir)
[ -d "/home/seprom/sepromcbmepi/sepromcbmepi/static" ] && sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/sepromcbmepi/static && sudo chmod -R 755 /home/seprom/sepromcbmepi/sepromcbmepi/static || true && \

# 3. Corrigir permissões do diretório media (se necessário)
[ -d "/home/seprom/sepromcbmepi/media" ] && sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/media && sudo chmod -R 755 /home/seprom/sepromcbmepi/media || true && \

# 4. Verificar se o Nginx pode ler os arquivos
sudo -u www-data test -r /home/seprom/sepromcbmepi/staticfiles && echo "✅ Nginx pode ler staticfiles" || echo "❌ Nginx NÃO pode ler staticfiles" && \

# 5. Verificar configuração do Nginx
echo "" && \
echo "=== Verificando configuração do Nginx ===" && \
grep -A 3 "location /static/" /etc/nginx/sites-available/seprom && \

# 6. Recarregar Nginx
sudo nginx -t && \
sudo systemctl reload nginx && \

# 7. Verificar status
echo "" && \
echo "✅ Correção aplicada!" && \
echo "" && \
echo "Teste agora: curl -I http://localhost/static/"
```

---

## 🔍 Verificação Detalhada

Se ainda der erro, execute estes comandos de diagnóstico:

```bash
# 1. Verificar permissões atuais
ls -la /home/seprom/sepromcbmepi/staticfiles | head -10

# 2. Verificar se o Nginx pode acessar
sudo -u www-data ls /home/seprom/sepromcbmepi/staticfiles | head -5

# 3. Verificar logs do Nginx
sudo tail -20 /var/log/nginx/seprom_error.log

# 4. Verificar se o diretório existe
test -d /home/seprom/sepromcbmepi/staticfiles && echo "✅ Diretório existe" || echo "❌ Diretório NÃO existe"

# 5. Verificar configuração do Nginx
cat /etc/nginx/sites-available/seprom | grep -A 5 "location /static/"
```

---

## 🔧 Solução Alternativa: Adicionar www-data ao grupo seprom

Se ainda não funcionar, adicione o usuário www-data ao grupo seprom:

```bash
# Adicionar www-data ao grupo seprom
sudo usermod -a -G seprom www-data

# Corrigir permissões do diretório pai
sudo chmod 755 /home/seprom
sudo chmod 755 /home/seprom/sepromcbmepi

# Corrigir permissões dos arquivos estáticos
sudo chown -R seprom:www-data /home/seprom/sepromcbmepi/staticfiles
sudo chmod -R 755 /home/seprom/sepromcbmepi/staticfiles

# Recarregar Nginx
sudo systemctl reload nginx
```

---

## 📋 Comando Mais Agressivo (Se Nada Funcionar)

```bash
# Dar permissão de leitura para todos (não recomendado para produção, mas funciona)
sudo chmod -R 755 /home/seprom/sepromcbmepi/staticfiles
sudo chmod -R 755 /home/seprom/sepromcbmepi
sudo chmod 755 /home/seprom

# Verificar
sudo -u www-data ls /home/seprom/sepromcbmepi/staticfiles | head -5
```

