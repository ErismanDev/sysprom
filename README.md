# SEPROM CBMEPI

Sistema de Promoções do Corpo de Bombeiros Militar do Estado do Piauí (CBMEPI).

## Descrição

Sistema web desenvolvido em Django para gerenciar promoções, efetivos e processos administrativos do CBMEPI.

## Funcionalidades

- Gestão de militares
- Controle de promoções
- Geração de almanaques
- Gestão de comissões
- Controle de vagas e efetivos
- Geração de documentação
- Sistema de assinaturas digitais

## Tecnologias Utilizadas

- **Backend:** Django 5.2.3
- **Frontend:** HTML, CSS, JavaScript
- **Editor de Texto:** CKEditor 5
- **Banco de Dados:** PostgreSQL
- **Autenticação:** Django Auth

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/ErismanDev/sysprom.git
cd sysprom
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o banco de dados:
```bash
python manage.py migrate
```

5. Crie um superusuário:
```bash
python manage.py createsuperuser
```

6. Execute o servidor:
```bash
python manage.py runserver
```

## Estrutura do Projeto

```
sepromcbmepi/
├── militares/           # App principal
├── sepromcbmepi/        # Configurações do projeto
├── media/              # Arquivos de mídia
├── static/             # Arquivos estáticos
├── templates/          # Templates HTML
└── docs/              # Documentação
```

## Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das suas mudanças
4. Abra um Pull Request

## Licença

Este projeto é de uso interno do CBMEPI.

## Autor

Desenvolvido para o Corpo de Bombeiros Militar do Estado do Piauí. 