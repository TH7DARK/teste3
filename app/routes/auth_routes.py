from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from app.models import Usuario
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Autentica um usuário e retorna tokens de acesso e refresh."""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('senha'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        usuario = Usuario.query.filter_by(email=data.get('email')).first()
        
        if not usuario or not check_password_hash(usuario.senha_hash, data.get('senha')):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not usuario.ativo:
            return jsonify({'error': 'Usuário inativo. Contate o administrador.'}), 403
        
        # Atualizar último acesso
        usuario.ultimo_acesso = datetime.datetime.utcnow()
        db.session.commit()
        
        # Gerar tokens
        access_token = create_access_token(identity=usuario.id)
        refresh_token = create_refresh_token(identity=usuario.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': usuario.id,
                'nome': usuario.nome,
                'email': usuario.email,
                'perfil': usuario.perfil,
                'departamento_id': usuario.departamento_id
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh-token', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renova o token de acesso usando um token de refresh válido."""
    try:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        
        return jsonify({
            'access_token': access_token
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Realiza o logout do usuário (implementação básica)."""
    # Em uma implementação mais completa, poderia adicionar o token a uma lista de bloqueio
    return jsonify({'message': 'Logout realizado com sucesso'}), 200
