from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Manutencao, Equipamento, Tecnico, TecnicoExterno, EmpresaExterna
from app import db
from app.utils.validators import validate_manutencao
import uuid
from datetime import datetime

manutencao_bp = Blueprint('manutencao', __name__)

@manutencao_bp.route('', methods=['GET'])
@jwt_required()
def get_manutencoes():
    """Retorna todas as manutenções cadastradas."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('size', 10, type=int)
        
        manutencoes = Manutencao.query.paginate(page=page, per_page=per_page)
        
        result = {
            'items': [{
                'id': m.id,
                'equipamento': m.equipamento.nome if m.equipamento else None,
                'tipo_manutencao': m.tipo_manutencao,
                'status': m.status,
                'prioridade': m.prioridade,
                'data_agendamento': m.data_agendamento.isoformat() if m.data_agendamento else None,
                'data_inicio': m.data_inicio.isoformat() if m.data_inicio else None,
                'data_fim': m.data_fim.isoformat() if m.data_fim else None,
                'tecnico': m.tecnico.nome if m.tecnico else (m.tecnico_externo.nome if m.tecnico_externo else None)
            } for m in manutencoes.items],
            'total': manutencoes.total,
            'pages': manutencoes.pages,
            'current_page': manutencoes.page
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@manutencao_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_manutencao(id):
    """Retorna uma manutenção específica pelo ID."""
    try:
        manutencao = Manutencao.query.get(id)
        
        if not manutencao:
            return jsonify({'error': 'Manutenção não encontrada'}), 404
        
        result = {
            'id': manutencao.id,
            'equipamento_id': manutencao.equipamento_id,
            'equipamento_nome': manutencao.equipamento.nome if manutencao.equipamento else None,
            'tipo_manutencao': manutencao.tipo_manutencao,
            'status': manutencao.status,
            'prioridade': manutencao.prioridade,
            'descricao': manutencao.descricao,
            'data_agendamento': manutencao.data_agendamento.isoformat() if manutencao.data_agendamento else None,
            'data_inicio': manutencao.data_inicio.isoformat() if manutencao.data_inicio else None,
            'data_fim': manutencao.data_fim.isoformat() if manutencao.data_fim else None,
            'tecnico_id': manutencao.tecnico_id,
            'tecnico_nome': manutencao.tecnico.nome if manutencao.tecnico else None,
            'tecnico_externo_id': manutencao.tecnico_externo_id,
            'tecnico_externo_nome': manutencao.tecnico_externo.nome if manutencao.tecnico_externo else None,
            'empresa_externa_id': manutencao.empresa_externa_id,
            'empresa_externa_nome': manutencao.empresa_externa.razao_social if manutencao.empresa_externa else None,
            'custo_mao_de_obra': float(manutencao.custo_mao_de_obra) if manutencao.custo_mao_de_obra else 0,
            'custo_pecas': float(manutencao.custo_pecas) if manutencao.custo_pecas else 0,
            'custo_total': float(manutencao.custo_total) if manutencao.custo_total else 0,
            'tempo_parada': manutencao.tempo_parada,
            'observacoes': manutencao.observacoes,
            'pecas_substituidas': manutencao.pecas_substituidas,
            'anexos_url': manutencao.anexos_url,
            'assinatura_responsavel_url': manutencao.assinatura_responsavel_url,
            'assinatura_tecnico_url': manutencao.assinatura_tecnico_url,
            'criado_em': manutencao.criado_em.isoformat(),
            'atualizado_em': manutencao.atualizado_em.isoformat()
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@manutencao_bp.route('', methods=['POST'])
@jwt_required()
def create_manutencao():
    """Cria uma nova manutenção."""
    try:
        data = request.get_json()
        
        # Validação dos dados
        validation_result = validate_manutencao(data)
        if validation_result:
            return jsonify({'error': validation_result}), 400
        
        # Verificar se o equipamento existe
        equipamento = Equipamento.query.get(data.get('equipamento_id'))
        if not equipamento:
            return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        # Verificar técnico interno, se fornecido
        if data.get('tecnico_id'):
            tecnico = Tecnico.query.get(data.get('tecnico_id'))
            if not tecnico:
                return jsonify({'error': 'Técnico não encontrado'}), 404
        
        # Verificar técnico externo, se fornecido
        if data.get('tecnico_externo_id'):
            tecnico_externo = TecnicoExterno.query.get(data.get('tecnico_externo_id'))
            if not tecnico_externo:
                return jsonify({'error': 'Técnico externo não encontrado'}), 404
        
        # Verificar empresa externa, se fornecida
        if data.get('empresa_externa_id'):
            empresa_externa = EmpresaExterna.query.get(data.get('empresa_externa_id'))
            if not empresa_externa:
                return jsonify({'error': 'Empresa externa não encontrada'}), 404
        
        # Criar nova manutenção
        nova_manutencao = Manutencao(
            id=str(uuid.uuid4()),
            equipamento_id=data.get('equipamento_id'),
            tipo_manutencao=data.get('tipo_manutencao'),
            status=data.get('status', 'AGENDADA'),
            prioridade=data.get('prioridade', 'NORMAL'),
            descricao=data.get('descricao'),
            data_agendamento=datetime.fromisoformat(data.get('data_agendamento')) if data.get('data_agendamento') else datetime.utcnow(),
            data_inicio=datetime.fromisoformat(data.get('data_inicio')) if data.get('data_inicio') else None,
            data_fim=datetime.fromisoformat(data.get('data_fim')) if data.get('data_fim') else None,
            tecnico_id=data.get('tecnico_id'),
            tecnico_externo_id=data.get('tecnico_externo_id'),
            empresa_externa_id=data.get('empresa_externa_id'),
            custo_mao_de_obra=data.get('custo_mao_de_obra', 0),
            custo_pecas=data.get('custo_pecas', 0),
            custo_total=data.get('custo_total', 0),
            tempo_parada=data.get('tempo_parada', 0),
            observacoes=data.get('observacoes'),
            pecas_substituidas=data.get('pecas_substituidas', []),
            anexos_url=data.get('anexos_url', []),
            assinatura_responsavel_url=data.get('assinatura_responsavel_url'),
            assinatura_tecnico_url=data.get('assinatura_tecnico_url')
        )
        
        db.session.add(nova_manutencao)
        
        # Atualizar status do equipamento se necessário
        if data.get('status') == 'EM_ANDAMENTO':
            equipamento.status = 'EM_MANUTENCAO'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Manutenção criada com sucesso',
            'id': nova_manutencao.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@manutencao_bp.route('/<id>', methods=['PUT'])
@jwt_required()
def update_manutencao(id):
    """Atualiza uma manutenção existente."""
    try:
        manutencao = Manutencao.query.get(id)
        
        if not manutencao:
            return jsonify({'error': 'Manutenção não encontrada'}), 404
        
        data = request.get_json()
        
        # Validação dos dados
        validation_result = validate_manutencao(data, update=True)
        if validation_result:
            return jsonify({'error': validation_result}), 400
        
        # Verificar equipamento, se estiver sendo atualizado
        if data.get('equipamento_id') and data.get('equipamento_id') != manutencao.equipamento_id:
            equipamento = Equipamento.query.get(data.get('equipamento_id'))
            if not equipamento:
                return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        # Verificar técnico interno, se estiver sendo atualizado
        if data.get('tecnico_id') and data.get('tecnico_id') != manutencao.tecnico_id:
            tecnico = Tecnico.query.get(data.get('tecnico_id'))
            if not tecnico:
                return jsonify({'error': 'Técnico não encontrado'}), 404
        
        # Verificar técnico externo, se estiver sendo atualizado
        if data.get('tecnico_externo_id') and data.get('tecnico_externo_id') != manutencao.tecnico_externo_id:
            tecnico_externo = TecnicoExterno.query.get(data.get('tecnico_externo_id'))
            if not tecnico_externo:
                return jsonify({'error': 'Técnico externo não encontrado'}), 404
        
        # Verificar empresa externa, se estiver sendo atualizada
        if data.get('empresa_externa_id') and data.get('empresa_externa_id') != manutencao.empresa_externa_id:
            empresa_externa = EmpresaExterna.query.get(data.get('empresa_externa_id'))
            if not empresa_externa:
                return jsonify({'error': 'Empresa externa não encontrada'}), 404
        
        # Atualizar campos
        if data.get('equipamento_id'):
            manutencao.equipamento_id = data.get('equipamento_id')
        if data.get('tipo_manutencao'):
            manutencao.tipo_manutencao = data.get('tipo_manutencao')
        if data.get('status'):
            manutencao.status = data.get('status')
        if data.get('prioridade'):
            manutencao.prioridade = data.get('prioridade')
        if data.get('descricao'):
            manutencao.descricao = data.get('descricao')
        if data.get('data_agendamento'):
            manutencao.data_agendamento = datetime.fromisoformat(data.get('data_agendamento'))
        if data.get('data_inicio'):
            manutencao.data_inicio = datetime.fromisoformat(data.get('data_inicio'))
        if data.get('data_fim'):
            manutencao.data_fim = datetime.fromisoformat(data.get('data_fim'))
        if 'tecnico_id' in data:
            manutencao.tecnico_id = data.get('tecnico_id')
        if 'tecnico_externo_id' in data:
            manutencao.tecnico_externo_id = data.get('tecnico_externo_id')
        if 'empresa_externa_id' in data:
            manutencao.empresa_externa_id = data.get('empresa_externa_id')
        if 'custo_mao_de_obra' in data:
            manutencao.custo_mao_de_obra = data.get('custo_mao_de_obra')
        if 'custo_pecas' in data:
            manutencao.custo_pecas = data.get('custo_pecas')
        if 'custo_total' in data:
            manutencao.custo_total = data.get('custo_total')
        if 'tempo_parada' in data:
            manutencao.tempo_parada = data.get('tempo_parada')
        if data.get('observacoes'):
            manutencao.observacoes = data.get('observacoes')
        if data.get('pecas_substituidas'):
            manutencao.pecas_substituidas = data.get('pecas_substituidas')
        if data.get('anexos_url'):
            manutencao.anexos_url = data.get('anexos_url')
        if data.get('assinatura_responsavel_url'):
            manutencao.assinatura_responsavel_url = data.get('assinatura_responsavel_url')
        if data.get('assinatura_tecnico_url'):
            manutencao.assinatura_tecnico_url = data.get('assinatura_tecnico_url')
        
        # Atualizar status do equipamento se necessário
        equipamento = Equipamento.query.get(manutencao.equipamento_id)
        if manutencao.status == 'EM_ANDAMENTO' and equipamento.status != 'EM_MANUTENCAO':
            equipamento.status = 'EM_MANUTENCAO'
        elif manutencao.status == 'CONCLUIDA' and equipamento.status == 'EM_MANUTENCAO':
            equipamento.status = 'ATIVO'
            equipamento.ultima_manutencao = datetime.utcnow().date()
        
        manutencao.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Manutenção atualizada com sucesso',
            'id': manutencao.id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@manutencao_bp.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete_manutencao(id):
    """Remove uma manutenção do sistema."""
    try:
        manutencao = Manutencao.query.get(id)
        
        if not manutencao:
            return jsonify({'error': 'Manutenção não encontrada'}), 404
        
        # Verificar se a manutenção está associada a uma ordem de serviço
        if manutencao.ordem_servico:
            return jsonify({
                'error': 'Não é possível excluir a manutenção pois está associada a uma ordem de serviço'
            }), 400
        
        db.session.delete(manutencao)
        db.session.commit()
        
        return jsonify({
            'message': 'Manutenção removida com sucesso'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@manutencao_bp.route('/<id>/status', methods=['PUT'])
@jwt_required()
def update_manutencao_status(id):
    """Atualiza o status de uma manutenção."""
    try:
        manutencao = Manutencao.query.get(id)
        
        if not manutencao:
            return jsonify({'error': 'Manutenção não encontrada'}), 404
        
        data = request.get_json()
        
        if not data or not data.get('status'):
            return jsonify({'error': 'Status não fornecido'}), 400
        
        status = data.get('status')
        status_validos = ['AGENDADA', 'EM_ANDAMENTO', 'CONCLUIDA', 'CANCELADA']
        
        if status not in status_validos:
            return jsonify({'error': f'Status inválido. Valores permitidos: {", ".join(status_validos)}'}), 400
        
        # Atualizar status
        manutencao.status = status
        
        # Atualizar datas conforme o status
        if status == 'EM_ANDAMENTO' and not manutencao.data_inicio:
            manutencao.data_inicio = datetime.utcnow()
        elif status == 'CONCLUIDA' and not manutencao.data_fim:
            manutencao.data_fim = datetime.utcnow()
            
            # Calcular tempo de parada se não estiver definido
            if not manutencao.tempo_parada and manutencao.data_inicio:
                delta = manutencao.data_fim - manutencao.data_inicio
                manutencao.tempo_parada = int(delta.total_seconds() / 60)  # em minutos
        
        # Atualizar status do equipamento
        equipamento = Equipamento.query.get(manutencao.equipamento_id)
        if status == 'EM_ANDAMENTO':
            equipamento.status = 'EM_MANUTENCAO'
        elif status == 'CONCLUIDA' and equipamento.status == 'EM_MANUTENCAO':
            equipamento.status = 'ATIVO'
            equipamento.ultima_manutencao = datetime.utcnow().date()
        
        manutencao.atualizado_em = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Status da manutenção atualizado com sucesso',
            'id': manutencao.id,
            'status': manutencao.status
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@manutencao_bp.route('/por-equipamento/<equipamento_id>', methods=['GET'])
@jwt_required()
def get_manutencoes_por_equipamento(equipamento_id):
    """Retorna todas as manutenções de um equipamento específico."""
    try:
        equipamento = Equipamento.query.get(equipamento_id)
        
        if not equipamento:
            return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        manutencoes = Manutencao.query.filter_by(equipamento_id=equipamento_id).all()
        
        result = [{
            'id': m.id,
            'tipo_manutencao': m.tipo_manutencao,
            'status': m.status,
            'prioridade': m.prioridade,
            'data_agendamento': m.data_agendamento.isoformat() if m.data_agendamento else None,
            'data_inicio': m.data_inicio.isoformat() if m.data_inicio else None,
            'data_fim': m.data_fim.isoformat() if m.data_fim else None,
            'tecnico': m.tecnico.nome if m.tecnico else (m.tecnico_externo.nome if m.tecnico_externo else None),
            'custo_total': float(m.custo_total) if m.custo_total else 0
        } for m in manutencoes]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@manutencao_bp.route('/por-tecnico/<tecnico_id>', methods=['GET'])
@jwt_required()
def get_manutencoes_por_tecnico(tecnico_id):
    """Retorna todas as manutenções atribuídas a um técnico específico."""
    try:
        tecnico = Tecnico.query.get(tecnico_id)
        
        if not tecnico:
            return jsonify({'error': 'Técnico não encontrado'}), 404
        
        manutencoes = Manutencao.query.filter_by(tecnico_id=tecnico_id).all()
        
        result = [{
            'id': m.id,
            'equipamento': m.equipamento.nome if m.equipamento else None,
            'tipo_manutencao': m.tipo_manutencao,
            'status': m.status,
            'prioridade': m.prioridade,
            'data_agendamento': m.data_agendamento.isoformat() if m.data_agendamento else None,
            'data_inicio': m.data_inicio.isoformat() if m.data_inicio else None,
            'data_fim': m.data_fim.isoformat() if m.data_fim else None
        } for m in manutencoes]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@manutencao_bp.route('/por-periodo', methods=['GET'])
@jwt_required()
def get_manutencoes_por_periodo():
    """Retorna todas as manutenções em um período específico."""
    try:
        inicio = request.args.get('inicio')
        fim = request.args.get('fim')
        
        if not inicio:
            return jsonify({'error': 'Data de início não fornecida'}), 400
        
        try:
            data_inicio = datetime.fromisoformat(inicio)
            data_fim = datetime.fromisoformat(fim) if fim else datetime.utcnow()
        except ValueError:
            return jsonify({'error': 'Formato de data inválido. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS)'}), 400
        
        # Buscar manutenções no período
        manutencoes = Manutencao.query.filter(
            Manutencao.data_agendamento >= data_inicio,
            Manutencao.data_agendamento <= data_fim
        ).all()
        
        result = [{
            'id': m.id,
            'equipamento': m.equipamento.nome if m.equipamento else None,
            'tipo_manutencao': m.tipo_manutencao,
            'status': m.status,
            'prioridade': m.prioridade,
            'data_agendamento': m.data_agendamento.isoformat() if m.data_agendamento else None,
            'data_inicio': m.data_inicio.isoformat() if m.data_inicio else None,
            'data_fim': m.data_fim.isoformat() if m.data_fim else None,
            'tecnico': m.tecnico.nome if m.tecnico else (m.tecnico_externo.nome if m.tecnico_externo else None)
        } for m in manutencoes]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
