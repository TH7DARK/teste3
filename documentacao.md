# Documentação da API de Manutenção de Equipamentos Clínicos

## Introdução

Esta documentação descreve a API desenvolvida para administração de manutenções de equipamentos em uma clínica médica. A API foi baseada no modelo EFORT (Sistema Effort) e adaptada para o contexto específico de equipamentos médicos e clínicos.

A API permite gerenciar todo o ciclo de vida da manutenção de equipamentos, incluindo:
- Cadastro e gestão de equipamentos
- Agendamento e acompanhamento de manutenções preventivas e corretivas
- Gestão de ordens de serviço
- Controle de técnicos e empresas terceirizadas
- Gestão de peças e fornecedores
- Certificações e documentação regulatória
- Relatórios e dashboards

## Estrutura do Projeto

```
api_manutencao_clinica/
├── app/
│   ├── models/         # Modelos de dados
│   ├── controllers/    # Controladores
│   ├── routes/         # Rotas da API
│   ├── services/       # Serviços de negócio
│   ├── utils/          # Utilitários
│   └── config/         # Configurações
├── tests/              # Testes automatizados
├── uploads/            # Arquivos enviados
└── requirements.txt    # Dependências
```

## Tecnologias Utilizadas

- **Python 3.11+**: Linguagem de programação
- **Flask**: Framework web
- **SQLAlchemy**: ORM para acesso ao banco de dados
- **Flask-RESTful**: Extensão para criação de APIs RESTful
- **Flask-JWT-Extended**: Autenticação JWT
- **Flask-Migrate**: Migrações de banco de dados
- **PostgreSQL**: Banco de dados (produção)
- **SQLite**: Banco de dados (desenvolvimento/testes)

## Instalação e Configuração

### Requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- PostgreSQL (para ambiente de produção)

### Passos para Instalação

1. Clone o repositório:
```bash
git clone https://github.com/sua-organizacao/api-manutencao-clinica.git
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

## Autenticação

A API utiliza autenticação JWT (JSON Web Token). Para acessar os endpoints protegidos, é necessário obter um token de acesso através do endpoint de login.

### Obter Token de Acesso

```
POST /api/auth/login
```

**Corpo da Requisição:**
```json
{
  "email": "usuario@exemplo.com",
  "senha": "senha123"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nome": "Nome do Usuário",
    "email": "usuario@exemplo.com",
    "perfil": "ADMIN"
  }
}
```

### Renovar Token de Acesso

```
POST /api/auth/refresh-token
```

**Cabeçalhos:**
```
Authorization: Bearer <refresh_token>
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Endpoints Principais

### Equipamentos

#### Listar Equipamentos
```
GET /api/equipamentos
```

**Parâmetros de Consulta:**
- `page`: Número da página (padrão: 1)
- `size`: Tamanho da página (padrão: 10)

**Resposta:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "codigo": "EQ-001",
      "nome": "Aparelho de Raio-X",
      "modelo": "RX-2000",
      "fabricante": "MedTech",
      "status": "ATIVO",
      "departamento": "Radiologia",
      "criticidade": "ALTA",
      "proxima_manutencao": "2025-06-15"
    },
    ...
  ],
  "total": 25,
  "pages": 3,
  "current_page": 1
}
```

#### Obter Equipamento por ID
```
GET /api/equipamentos/{id}
```

**Resposta:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "codigo": "EQ-001",
  "nome": "Aparelho de Raio-X",
  "modelo": "RX-2000",
  "fabricante": "MedTech",
  "numero_serie": "SN12345",
  "data_aquisicao": "2023-01-15",
  "data_garantia": "2025-01-15",
  "valor_aquisicao": 150000.00,
  "departamento_id": "550e8400-e29b-41d4-a716-446655440001",
  "departamento_nome": "Radiologia",
  "localizacao": "Sala 101",
  "status": "ATIVO",
  "criticidade": "ALTA",
  "ultima_manutencao": "2025-01-10",
  "proxima_manutencao_planejada": "2025-06-15",
  "especificacoes_tecnicas": {...},
  "documentacao": {...},
  "imagens_url": [...],
  "qr_code": "/uploads/qrcodes/qrcode_EQ-001_20250528123456.png",
  "criado_em": "2025-01-01T10:00:00",
  "atualizado_em": "2025-05-28T10:00:00"
}
```

#### Criar Equipamento
```
POST /api/equipamentos
```

