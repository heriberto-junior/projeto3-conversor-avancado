import json
import subprocess
import functions_framework
import logging
import os
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def conversor_moedas(request):
    """Cloud Function que compila e executa COBOL em runtime"""
    
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
            return json.dumps({'erro': f'Moeda inválida', 'sucesso': False}), 400, {'Content-Type': 'application/json'}
        
        logger.info(f"Convertendo: {valor} BRL → {moeda}")
        
        # ===== Compilar COBOL em runtime =====
        try:
            # Usar diretório temporário
            with tempfile.TemporaryDirectory() as tmpdir:
                cob_path = os.path.join(tmpdir, 'coin.cob')
                exe_path = os.path.join(tmpdir, 'coin')
                
                # Copiar coin.cob do /workspace para temp
                if os.path.exists('/workspace/coin.cob'):
                    with open('/workspace/coin.cob', 'r') as src:
                        with open(cob_path, 'w') as dst:
                            dst.write(src.read())
                else:
                    logger.error("coin.cob não encontrado em /workspace")
                    return json.dumps({'erro': 'coin.cob não encontrado', 'sucesso': False}), 500, {'Content-Type': 'application/json'}
                
                # Copiar cotacao.txt para temp
                if os.path.exists('/workspace/cotacao.txt'):
                    with open('/workspace/cotacao.txt', 'r') as src:
                        with open(os.path.join(tmpdir, 'cotacao.txt'), 'w') as dst:
                            dst.write(src.read())
                
                # Compilar coin.cob
                logger.info(f"Compilando {cob_path} para {exe_path}")
                compile_result = subprocess.run(
                    ['cobc', '-x', '-free', '-static', '-o', exe_path, cob_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=tmpdir
                )
                
                if compile_result.returncode != 0:
                    logger.error(f"Compilação falhou: {compile_result.stderr}")
                    return json.dumps({'erro': f'Erro ao compilar: {compile_result.stderr}', 'sucesso': False}), 500, {'Content-Type': 'application/json'}
                
                logger.info("Compilação bem-sucedida")
                
                # Executar binário compilado
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
            return json.dumps({'erro': 'Timeout na execução', 'sucesso': False}), 408, {'Content-Type': 'application/json'}
        except Exception as e:
            logger.error(f"Erro: {str(e)}", exc_info=True)
            return json.dumps({'erro': f'Erro: {str(e)}', 'sucesso': False}), 500, {'Content-Type': 'application/json'}
        
        if resultado.returncode != 0:
            logger.error(f"Erro COBOL: {resultado.stderr}")
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
        logger.error(f"Erro não tratado: {str(e)}", exc_info=True)
        return json.dumps({'erro': str(e), 'sucesso': False}), 500, {'Content-Type': 'application/json'}
