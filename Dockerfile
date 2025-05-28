FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante dos arquivos
COPY . .

# Criar diretório para uploads
RUN mkdir -p uploads/qrcodes

# Expor a porta que a aplicação usará
EXPOSE 8080

# Configurar variáveis de ambiente
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PORT=8080

# Comando para iniciar a aplicação
CMD gunicorn --bind 0.0.0.0:$PORT run:app
