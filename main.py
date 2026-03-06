import json
import subprocess
import functions_framework
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def conversor_moedas(request):
    """
    Cloud Function para converter moedas usando COBOL
    
    POST /conversor_moedas
    {
        "valor": "100",
        "moeda": "USD"
    }
    """
    
    try:
        # Validar método
        if request.method != 'POST':
            return json.dumps({
                'erro': 'Use POST',
                'sucesso': False
            }), 405, {'Content-Type': 'application/json'}
        
        # Parse JSON
        try:
            data = request.get_json()
        except:
            return json.dumps({
                'erro': 'JSON inválido',
                'sucesso': False
            }), 400, {'Content-Type': 'application/json'}
        
        if not data:
            return json.dumps({
                'erro': 'Corpo vazio',
                'sucesso': False
            }), 400, {'Content-Type': 'application/json'}
        
        # Extrair parâmetros
        valor = str(data.get('valor', '')).strip()
        moeda = str(data.get('moeda', '')).strip().upper()
        
        # Validar
        if not valor or not moeda:
            return json.dumps({
                'erro': 'Faltam parâmetros: valor e moeda',
                'sucesso': False
            }), 400, {'Content-Type': 'application/json'}
        
        # Validar moedas
        moedas_validas = ['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD']
        if moeda not in moedas_validas:
            return json.dumps({
                'erro': f'Moeda inválida. Válidas: {", ".join(moedas_validas)}',
                'sucesso': False
            }), 400, {'Content-Type': 'application/json'}
        
        logger.info(f"Convertendo: {valor} BRL → {moeda}")
        
        # ===== EXECUTAR COBOL =====
        # O binário foi compilado em /workspace/coin pelo Dockerfile
        coin_path = '/workspace/coin'
        
        # Verificar se binário existe
        if not os.path.exists(coin_path):
            logger.error(f"Binário não encontrado: {coin_path}")
            logger.error(f"Arquivos em /workspace: {os.listdir('/workspace') if os.path.exists('/workspace') else 'não existe'}")
            return json.dumps({
                'erro': 'Erro interno: binário não encontrado',
                'sucesso': False
            }), 500, {'Content-Type': 'application/json'}
        
        # Verificar se é executável
        if not os.access(coin_path, os.X_OK):
            logger.warning(f"Binário não é executável, tentando mesmo assim...")
        
        # Executar
        try:
            resultado = subprocess.run(
                [coin_path, valor, moeda],
                capture_output=True,
                text=True,
                timeout=5,
                cwd='/workspace'  # Diretório onde está cotacao.txt
            )
        except subprocess.TimeoutExpired:
            logger.error("Timeout ao executar COBOL")
            return json.dumps({
                'erro': 'Execução demorou muito',
                'sucesso': False
            }), 408, {'Content-Type': 'application/json'}
        except Exception as e:
            logger.error(f"Erro ao executar: {str(e)}")
            return json.dumps({
                'erro': f'Erro na execução: {str(e)}',
                'sucesso': False
            }), 500, {'Content-Type': 'application/json'}
        
        # Verificar resultado
        if resultado.returncode != 0:
            logger.error(f"COBOL retornou código {resultado.returncode}")
            logger.error(f"Stderr: {resultado.stderr}")
            return json.dumps({
                'erro': resultado.stderr.strip() if resultado.stderr else 'Erro na conversão',
                'sucesso': False
            }), 400, {'Content-Type': 'application/json'}
        
        # Sucesso!
        output = resultado.stdout.strip()
        logger.info(f"Sucesso: {output}")
        
        return json.dumps({
            'resultado': output,
            'sucesso': True,
            'moeda': moeda,
            'valor_original': valor
        }), 200, {'Content-Type': 'application/json'}
    
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        return json.dumps({
            'erro': f'Erro: {str(e)}',
            'sucesso': False
        }), 500, {'Content-Type': 'application/json'}
