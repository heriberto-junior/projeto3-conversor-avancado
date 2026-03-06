import json
import subprocess
import functions_framework
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def conversor_moedas(request):
    """Cloud Function com DEBUG"""
    
    try:
        # ===== DEBUG: Listar arquivos =====
        logger.info("=== DEBUG: Listando arquivos em /workspace ===")
        if os.path.exists('/workspace'):
            arquivos = os.listdir('/workspace')
            logger.info(f"Arquivos em /workspace: {arquivos}")
            for arq in arquivos:
                caminho = os.path.join('/workspace', arq)
                tamanho = os.path.getsize(caminho) if os.path.isfile(caminho) else "dir"
                executavel = "✓" if os.access(caminho, os.X_OK) else "✗"
                logger.info(f"  {arq}: {tamanho} bytes, executável: {executavel}")
        else:
            logger.error("/workspace não existe!")
            return json.dumps({'erro': '/workspace não existe', 'sucesso': False}), 500, {'Content-Type': 'application/json'}
        
        # ===== Validar requisição =====
        if request.method != 'POST':
            return json.dumps({'erro': 'Use POST', 'sucesso': False}), 405, {'Content-Type': 'application/json'}
        
        try:
            data = request.get_json()
        except:
            return json.dumps({'erro': 'JSON inválido', 'sucesso': False}), 400, {'Content-Type': 'application/json'}
        
        if not data:
            return json.dumps({'erro': 'Corpo vazio', 'sucesso': False}), 400, {'Content-Type': 'application/json'}
        
        valor = str(data.get('valor', '')).strip()
        moeda = str(data.get('moeda', '')).strip().upper()
        
        if not valor or not moeda:
            return json.dumps({'erro': 'Faltam parâmetros', 'sucesso': False}), 400, {'Content-Type': 'application/json'}
        
        moedas_validas = ['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD']
        if moeda not in moedas_validas:
            return json.dumps({'erro': f'Moeda inválida', 'sucesso': False}), 400, {'Content-Type': 'application/json'}
        
        logger.info(f"Convertendo: {valor} BRL → {moeda}")
        
        # ===== Procurar coin em vários caminhos =====
        caminhos = ['/workspace/coin', '/app/coin', './coin']
        coin_path = None
        
        for caminho in caminhos:
            if os.path.exists(caminho):
                coin_path = caminho
                logger.info(f"Encontrado coin em: {caminho}")
                break
        
        if not coin_path:
            logger.error(f"coin não encontrado em nenhum caminho: {caminhos}")
            logger.error(f"Arquivos disponíveis: {os.listdir('/workspace') if os.path.exists('/workspace') else 'N/A'}")
            return json.dumps({
                'erro': 'Binário coin não encontrado',
                'debug': f'Procurei em: {caminhos}',
                'sucesso': False
            }), 500, {'Content-Type': 'application/json'}
        
        # ===== Executar =====
        try:
            resultado = subprocess.run(
                [coin_path, valor, moeda],
                capture_output=True,
                text=True,
                timeout=5,
                cwd='/workspace'
            )
        except subprocess.TimeoutExpired:
            return json.dumps({'erro': 'Timeout', 'sucesso': False}), 408, {'Content-Type': 'application/json'}
        except Exception as e:
            logger.error(f"Erro ao executar: {str(e)}")
            return json.dumps({'erro': f'Erro: {str(e)}', 'sucesso': False}), 500, {'Content-Type': 'application/json'}
        
        if resultado.returncode != 0:
            logger.error(f"COBOL erro: {resultado.stderr}")
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
