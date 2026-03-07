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
    # Rodar na porta 5000, acessível de fora
    app.run(host='0.0.0.0', port=5000, debug=True)
