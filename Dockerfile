FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    gnucobol \
    libcob4 \
    python3-pip \
    python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY coin.cob /workspace/coin.cob
COPY cotacao.txt /workspace/cotacao.txt

RUN cobc -x -free -static -o /workspace/coin /workspace/coin.cob

COPY main.py /workspace/main.py
COPY requirements.txt /workspace/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

CMD exec functions-framework --target=conversor_moedas --debug --port=$PORT
