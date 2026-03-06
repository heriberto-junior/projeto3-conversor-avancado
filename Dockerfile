# Começa com imagem Ubuntu
FROM ubuntu:24.04

# Instala COBOL e bibliotecas
RUN apt-get update && apt-get install -y \
    gnucobol \
    libcob4 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Define pasta de trabalho
WORKDIR /app

# Copia seus arquivos do repositório para dentro da imagem
COPY coin.cob /app/
COPY cotacao.txt /app/
COPY entrypoint.sh /app/

# Compila o COBOL (uma vez, não toda vez que usar)
RUN cobc -x -free -static -o coin coin.cob

# Torna o entrypoint executável
RUN chmod +x /app/entrypoint.sh

# Define o que roda quando alguém chamar essa imagem
ENTRYPOINT ["/app/entrypoint.sh"]
