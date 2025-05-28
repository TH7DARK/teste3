import unittest
from app import create_app, db
from app.models import OrdemServico, Equipamento, Departamento, Usuario, Manutencao
from werkzeug.security import generate_password_hash
import json
import uuid
from datetime import datetime, timedelta

class TestOrdemServicoAPI(unittest.TestCase):
    """Testes para a API de Ordens de Serviço"""

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
        db.session.add(equipamento)
        db.session.commit()
        
        self.usuario_id = usuario_id
        self.departamento_id = departamento_id
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
    
    def test_criar_ordem_servico(self):
        """Teste para criação de ordem de serviço"""
        # Dados da ordem de serviço
        ordem_data = {
            'equipamento_id': self.equipamento_id,
            'departamento_id': self.departamento_id,
            'solicitante_id': self.usuario_id,
            'tipo_servico': 'MANUTENCAO_PREVENTIVA',
            'descricao_problema': 'Verificação de rotina',
            'prioridade': 'NORMAL'
        }
        
        # Enviar requisição
        response = self.client.post(
            '/api/ordens-servico',
            json=ordem_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.assertIn('codigo', data)
        self.assertIn('message', data)
        
        # Verificar se a ordem foi criada no banco
        ordem = OrdemServico.query.get(data['id'])
        self.assertIsNotNone(ordem)
        self.assertEqual(ordem.tipo_servico, 'MANUTENCAO_PREVENTIVA')
        self.assertEqual(ordem.equipamento_id, self.equipamento_id)
    
    def test_obter_ordem_servico(self):
        """Teste para obtenção de ordem de serviço por ID"""
        # Criar ordem de serviço
        ordem_id = str(uuid.uuid4())
        ordem = OrdemServico(
            id=ordem_id,
            codigo='OS-000001',
            equipamento_id=self.equipamento_id,
            departamento_id=self.departamento_id,
            solicitante_id=self.usuario_id,
            tipo_servico='MANUTENCAO_CORRETIVA',
            descricao_problema='Equipamento com falha',
            prioridade='ALTA',
            status='ABERTA',
            data_abertura=datetime.now()
        )
        db.session.add(ordem)
        db.session.commit()
        
        # Enviar requisição
        response = self.client.get(
            f'/api/ordens-servico/{ordem_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], ordem_id)
        self.assertEqual(data['codigo'], 'OS-000001')
        self.assertEqual(data['tipo_servico'], 'MANUTENCAO_CORRETIVA')
        self.assertEqual(data['prioridade'], 'ALTA')
    
    def test_atualizar_ordem_servico(self):
        """Teste para atualização de ordem de serviço"""
        # Criar ordem de serviço
        ordem_id = str(uuid.uuid4())
        ordem = OrdemServico(
            id=ordem_id,
            codigo='OS-000002',
            equipamento_id=self.equipamento_id,
            departamento_id=self.departamento_id,
            solicitante_id=self.usuario_id,
            tipo_servico='MANUTENCAO_PREVENTIVA',
            descricao_problema='Verificação de rotina',
            prioridade='NORMAL',
            status='ABERTA',
            data_abertura=datetime.now()
        )
        db.session.add(ordem)
        db.session.commit()
        
        # Dados para atualização
        update_data = {
            'status': 'ATRIBUIDA',
            'prioridade': 'ALTA',
            'observacoes': 'Atribuída para equipe técnica'
        }
        
        # Enviar requisição
        response = self.client.put(
            f'/api/ordens-servico/{ordem_id}',
            json=update_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        
        # Verificar se a ordem foi atualizada no banco
        ordem = OrdemServico.query.get(ordem_id)
        self.assertEqual(ordem.status, 'ATRIBUIDA')
        self.assertEqual(ordem.prioridade, 'ALTA')
        self.assertEqual(ordem.observacoes, 'Atribuída para equipe técnica')
    
    def test_atualizar_status_ordem_servico(self):
        """Teste para atualização de status de ordem de serviço"""
        # Criar ordem de serviço
        ordem_id = str(uuid.uuid4())
        ordem = OrdemServico(
            id=ordem_id,
            codigo='OS-000003',
            equipamento_id=self.equipamento_id,
            departamento_id=self.departamento_id,
            solicitante_id=self.usuario_id,
            tipo_servico='MANUTENCAO_PREVENTIVA',
            descricao_problema='Verificação de rotina',
            prioridade='NORMAL',
            status='ABERTA',
            data_abertura=datetime.now()
        )
        db.session.add(ordem)
        db.session.commit()
        
        # Dados para atualização de status
        status_data = {
            'status': 'EM_ANDAMENTO'
        }
        
        # Enviar requisição
        response = self.client.put(
            f'/api/ordens-servico/{ordem_id}/status',
            json=status_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        
        # Verificar se o status foi atualizado no banco
        ordem = OrdemServico.query.get(ordem_id)
        self.assertEqual(ordem.status, 'EM_ANDAMENTO')
        self.assertIsNotNone(ordem.data_inicio)
    
    def test_avaliar_ordem_servico(self):
        """Teste para avaliação de ordem de serviço concluída"""
        # Criar ordem de serviço concluída
        ordem_id = str(uuid.uuid4())
        ordem = OrdemServico(
            id=ordem_id,
            codigo='OS-000004',
            equipamento_id=self.equipamento_id,
            departamento_id=self.departamento_id,
            solicitante_id=self.usuario_id,
            tipo_servico='MANUTENCAO_PREVENTIVA',
            descricao_problema='Verificação de rotina',
            prioridade='NORMAL',
            status='CONCLUIDA',
            data_abertura=datetime.now() - timedelta(days=2),
            data_atribuicao=datetime.now() - timedelta(days=1),
            data_inicio=datetime.now() - timedelta(days=1),
            data_fim=datetime.now()
        )
        db.session.add(ordem)
        db.session.commit()
        
        # Dados para avaliação
        avaliacao_data = {
            'avaliacao': 5,
            'comentario': 'Serviço excelente, rápido e eficiente'
        }
        
        # Enviar requisição
        response = self.client.post(
            f'/api/ordens-servico/{ordem_id}/avaliacao',
            json=avaliacao_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        
        # Verificar se a avaliação foi registrada no banco
        ordem = OrdemServico.query.get(ordem_id)
        self.assertEqual(ordem.avaliacao_satisfacao, 5)
        self.assertEqual(ordem.comentario_avaliacao, 'Serviço excelente, rápido e eficiente')
    
    def test_listar_ordens_servico(self):
        """Teste para listagem de ordens de serviço"""
        # Criar várias ordens de serviço
        for i in range(5):
            ordem = OrdemServico(
                id=str(uuid.uuid4()),
                codigo=f'OS-{100+i:06d}',
                equipamento_id=self.equipamento_id,
                departamento_id=self.departamento_id,
                solicitante_id=self.usuario_id,
                tipo_servico='MANUTENCAO_PREVENTIVA',
                descricao_problema=f'Ordem de teste {i+1}',
                prioridade='NORMAL',
                status='ABERTA',
                data_abertura=datetime.now()
            )
            db.session.add(ordem)
        db.session.commit()
        
        # Enviar requisição
        response = self.client.get(
            '/api/ordens-servico',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('items', data)
        self.assertIn('total', data)
        self.assertGreaterEqual(data['total'], 5)
        self.assertGreaterEqual(len(data['items']), 5)
    
    def test_ordens_por_departamento(self):
        """Teste para listagem de ordens de serviço por departamento"""
        # Criar várias ordens de serviço para o departamento
        for i in range(3):
            ordem = OrdemServico(
                id=str(uuid.uuid4()),
                codigo=f'OS-{200+i:06d}',
                equipamento_id=self.equipamento_id,
                departamento_id=self.departamento_id,
                solicitante_id=self.usuario_id,
                tipo_servico='MANUTENCAO_PREVENTIVA',
                descricao_problema=f'Ordem de teste {i+1}',
                prioridade='NORMAL',
                status='ABERTA',
                data_abertura=datetime.now()
            )
            db.session.add(ordem)
        db.session.commit()
        
        # Enviar requisição
        response = self.client.get(
            f'/api/ordens-servico/por-departamento/{self.departamento_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

if __name__ == '__main__':
    unittest.main()
