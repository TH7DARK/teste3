from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import OrdemServico, Equipamento, Departamento, Usuario, Manutencao
from app import db
from app.utils.validators import validate_ordem_servico
import uuid
from datetime import datetime

ordem_servico_bp = Blueprint('ordem_servico', __name__)

@ordem_servico_bp.route('', methods=['GET'])
@jwt_required()
def get_ordens_servico():
    """Retorna todas as ordens de serviço cadastradas."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('size', 10, type=int)
        
        ordens = OrdemServico.query.paginate(page=page, per_page=per_page)
        
        result = {
            'items': [{
                'id': os.id,
                'codigo': os.codigo,
                'equipamento': os.equipamento.nome if os.equipamento else None,
                'departamento': os.departamento.nome if os.departamento else None,
                'solicitante': os.solicitante.nome if os.solicitante else None,
                'tipo_servico': os.tipo_servico,
                'prioridade': os.prioridade,
                'status': os.status,
                'data_abertura': os.data_abertura.isoformat() if os.data_abertura else None
            } for os in ordens.items],
            'total': ordens.total,
            'pages': ordens.pages,
            'current_page': ordens.page
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ordem_servico_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_ordem_servico(id):
    """Retorna uma ordem de serviço específica pelo ID."""
    try:
        ordem = OrdemServico.query.get(id)
        
        if not ordem:
            return jsonify({'error': 'Ordem de serviço não encontrada'}), 404
        
        result = {
            'id': ordem.id,
            'codigo': ordem.codigo,
            'equipamento_id': ordem.equipamento_id,
            'equipamento_nome': ordem.equipamento.nome if ordem.equipamento else None,
            'departamento_id': ordem.departamento_id,
            'departamento_nome': ordem.departamento.nome if ordem.departamento else None,
            'solicitante_id': ordem.solicitante_id,
            'solicitante_nome': ordem.solicitante.nome if ordem.solicitante else None,
            'tipo_servico': ordem.tipo_servico,
            'descricao_problema': ordem.descricao_problema,
            'prioridade': ordem.prioridade,
            'status': ordem.status,
            'data_abertura': ordem.data_abertura.isoformat() if ordem.data_abertura else None,
            'data_atribuicao': ordem.data_atribuicao.isoformat() if ordem.data_atribuicao else None,
            'data_inicio': ordem.data_inicio.isoformat() if ordem.data_inicio else None,
            'data_fim': ordem.data_fim.isoformat() if ordem.data_fim else None,
            'manutencao_id': ordem.manutencao_id,
            'anexos_url': ordem.anexos_url,
            'observacoes': ordem.observacoes,
            'avaliacao_satisfacao': ordem.avaliacao_satisfacao,
            'comentario_avaliacao': ordem.comentario_avaliacao,
            'criado_em': ordem.criado_em.isoformat(),
            'atualizado_em': ordem.atualizado_em.isoformat()
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ordem_servico_bp.route('', methods=['POST'])
@jwt_required()
def create_ordem_servico():
    """Cria uma nova ordem de serviço."""
    try:
        data = request.get_json()
        
        # Validação dos dados
        validation_result = validate_ordem_servico(data)
        if validation_result:
            return jsonify({'error': validation_result}), 400
        
        # Verificar se o equipamento existe
        equipamento = Equipamento.query.get(data.get('equipamento_id'))
        if not equipamento:
            return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        # Verificar se o departamento existe
        departamento = Departamento.query.get(data.get('departamento_id'))
        if not departamento:
            return jsonify({'error': 'Departamento não encontrado'}), 404
        
        # Verificar se o solicitante existe
        solicitante = Usuario.query.get(data.get('solicitante_id'))
        if not solicitante:
            return jsonify({'error': 'Solicitante não encontrado'}), 404
        
        # Gerar código único para a ordem de serviço
        ultimo_codigo = OrdemServico.query.order_by(OrdemServico.codigo.desc()).first()
        if ultimo_codigo:
            try:
                num = int(ultimo_codigo.codigo.split('-')[1]) + 1
                codigo = f"OS-{num:06d}"
            except:
                codigo = f"OS-{1:06d}"
        else:
            codigo = f"OS-{1:06d}"
        
        # Criar nova ordem de serviço
        nova_ordem = OrdemServico(
            id=str(uuid.uuid4()),
            codigo=codigo,
            equipamento_id=data.get('equipamento_id'),
            departamento_id=data.get('departamento_id'),
            solicitante_id=data.get('solicitante_id'),
            tipo_servico=data.get('tipo_servico'),
            descricao_problema=data.get('descricao_problema'),
            prioridade=data.get('prioridade', 'NORMAL'),
            status=data.get('status', 'ABERTA'),
            data_abertura=datetime.utcnow(),
            anexos_url=data.get('anexos_url', []),
            observacoes=data.get('observacoes')
        )
        
        db.session.add(nova_ordem)
        db.session.commit()
        
        return jsonify({
            'message': 'Ordem de serviço criada com sucesso',
            'id': nova_ordem.id,
            'codigo': nova_ordem.codigo
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ordem_servico_bp.route('/<id>', methods=['PUT'])
@jwt_required()
def update_ordem_servico(id):
    """Atualiza uma ordem de serviço existente."""
    try:
        ordem = OrdemServico.query.get(id)
        
        if not ordem:
            return jsonify({'error': 'Ordem de serviço não encontrada'}), 404
        
        data = request.get_json()
        
        # Validação dos dados
        validation_result = validate_ordem_servico(data, update=True)
        if validation_result:
            return jsonify({'error': validation_result}), 400
        
        # Verificar equipamento, se estiver sendo atualizado
        if data.get('equipamento_id') and data.get('equipamento_id') != ordem.equipamento_id:
            equipamento = Equipamento.query.get(data.get('equipamento_id'))
            if not equipamento:
                return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        # Verificar departamento, se estiver sendo atualizado
        if data.get('departamento_id') and data.get('departamento_id') != ordem.departamento_id:
            departamento = Departamento.query.get(data.get('departamento_id'))
            if not departamento:
                return jsonify({'error': 'Departamento não encontrado'}), 404
        
        # Verificar solicitante, se estiver sendo atualizado
        if data.get('solicitante_id') and data.get('solicitante_id') != ordem.solicitante_id:
            solicitante = Usuario.query.get(data.get('solicitante_id'))
            if not solicitante:
                return jsonify({'error': 'Solicitante não encontrado'}), 404
        
        # Verificar manutenção, se estiver sendo atualizada
        if data.get('manutencao_id') and data.get('manutencao_id') != ordem.manutencao_id:
            manutencao = Manutencao.query.get(data.get('manutencao_id'))
            if not manutencao:
                return jsonify({'error': 'Manutenção não encontrada'}), 404
        
        # Atualizar campos
        if data.get('equipamento_id'):
            ordem.equipamento_id = data.get('equipamento_id')
        if data.get('departamento_id'):
            ordem.departamento_id = data.get('departamento_id')
        if data.get('solicitante_id'):
            ordem.solicitante_id = data.get('solicitante_id')
        if data.get('tipo_servico'):
            ordem.tipo_servico = data.get('tipo_servico')
        if data.get('descricao_problema'):
            ordem.descricao_problema = data.get('descricao_problema')
        if data.get('prioridade'):
            ordem.prioridade = data.get('prioridade')
        if data.get('status'):
            ordem.status = data.get('status')
        if data.get('data_atribuicao'):
            ordem.data_atribuicao = datetime.fromisoformat(data.get('data_atribuicao'))
        if data.get('data_inicio'):
            ordem.data_inicio = datetime.fromisoformat(data.get('data_inicio'))
        if data.get('data_fim'):
            ordem.data_fim = datetime.fromisoformat(data.get('data_fim'))
        if 'manutencao_id' in data:
            ordem.manutencao_id = data.get('manutencao_id')
        if data.get('anexos_url'):
            ordem.anexos_url = data.get('anexos_url')
        if data.get('observacoes'):
            ordem.observacoes = data.get('observacoes')
        if 'avaliacao_satisfacao' in data:
            ordem.avaliacao_satisfacao = data.get('avaliacao_satisfacao')
        if data.get('comentario_avaliacao'):
            ordem.comentario_avaliacao = data.get('comentario_avaliacao')
        
        ordem.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Ordem de serviço atualizada com sucesso',
            'id': ordem.id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ordem_servico_bp.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete_ordem_servico(id):
    """Remove uma ordem de serviço do sistema."""
    try:
        ordem = OrdemServico.query.get(id)
        
        if not ordem:
            return jsonify({'error': 'Ordem de serviço não encontrada'}), 404
        
        # Verificar se a ordem está associada a uma manutenção
        if ordem.manutencao_id:
            return jsonify({
                'error': 'Não é possível excluir a ordem de serviço pois está associada a uma manutenção'
            }), 400
        
        db.session.delete(ordem)
        db.session.commit()
        
        return jsonify({
            'message': 'Ordem de serviço removida com sucesso'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ordem_servico_bp.route('/<id>/status', methods=['PUT'])
@jwt_required()
def update_ordem_servico_status(id):
    """Atualiza o status de uma ordem de serviço."""
    try:
        ordem = OrdemServico.query.get(id)
        
        if not ordem:
            return jsonify({'error': 'Ordem de serviço não encontrada'}), 404
        
        data = request.get_json()
        
        if not data or not data.get('status'):
            return jsonify({'error': 'Status não fornecido'}), 400
        
        status = data.get('status')
        status_validos = ['ABERTA', 'ATRIBUIDA', 'EM_ANDAMENTO', 'AGUARDANDO_PECAS', 'CONCLUIDA', 'CANCELADA']
        
        if status not in status_validos:
            return jsonify({'error': f'Status inválido. Valores permitidos: {", ".join(status_validos)}'}), 400
        
        # Atualizar status
        ordem.status = status
        
        # Atualizar datas conforme o status
        if status == 'ATRIBUIDA' and not ordem.data_atribuicao:
            ordem.data_atribuicao = datetime.utcnow()
        elif status == 'EM_ANDAMENTO' and not ordem.data_inicio:
            ordem.data_inicio = datetime.utcnow()
        elif status == 'CONCLUIDA' and not ordem.data_fim:
            ordem.data_fim = datetime.utcnow()
        
        ordem.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Status da ordem de serviço atualizado com sucesso',
            'id': ordem.id,
            'status': ordem.status
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ordem_servico_bp.route('/por-solicitante/<solicitante_id>', methods=['GET'])
@jwt_required()
def get_ordens_por_solicitante(solicitante_id):
    """Retorna todas as ordens de serviço de um solicitante específico."""
    try:
        solicitante = Usuario.query.get(solicitante_id)
        
        if not solicitante:
            return jsonify({'error': 'Solicitante não encontrado'}), 404
        
        ordens = OrdemServico.query.filter_by(solicitante_id=solicitante_id).all()
        
        result = [{
            'id': os.id,
            'codigo': os.codigo,
            'equipamento': os.equipamento.nome if os.equipamento else None,
            'tipo_servico': os.tipo_servico,
            'prioridade': os.prioridade,
            'status': os.status,
            'data_abertura': os.data_abertura.isoformat() if os.data_abertura else None
        } for os in ordens]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ordem_servico_bp.route('/por-departamento/<departamento_id>', methods=['GET'])
@jwt_required()
def get_ordens_por_departamento(departamento_id):
    """Retorna todas as ordens de serviço de um departamento específico."""
    try:
        departamento = Departamento.query.get(departamento_id)
        
        if not departamento:
            return jsonify({'error': 'Departamento não encontrado'}), 404
        
        ordens = OrdemServico.query.filter_by(departamento_id=departamento_id).all()
        
        result = [{
            'id': os.id,
            'codigo': os.codigo,
            'equipamento': os.equipamento.nome if os.equipamento else None,
            'solicitante': os.solicitante.nome if os.solicitante else None,
            'tipo_servico': os.tipo_servico,
            'prioridade': os.prioridade,
            'status': os.status,
            'data_abertura': os.data_abertura.isoformat() if os.data_abertura else None
        } for os in ordens]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ordem_servico_bp.route('/por-equipamento/<equipamento_id>', methods=['GET'])
@jwt_required()
def get_ordens_por_equipamento(equipamento_id):
    """Retorna todas as ordens de serviço de um equipamento específico."""
    try:
        equipamento = Equipamento.query.get(equipamento_id)
        
        if not equipamento:
            return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        ordens = OrdemServico.query.filter_by(equipamento_id=equipamento_id).all()
        
        result = [{
            'id': os.id,
            'codigo': os.codigo,
            'departamento': os.departamento.nome if os.departamento else None,
            'solicitante': os.solicitante.nome if os.solicitante else None,
            'tipo_servico': os.tipo_servico,
            'prioridade': os.prioridade,
            'status': os.status,
            'data_abertura': os.data_abertura.isoformat() if os.data_abertura else None
        } for os in ordens]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ordem_servico_bp.route('/por-status/<status>', methods=['GET'])
@jwt_required()
def get_ordens_por_status(status):
    """Retorna todas as ordens de serviço com um status específico."""
    try:
        status_validos = ['ABERTA', 'ATRIBUIDA', 'EM_ANDAMENTO', 'AGUARDANDO_PECAS', 'CONCLUIDA', 'CANCELADA']
        
        if status.upper() not in status_validos:
            return jsonify({'error': f'Status inválido. Valores permitidos: {", ".join(status_validos)}'}), 400
        
        ordens = OrdemServico.query.filter_by(status=status.upper()).all()
        
        result = [{
            'id': os.id,
            'codigo': os.codigo,
            'equipamento': os.equipamento.nome if os.equipamento else None,
            'departamento': os.departamento.nome if os.departamento else None,
            'solicitante': os.solicitante.nome if os.solicitante else None,
            'tipo_servico': os.tipo_servico,
            'prioridade': os.prioridade,
            'data_abertura': os.data_abertura.isoformat() if os.data_abertura else None
        } for os in ordens]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ordem_servico_bp.route('/<id>/avaliacao', methods=['POST'])
@jwt_required()
def avaliar_ordem_servico(id):
    """Registra a avaliação de satisfação para uma ordem de serviço concluída."""
    try:
        ordem = OrdemServico.query.get(id)
        
        if not ordem:
            return jsonify({'error': 'Ordem de serviço não encontrada'}), 404
        
        if ordem.status != 'CONCLUIDA':
            return jsonify({'error': 'Apenas ordens de serviço concluídas podem ser avaliadas'}), 400
        
        data = request.get_json()
        
        if not data or 'avaliacao' not in data:
            return jsonify({'error': 'Avaliação não fornecida'}), 400
        
        avaliacao = data.get('avaliacao')
        
        if not isinstance(avaliacao, int) or avaliacao < 1 or avaliacao > 5:
            return jsonify({'error': 'Avaliação deve ser um número inteiro entre 1 e 5'}), 400
        
        ordem.avaliacao_satisfacao = avaliacao
        ordem.comentario_avaliacao = data.get('comentario', '')
        ordem.atualizado_em = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Avaliação registrada com sucesso',
            'id': ordem.id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
