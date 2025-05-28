#!/usr/bin/env python3
import unittest
import sys
import os

# Adicionar diretório raiz ao path para importação dos módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar todos os testes
from tests.test_auth_api import TestAuthAPI
from tests.test_equipamento_api import TestEquipamentoAPI
from tests.test_manutencao_api import TestManutencaoAPI
from tests.test_ordem_servico_api import TestOrdemServicoAPI

if __name__ == '__main__':
    # Criar test suite com todos os testes
    test_suite = unittest.TestSuite()
    
    # Adicionar classes de teste
    test_suite.addTest(unittest.makeSuite(TestAuthAPI))
    test_suite.addTest(unittest.makeSuite(TestEquipamentoAPI))
    test_suite.addTest(unittest.makeSuite(TestManutencaoAPI))
    test_suite.addTest(unittest.makeSuite(TestOrdemServicoAPI))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Retornar código de saída adequado
    sys.exit(not result.wasSuccessful())