**Corpo da Requisição:**
```json
{
  "codigo": "EQ-002",
  "nome": "Ultrassom",
  "modelo": "US-3000",
  "fabricante": "MedTech",
  "numero_serie": "SN67890",
  "data_aquisicao": "2024-03-10",
  "data_garantia": "2026-03-10",
  "valor_aquisicao": 80000.00,
  "departamento_id": "550e8400-e29b-41d4-a716-446655440002",
  "localizacao": "Sala 202",
  "status": "ATIVO",
  "criticidade": "MEDIA",
  "especificacoes_tecnicas": {...},
  "documentacao": {...},
  "gerar_qrcode": true
}
```

**Resposta:**
```json
{
  "message": "Equipamento criado com sucesso",
  "id": "550e8400-e29b-41d4-a716-446655440003"
}
```

#### Atualizar Equipamento
```
PUT /api/equipamentos/{id}
```

**Corpo da Requisição:**
```json
{
  "nome": "Ultrassom Portátil",
  "localizacao": "Sala 203",
  "status": "EM_MANUTENCAO"
}
```

**Resposta:**
```json
{
  "message": "Equipamento atualizado com sucesso",
  "id": "550e8400-e29b-41d4-a716-446655440003"
}
```

#### Excluir Equipamento
```
DELETE /api/equipamentos/{id}
```

**Resposta:**
```json
{
  "message": "Equipamento removido com sucesso"
}
```

### Manutenções

#### Listar Manutenções
```
GET /api/manutencoes
```

**Parâmetros de Consulta:**
- `page`: Número da página (padrão: 1)
- `size`: Tamanho da página (padrão: 10)

**Resposta:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440004",
      "equipamento": "Aparelho de Raio-X",
      "tipo_manutencao": "PREVENTIVA",
      "status": "AGENDADA",
      "prioridade": "NORMAL",
      "data_agendamento": "2025-06-15T09:00:00",
      "data_inicio": null,
      "data_fim": null,
      "tecnico": "João Silva"
    },
    ...
  ],
  "total": 15,
  "pages": 2,
  "current_page": 1
}
```

#### Obter Manutenção por ID
```
GET /api/manutencoes/{id}
```

**Resposta:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "equipamento_id": "550e8400-e29b-41d4-a716-446655440000",
  "equipamento_nome": "Aparelho de Raio-X",
  "tipo_manutencao": "PREVENTIVA",
  "status": "AGENDADA",
  "prioridade": "NORMAL",
  "descricao": "Manutenção preventiva semestral",
  "data_agendamento": "2025-06-15T09:00:00",
  "data_inicio": null,
  "data_fim": null,
  "tecnico_id": "550e8400-e29b-41d4-a716-446655440005",
  "tecnico_nome": "João Silva",
  "tecnico_externo_id": null,
  "tecnico_externo_nome": null,
  "empresa_externa_id": null,
  "empresa_externa_nome": null,
  "custo_mao_de_obra": 0.00,
  "custo_pecas": 0.00,
  "custo_total": 0.00,
  "tempo_parada": 0,
  "observacoes": null,
  "pecas_substituidas": [],
  "anexos_url": [],
  "assinatura_responsavel_url": null,
  "assinatura_tecnico_url": null,
  "criado_em": "2025-05-28T10:00:00",
  "atualizado_em": "2025-05-28T10:00:00"
}
```

#### Criar Manutenção
```
POST /api/manutencoes
```

**Corpo da Requisição:**
```json
{
  "equipamento_id": "550e8400-e29b-41d4-a716-446655440000",
  "tipo_manutencao": "PREVENTIVA",
  "descricao": "Manutenção preventiva semestral",
  "data_agendamento": "2025-06-15T09:00:00",
  "tecnico_id": "550e8400-e29b-41d4-a716-446655440005",
  "prioridade": "NORMAL"
}
```

**Resposta:**
```json
{
  "message": "Manutenção criada com sucesso",
  "id": "550e8400-e29b-41d4-a716-446655440004"
}
```

#### Atualizar Status da Manutenção
```
PUT /api/manutencoes/{id}/status
```

**Corpo da Requisição:**
```json
{
  "status": "EM_ANDAMENTO"
}
```

**Resposta:**
```json
{
  "message": "Status da manutenção atualizado com sucesso",
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "status": "EM_ANDAMENTO"
}
```

### Ordens de Serviço

#### Listar Ordens de Serviço
```
GET /api/ordens-servico
```

