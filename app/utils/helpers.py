import os
import qrcode
from datetime import datetime

def generate_qrcode(equipment_id, equipment_code):
    """
    Gera um QR Code para um equipamento e salva como imagem.
    
    Args:
        equipment_id (str): ID do equipamento
        equipment_code (str): Código do equipamento
        
    Returns:
        str: Caminho relativo para a imagem do QR Code
    """
    # Criar diretório para QR Codes se não existir
    qr_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'uploads', 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Gerar conteúdo do QR Code (URL para acessar o equipamento)
    qr_content = f"https://manutencao-clinica.com/equipamentos/{equipment_id}"
    
    # Criar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)
    
    # Criar imagem
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Salvar imagem
    filename = f"qrcode_{equipment_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    file_path = os.path.join(qr_dir, filename)
    img.save(file_path)
    
    # Retornar caminho relativo
    return f"/uploads/qrcodes/{filename}"

def format_currency(value):
    """
    Formata um valor para moeda brasileira.
    
    Args:
        value (float): Valor a ser formatado
        
    Returns:
        str: Valor formatado como moeda brasileira
    """
    if value is None:
        return "R$ 0,00"
    
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calculate_next_maintenance_date(last_maintenance_date, frequency):
    """
    Calcula a próxima data de manutenção com base na última manutenção e frequência.
    
    Args:
        last_maintenance_date (datetime.date): Data da última manutenção
        frequency (str): Frequência de manutenção (DIARIA, SEMANAL, QUINZENAL, MENSAL, etc.)
        
    Returns:
        datetime.date: Data da próxima manutenção
    """
    if not last_maintenance_date:
        return None
    
    from datetime import timedelta
    
    if frequency == 'DIARIA':
        return last_maintenance_date + timedelta(days=1)
    elif frequency == 'SEMANAL':
        return last_maintenance_date + timedelta(weeks=1)
    elif frequency == 'QUINZENAL':
        return last_maintenance_date + timedelta(weeks=2)
    elif frequency == 'MENSAL':
        # Aproximação simples para um mês
        return last_maintenance_date + timedelta(days=30)
    elif frequency == 'TRIMESTRAL':
        return last_maintenance_date + timedelta(days=90)
    elif frequency == 'SEMESTRAL':
        return last_maintenance_date + timedelta(days=180)
    elif frequency == 'ANUAL':
        return last_maintenance_date + timedelta(days=365)
    else:
        return None

def is_certificate_expired(expiration_date):
    """
    Verifica se um certificado está vencido.
    
    Args:
        expiration_date (datetime.date): Data de validade do certificado
        
    Returns:
        bool: True se estiver vencido, False caso contrário
    """
    if not expiration_date:
        return True
    
    return expiration_date < datetime.now().date()

def is_certificate_expiring_soon(expiration_date, days=30):
    """
    Verifica se um certificado está prestes a vencer.
    
    Args:
        expiration_date (datetime.date): Data de validade do certificado
        days (int): Número de dias para considerar como "prestes a vencer"
        
    Returns:
        bool: True se estiver prestes a vencer, False caso contrário
    """
    if not expiration_date:
        return False
    
    from datetime import timedelta
    
    return not is_certificate_expired(expiration_date) and expiration_date <= (datetime.now().date() + timedelta(days=days))

def calculate_maintenance_cost(labor_cost, parts_cost):
    """
    Calcula o custo total de uma manutenção.
    
    Args:
        labor_cost (float): Custo de mão de obra
        parts_cost (float): Custo de peças
        
    Returns:
        float: Custo total
    """
    labor_cost = float(labor_cost) if labor_cost is not None else 0
    parts_cost = float(parts_cost) if parts_cost is not None else 0
    
    return labor_cost + parts_cost
