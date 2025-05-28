from datetime import datetime
import uuid
from app import db

class BaseModel(db.Model):
    """Modelo base com campos comuns para todos os modelos."""
    __abstract__ = True
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Equipamento(BaseModel):
    """Modelo para equipamentos médicos e clínicos."""
    __tablename__ = 'equipamentos'
    
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    fabricante = db.Column(db.String(100), nullable=False)
    numero_serie = db.Column(db.String(100), unique=True, nullable=False)
    data_aquisicao = db.Column(db.Date, nullable=False)
    data_garantia = db.Column(db.Date)
    valor_aquisicao = db.Column(db.Numeric(10, 2))
    departamento_id = db.Column(db.String(36), db.ForeignKey('departamentos.id'), nullable=False)
    localizacao = db.Column(db.String(200))
    status = db.Column(db.String(20), nullable=False, default='ATIVO')
    criticidade = db.Column(db.String(20), nullable=False, default='MEDIA')
    ultima_manutencao = db.Column(db.Date)
    proxima_manutencao_planejada = db.Column(db.Date)
    especificacoes_tecnicas = db.Column(db.JSON)
    documentacao = db.Column(db.JSON)
    imagens_url = db.Column(db.JSON)
    qr_code = db.Column(db.String(255))
    
    # Relacionamentos
    departamento = db.relationship('Departamento', backref=db.backref('equipamentos', lazy=True))
    manutencoes = db.relationship('Manutencao', backref='equipamento', lazy=True)
    ordens_servico = db.relationship('OrdemServico', backref='equipamento', lazy=True)
    certificados = db.relationship('Certificado', backref='equipamento', lazy=True)
    programas_manutencao = db.relationship('ProgramaManutencao', backref='equipamento', lazy=True)
    
    def __repr__(self):
        return f'<Equipamento {self.codigo} - {self.nome}>'

class Departamento(BaseModel):
    """Modelo para departamentos ou setores da clínica."""
    __tablename__ = 'departamentos'
    
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    responsavel_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'))
    localizacao = db.Column(db.String(200))
    
    # Relacionamentos
    responsavel = db.relationship('Usuario', backref=db.backref('departamentos_responsavel', lazy=True))
    
    def __repr__(self):
        return f'<Departamento {self.nome}>'

class Manutencao(BaseModel):
    """Modelo para registros de manutenção de equipamentos."""
    __tablename__ = 'manutencoes'
    
    equipamento_id = db.Column(db.String(36), db.ForeignKey('equipamentos.id'), nullable=False)
    tipo_manutencao = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='AGENDADA')
    prioridade = db.Column(db.String(20), nullable=False, default='NORMAL')
    descricao = db.Column(db.Text, nullable=False)
    data_agendamento = db.Column(db.DateTime, nullable=False)
    data_inicio = db.Column(db.DateTime)
    data_fim = db.Column(db.DateTime)
    tecnico_id = db.Column(db.String(36), db.ForeignKey('tecnicos.id'))
    tecnico_externo_id = db.Column(db.String(36), db.ForeignKey('tecnicos_externos.id'))
    empresa_externa_id = db.Column(db.String(36), db.ForeignKey('empresas_externas.id'))
    custo_mao_de_obra = db.Column(db.Numeric(10, 2), default=0)
    custo_pecas = db.Column(db.Numeric(10, 2), default=0)
    custo_total = db.Column(db.Numeric(10, 2), default=0)
    tempo_parada = db.Column(db.Integer, default=0)  # em minutos
    observacoes = db.Column(db.Text)
    pecas_substituidas = db.Column(db.JSON)
    anexos_url = db.Column(db.JSON)
    assinatura_responsavel_url = db.Column(db.String(255))
    assinatura_tecnico_url = db.Column(db.String(255))
    
    # Relacionamentos
    tecnico = db.relationship('Tecnico', backref=db.backref('manutencoes', lazy=True))
    tecnico_externo = db.relationship('TecnicoExterno', backref=db.backref('manutencoes', lazy=True))
    empresa_externa = db.relationship('EmpresaExterna', backref=db.backref('manutencoes', lazy=True))
    ordem_servico = db.relationship('OrdemServico', backref=db.backref('manutencao', uselist=False), lazy=True)
    
    def __repr__(self):
        return f'<Manutencao {self.id} - {self.tipo_manutencao}>'

class Tecnico(BaseModel):
    """Modelo para técnicos internos responsáveis por manutenções."""
    __tablename__ = 'tecnicos'
    
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    especialidades = db.Column(db.JSON)
    certificacoes = db.Column(db.JSON)
    interno = db.Column(db.Boolean, default=True)
    disponivel = db.Column(db.Boolean, default=True)
    usuario_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'))
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref=db.backref('tecnico', uselist=False), lazy=True)
    
    def __repr__(self):
        return f'<Tecnico {self.nome}>'

