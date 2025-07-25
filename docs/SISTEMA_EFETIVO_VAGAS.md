# Sistema de Atualização Automática do Efetivo nas Vagas

## Visão Geral

O sistema implementa uma atualização automática do efetivo atual nas vagas do sistema SEPROM CBMEPI, refletindo automaticamente os militares cadastrados nas vagas correspondentes.

## Funcionalidades

### 1. Atualização Manual
- **Comando**: `python manage.py atualizar_efetivo_vagas`
- **Interface Web**: Acesso via menu "Efetivo" > "Status do Efetivo - Vagas"
- **Funcionalidade**: Atualiza manualmente o efetivo nas vagas

### 2. Atualização Automática
- **Comando**: `python manage.py atualizar_efetivo_automatico`
- **Funcionalidade**: Atualização automática com relatório por email
- **Opções**:
  - `--email`: Envia relatório por email
  - `--recipients email1@exemplo.com email2@exemplo.com`: Lista de destinatários

### 3. Signals Automáticos
- **Trigger**: Quando um militar é salvo, editado ou excluído
- **Funcionalidade**: Atualização automática das vagas correspondentes

## Como Usar

### Atualização Manual via Comando

```bash
# Modo de teste (não salva alterações)
python manage.py atualizar_efetivo_vagas --dry-run --verbose

# Atualização real
python manage.py atualizar_efetivo_vagas --verbose

# Atualização automática com email
python manage.py atualizar_efetivo_automatico --email --recipients admin@exemplo.com
```

### Atualização via Interface Web

1. Acesse o sistema SEPROM CBMEPI
2. Vá em "Efetivo" > "Status do Efetivo - Vagas"
3. Clique em "Atualizar Efetivo Automaticamente"
4. Aguarde a conclusão e visualize o relatório

### Configuração de Cron (Atualização Automática)

Para configurar atualização automática diária, adicione ao crontab:

```bash
# Atualização diária às 06:00
0 6 * * * cd /caminho/para/sepromcbmepi && python manage.py atualizar_efetivo_automatico --email --recipients admin@exemplo.com

# Atualização semanal às 06:00 de segunda-feira
0 6 * * 1 cd /caminho/para/sepromcbmepi && python manage.py atualizar_efetivo_automatico --email --recipients admin@exemplo.com
```

## Estrutura do Sistema

### Arquivos Principais

1. **`militares/management/commands/atualizar_efetivo_vagas.py`**
   - Comando principal de atualização
   - Processa militares ativos e atualiza vagas

2. **`militares/signals.py`**
   - Signals para atualização automática
   - Triggered quando militares são salvos/editados

3. **`militares/views.py`** (função `status_efetivo_vagas`)
   - View para interface web
   - Mostra status e permite atualização manual

4. **`militares/templates/militares/status_efetivo_vagas.html`**
   - Template da interface web
   - Exibe relatório detalhado do efetivo

5. **`militares/management/commands/atualizar_efetivo_automatico.py`**
   - Comando para atualização automática
   - Inclui relatório por email

### URLs

- **Status do Efetivo**: `/militares/status-efetivo-vagas/`
- **Menu**: Adicionado ao dropdown "Efetivo" no menu principal

## Relatório de Atualização

O sistema gera relatórios detalhados incluindo:

- **Militares processados**: Total de militares ativos
- **Vagas criadas**: Novas vagas criadas
- **Vagas atualizadas**: Vagas existentes atualizadas
- **Previsões atualizadas**: Previsões de vagas atualizadas
- **Efetivo por posto/quadro**: Distribuição detalhada

### Exemplo de Relatório

```
============================================================
📊 RESUMO DA ATUALIZAÇÃO
============================================================
👥 Militares ativos processados: 494
🆕 Vagas criadas: 15
🔄 Vagas atualizadas: 0
📈 Previsões atualizadas: 15

📋 EFETIVO POR POSTO/QUADRO:
----------------------------------------
  1S - PRACAS: 26 militares
  1T - COMB: 15 militares
  1T - COMP: 36 militares
  2S - PRACAS: 16 militares
  2T - COMP: 29 militares
  3S - PRACAS: 10 militares
  CAB - PRACAS: 51 militares
  CB - COMB: 6 militares
  CP - COMB: 10 militares
  CP - COMP: 22 militares
  CP - ENG: 2 militares
  MJ - COMP: 7 militares
  SD - PRACAS: 195 militares
  ST - PRACAS: 56 militares
  TC - COMB: 13 militares
```

## Configuração de Email

Para usar o sistema de relatório por email, configure no `settings.py`:

```python
# Configurações de Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.exemplo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@exemplo.com'
EMAIL_HOST_PASSWORD = 'sua-senha'
DEFAULT_FROM_EMAIL = 'SysProm - CBMEPI <noreply@exemplo.com>'
```

## Monitoramento

### Logs

O sistema registra logs detalhados:
- **Info**: Atualizações bem-sucedidas
- **Error**: Erros durante atualização
- **Warning**: Situações que requerem atenção

### Alertas

- **Email de sucesso**: Relatório completo da atualização
- **Email de erro**: Notificação imediata de problemas
- **Interface web**: Status em tempo real

## Manutenção

### Verificação Regular

1. **Verificar logs**: Monitorar logs do sistema
2. **Validar dados**: Comparar efetivo com vagas
3. **Testar comandos**: Executar comandos em modo de teste

### Backup

- **Dados**: Backup regular do banco de dados
- **Logs**: Preservar logs de atualização
- **Configurações**: Backup das configurações de email

## Troubleshooting

### Problemas Comuns

1. **Erro de conexão com banco**
   - Verificar configurações do banco
   - Testar conectividade

2. **Erro de email**
   - Verificar configurações SMTP
   - Testar envio manual

3. **Dados inconsistentes**
   - Executar comando em modo de teste
   - Verificar integridade dos dados

### Comandos de Diagnóstico

```bash
# Verificar status atual
python manage.py atualizar_efetivo_vagas --dry-run --verbose

# Testar email
python manage.py atualizar_efetivo_automatico --email --recipients teste@exemplo.com

# Verificar logs
tail -f /var/log/django/atualizacao_efetivo.log
```

## Segurança

- **Autenticação**: Acesso restrito a usuários autorizados
- **Logs**: Registro de todas as operações
- **Validação**: Verificação de integridade dos dados
- **Backup**: Preservação de dados críticos

## Suporte

Para suporte técnico:
- **Logs**: Verificar logs do sistema
- **Documentação**: Consultar esta documentação
- **Desenvolvedor**: Contatar equipe de desenvolvimento 