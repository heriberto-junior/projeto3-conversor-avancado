FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libcob4 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY coin.cob /workspace/coin.cob
COPY cotacao.txt /workspace/cotacao.txt
COPY coin /workspace/coin
COPY main.py /workspace/main.py
COPY requirements.txt /workspace/requirements.txt

RUN chmod +x /workspace/coin

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

CMD exec functions-framework --target=conversor_moedas --debug --port=$PORT
