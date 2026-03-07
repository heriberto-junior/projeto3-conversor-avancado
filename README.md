## Projeto 3 - Conversor de moedas desenvolvido em COBOL que executa via API REST em Python

---

## Ambiente

### Hardware Utilizado
- **PC:** Windows 10
- **Virtualização:** VirtualBox (Linux)
- **Sistema Operacional VM:** Ubuntu 24.04 LTS

### Softwares Instalados na VM
- GNU COBOL (compilador)
- Python 3.12
- Flask (framework web)
- Git (controle de versão)
- VSCode (editor de código)
- cURL (teste de API)

---

## O que foi instalado

### 1: VM VirtualBox

```bash
# Baixado VirtualBox: https://www.virtualbox.org/wiki/Downloads
# Baixado Ubuntu ISO: https://ubuntu.com/download/desktop (24.04 LTS)

# No VirtualBox foi setado:
# - Tipo: Linux / Ubuntu 64-bit
# - RAM: 4096 MB
# - Processadores: 2
# - Disco: 10 GB
```

### 2: Instalações de Dependências do Sistema

Após logar na VM, foi necessário entrar no Terminal e efetuar os comandos:

```bash
# Atualização sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalação do Git
sudo apt-get install -y git

# Instalação do COBOL GNU
sudo apt-get install -y gnucobol

# Instalação do Python
sudo apt-get install -y python3 python3-pip

# Instalação do Python venv (para isolamento de ambiente)
sudo apt install -y python3.12-venv

# Instalação do VSCode
sudo snap install --classic code

# Instalação do cURL (para testar API)
sudo apt install -y curl
```

---

## Configuração do Git na VM

Após efetuar as instalações, foi necessário entrar no no VSCode, abrir o terminal com ctrl+j e efetuar os comandos para configurar o git:

### 1: Configurar Identidade Git

```bash
# Configurar o nome
git config --global user.name "Meu Nome no git"

# Configurar meu e-mail
git config --global user.email "meu.email@gmail.com do git"
```

### 2: Gerar Chave SSH

```bash
# Gerar chave SSH
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Gerar chave pública
cat ~/.ssh/id_rsa.pub
```

**Foi encessário copiar todo o código da chave gerada.**

### 3: Adicionar Chave no GitHub

1. Ir em: https://github.com/settings/keys
2. Cliquar em "New SSH key"
3. Colar a chave copiada
4. Cliquar em "Add SSH key"

### 4: Clonar Repositório

```bash
# Clonar meu repositório
git clone git@github.com:heriberto-junior/projeto3-conversor-avancado.git

# Entrar na pasta
cd projeto3-conversor-avancado
```

---

## Compilação do COBOL

### Estrutura de Arquivos

```
projeto3-conversor-avancado/
├── coin.cob          (Programa COBOL principal)
├── cotacao.txt       (Arquivo de dados com cotações)
├── app.py            (API Python que chama COBOL)
├── coin              (Binário compilado - Gerado no VSCode)
├── venv/             (Virtual environment Python - Gerado no VSCode)
├── README.md         (Documentação)
└── .gitignore        (Arquivos ignorados pelo Git)
```

### Compilação do COBOL

```bash
# Foi necessário compilar o coin.cob para gerar binário 'coin'
cobc -x -free -static -o coin coin.cob
```

**Explicação das flags da compilação:**
- `cobc` : Instrução de compilação
- `-x` : Gera executável
- `-free` : Formato livre (não fixado)
- `-static` : Compilação estática (para não ter dependências externas)
- `-o coin` : Nome do executável

### Comandos usados para verificar a compilação

```bash
# Lista arquivo compilado
ls -lah coin

# Deve aparecer algo como: -rwxr-xr-x 1 cobol cobol 69K Mar 6 12:00 coin
```

### Comando para testar o COBOL Manualmente

```bash
# Testar conversão
./coin 100 USD

# Resposta esperada:
# Resultado:  19330.000 USD
```

---

## Configuração API Python

### 1: Criação do Virtual Environment

O virtual environment foi usado para isolar pacotes Python para este projeto.

```bash
# Criação do venv
python3 -m venv venv

# Ativação do venv
source venv/bin/activate
```

### 2: Instalação do Flask

```bash
# Instalar Flask (framework web)
pip install flask
```

**Nota de lembrança:** Dentro do venv, tive que usar `pip` (não `pip3`)

### 3: Criação do app.py

Criado o app.py para chamar o Cobol e testar a execução.


### 4: Verificação do app.py

```bash
# Listagem do arquivo criado
ls -lah app.py

# Verificação conteúdo
head -10 app.py
```

---

## Testes

### 1: Rodar API em 1 aba do terminal do VSCode

Em uma aba do terminal foi necessário:

```bash
# Entrar na pasta do projeto
cd ~/projeto3-conversor-avancado

# Ativar venv
source venv/bin/activate

# Rodar API
python3 app.py
```

**Isso me deve dar a resposta:**
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
 * Debugger is active!
```

### 2: Testar em Outra Aba

Sem fechar a primeira aba foi necessário:

```bash
# Entrar na pasta do projeto
cd ~/projeto3-conversor-avancado

# Ativar o venv
source venv/bin/activate

# Testar API
curl -X POST http://localhost:5000/converter \
  -H "Content-Type: application/json" \
  -d '{"valor":"100","moeda":"USD"}'
```

**Isso deve me trazer o resultado esperado:**
```json
{
  "moeda": "USD",
  "resultado": "Resultado:  19330.000 USD",
  "sucesso": true,
  "valor": "100"
}
```

### 3: Testar Health Check

```bash
curl http://localhost:5000/health
```

**Resposta esperada:**
```json
{
  "servico": "Conversor de Moedas COBOL",
  "status": "online"
}
```

### 4: Demais testes com outras moedas

```bash
# EUR (Euro)
curl -X POST http://localhost:5000/converter \
  -H "Content-Type: application/json" \
  -d '{"valor":"50","moeda":"EUR"}'

# JPY (Iene)
curl -X POST http://localhost:5000/converter \
  -H "Content-Type: application/json" \
  -d '{"valor":"1000","moeda":"JPY"}'
```

---

## Estrutura de Dados atual

### Arquivo cotacao.txt

```
USD00019330     # Dólar: 1 BRL = 0.19330 USD
EUR00016653     # Euro: 1 BRL = 0.16653 EUR
JPY03041189     # Iene: 1 BRL = 0.3041189 JPY
GBP00014400     # Libra: 1 BRL = 0.14400 GBP
AUD00027190     # Dólar Australiano: 1 BRL = 0.27190 AUD
CAD00026360     # Dólar Canadense: 1 BRL = 0.26360 CAD
```

**Formato:** 
- `MOEDA`: 3 caracteres (USD, EUR, JPY, etc)
- `TAXA`: 8 dígitos, sendo internamente usado no cobol como 3 campos inteiros e 5 campos fracionados

---

## Fluxo de Funcionamento

```
1. Usuário envia requisição HTTP POST
   ↓
2. API Python (Flask) recebe JSON
   ↓
3. Valida parâmetros (valor, moeda)
   ↓
4. Chama binário COBOL: ./coin 100 USD
   ↓
5. COBOL lê cotacao.txt
   ↓
6. COBOL calcula conversão
   ↓
7. COBOL retorna: "Resultado: 19330.000 USD"
   ↓
8. API converte para JSON
   ↓
9. Retorna resposta ao usuário
```