class EmpresaExterna(BaseModel):
    """Modelo para empresas terceirizadas de manutenção."""
    __tablename__ = 'empresas_externas'
    
    razao_social = db.Column(db.String(200), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    endereco = db.Column(db.String(255))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    contato_principal = db.Column(db.String(100))
    especialidades = db.Column(db.JSON)
    contrato_url = db.Column(db.String(255))
    data_inicio_contrato = db.Column(db.Date)
    data_fim_contrato = db.Column(db.Date)
    
    # Relacionamentos
    tecnicos_externos = db.relationship('TecnicoExterno', backref='empresa', lazy=True)
    
    def __repr__(self):
        return f'<EmpresaExterna {self.razao_social}>'

class TecnicoExterno(BaseModel):
    """Modelo para técnicos de empresas terceirizadas."""
    __tablename__ = 'tecnicos_externos'
    
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    empresa_id = db.Column(db.String(36), db.ForeignKey('empresas_externas.id'), nullable=False)
    especialidades = db.Column(db.JSON)
    certificacoes = db.Column(db.JSON)
    
    def __repr__(self):
        return f'<TecnicoExterno {self.nome}>'

class Peca(BaseModel):
    """Modelo para peças e componentes de reposição."""
    __tablename__ = 'pecas'
    
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    fabricante = db.Column(db.String(100))
    modelo_compativel = db.Column(db.JSON)
    quantidade_estoque = db.Column(db.Integer, default=0)
    localizacao_estoque = db.Column(db.String(100))
    preco_unitario = db.Column(db.Numeric(10, 2))
    fornecedor_id = db.Column(db.String(36), db.ForeignKey('fornecedores.id'))
    ponto_reposicao = db.Column(db.Integer, default=5)
    
    # Relacionamentos
    fornecedor = db.relationship('Fornecedor', backref=db.backref('pecas', lazy=True))
    
    def __repr__(self):
        return f'<Peca {self.codigo} - {self.nome}>'

class Fornecedor(BaseModel):
    """Modelo para fornecedores de peças e equipamentos."""
    __tablename__ = 'fornecedores'
    
    razao_social = db.Column(db.String(200), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    endereco = db.Column(db.String(255))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    contato_principal = db.Column(db.String(100))
    categorias_atendidas = db.Column(db.JSON)
    
    def __repr__(self):
        return f'<Fornecedor {self.razao_social}>'

class OrdemServico(BaseModel):
    """Modelo para ordens de serviço de manutenção."""
    __tablename__ = 'ordens_servico'
    
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    equipamento_id = db.Column(db.String(36), db.ForeignKey('equipamentos.id'), nullable=False)
    departamento_id = db.Column(db.String(36), db.ForeignKey('departamentos.id'), nullable=False)
    solicitante_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'), nullable=False)
    tipo_servico = db.Column(db.String(30), nullable=False)
    descricao_problema = db.Column(db.Text, nullable=False)
    prioridade = db.Column(db.String(20), nullable=False, default='NORMAL')
    status = db.Column(db.String(20), nullable=False, default='ABERTA')
    data_abertura = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_atribuicao = db.Column(db.DateTime)
    data_inicio = db.Column(db.DateTime)
    data_fim = db.Column(db.DateTime)
    manutencao_id = db.Column(db.String(36), db.ForeignKey('manutencoes.id'))
    anexos_url = db.Column(db.JSON)
    observacoes = db.Column(db.Text)
    avaliacao_satisfacao = db.Column(db.Integer)
    comentario_avaliacao = db.Column(db.Text)
    
    # Relacionamentos
    departamento = db.relationship('Departamento', backref=db.backref('ordens_servico', lazy=True))
    solicitante = db.relationship('Usuario', backref=db.backref('ordens_servico', lazy=True))
    
    def __repr__(self):
        return f'<OrdemServico {self.codigo}>'

class Usuario(BaseModel):
    """Modelo para usuários do sistema."""
    __tablename__ = 'usuarios'
    
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.String(100))
    departamento_id = db.Column(db.String(36), db.ForeignKey('departamentos.id'))
    telefone = db.Column(db.String(20))
    perfil = db.Column(db.String(20), nullable=False, default='SOLICITANTE')
    ativo = db.Column(db.Boolean, default=True)
    ultimo_acesso = db.Column(db.DateTime)
    
    # Relacionamentos
    departamento = db.relationship('Departamento', backref=db.backref('usuarios', lazy=True), 
                                  foreign_keys=[departamento_id])
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'

class ProgramaManutencao(BaseModel):
    """Modelo para programas de manutenção preventiva."""
    __tablename__ = 'programas_manutencao'
    
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    equipamento_id = db.Column(db.String(36), db.ForeignKey('equipamentos.id'))
    tipo_equipamento = db.Column(db.String(100))
    frequencia = db.Column(db.String(20), nullable=False)
    checklist = db.Column(db.JSON)
    duracao_estimada = db.Column(db.Integer)  # em minutos
    responsavel_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'))
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    responsavel = db.relationship('Usuario', backref=db.backref('programas_manutencao', lazy=True))
    
    def __repr__(self):
        return f'<ProgramaManutencao {self.nome}>'

class Certificado(BaseModel):
    """Modelo para certificados e documentos regulatórios."""
    __tablename__ = 'certificados'
    
    equipamento_id = db.Column(db.String(36), db.ForeignKey('equipamentos.id'), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    numero = db.Column(db.String(100))
    data_emissao = db.Column(db.Date, nullable=False)
    data_validade = db.Column(db.Date, nullable=False)
    emissor = db.Column(db.String(100), nullable=False)
    documento_url = db.Column(db.String(255))
    observacoes = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='VALIDO')
    
    def __repr__(self):
        return f'<Certificado {self.tipo} - {self.numero}>'

class Notificacao(BaseModel):
    """Modelo para notificações do sistema."""
    __tablename__ = 'notificacoes'
    
    usuario_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    lida = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(255))
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref=db.backref('notificacoes', lazy=True))
    
    def __repr__(self):
        return f'<Notificacao {self.titulo}>'
