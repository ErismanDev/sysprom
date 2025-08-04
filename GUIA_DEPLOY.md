# Guia de Deploy - SEPROM CBMEPI

## Sistema Limpo e Pronto para Deploy

O sistema foi limpo e está pronto para ser enviado ao GitHub e fazer deploy em servidores web.

## Estrutura Final

```
sepromcbmepi/
├── militares/              # App principal Django
├── sepromcbmepi/           # Configurações do projeto
├── static/                # Arquivos estáticos
├── templates/             # Templates HTML
├── media/                 # Arquivos de mídia
├── scripts/               # Scripts utilitários
├── docs/                  # Documentação
├── .github/               # Configurações GitHub
├── .ebextensions/         # Configurações AWS Elastic Beanstalk
├── manage.py              # Script de gerenciamento Django
├── requirements.txt       # Dependências Python
├── runtime.txt           # Versão do Python
├── .gitignore            # Arquivos ignorados pelo Git
├── README.md             # Documentação principal
├── .env.example          # Exemplo de variáveis de ambiente
├── funcao_atualizacao_manual.py  # Função manual de atualização
├── build.sh              # Script de build
├── Procfile              # Configuração Heroku/Railway
├── railway.json          # Configuração Railway
└── render.yaml           # Configuração Render.com
```

## Passos para Deploy

### 1. Enviar para GitHub

```bash
# Adicionar todos os arquivos
git add .

# Fazer commit
git commit -m "Sistema limpo para deploy"

# Enviar para GitHub
git push origin main
```

### 2. Deploy no Render.com

1. Acesse [render.com](https://render.com)
2. Conecte seu repositório GitHub
3. Crie um novo **Web Service**
4. Configure as variáveis de ambiente:
   - `DEBUG`: `False`
   - `SECRET_KEY`: Sua chave secreta
   - `DATABASE_URL`: URL do banco PostgreSQL
   - `ALLOWED_HOSTS`: `.onrender.com`
5. O arquivo `render.yaml` já está configurado

### 3. Deploy no Railway

1. Acesse [railway.app](https://railway.app)
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente:
   - `DEBUG`: `False`
   - `SECRET_KEY`: Sua chave secreta
   - `DATABASE_URL`: URL do banco PostgreSQL
   - `ALLOWED_HOSTS`: `.railway.app`
4. O arquivo `railway.json` já está configurado

### 4. Deploy no Heroku

1. Acesse [heroku.com](https://heroku.com)
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente
4. O arquivo `Procfile` já está configurado

### 5. Deploy no AWS Elastic Beanstalk

1. Use o diretório `.ebextensions/` já configurado
2. Faça upload via AWS CLI ou console
3. Configure as variáveis de ambiente

## Variáveis de Ambiente Necessárias

```bash
# Django
DEBUG=False
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com,.railway.app,.herokuapp.com

# Banco de Dados
DATABASE_URL=postgresql://usuario:senha@host:porta/banco

# Supabase (se usar)
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres.xxx
SUPABASE_PASSWORD=sua-senha
SUPABASE_HOST=aws-0-sa-east-1.pooler.supabase.com
SUPABASE_PORT=6543

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

## Funcionalidades Implementadas

### ✅ Sistema de Promoções
- Gestão completa de militares
- Controle de promoções
- Fichas de conceito
- Comissões de promoção
- Quadros de fixação

### ✅ Função Automática
- Atualização automática da data de promoção
- Cálculo correto do tempo no posto
- Recalculação automática de pontuações

### ✅ Deploy Automático
- Configurações para múltiplas plataformas
- Scripts de build otimizados
- Health checks configurados

## Comandos Úteis

### Atualização Manual de Promoções
```bash
python funcao_atualizacao_manual.py
```

### Verificação de Status
```bash
python manage.py check
python manage.py collectstatic
python manage.py migrate
```

### Criação de Superusuário
```bash
python manage.py createsuperuser
```

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs da aplicação
2. Confirme as variáveis de ambiente
3. Teste localmente antes do deploy
4. Use a função manual de atualização se necessário

## Status do Sistema

✅ **Sistema limpo e organizado**
✅ **Configurações de deploy prontas**
✅ **Função automática implementada**
✅ **Documentação completa**
✅ **Pronto para produção**

O sistema está completamente preparado para deploy em qualquer plataforma de hospedagem web! 