#!/bin/bash

# Pega o primeiro argumento ($1) e coloca em VALOR
# Pega o segundo argumento ($2) e coloca em MOEDA
VALOR=$1
MOEDA=$2

# Validação básica
if [ -z "$VALOR" ] || [ -z "$MOEDA" ]; then
  echo "Erro: Uso: entrypoint.sh <valor> <moeda>"
  exit 1
fi

# Executa o COBOL compilado
# /app/coin é o binário que foi compilado no Dockerfile
RESULTADO=$(/app/coin "$VALOR" "$MOEDA" 2>&1)

# Mostra o resultado (pode ser JSON ou texto)
echo "$RESULTADO"
