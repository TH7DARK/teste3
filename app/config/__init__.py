import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env se existir
load_dotenv()

class Config:
    """Configuração base para a aplicação."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-secreta-padrao-deve-ser-alterada')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-chave-secreta-padrao-deve-ser-alterada')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 dias
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 horas em desenvolvimento

class TestingConfig(Config):
    """Configuração para ambiente de testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')
    JWT_ACCESS_TOKEN_EXPIRES = 300  # 5 minutos em testes

class ProductionConfig(Config):
    """Configuração para ambiente de produção."""
    DEBUG = False
    # Usar SQLite para o plano gratuito do Render, mas pode ser alterado para PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///prod.db')
    # Em produção, certifique-se de definir SECRET_KEY e JWT_SECRET_KEY como variáveis de ambiente
    # Configurações específicas para o Render
    PORT = int(os.getenv('PORT', 8080))
