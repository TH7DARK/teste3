def validate_equipamento(data, update=False):
    """
    Valida os dados de um equipamento.
    
    Args:
        data (dict): Dados do equipamento a serem validados
        update (bool): Indica se é uma atualização (True) ou criação (False)
        
    Returns:
        str: Mensagem de erro ou None se válido
    """
    # Campos obrigatórios para criação
    if not update:
        required_fields = ['codigo', 'nome', 'modelo', 'fabricante', 'numero_serie', 'data_aquisicao', 'departamento_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return f"Campo '{field}' é obrigatório"
    
    # Validações específicas
    if 'codigo' in data and data['codigo']:
        if len(data['codigo']) > 50:
            return "Código deve ter no máximo 50 caracteres"
    
    if 'nome' in data and data['nome']:
        if len(data['nome']) > 100:
            return "Nome deve ter no máximo 100 caracteres"
    
    if 'status' in data and data['status']:
        valid_status = ['ATIVO', 'INATIVO', 'EM_MANUTENCAO', 'DESCONTINUADO']
        if data['status'] not in valid_status:
            return f"Status inválido. Valores permitidos: {', '.join(valid_status)}"
    
    if 'criticidade' in data and data['criticidade']:
        valid_criticidade = ['BAIXA', 'MEDIA', 'ALTA', 'CRITICA']
        if data['criticidade'] not in valid_criticidade:
            return f"Criticidade inválida. Valores permitidos: {', '.join(valid_criticidade)}"
    
    return None

def validate_manutencao(data, update=False):
    """
    Valida os dados de uma manutenção.
    
    Args:
        data (dict): Dados da manutenção a serem validados
        update (bool): Indica se é uma atualização (True) ou criação (False)
        
    Returns:
        str: Mensagem de erro ou None se válido
    """
    # Campos obrigatórios para criação
    if not update:
        required_fields = ['equipamento_id', 'tipo_manutencao', 'descricao']
        for field in required_fields:
            if field not in data or not data[field]:
                return f"Campo '{field}' é obrigatório"
    
    # Validações específicas
    if 'tipo_manutencao' in data and data['tipo_manutencao']:
        valid_tipos = ['PREVENTIVA', 'CORRETIVA', 'CALIBRACAO', 'VERIFICACAO']
        if data['tipo_manutencao'] not in valid_tipos:
            return f"Tipo de manutenção inválido. Valores permitidos: {', '.join(valid_tipos)}"
    
    if 'status' in data and data['status']:
        valid_status = ['AGENDADA', 'EM_ANDAMENTO', 'CONCLUIDA', 'CANCELADA']
        if data['status'] not in valid_status:
            return f"Status inválido. Valores permitidos: {', '.join(valid_status)}"
    
    if 'prioridade' in data and data['prioridade']:
        valid_prioridade = ['BAIXA', 'NORMAL', 'ALTA', 'EMERGENCIA']
        if data['prioridade'] not in valid_prioridade:
            return f"Prioridade inválida. Valores permitidos: {', '.join(valid_prioridade)}"
    
    # Validar que não tenha técnico interno e externo simultaneamente
    if ('tecnico_id' in data and data['tecnico_id']) and ('tecnico_externo_id' in data and data['tecnico_externo_id']):
        return "Não é possível atribuir técnico interno e externo simultaneamente"
    
    return None

def validate_ordem_servico(data, update=False):
    """
    Valida os dados de uma ordem de serviço.
    
    Args:
        data (dict): Dados da ordem de serviço a serem validados
        update (bool): Indica se é uma atualização (True) ou criação (False)
        
    Returns:
        str: Mensagem de erro ou None se válido
    """
    # Campos obrigatórios para criação
    if not update:
        required_fields = ['equipamento_id', 'departamento_id', 'solicitante_id', 'tipo_servico', 'descricao_problema']
        for field in required_fields:
            if field not in data or not data[field]:
                return f"Campo '{field}' é obrigatório"
    
    # Validações específicas
    if 'tipo_servico' in data and data['tipo_servico']:
        valid_tipos = ['MANUTENCAO_PREVENTIVA', 'MANUTENCAO_CORRETIVA', 'INSTALACAO', 'REMOCAO', 'CALIBRACAO']
        if data['tipo_servico'] not in valid_tipos:
            return f"Tipo de serviço inválido. Valores permitidos: {', '.join(valid_tipos)}"
    
    if 'status' in data and data['status']:
        valid_status = ['ABERTA', 'ATRIBUIDA', 'EM_ANDAMENTO', 'AGUARDANDO_PECAS', 'CONCLUIDA', 'CANCELADA']
        if data['status'] not in valid_status:
            return f"Status inválido. Valores permitidos: {', '.join(valid_status)}"
    
    if 'prioridade' in data and data['prioridade']:
        valid_prioridade = ['BAIXA', 'NORMAL', 'ALTA', 'EMERGENCIA']
        if data['prioridade'] not in valid_prioridade:
            return f"Prioridade inválida. Valores permitidos: {', '.join(valid_prioridade)}"
    
    if 'avaliacao_satisfacao' in data and data['avaliacao_satisfacao'] is not None:
        if not isinstance(data['avaliacao_satisfacao'], int) or data['avaliacao_satisfacao'] < 1 or data['avaliacao_satisfacao'] > 5:
            return "Avaliação de satisfação deve ser um número inteiro entre 1 e 5"
    
    return None

def validate_usuario(data, update=False):
    """
    Valida os dados de um usuário.
    
    Args:
        data (dict): Dados do usuário a serem validados
        update (bool): Indica se é uma atualização (True) ou criação (False)
        
    Returns:
        str: Mensagem de erro ou None se válido
    """
    # Campos obrigatórios para criação
    if not update:
        required_fields = ['nome', 'email', 'senha']
        for field in required_fields:
            if field not in data or not data[field]:
                return f"Campo '{field}' é obrigatório"
    
    # Validações específicas
    if 'email' in data and data['email']:
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, data['email']):
            return "Email inválido"
    
    if 'senha' in data and data['senha']:
        if len(data['senha']) < 6:
            return "Senha deve ter pelo menos 6 caracteres"
    
    if 'perfil' in data and data['perfil']:
        valid_perfis = ['ADMIN', 'GESTOR', 'TECNICO', 'SOLICITANTE', 'VISUALIZADOR']
        if data['perfil'] not in valid_perfis:
            return f"Perfil inválido. Valores permitidos: {', '.join(valid_perfis)}"
    
    return None

