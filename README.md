# 📚 Documentação Completa - Conversor de Moedas COBOL

## 🎯 Projeto Final

Um **conversor de moedas desenvolvido em COBOL** que executa via **API REST em Python**, demonstrando integração entre linguagens clássicas (COBOL) com tecnologias modernas.

**Status:** ✅ Funcionando 100%

---

## 📋 Índice

1. [Ambiente](#ambiente)
2. [Instalação Completa](#instalação-completa)
3. [Compilação COBOL](#compilação-cobol)
4. [Configuração API Python](#configuração-api-python)
5. [Testes](#testes)
6. [Deploy no GitHub](#deploy-no-github)
7. [Comandos Rápidos](#comandos-rápidos)

---

## 🖥️ Ambiente

### Hardware Utilizado
- **PC:** Windows 10/11
- **Virtualização:** VirtualBox (grátis)
- **Sistema Operacional VM:** Ubuntu 24.04 LTS

### Softwares Instalados na VM
- GNU COBOL (compilador)
- Python 3.12
- Flask (framework web)
- Git (controle de versão)
- VSCode (editor de código)
- cURL (teste de API)

---

## 📦 Instalação Completa

### PASSO 1: Criar VM VirtualBox

```bash
# Baixar VirtualBox: https://www.virtualbox.org/wiki/Downloads
# Baixar Ubuntu ISO: https://ubuntu.com/download/desktop (24.04 LTS)

# No VirtualBox:
# - Clique "Novo"
# - Nome: Ubuntu-COBOL
# - ISO: selecione arquivo Ubuntu
# - Tipo: Linux / Ubuntu 64-bit
# - RAM: 4096 MB
# - Processadores: 2
# - Disco: 50 GB
# - Firewall: ✓ HTTP, ✓ HTTPS
# - Clique "Finish"
```

### PASSO 2: Instalar Ubuntu na VM

```bash
# Após iniciar VM:
# - Português (ou English)
# - Install Ubuntu
# - Normal Installation
# - ✓ Install third-party software
# - Create user: username=cobol, password=123456
# - Aguarde ~15 minutos
```

### PASSO 3: Instalar Dependências do Sistema

Após logar na VM, abrir Terminal:

```bash
# Atualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar Git
sudo apt-get install -y git

# Instalar COBOL
sudo apt-get install -y gnucobol

# Instalar Python
sudo apt-get install -y python3 python3-pip

# Instalar Python venv (para isolamento de ambiente)
sudo apt install -y python3.12-venv

# Instalar VSCode
sudo snap install --classic code

# Instalar cURL (para testar API)
sudo apt install -y curl
```

**Tempo total:** ~15-20 minutos

---

## 🔐 Configurar Git na VM

### PASSO 1: Configurar Identidade Git

```bash
# Seu nome
git config --global user.name "Seu Nome"

# Seu email
git config --global user.email "seu.email@gmail.com"
```

### PASSO 2: Gerar Chave SSH

```bash
# Gerar chave SSH
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Copiar chave pública
cat ~/.ssh/id_rsa.pub
```

**Copie TODO o texto que aparecer.**

### PASSO 3: Adicionar Chave no GitHub

1. Vá para: https://github.com/settings/keys
2. Clique "New SSH key"
3. Cole a chave copiada
4. Clique "Add SSH key"

### PASSO 4: Clonar Repositório

```bash
# Clonar seu repositório
git clone git@github.com:heriberto-junior/projeto3-conversor-avancado.git

# Entrar na pasta
cd projeto3-conversor-avancado
```

---

## 🔧 Compilação COBOL

### Estrutura de Arquivos

```
projeto3-conversor-avancado/
├── coin.cob          (Programa COBOL principal)
├── cotacao.txt       (Arquivo de dados com cotações)
├── app.py            (API Python que chama COBOL)
├── coin              (Binário compilado - GERADO)
├── venv/             (Virtual environment Python - GERADO)
├── README.md         (Documentação)
└── .gitignore        (Arquivos ignorados pelo Git)
```

### Compilar COBOL

```bash
# Compilar coin.cob para gerar binário 'coin'
cobc -x -free -static -o coin coin.cob
```

**Explicação de flags:**
- `-x` : Gera executável
- `-free` : Formato livre (não fixed)
- `-static` : Compilação estática (sem dependências externas)
- `-o coin` : Nome do executável

### Verificar Compilação

```bash
# Listar arquivo compilado
ls -lah coin

# Deve aparecer algo como: -rwxr-xr-x 1 cobol cobol 69K Mar 6 12:00 coin
```

### Testar COBOL Manualmente

```bash
# Testar conversão
./coin 100 USD

# Resposta esperada:
# Resultado:  19330.000 USD
```

---

## 🐍 Configuração API Python

### PASSO 1: Criar Virtual Environment

O virtual environment isola pacotes Python para este projeto.

```bash
# Criar venv
python3 -m venv venv

# Ativar venv
source venv/bin/activate

# Você deve ver (venv) antes do prompt
```

### PASSO 2: Instalar Flask

```bash
# Instalar Flask (framework web)
pip install flask
```

**Nota:** Dentro do venv, use `pip` (não `pip3`)

### PASSO 3: Criar app.py

No terminal (não em Python!):

```bash
cat > app.py << 'EOF'
from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Diretório onde está o binário coin
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/converter', methods=['POST'])
def converter():
    """Endpoint que chama COBOL"""
    try:
        # Receber JSON
        data = request.get_json()
        valor = str(data.get('valor', ''))
        moeda = str(data.get('moeda', ''))
        
        # Validar
        if not valor or not moeda:
            return jsonify({
                'erro': 'Faltam parâmetros: valor e moeda',
                'sucesso': False
            }), 400
        
        # Executar COBOL
        resultado = subprocess.run(
            [os.path.join(PROJECT_DIR, 'coin'), valor, moeda],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=PROJECT_DIR
        )
        
        # Verificar resultado
        if resultado.returncode == 0:
            return jsonify({
                'resultado': resultado.stdout.strip(),
                'sucesso': True,
                'valor': valor,
                'moeda': moeda
            }), 200
        else:
            return jsonify({
                'erro': resultado.stderr.strip(),
                'sucesso': False
            }), 400
    
    except subprocess.TimeoutExpired:
        return jsonify({
            'erro': 'Execução demorou muito',
            'sucesso': False
        }), 408
    except Exception as e:
        return jsonify({
            'erro': str(e),
            'sucesso': False
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Verificar se API está online"""
    return jsonify({
        'status': 'online',
        'servico': 'Conversor de Moedas COBOL'
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF
```

**Importante:** Este é um comando bash. Copie EXATAMENTE como está, sem modificações.

### Verificar app.py

```bash
# Listar arquivo criado
ls -lah app.py

# Verificar conteúdo
head -10 app.py
```

---

## 🧪 Testes

### PASSO 1: Rodar API

Na aba 1 do terminal:

```bash
# Certifique-se de estar na pasta do projeto
cd ~/projeto3-conversor-avancado

# Ativar venv
source venv/bin/activate

# Rodar API
python3 app.py
```

**Resposta esperada:**
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
 * Debugger is active!
```

### PASSO 2: Testar em Outra Aba

Abra **OUTRA aba** do terminal (não feche a primeira):

```bash
# Entrar na pasta do projeto
cd ~/projeto3-conversor-avancado

# Ativar venv (importante!)
source venv/bin/activate

# Testar API
curl -X POST http://localhost:5000/converter \
  -H "Content-Type: application/json" \
  -d '{"valor":"100","moeda":"USD"}'
```

**Resposta esperada:**
```json
{
  "moeda": "USD",
  "resultado": "Resultado:  19330.000 USD",
  "sucesso": true,
  "valor": "100"
}
```

### PASSO 3: Testar Health Check

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

### PASSO 4: Testar Outras Moedas

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

## 📤 Deploy no GitHub

### PASSO 1: Verificar Status

```bash
# Ver arquivos modificados/criados
git status
```

**Resposta esperada:**
```
Changes not staged for commit:
  modified:   coin.cob
  
Untracked files:
  app.py
  coin
```

### PASSO 2: Criar .gitignore

Para não enviar arquivos desnecessários:

```bash
cat > .gitignore << 'EOF'
venv/
__pycache__/
*.pyc
.DS_Store
.vscode/
*.swp
EOF
```

### PASSO 3: Adicionar Arquivos

```bash
# Adicionar arquivos
git add coin.cob app.py coin README.md .gitignore

# Verificar o que será commitado
git status
```

### PASSO 4: Fazer Commit

```bash
git commit -m "Add COBOL API: Python Flask wrapper for COBOL converter"
```

### PASSO 5: Fazer Push

```bash
git push
```

**Resposta esperada:**
```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 4 threads
Writing objects: 100% (3/3), 2.5 KiB | 2.5 MiB/s, done.
Total 3 (delta 1), reused 0 (delta 0)
remote: Resolving deltas: 100% (1/1), completed with 1 local object.
To https://github.com/heriberto-junior/projeto3-conversor-avancado.git
   abc1234..def5678  main -> main
```

---

## ⚡ Comandos Rápidos (Cheat Sheet)

### Iniciar Desenvolvendo

```bash
# 1. Entrar na pasta
cd ~/projeto3-conversor-avancado

# 2. Ativar venv
source venv/bin/activate

# 3. Compilar COBOL (se modificou coin.cob)
cobc -x -free -static -o coin coin.cob

# 4. Rodar API
python3 app.py
```

### Testar API

```bash
# Em outra aba, com venv ativado:
curl -X POST http://localhost:5000/converter \
  -H "Content-Type: application/json" \
  -d '{"valor":"100","moeda":"USD"}'
```

### Fazer Commit

```bash
git add app.py coin.cob
git commit -m "Sua mensagem aqui"
git push
```

### Parar API

```bash
# Na aba onde app.py está rodando, pressione:
CTRL + C
```

### Desativar venv

```bash
deactivate
```

---

## 📊 Estrutura de Dados

### Arquivo cotacao.txt

```
USD00019330     # Dólar: 1 BRL = 0.19330 USD
EUR00016653     # Euro: 1 BRL = 0.16653 EUR
JPY03041189     # Iene: 1 BRL = 0.3041189 JPY
GBP00014400     # Libra: 1 BRL = 0.14400 GBP
AUD00027190     # Dólar Australiano: 1 BRL = 0.27190 AUD
CAD00026360     # Dólar Canadense: 1 BRL = 0.26360 CAD
```

**Formato:** `MOEDATAXA`
- `MOEDA`: 3 caracteres (USD, EUR, JPY, etc)
- `TAXA`: 8 dígitos sem ponto decimal (multiplicar por 0.00001)

---

## 🔄 Fluxo de Funcionamento

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

---

## 🐛 Troubleshooting

### Erro: "pip: command not found"
**Solução:** Você saiu do venv. Execute `source venv/bin/activate`

### Erro: "No module named 'flask'"
**Solução:** Ative venv e instale: `pip install flask`

### Erro: "./coin: command not found"
**Solução:** Compile COBOL: `cobc -x -free -static -o coin coin.cob`

### Erro: "Arquivo ou diretório inexistente" ao ativar venv
**Solução:** Crie venv: `python3 -m venv venv`

### Porta 5000 já em uso
**Solução:** 
```bash
# Encontrar processo usando porta 5000
lsof -i :5000

# Matar processo (substitua PID)
kill -9 PID
```

---

## 📝 Próximos Passos

1. **Melhorar README.md** com instruções para entrevistadores
2. **Adicionar Docker** para facilitar setup (opcional)
3. **Deploy na nuvem** (Google Cloud, AWS, etc)
4. **Integração com IA** no VSCode
5. **Adicionar testes automatizados**

---

## 📞 Resumo Executivo

| Aspecto | Detalhes |
|---------|----------|
| **Linguagem Principal** | COBOL |
| **API** | Python + Flask |
| **Sistema Operacional** | Ubuntu 24.04 LTS |
| **Compilador COBOL** | GNU COBOL |
| **Framework Web** | Flask 3.x |
| **Porta API** | 5000 |
| **Status** | ✅ Funcionando |
| **GitHub** | https://github.com/heriberto-junior/projeto3-conversor-avancado |

---

**Última atualização:** 2026-03-06
**Status:** Completo e funcionando 100%
