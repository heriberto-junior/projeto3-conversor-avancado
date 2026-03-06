import json
import subprocess
import functions_framework
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def conversor_moedas(request):
    """Cloud Function que executa COBOL"""
    
    try:
        if request.method != 'POST':
            return json.dumps({'erro': 'Use POST', 'sucesso': False}), 405
        
        request_json = request.get_json()
        if not request_json:
            return json.dumps({'erro': 'JSON vazio', 'sucesso': False}), 400
        
        valor = str(request_json.get('valor', ''))
        moeda = str(request_json.get('moeda', '')).upper()
        
        if not valor or not moeda:
            return json.dumps({'erro': 'Faltam valor ou moeda', 'sucesso': False}), 400
        
        moedas_validas = ['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD']
        if moeda not in moedas_validas:
            return json.dumps({'erro': f'Moeda inválida: {moeda}', 'sucesso': False}), 400
        
        logger.info(f"Convertendo {valor} para {moeda}")
        
        # Procurar coin em /workspace
        coin_path = '/workspace/coin'
        
        if not os.path.exists(coin_path):
            logger.error(f"coin não encontrado em {coin_path}")
            return json.dumps({'erro': 'Binário COBOL não encontrado', 'sucesso': False}), 500
        
        # Executar COBOL
        resultado = subprocess.run(
            [coin_path, valor, moeda],
            capture_output=True,
            text=True,
            timeout=5,
            cwd='/workspace'
        )
        
        if resultado.returncode != 0:
            logger.error(f"Erro COBOL: {resultado.stderr}")
            return json.dumps({'erro': resultado.stderr.strip(), 'sucesso': False}), 400
        
        output = resultado.stdout.strip()
        logger.info(f"Resultado: {output}")
        
        return json.dumps({
            'resultado': output,
            'sucesso': True,
            'moeda': moeda,
            'valor_original': valor
        }), 200
    
    except subprocess.TimeoutExpired:
        return json.dumps({'erro': 'Timeout na execução', 'sucesso': False}), 408
    except Exception as e:
        logger.error(f"Erro: {str(e)}", exc_info=True)
        return json.dumps({'erro': str(e), 'sucesso': False}), 500