def validate_certificado(data, update=False):
    """
    Valida os dados de um certificado.
    
    Args:
        data (dict): Dados do certificado a serem validados
        update (bool): Indica se é uma atualização (True) ou criação (False)
        
    Returns:
        str: Mensagem de erro ou None se válido
    """
    # Campos obrigatórios para criação
    if not update:
        required_fields = ['equipamento_id', 'tipo', 'data_emissao', 'data_validade', 'emissor']
        for field in required_fields:
            if field not in data or not data[field]:
                return f"Campo '{field}' é obrigatório"
    
    # Validações específicas
    if 'tipo' in data and data['tipo']:
        valid_tipos = ['CALIBRACAO', 'SEGURANCA_ELETRICA', 'CONFORMIDADE', 'QUALIDADE']
        if data['tipo'] not in valid_tipos:
            return f"Tipo de certificado inválido. Valores permitidos: {', '.join(valid_tipos)}"
    
    if 'status' in data and data['status']:
        valid_status = ['VALIDO', 'VENCIDO', 'PENDENTE']
        if data['status'] not in valid_status:
            return f"Status inválido. Valores permitidos: {', '.join(valid_status)}"
    
    # Validar datas
    if 'data_emissao' in data and 'data_validade' in data:
        from datetime import datetime
        try:
            data_emissao = datetime.fromisoformat(data['data_emissao'])
            data_validade = datetime.fromisoformat(data['data_validade'])
            
            if data_validade < data_emissao:
                return "Data de validade não pode ser anterior à data de emissão"
        except ValueError:
            return "Formato de data inválido. Use ISO 8601 (YYYY-MM-DD)"
    
    return None
