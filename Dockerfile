FROM python:latest

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Verifica se os arquivos foram copiados corretamente
RUN echo "=== Estrutura de arquivos ===" && \
    ls -la && \
    echo "=== Arquivos Python ===" && \
    find . -name "*.py"

EXPOSE 8000

# Comando mais robusto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]