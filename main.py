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
            return json.dumps({'erro': 'Use POST', 'sucesso': False}), 405, {'Content-Type': 'application/json'}
        
        data = request.get_json()
        if not data:
            return json.dumps({'erro': 'JSON vazio', 'sucesso': False}), 400, {'Content-Type': 'application/json'}
        
        valor = str(data.get('valor', '')).strip()
        moeda = str(data.get('moeda', '')).strip().upper()
        
        if not valor or not moeda:
            return json.dumps({'erro': 'Faltam parâmetros: valor e moeda', 'sucesso': False}), 400, {'Content-Type': 'application/json'}
        
        moedas_validas = ['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD']
        if moeda not in moedas_validas:
            return json.dumps({'erro': f'Moeda inválida: {moeda}', 'sucesso': False}), 400, {'Content-Type': 'application/json'}
        
        logger.info(f"Convertendo: {valor} BRL → {moeda}")
        
        coin_path = '/workspace/coin'
        
        if not os.path.exists(coin_path):
            logger.error(f"coin não encontrado em {coin_path}")
            return json.dumps({'erro': 'Binário COBOL não encontrado', 'sucesso': False}), 500, {'Content-Type': 'application/json'}
        
        try:
            resultado = subprocess.run(
                [coin_path, valor, moeda],
                capture_output=True,
                text=True,
                timeout=5,
                cwd='/workspace'
            )
        except subprocess.TimeoutExpired:
            return json.dumps({'erro': 'Timeout na execução', 'sucesso': False}), 408, {'Content-Type': 'application/json'}
        except Exception as e:
            logger.error(f"Erro: {str(e)}")
            return json.dumps({'erro': f'Erro na execução: {str(e)}', 'sucesso': False}), 500, {'Content-Type': 'application/json'}
        
        if resultado.returncode != 0:
            logger.error(f"COBOL error: {resultado.stderr}")
            return json.dumps({'erro': resultado.stderr.strip(), 'sucesso': False}), 400, {'Content-Type': 'application/json'}
        
        output = resultado.stdout.strip()
        logger.info(f"Sucesso: {output}")
        
        return json.dumps({
            'resultado': output,
            'sucesso': True,
            'moeda': moeda,
            'valor_original': valor
        }), 200, {'Content-Type': 'application/json'}
    
    except Exception as e:
        logger.error(f"Erro: {str(e)}", exc_info=True)
        return json.dumps({'erro': str(e), 'sucesso': False}), 500, {'Content-Type': 'application/json'}
