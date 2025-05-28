import unittest
from app import create_app, db
from app.models import Equipamento, Departamento, Usuario
from werkzeug.security import generate_password_hash
import json
import uuid
from datetime import datetime, timedelta

class TestEquipamentoAPI(unittest.TestCase):
    """Testes para a API de Equipamentos"""

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
        
        # Criar departamento de teste
        departamento_id = str(uuid.uuid4())
        departamento = Departamento(
            id=departamento_id,
            nome='Departamento Teste',
            descricao='Departamento para testes'
        )
        
        db.session.add(usuario)
        db.session.add(departamento)
        db.session.commit()
        
        self.usuario_id = usuario_id
        self.departamento_id = departamento_id
        
        # Obter token de autenticação
        response = self.client.post('/api/auth/login', json={
            'email': 'teste@example.com',
            'senha': 'senha123'
        })
        data = json.loads(response.data)
        self.token = data['access_token']
        
    def tearDown(self):
        """Limpeza após cada teste"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_criar_equipamento(self):
        """Teste para criação de equipamento"""
        # Dados do equipamento
        equipamento_data = {
            'codigo': 'EQ-001',
            'nome': 'Equipamento Teste',
            'modelo': 'Modelo Teste',
            'fabricante': 'Fabricante Teste',
            'numero_serie': 'SN12345',
            'data_aquisicao': datetime.now().date().isoformat(),
            'departamento_id': self.departamento_id,
            'status': 'ATIVO',
            'criticidade': 'MEDIA'
        }
        
        # Enviar requisição
        response = self.client.post(
            '/api/equipamentos',
            json=equipamento_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.assertIn('message', data)
        
        # Verificar se o equipamento foi criado no banco
        equipamento = Equipamento.query.filter_by(codigo='EQ-001').first()
        self.assertIsNotNone(equipamento)
        self.assertEqual(equipamento.nome, 'Equipamento Teste')
    
    def test_obter_equipamento(self):
        """Teste para obtenção de equipamento por ID"""
        # Criar equipamento
        equipamento_id = str(uuid.uuid4())
        equipamento = Equipamento(
            id=equipamento_id,
            codigo='EQ-002',
            nome='Equipamento Teste 2',
            modelo='Modelo Teste 2',
            fabricante='Fabricante Teste 2',
            numero_serie='SN67890',
            data_aquisicao=datetime.now().date(),
            departamento_id=self.departamento_id,
            status='ATIVO',
            criticidade='MEDIA'
        )
        db.session.add(equipamento)
        db.session.commit()
        
        # Enviar requisição
        response = self.client.get(
            f'/api/equipamentos/{equipamento_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], equipamento_id)
        self.assertEqual(data['codigo'], 'EQ-002')
        self.assertEqual(data['nome'], 'Equipamento Teste 2')
    
    def test_atualizar_equipamento(self):
        """Teste para atualização de equipamento"""
        # Criar equipamento
        equipamento_id = str(uuid.uuid4())
        equipamento = Equipamento(
            id=equipamento_id,
            codigo='EQ-003',
            nome='Equipamento Teste 3',
            modelo='Modelo Teste 3',
            fabricante='Fabricante Teste 3',
            numero_serie='SN13579',
            data_aquisicao=datetime.now().date(),
            departamento_id=self.departamento_id,
            status='ATIVO',
            criticidade='MEDIA'
        )
        db.session.add(equipamento)
        db.session.commit()
        
        # Dados para atualização
        update_data = {
            'nome': 'Equipamento Atualizado',
            'status': 'INATIVO'
        }
        
        # Enviar requisição
        response = self.client.put(
            f'/api/equipamentos/{equipamento_id}',
            json=update_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        
        # Verificar se o equipamento foi atualizado no banco
        equipamento = Equipamento.query.get(equipamento_id)
        self.assertEqual(equipamento.nome, 'Equipamento Atualizado')
        self.assertEqual(equipamento.status, 'INATIVO')
    
    def test_excluir_equipamento(self):
        """Teste para exclusão de equipamento"""
        # Criar equipamento
        equipamento_id = str(uuid.uuid4())
        equipamento = Equipamento(
            id=equipamento_id,
            codigo='EQ-004',
            nome='Equipamento Teste 4',
            modelo='Modelo Teste 4',
            fabricante='Fabricante Teste 4',
            numero_serie='SN24680',
            data_aquisicao=datetime.now().date(),
            departamento_id=self.departamento_id,
            status='ATIVO',
            criticidade='MEDIA'
        )
        db.session.add(equipamento)
        db.session.commit()
        
        # Enviar requisição
        response = self.client.delete(
            f'/api/equipamentos/{equipamento_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        
        # Verificar se o equipamento foi removido do banco
        equipamento = Equipamento.query.get(equipamento_id)
        self.assertIsNone(equipamento)
    
    def test_listar_equipamentos(self):
        """Teste para listagem de equipamentos"""
        # Criar vários equipamentos
        for i in range(5):
            equipamento = Equipamento(
                id=str(uuid.uuid4()),
                codigo=f'EQ-{100+i}',
                nome=f'Equipamento Teste {100+i}',
                modelo=f'Modelo Teste {100+i}',
                fabricante=f'Fabricante Teste {100+i}',
                numero_serie=f'SN{100+i}',
                data_aquisicao=datetime.now().date(),
                departamento_id=self.departamento_id,
                status='ATIVO',
                criticidade='MEDIA'
            )
            db.session.add(equipamento)
        db.session.commit()
        
        # Enviar requisição
        response = self.client.get(
            '/api/equipamentos',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('items', data)
        self.assertIn('total', data)
        self.assertGreaterEqual(data['total'], 5)
        self.assertGreaterEqual(len(data['items']), 5)

if __name__ == '__main__':
    unittest.main()
