# ✅ Verificar Aplicação Após Restore

## 🔍 Comandos de Verificação

### 1. Verificar Status dos Serviços

```bash
# Verificar status do Gunicorn
sudo systemctl status seprom --no-pager

# Verificar status do Nginx
sudo systemctl status nginx --no-pager

# Verificar status do PostgreSQL
sudo systemctl status postgresql --no-pager
```

### 2. Verificar Logs

```bash
# Logs do Gunicorn (últimas 50 linhas)
sudo journalctl -u seprom -n 50 --no-pager

# Logs do Nginx (últimas 50 linhas)
sudo journalctl -u nginx -n 50 --no-pager

# Logs de erros do Nginx
sudo tail -n 50 /var/log/nginx/error.log
```

### 3. Testar Aplicação

```bash
# Testar localmente
curl -I http://localhost

# Testar pelo IP externo
curl -I http://64.23.185.235

# Testar página de login
curl http://64.23.185.235/login/ | head -20
```

### 4. Verificar Banco de Dados

```bash
# Verificar quantidade de registros principais
su - postgres -c "psql sepromcbmepi -c \"
SELECT 
    'militares_militar' as tabela, COUNT(*) as registros FROM militares_militar
UNION ALL
SELECT 'auth_user', COUNT(*) FROM auth_user
UNION ALL
SELECT 'militares_fichaconceitooficiais', COUNT(*) FROM militares_fichaconceitooficiais
UNION ALL
SELECT 'militares_fichaconceitopracas', COUNT(*) FROM militares_fichaconceitopracas;
\""
```

### 5. Verificar Dados Órfãos (se necessário)

```bash
# Verificar fichas de conceito sem militar
su - postgres -c "psql sepromcbmepi -c \"
SELECT COUNT(*) as fichas_oficiais_orfas 
FROM militares_fichaconceitooficiais 
WHERE militar_id NOT IN (SELECT id FROM militares_militar);

SELECT COUNT(*) as fichas_pracas_orfas 
FROM militares_fichaconceitopracas 
WHERE militar_id NOT IN (SELECT id FROM militares_militar);
\""
```

---

## ✅ Checklist de Verificação

- [ ] Serviço `seprom` está rodando
- [ ] Serviço `nginx` está rodando
- [ ] Serviço `postgresql` está rodando
- [ ] Aplicação responde em `http://64.23.185.235`
- [ ] Página de login carrega corretamente
- [ ] Não há erros críticos nos logs
- [ ] Dados foram restaurados (verificar contagem de registros)

---

## 🔧 Se Houver Problemas

### Aplicação não responde

```bash
# Reiniciar serviços
sudo systemctl restart seprom
sudo systemctl restart nginx

# Verificar logs de erro
sudo journalctl -u seprom -n 100 --no-pager | grep -i error
```

### Erros de permissão

```bash
# Verificar permissões
ls -la /home/seprom/sepromcbmepi/
ls -la /home/seprom/sepromcbmepi/staticfiles/
```

### Erros de banco de dados

```bash
# Verificar conexão
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py check --database default"
```

---

## 🎉 Tudo Funcionando?

Se tudo estiver OK, você pode acessar:
- **URL**: http://64.23.185.235
- **Login**: Use suas credenciais normais

