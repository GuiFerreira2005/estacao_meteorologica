import sqlite3
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_NAME = "db_estacao.db"

# Define o caminho absoluto para a pasta 'site' onde está o seu frontend
PASTA_SITE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'site'))

def consultar_banco(query, params=(), um_registro=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    linhas = cursor.fetchall()
    conn.close()

    if um_registro:
        return dict(linhas[0]) if linhas else {}
    return [dict(linha) for linha in linhas]


# ==========================================
# ROTAS DO FRONTEND (ENTREGA DE ARQUIVOS)
# ==========================================

@app.route('/')
def index():
    # Quando acessar localhost:8000, o Flask entrega o index.html
    return send_from_directory(PASTA_SITE, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    # Libera o acesso para o HTML carregar o CSS e o JS
    return send_from_directory(PASTA_SITE, filename)


# ==========================================
# ROTAS DA API DE DADOS (BACKEND)
# ==========================================

@app.route('/api/atual', methods=['GET'])
def api_atual():
    sql = """
        SELECT 
            l.temperatura AS temp_dht, 
            l.umidade AS umidade, 
            l.pressao AS pressao, 
            l.qualidade_ar AS gas, 
            l.luminosidade AS luz, 
            e.latitude AS latitude, 
            e.longitude AS longitude, 
            datetime(l.data_hora, '-3 hours') AS timestamp 
        FROM leitura l 
        JOIN estacao e ON l.id_estacao = e.id_estacao 
        ORDER BY l.id_leitura DESC 
        LIMIT 1
    """
    return jsonify(consultar_banco(sql, um_registro=True))


@app.route('/api/historico', methods=['GET'])
def api_historico():
    sql = """
        SELECT 
            l.temperatura AS temp_dht, 
            l.umidade AS umidade, 
            l.pressao AS pressao, 
            l.qualidade_ar AS gas, 
            l.luminosidade AS luz, 
            datetime(l.data_hora, '-3 hours') AS timestamp 
        FROM leitura l 
        ORDER BY l.id_leitura DESC 
        LIMIT 60
    """
    dados = consultar_banco(sql)
    dados.reverse()  
    return jsonify(dados)

if __name__ == '__main__':
    print("🚀 Servidor Flask iniciado em http://localhost:8000")
    # host='0.0.0.0' permite que outros dispositivos na rede acessem seu IP
    app.run(host='0.0.0.0', port=8000, debug=True)