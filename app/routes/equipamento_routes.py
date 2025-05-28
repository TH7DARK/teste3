from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Equipamento, Departamento
from app import db
from app.utils.validators import validate_equipamento
from app.utils.helpers import generate_qrcode
import uuid
from datetime import datetime

equipamento_bp = Blueprint('equipamento', __name__)

@equipamento_bp.route('', methods=['GET'])
@jwt_required()
def get_equipamentos():
    """Retorna todos os equipamentos cadastrados."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('size', 10, type=int)
        
        equipamentos = Equipamento.query.paginate(page=page, per_page=per_page)
        
        result = {
            'items': [{
                'id': eq.id,
                'codigo': eq.codigo,
                'nome': eq.nome,
                'modelo': eq.modelo,
                'fabricante': eq.fabricante,
                'status': eq.status,
                'departamento': eq.departamento.nome if eq.departamento else None,
                'criticidade': eq.criticidade,
                'proxima_manutencao': eq.proxima_manutencao_planejada.isoformat() if eq.proxima_manutencao_planejada else None
            } for eq in equipamentos.items],
            'total': equipamentos.total,
            'pages': equipamentos.pages,
            'current_page': equipamentos.page
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipamento_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_equipamento(id):
    """Retorna um equipamento específico pelo ID."""
    try:
        equipamento = Equipamento.query.get(id)
        
        if not equipamento:
            return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        result = {
            'id': equipamento.id,
            'codigo': equipamento.codigo,
            'nome': equipamento.nome,
            'modelo': equipamento.modelo,
            'fabricante': equipamento.fabricante,
            'numero_serie': equipamento.numero_serie,
            'data_aquisicao': equipamento.data_aquisicao.isoformat() if equipamento.data_aquisicao else None,
            'data_garantia': equipamento.data_garantia.isoformat() if equipamento.data_garantia else None,
            'valor_aquisicao': float(equipamento.valor_aquisicao) if equipamento.valor_aquisicao else None,
            'departamento_id': equipamento.departamento_id,
            'departamento_nome': equipamento.departamento.nome if equipamento.departamento else None,
            'localizacao': equipamento.localizacao,
            'status': equipamento.status,
            'criticidade': equipamento.criticidade,
            'ultima_manutencao': equipamento.ultima_manutencao.isoformat() if equipamento.ultima_manutencao else None,
            'proxima_manutencao_planejada': equipamento.proxima_manutencao_planejada.isoformat() if equipamento.proxima_manutencao_planejada else None,
            'especificacoes_tecnicas': equipamento.especificacoes_tecnicas,
            'documentacao': equipamento.documentacao,
            'imagens_url': equipamento.imagens_url,
            'qr_code': equipamento.qr_code,
            'criado_em': equipamento.criado_em.isoformat(),
            'atualizado_em': equipamento.atualizado_em.isoformat()
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipamento_bp.route('', methods=['POST'])
@jwt_required()
def create_equipamento():
    """Cria um novo equipamento."""
    try:
        data = request.get_json()
        
        # Validação dos dados
        validation_result = validate_equipamento(data)
        if validation_result:
            return jsonify({'error': validation_result}), 400
        
        # Verificar se o departamento existe
        departamento = Departamento.query.get(data.get('departamento_id'))
        if not departamento:
            return jsonify({'error': 'Departamento não encontrado'}), 404
        
        # Verificar se já existe equipamento com o mesmo código ou número de série
        if Equipamento.query.filter_by(codigo=data.get('codigo')).first():
            return jsonify({'error': 'Já existe um equipamento com este código'}), 400
        
        if Equipamento.query.filter_by(numero_serie=data.get('numero_serie')).first():
            return jsonify({'error': 'Já existe um equipamento com este número de série'}), 400
        
        # Criar novo equipamento
        novo_equipamento = Equipamento(
            id=str(uuid.uuid4()),
            codigo=data.get('codigo'),
            nome=data.get('nome'),
            modelo=data.get('modelo'),
            fabricante=data.get('fabricante'),
            numero_serie=data.get('numero_serie'),
            data_aquisicao=datetime.fromisoformat(data.get('data_aquisicao')) if data.get('data_aquisicao') else None,
            data_garantia=datetime.fromisoformat(data.get('data_garantia')) if data.get('data_garantia') else None,
            valor_aquisicao=data.get('valor_aquisicao'),
            departamento_id=data.get('departamento_id'),
            localizacao=data.get('localizacao'),
            status=data.get('status', 'ATIVO'),
            criticidade=data.get('criticidade', 'MEDIA'),
            especificacoes_tecnicas=data.get('especificacoes_tecnicas'),
            documentacao=data.get('documentacao'),
            imagens_url=data.get('imagens_url')
        )
        
        # Gerar QR Code se solicitado
        if data.get('gerar_qrcode', False):
            qr_code_url = generate_qrcode(novo_equipamento.id, novo_equipamento.codigo)
            novo_equipamento.qr_code = qr_code_url
        
        db.session.add(novo_equipamento)
        db.session.commit()
        
        return jsonify({
            'message': 'Equipamento criado com sucesso',
            'id': novo_equipamento.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipamento_bp.route('/<id>', methods=['PUT'])
@jwt_required()
def update_equipamento(id):
    """Atualiza um equipamento existente."""
    try:
        equipamento = Equipamento.query.get(id)
        
        if not equipamento:
            return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        data = request.get_json()
        
        # Validação dos dados
        validation_result = validate_equipamento(data, update=True)
        if validation_result:
            return jsonify({'error': validation_result}), 400
        
        # Verificar se o departamento existe, se estiver sendo atualizado
        if data.get('departamento_id') and data.get('departamento_id') != equipamento.departamento_id:
            departamento = Departamento.query.get(data.get('departamento_id'))
            if not departamento:
                return jsonify({'error': 'Departamento não encontrado'}), 404
        
        # Verificar duplicidade de código ou número de série
        if data.get('codigo') and data.get('codigo') != equipamento.codigo:
            if Equipamento.query.filter_by(codigo=data.get('codigo')).first():
                return jsonify({'error': 'Já existe um equipamento com este código'}), 400
        
        if data.get('numero_serie') and data.get('numero_serie') != equipamento.numero_serie:
            if Equipamento.query.filter_by(numero_serie=data.get('numero_serie')).first():
                return jsonify({'error': 'Já existe um equipamento com este número de série'}), 400
        
        # Atualizar campos
        if data.get('codigo'):
            equipamento.codigo = data.get('codigo')
        if data.get('nome'):
            equipamento.nome = data.get('nome')
        if data.get('modelo'):
            equipamento.modelo = data.get('modelo')
        if data.get('fabricante'):
            equipamento.fabricante = data.get('fabricante')
        if data.get('numero_serie'):
            equipamento.numero_serie = data.get('numero_serie')
        if data.get('data_aquisicao'):
            equipamento.data_aquisicao = datetime.fromisoformat(data.get('data_aquisicao'))
        if data.get('data_garantia'):
            equipamento.data_garantia = datetime.fromisoformat(data.get('data_garantia'))
        if data.get('valor_aquisicao'):
            equipamento.valor_aquisicao = data.get('valor_aquisicao')
        if data.get('departamento_id'):
            equipamento.departamento_id = data.get('departamento_id')
        if data.get('localizacao'):
            equipamento.localizacao = data.get('localizacao')
        if data.get('status'):
            equipamento.status = data.get('status')
        if data.get('criticidade'):
            equipamento.criticidade = data.get('criticidade')
        if data.get('especificacoes_tecnicas'):
            equipamento.especificacoes_tecnicas = data.get('especificacoes_tecnicas')
        if data.get('documentacao'):
            equipamento.documentacao = data.get('documentacao')
        if data.get('imagens_url'):
            equipamento.imagens_url = data.get('imagens_url')
        
        # Atualizar QR Code se solicitado
        if data.get('gerar_qrcode', False):
            qr_code_url = generate_qrcode(equipamento.id, equipamento.codigo)
            equipamento.qr_code = qr_code_url
        
        equipamento.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Equipamento atualizado com sucesso',
            'id': equipamento.id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipamento_bp.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete_equipamento(id):
    """Remove um equipamento do sistema."""
    try:
        equipamento = Equipamento.query.get(id)
        
        if not equipamento:
            return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        # Verificar se existem manutenções ou ordens de serviço associadas
        if equipamento.manutencoes or equipamento.ordens_servico:
            return jsonify({
                'error': 'Não é possível excluir o equipamento pois existem manutenções ou ordens de serviço associadas'
            }), 400
        
        db.session.delete(equipamento)
        db.session.commit()
        
        return jsonify({
            'message': 'Equipamento removido com sucesso'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipamento_bp.route('/<id>/historico', methods=['GET'])
@jwt_required()
def get_equipamento_historico(id):
    """Retorna o histórico de manutenções de um equipamento."""
    try:
        equipamento = Equipamento.query.get(id)
        
        if not equipamento:
            return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        manutencoes = equipamento.manutencoes
        
        result = [{
            'id': m.id,
            'tipo_manutencao': m.tipo_manutencao,
            'status': m.status,
            'data_inicio': m.data_inicio.isoformat() if m.data_inicio else None,
            'data_fim': m.data_fim.isoformat() if m.data_fim else None,
            'tecnico': m.tecnico.nome if m.tecnico else (m.tecnico_externo.nome if m.tecnico_externo else None),
            'custo_total': float(m.custo_total) if m.custo_total else 0,
            'tempo_parada': m.tempo_parada
        } for m in manutencoes]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipamento_bp.route('/<id>/gerar-qrcode', methods=['POST'])
@jwt_required()
def gerar_qrcode_equipamento(id):
    """Gera ou regenera o QR Code para um equipamento."""
    try:
        equipamento = Equipamento.query.get(id)
        
        if not equipamento:
            return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        qr_code_url = generate_qrcode(equipamento.id, equipamento.codigo)
        equipamento.qr_code = qr_code_url
        
        db.session.commit()
        
        return jsonify({
            'message': 'QR Code gerado com sucesso',
            'qr_code_url': qr_code_url
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipamento_bp.route('/por-departamento/<departamento_id>', methods=['GET'])
@jwt_required()
def get_equipamentos_por_departamento(departamento_id):
    """Retorna todos os equipamentos de um departamento específico."""
    try:
        departamento = Departamento.query.get(departamento_id)
        
        if not departamento:
            return jsonify({'error': 'Departamento não encontrado'}), 404
        
        equipamentos = Equipamento.query.filter_by(departamento_id=departamento_id).all()
        
        result = [{
            'id': eq.id,
            'codigo': eq.codigo,
            'nome': eq.nome,
            'modelo': eq.modelo,
            'status': eq.status,
            'criticidade': eq.criticidade
        } for eq in equipamentos]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipamento_bp.route('/por-status/<status>', methods=['GET'])
@jwt_required()
def get_equipamentos_por_status(status):
    """Retorna todos os equipamentos com um status específico."""
    try:
        equipamentos = Equipamento.query.filter_by(status=status.upper()).all()
        
        result = [{
            'id': eq.id,
            'codigo': eq.codigo,
            'nome': eq.nome,
            'modelo': eq.modelo,
            'departamento': eq.departamento.nome if eq.departamento else None,
            'criticidade': eq.criticidade
        } for eq in equipamentos]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipamento_bp.route('/busca', methods=['GET'])
@jwt_required()
def buscar_equipamentos():
    """Busca equipamentos por termo em vários campos."""
    try:
        termo = request.args.get('termo', '')
        
        if not termo:
            return jsonify({'error': 'Termo de busca não fornecido'}), 400
        
        # Busca em vários campos
        equipamentos = Equipamento.query.filter(
            (Equipamento.codigo.ilike(f'%{termo}%')) |
            (Equipamento.nome.ilike(f'%{termo}%')) |
            (Equipamento.modelo.ilike(f'%{termo}%')) |
            (Equipamento.fabricante.ilike(f'%{termo}%')) |
            (Equipamento.numero_serie.ilike(f'%{termo}%'))
        ).all()
        
        result = [{
            'id': eq.id,
            'codigo': eq.codigo,
            'nome': eq.nome,
            'modelo': eq.modelo,
            'fabricante': eq.fabricante,
            'numero_serie': eq.numero_serie,
            'departamento': eq.departamento.nome if eq.departamento else None,
            'status': eq.status
        } for eq in equipamentos]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
