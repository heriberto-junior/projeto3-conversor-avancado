FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    gnucobol \
    libcob4 \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY coin.cob /workspace/coin.cob
COPY cotacao.txt /workspace/cotacao.txt
COPY main.py /workspace/main.py
COPY requirements.txt /workspace/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

CMD exec python3 -m functions_framework --target=conversor_moedas --debug --port=$PORT
