# SEPROM CBMEPI - Sistema de Promoções

Sistema de gerenciamento de promoções para o Corpo de Bombeiros Militar do Estado do Piauí.

## Funcionalidades

- Gestão de militares
- Controle de promoções
- Fichas de conceito
- Comissões de promoção
- Quadros de fixação
- Relatórios e estatísticas

## Tecnologias

- Django 5.2.3
- PostgreSQL
- Bootstrap
- JavaScript

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/sepromcbmepi.git
cd sepromcbmepi
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Execute as migrações:
```bash
python manage.py migrate
```

6. Crie um superusuário:
```bash
python manage.py createsuperuser
```

7. Execute o servidor:
```bash
python manage.py runserver
```

## Deploy

### Render.com

1. Conecte seu repositório ao Render
2. Configure as variáveis de ambiente
3. Deploy automático

### Railway

1. Conecte seu repositório ao Railway
2. Configure as variáveis de ambiente
3. Deploy automático

## Estrutura do Projeto

```
sepromcbmepi/
├── militares/          # App principal
├── sepromcbmepi/       # Configurações do projeto
├── static/            # Arquivos estáticos
├── templates/         # Templates HTML
├── media/            # Arquivos de mídia
└── manage.py         # Script de gerenciamento Django
```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT.
