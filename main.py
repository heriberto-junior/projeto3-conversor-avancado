import json
import subprocess
import functions_framework
import logging
import os
import tempfile
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_cobc():
    """Procura cobc em vários caminhos"""
    possibles = ['cobc', '/usr/bin/cobc', '/bin/cobc', 'cobc.exe']
    for cmd in possibles:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, timeout=1)
            if result.returncode == 0:
                logger.info(f"Encontrado cobc em: {cmd}")
                return cmd
        except:
            pass
    return None

@functions_framework.http
def conversor_moedas(request):
    """Cloud Function que compila e executa COBOL"""
    
    try:
        if request.method != 'POST':
            return json.dumps({'erro': 'Use POST', 'sucesso': False}), 405, {'Content-Type': 'application/json'}
        
        data = request.get_json()
        if not data:
            return json.dumps({'erro': 'JSON vazio', 'sucesso': False}), 400, {'Content-Type': 'application/json'}
        
        valor = str(data.get('valor', '')).strip()
        moeda = str(data.get('moeda', '')).strip().upper()
        
        if not valor or not moeda:
            return json.dumps({'erro': 'Faltam parâmetros', 'sucesso': False}), 400, {'Content-Type': 'application/json'}
        
        moedas_validas = ['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD']
        if moeda not in moedas_validas:
            return json.dumps({'erro': 'Moeda inválida', 'sucesso': False}), 400, {'Content-Type': 'application/json'}
        
        logger.info(f"Convertendo: {valor} BRL → {moeda}")
        
        # ===== Encontrar cobc =====
        cobc_cmd = find_cobc()
        if not cobc_cmd:
            logger.error("cobc não encontrado")
            return json.dumps({'erro': 'Compilador COBOL não encontrado', 'sucesso': False}), 500, {'Content-Type': 'application/json'}
        
        logger.info(f"Usando compilador: {cobc_cmd}")
        
        # ===== Compilar e executar =====
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                cob_path = os.path.join(tmpdir, 'coin.cob')
                exe_path = os.path.join(tmpdir, 'coin')
                
                # Copiar coin.cob
                if os.path.exists('/workspace/coin.cob'):
                    with open('/workspace/coin.cob', 'r') as src:
                        with open(cob_path, 'w') as dst:
                            dst.write(src.read())
                else:
                    logger.error("coin.cob não encontrado")
                    return json.dumps({'erro': 'coin.cob não encontrado', 'sucesso': False}), 500, {'Content-Type': 'application/json'}
                
                # Copiar cotacao.txt
                if os.path.exists('/workspace/cotacao.txt'):
                    with open('/workspace/cotacao.txt', 'r') as src:
                        with open(os.path.join(tmpdir, 'cotacao.txt'), 'w') as dst:
                            dst.write(src.read())
                
                # Compilar
                logger.info(f"Compilando {cob_path}")
                compile_result = subprocess.run(
                    [cobc_cmd, '-x', '-free', '-static', '-o', exe_path, cob_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=tmpdir
                )
                
                if compile_result.returncode != 0:
                    logger.error(f"Compilação falhou: {compile_result.stderr}")
                    return json.dumps({'erro': f'Erro compilação: {compile_result.stderr[:100]}', 'sucesso': False}), 500, {'Content-Type': 'application/json'}
                
                logger.info("Compilação OK")
                
                # Executar
                logger.info(f"Executando {exe_path}")
                resultado = subprocess.run(
                    [exe_path, valor, moeda],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=tmpdir
                )
        
        except subprocess.TimeoutExpired:
            logger.error("Timeout")
            return json.dumps({'erro': 'Timeout', 'sucesso': False}), 408, {'Content-Type': 'application/json'}
        except Exception as e:
            logger.error(f"Erro: {str(e)}", exc_info=True)
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
