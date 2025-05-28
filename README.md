# API de Manutenção de Equipamentos Clínicos

API completa para administração de manutenções de equipamentos em uma clínica médica, baseada no modelo EFORT e adaptada para o contexto específico de equipamentos médicos.

## Funcionalidades

- Cadastro e gestão de equipamentos médicos
- Agendamento e acompanhamento de manutenções preventivas e corretivas
- Gestão de ordens de serviço
- Controle de técnicos e empresas terceirizadas
- Gestão de peças e fornecedores
- Certificações e documentação regulatória
- Relatórios e dashboards

## Tecnologias

- Python 3.11+
- Flask
- SQLAlchemy
- JWT para autenticação
- SQLite (desenvolvimento) / PostgreSQL (produção)
- Docker para implantação

## Instalação e Configuração

### Requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- PostgreSQL (para ambiente de produção)

### Passos para Instalação

1. Clone o repositório:
```bash
git clone https://github.com/EquipamentosCerdil/api-manutencao-clinica.git
cd api-manutencao-clinica
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
# Desenvolvimento
export FLASK_ENV=development
export SECRET_KEY=sua-chave-secreta
export JWT_SECRET_KEY=sua-chave-jwt-secreta
export DATABASE_URL=sqlite:///dev.db

# Produção
export FLASK_ENV=production
export SECRET_KEY=sua-chave-secreta-producao
export JWT_SECRET_KEY=sua-chave-jwt-secreta-producao
export DATABASE_URL=postgresql://usuario:senha@localhost/manutencao_clinica
```

5. Inicialize o banco de dados:
```bash
flask db init
flask db migrate -m "Migração inicial"
flask db upgrade
```

6. Execute a aplicação:
```bash
flask run
```

## Deploy no Render (Nuvem)

Para implantar a API no Render:

1. Crie uma conta no [Render](https://render.com)
2. Crie um novo Web Service
3. Conecte ao repositório Git
4. Selecione "Docker" como Runtime
5. Configure as variáveis de ambiente no dashboard do Render
6. Defina o nome do serviço e região
7. Clique em "Create Web Service"

## Documentação

A documentação completa da API está disponível no arquivo `documentacao.md`.

## Testes

Para executar os testes automatizados:

```bash
python run_tests.py
```

## Licença

Uso privado - Todos os direitos reservados.
