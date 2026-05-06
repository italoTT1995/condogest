from waitress import serve
from app import create_app, db
import os
import socket

app = create_app()

import logging
logging.basicConfig(level=logging.INFO)


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == "__main__":
    host_ip = get_ip_address()
    port = 8080
    
    print("="*50)
    print(f"CONDO MANAGER - SERVIDOR DE PRODUCAO INICIADO")
    print("="*50)
    print(f"Pasta do Projeto: {os.getcwd()}")
    print("-" * 50)
    print(f"Acesso Interno: http://localhost:{port}")
    print(f"Acesso Externo: http://{host_ip}:{port}")
    print("-" * 50)
    print("Para parar o servidor, feche esta janela.")
    print("="*50)
    
    serve(app, host='0.0.0.0', port=port, threads=6)
