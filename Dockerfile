FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gnucobol \
    libcob4 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY coin.cob .
COPY cotacao.txt .

RUN cobc -x -free -static -o coin coin.cob

COPY main.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8080

CMD exec functions-framework --target=conversor_moedas --debug --port=$PORT
