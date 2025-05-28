import unittest
from app import create_app, db
from app.models import Manutencao, Equipamento, Departamento, Usuario, Tecnico
from werkzeug.security import generate_password_hash
import json
import uuid
from datetime import datetime, timedelta

class TestManutencaoAPI(unittest.TestCase):
    """Testes para a API de Manutenções"""

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
        
        # Criar técnico de teste
        tecnico_id = str(uuid.uuid4())
        tecnico = Tecnico(
            id=tecnico_id,
            nome='Técnico Teste',
            email='tecnico@example.com',
            especialidades=['Raio-X', 'Ultrassom'],
            interno=True,
            disponivel=True
        )
        
        # Criar equipamento de teste
        equipamento_id = str(uuid.uuid4())
        equipamento = Equipamento(
            id=equipamento_id,
            codigo='EQ-TEST',
            nome='Equipamento Teste',
            modelo='Modelo Teste',
            fabricante='Fabricante Teste',
            numero_serie='SN12345',
            data_aquisicao=datetime.now().date(),
            departamento_id=departamento_id,
            status='ATIVO',
            criticidade='MEDIA'
        )
        
        db.session.add(usuario)
        db.session.add(departamento)
        db.session.add(tecnico)
        db.session.add(equipamento)
        db.session.commit()
        
        self.usuario_id = usuario_id
        self.departamento_id = departamento_id
        self.tecnico_id = tecnico_id
        self.equipamento_id = equipamento_id
        
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
    
    def test_criar_manutencao(self):
        """Teste para criação de manutenção"""
        # Dados da manutenção
        manutencao_data = {
            'equipamento_id': self.equipamento_id,
            'tipo_manutencao': 'PREVENTIVA',
            'descricao': 'Manutenção preventiva de rotina',
            'data_agendamento': (datetime.now() + timedelta(days=1)).isoformat(),
            'tecnico_id': self.tecnico_id,
            'prioridade': 'NORMAL'
        }
        
        # Enviar requisição
        response = self.client.post(
            '/api/manutencoes',
            json=manutencao_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.assertIn('message', data)
        
        # Verificar se a manutenção foi criada no banco
        manutencao = Manutencao.query.get(data['id'])
        self.assertIsNotNone(manutencao)
        self.assertEqual(manutencao.tipo_manutencao, 'PREVENTIVA')
        self.assertEqual(manutencao.equipamento_id, self.equipamento_id)
    
    def test_obter_manutencao(self):
        """Teste para obtenção de manutenção por ID"""
        # Criar manutenção
        manutencao_id = str(uuid.uuid4())
        manutencao = Manutencao(
            id=manutencao_id,
            equipamento_id=self.equipamento_id,
            tipo_manutencao='CORRETIVA',
            status='AGENDADA',
            prioridade='ALTA',
            descricao='Manutenção corretiva urgente',
            data_agendamento=datetime.now() + timedelta(days=1),
            tecnico_id=self.tecnico_id
        )
        db.session.add(manutencao)
        db.session.commit()
        
        # Enviar requisição
        response = self.client.get(
            f'/api/manutencoes/{manutencao_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], manutencao_id)
        self.assertEqual(data['tipo_manutencao'], 'CORRETIVA')
        self.assertEqual(data['prioridade'], 'ALTA')
    
    def test_atualizar_manutencao(self):
        """Teste para atualização de manutenção"""
        # Criar manutenção
        manutencao_id = str(uuid.uuid4())
        manutencao = Manutencao(
            id=manutencao_id,
            equipamento_id=self.equipamento_id,
            tipo_manutencao='PREVENTIVA',
            status='AGENDADA',
            prioridade='NORMAL',
            descricao='Manutenção preventiva de rotina',
            data_agendamento=datetime.now() + timedelta(days=2),
            tecnico_id=self.tecnico_id
        )
        db.session.add(manutencao)
        db.session.commit()
        
        # Dados para atualização
        update_data = {
            'status': 'EM_ANDAMENTO',
            'data_inicio': datetime.now().isoformat(),
            'observacoes': 'Iniciada a manutenção preventiva'
        }
        
        # Enviar requisição
        response = self.client.put(
            f'/api/manutencoes/{manutencao_id}',
            json=update_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        
        # Verificar se a manutenção foi atualizada no banco
        manutencao = Manutencao.query.get(manutencao_id)
        self.assertEqual(manutencao.status, 'EM_ANDAMENTO')
        self.assertIsNotNone(manutencao.data_inicio)
        self.assertEqual(manutencao.observacoes, 'Iniciada a manutenção preventiva')
    
    def test_atualizar_status_manutencao(self):
        """Teste para atualização de status de manutenção"""
        # Criar manutenção
        manutencao_id = str(uuid.uuid4())
        manutencao = Manutencao(
            id=manutencao_id,
            equipamento_id=self.equipamento_id,
            tipo_manutencao='PREVENTIVA',
            status='AGENDADA',
            prioridade='NORMAL',
            descricao='Manutenção preventiva de rotina',
            data_agendamento=datetime.now() + timedelta(days=2),
            tecnico_id=self.tecnico_id
        )
        db.session.add(manutencao)
        db.session.commit()
        
        # Dados para atualização de status
        status_data = {
            'status': 'CONCLUIDA'
        }
        
        # Enviar requisição
        response = self.client.put(
            f'/api/manutencoes/{manutencao_id}/status',
            json=status_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        
        # Verificar se o status foi atualizado no banco
        manutencao = Manutencao.query.get(manutencao_id)
        self.assertEqual(manutencao.status, 'CONCLUIDA')
        self.assertIsNotNone(manutencao.data_fim)
        
        # Verificar se o equipamento foi atualizado
        equipamento = Equipamento.query.get(self.equipamento_id)
        self.assertEqual(equipamento.status, 'ATIVO')
        self.assertIsNotNone(equipamento.ultima_manutencao)
    
    def test_listar_manutencoes(self):
        """Teste para listagem de manutenções"""
        # Criar várias manutenções
        for i in range(5):
            manutencao = Manutencao(
                id=str(uuid.uuid4()),
                equipamento_id=self.equipamento_id,
                tipo_manutencao='PREVENTIVA',
                status='AGENDADA',
                prioridade='NORMAL',
                descricao=f'Manutenção de teste {i+1}',
                data_agendamento=datetime.now() + timedelta(days=i+1),
                tecnico_id=self.tecnico_id
            )
            db.session.add(manutencao)
        db.session.commit()
        
        # Enviar requisição
        response = self.client.get(
            '/api/manutencoes',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('items', data)
        self.assertIn('total', data)
        self.assertGreaterEqual(data['total'], 5)
        self.assertGreaterEqual(len(data['items']), 5)
    
    def test_manutencoes_por_equipamento(self):
        """Teste para listagem de manutenções por equipamento"""
        # Criar várias manutenções para o equipamento
        for i in range(3):
            manutencao = Manutencao(
                id=str(uuid.uuid4()),
                equipamento_id=self.equipamento_id,
                tipo_manutencao='PREVENTIVA',
                status='AGENDADA',
                prioridade='NORMAL',
                descricao=f'Manutenção de teste {i+1}',
                data_agendamento=datetime.now() + timedelta(days=i+1),
                tecnico_id=self.tecnico_id
            )
            db.session.add(manutencao)
        db.session.commit()
        
        # Enviar requisição
        response = self.client.get(
            f'/api/manutencoes/por-equipamento/{self.equipamento_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

if __name__ == '__main__':
    unittest.main()
