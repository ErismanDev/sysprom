# 🚀 Scripts de Deploy

Scripts para atualizar o sistema no servidor diretamente do terminal do Cursor.

## 📋 Scripts Disponíveis

### 1. `deploy_completo.ps1` (Recomendado)
Script completo que faz tudo: commit, push e atualização no servidor.

**Uso:**
```powershell
.\deploy_completo.ps1
```

**O que faz:**
- ✅ Verifica status do Git
- ✅ Pergunta se deseja fazer commit/push
- ✅ Conecta ao servidor
- ✅ Faz backup automático
- ✅ Executa `git pull` no servidor
- ✅ Executa migrations
- ✅ Coleta arquivos estáticos
- ✅ Reinicia o serviço Gunicorn
- ✅ Verifica status do serviço

### 2. `atualizar_servidor.ps1`
Apenas atualiza no servidor (sem commit/push).

**Uso:**
```powershell
.\atualizar_servidor.ps1
```

### 3. `atualizar_servidor.sh`
Versão Bash (para Git Bash ou Linux).

**Uso:**
```bash
./atualizar_servidor.sh
```

## ⚙️ Configurações

Os scripts estão configurados para:
- **Servidor:** 64.23.185.235
- **Usuário:** root
- **Caminho:** /home/seprom/sepromcbmepi
- **Serviço:** seprom

Para alterar, edite as variáveis no início dos scripts.

## 🔐 Pré-requisitos

1. **SSH configurado** com acesso ao servidor
2. **Chave SSH** adicionada ao servidor
3. **Git** instalado e configurado

## 📝 Exemplo de Uso Completo

```powershell
# 1. Fazer suas alterações nos arquivos

# 2. Executar o script completo
.\deploy_completo.ps1

# 3. Responder às perguntas:
#    - Deseja fazer commit? (S/N)
#    - Mensagem do commit (ou Enter para padrão)

# 4. Aguardar a atualização no servidor
```

## ⚠️ Notas Importantes

- O script cria um backup automático antes de atualizar
- O serviço é reiniciado automaticamente
- Verifique o status do serviço ao final
- Em caso de erro, verifique os logs do Gunicorn

## 🐛 Troubleshooting

**Erro de conexão SSH:**
- Verifique se o servidor está online
- Confirme que a chave SSH está configurada
- Teste a conexão manualmente: `ssh root@64.23.185.235`

**Erro no Git:**
- Verifique se há alterações não commitadas
- Confirme que está na branch correta (master/main)

**Erro no serviço:**
- Verifique os logs: `sudo journalctl -u seprom -n 50`
- Verifique o status: `sudo systemctl status seprom`