**Parâmetros de Consulta:**
- `page`: Número da página (padrão: 1)
- `size`: Tamanho da página (padrão: 10)

**Resposta:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440006",
      "codigo": "OS-000001",
      "equipamento": "Ultrassom",
      "departamento": "Obstetrícia",
      "solicitante": "Maria Santos",
      "tipo_servico": "MANUTENCAO_CORRETIVA",
      "prioridade": "ALTA",
      "status": "ABERTA",
      "data_abertura": "2025-05-28T08:30:00"
    },
    ...
  ],
  "total": 10,
  "pages": 1,
  "current_page": 1
}
```

#### Criar Ordem de Serviço
```
POST /api/ordens-servico
```

**Corpo da Requisição:**
```json
{
  "equipamento_id": "550e8400-e29b-41d4-a716-446655440003",
  "departamento_id": "550e8400-e29b-41d4-a716-446655440002",
  "solicitante_id": "550e8400-e29b-41d4-a716-446655440007",
  "tipo_servico": "MANUTENCAO_CORRETIVA",
  "descricao_problema": "Equipamento apresentando ruído anormal durante exames",
  "prioridade": "ALTA"
}
```

**Resposta:**
```json
{
  "message": "Ordem de serviço criada com sucesso",
  "id": "550e8400-e29b-41d4-a716-446655440006",
  "codigo": "OS-000001"
}
```

#### Atualizar Status da Ordem de Serviço
```
PUT /api/ordens-servico/{id}/status
```

**Corpo da Requisição:**
```json
{
  "status": "ATRIBUIDA"
}
```

**Resposta:**
```json
{
  "message": "Status da ordem de serviço atualizado com sucesso",
  "id": "550e8400-e29b-41d4-a716-446655440006",
  "status": "ATRIBUIDA"
}
```

#### Avaliar Ordem de Serviço
```
POST /api/ordens-servico/{id}/avaliacao
```

**Corpo da Requisição:**
```json
{
  "avaliacao": 5,
  "comentario": "Serviço excelente, rápido e eficiente"
}
```

**Resposta:**
```json
{
  "message": "Avaliação registrada com sucesso",
  "id": "550e8400-e29b-41d4-a716-446655440006"
}
```

## Relatórios e Dashboards

A API oferece endpoints para geração de relatórios e visualização de dashboards:

```
GET /api/relatorios/manutencoes?inicio=2025-01-01&fim=2025-05-31
GET /api/relatorios/equipamentos-criticos
GET /api/relatorios/tempo-medio-atendimento?inicio=2025-01-01&fim=2025-05-31
GET /api/relatorios/custos-manutencao?inicio=2025-01-01&fim=2025-05-31
GET /api/relatorios/disponibilidade-equipamentos?inicio=2025-01-01&fim=2025-05-31
GET /api/relatorios/certificados-vencidos
GET /api/relatorios/manutencoes-preventivas-pendentes
GET /api/relatorios/desempenho-tecnicos?inicio=2025-01-01&fim=2025-05-31
GET /api/relatorios/satisfacao-usuarios?inicio=2025-01-01&fim=2025-05-31

GET /api/dashboards/visao-geral
GET /api/dashboards/manutencoes-por-status
GET /api/dashboards/equipamentos-por-status
GET /api/dashboards/ordens-servico-por-prioridade
GET /api/dashboards/custos-mensais?ano=2025
GET /api/dashboards/tempo-medio-resolucao?inicio=2025-01-01&fim=2025-05-31
GET /api/dashboards/indicadores-desempenho?inicio=2025-01-01&fim=2025-05-31
```

## Códigos de Status HTTP

A API utiliza os seguintes códigos de status HTTP:

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Requisição inválida ou mal-formada
- `401 Unauthorized`: Autenticação necessária
- `403 Forbidden`: Acesso negado
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro interno do servidor

## Testes

O projeto inclui testes automatizados para validar o funcionamento da API. Para executar os testes:

```bash
python run_tests.py
```

## Considerações de Segurança

- Todas as senhas são armazenadas com hash seguro
- Autenticação JWT com tokens de acesso e refresh
- Validação de entrada em todos os endpoints
- Controle de acesso baseado em perfis de usuário
- Logs de auditoria para operações críticas

## Suporte e Contato

Para suporte técnico ou dúvidas sobre a API, entre em contato:

- Email: suporte@manutencao-clinica.com
- Telefone: (11) 1234-5678

---

© 2025 API de Manutenção de Equipamentos Clínicos. Todos os direitos reservados.
