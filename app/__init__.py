import os
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Inicialização das extensões
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuração
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    if config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # Inicialização das extensões com o app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # Registro de blueprints
    from app.routes.equipamento_routes import equipamento_bp
    from app.routes.manutencao_routes import manutencao_bp
    from app.routes.ordem_servico_routes import ordem_servico_bp
    from app.routes.usuario_routes import usuario_bp
    from app.routes.departamento_routes import departamento_bp
    from app.routes.tecnico_routes import tecnico_bp
    from app.routes.peca_routes import peca_bp
    from app.routes.certificado_routes import certificado_bp
    from app.routes.relatorio_routes import relatorio_bp
    from app.routes.auth_routes import auth_bp
    
    app.register_blueprint(equipamento_bp, url_prefix='/api/equipamentos')
    app.register_blueprint(manutencao_bp, url_prefix='/api/manutencoes')
    app.register_blueprint(ordem_servico_bp, url_prefix='/api/ordens-servico')
    app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')
    app.register_blueprint(departamento_bp, url_prefix='/api/departamentos')
    app.register_blueprint(tecnico_bp, url_prefix='/api/tecnicos')
    app.register_blueprint(peca_bp, url_prefix='/api/pecas')
    app.register_blueprint(certificado_bp, url_prefix='/api/certificados')
    app.register_blueprint(relatorio_bp, url_prefix='/api/relatorios')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Configuração de tratamento de erros
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Recurso não encontrado'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Erro interno do servidor'}, 500
    
    # Rota de verificação de saúde da API
    @app.route('/api/health')
    def health_check():
        return {'status': 'online', 'version': '1.0.0'}, 200
    
    return app
