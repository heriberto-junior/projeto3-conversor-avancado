import json
import subprocess
import functions_framework

@functions_framework.http
def conversor_moedas(request):
    """
    Cloud Function que recebe JSON e executa COBOL
    
    Exemplo de requisição:
    POST /conversor_moedas
    {
        "valor": "100",
        "moeda": "USD"
    }
    
    Exemplo de resposta:
    {
        "resultado": "Resultado: 19330.000 USD"
    }
    """
    
    try:
        # Parse do JSON que veio da requisição
        request_json = request.get_json()
        
        # Extrai valores (ou usa padrão se vazio)
        valor = request_json.get('valor', '1.00')
        moeda = request_json.get('moeda', 'USD')
        
        # Validação simples
        if not valor or not moeda:
            return json.dumps({
                'erro': 'Faltam parametros: valor, moeda'
            }), 400
        
        # ⭐ AQUI EXECUTA O COBOL ⭐
        # Chama o entrypoint.sh que executa o binário coin
        resultado = subprocess.run(
            ['/workspace/entrypoint.sh', valor, moeda],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Se houve erro na execução
        if resultado.returncode != 0:
            return json.dumps({
                'erro': resultado.stderr
            }), 400
        
        # Sucesso! Retorna resultado
        return json.dumps({
            'resultado': resultado.stdout.strip(),
            'sucesso': True
        }), 200
    
    except json.JSONDecodeError:
        return json.dumps({'erro': 'JSON inválido'}), 400
    except subprocess.TimeoutExpired:
        return json.dumps({'erro': 'Timeout - execução demorou demais'}), 408
    except Exception as e:
        return json.dumps({'erro': str(e)}), 500
