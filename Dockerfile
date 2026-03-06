FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libcob4 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY coin /workspace/coin
COPY cotacao.txt /workspace/

RUN chmod +x /workspace/coin

COPY main.py /workspace/
COPY requirements.txt /workspace/

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8080

CMD exec functions-framework --target=conversor_moedas --debug --port=$PORT
