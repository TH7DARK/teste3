import unittest
from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
import json
import uuid
from datetime import datetime

class TestAuthAPI(unittest.TestCase):
    """Testes para a API de Autenticação"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Criar usuário de teste
        usuario_id = str(uuid.uuid4())
        usuario = Usuario(
            id=usuario_id,
            nome='Usuário Teste',
            email='teste@example.com',
            senha_hash=generate_password_hash('senha123'),
            perfil='ADMIN',
            ativo=True
        )
        
        db.session.add(usuario)
        db.session.commit()
        
        self.usuario_id = usuario_id
        
    def tearDown(self):
        """Limpeza após cada teste"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_login_sucesso(self):
        """Teste para login com credenciais válidas"""
        # Dados de login
        login_data = {
            'email': 'teste@example.com',
            'senha': 'senha123'
        }
        
        # Enviar requisição
        response = self.client.post(
            '/api/auth/login',
            json=login_data
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['id'], self.usuario_id)
    
    def test_login_falha_credenciais_invalidas(self):
        """Teste para login com credenciais inválidas"""
        # Dados de login inválidos
        login_data = {
            'email': 'teste@example.com',
            'senha': 'senha_errada'
        }
        
        # Enviar requisição
        response = self.client.post(
            '/api/auth/login',
            json=login_data
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_login_falha_usuario_inativo(self):
        """Teste para login com usuário inativo"""
        # Desativar usuário
        usuario = Usuario.query.get(self.usuario_id)
        usuario.ativo = False
        db.session.commit()
        
        # Dados de login
        login_data = {
            'email': 'teste@example.com',
            'senha': 'senha123'
        }
        
        # Enviar requisição
        response = self.client.post(
            '/api/auth/login',
            json=login_data
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_refresh_token(self):
        """Teste para renovação de token de acesso"""
        # Primeiro fazer login para obter refresh token
        login_data = {
            'email': 'teste@example.com',
            'senha': 'senha123'
        }
        
        login_response = self.client.post(
            '/api/auth/login',
            json=login_data
        )
        
        login_data = json.loads(login_response.data)
        refresh_token = login_data['refresh_token']
        
        # Enviar requisição de refresh
        response = self.client.post(
            '/api/auth/refresh-token',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
    
    def test_acesso_protegido_sem_token(self):
        """Teste para acesso a rota protegida sem token"""
        # Enviar requisição sem token
        response = self.client.get('/api/equipamentos')
        
        # Verificar resposta
        self.assertEqual(response.status_code, 401)
    
    def test_acesso_protegido_com_token(self):
        """Teste para acesso a rota protegida com token válido"""
        # Primeiro fazer login para obter token
        login_data = {
            'email': 'teste@example.com',
            'senha': 'senha123'
        }
        
        login_response = self.client.post(
            '/api/auth/login',
            json=login_data
        )
        
        login_data = json.loads(login_response.data)
        access_token = login_data['access_token']
        
        # Enviar requisição com token
        response = self.client.get(
            '/api/equipamentos',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
