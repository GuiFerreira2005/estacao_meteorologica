import sqlite3
from flask import Flask, g, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder=".", static_url_path="")

# Habilita CORS para permitir que o dashboard acesse a API
CORS(app)

DATABASE = "estacao.db"


def get_db():
    """Conecta ao banco de dados sob demanda utilizando Row Factory."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Permite acessar colunas pelo nome em vez de índice
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Encerra a conexão ao final da requisição HTTP."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def formatar_para_frontend(linha):
    """Mapeia as colunas do SQLite para os nomes esperados pelo api.js e main.js."""
    if not linha:
        return {}
    return {
        "timestamp": linha["data_hora"],
        "temp_dht": linha["dht_temp"],
        "umidade": linha["dht_umidade"],
        "pressao": linha["bmp_pressao"],
        "gas": linha["mq_qualidade_ar"],
        "luz": linha["ldr_luminosidade"],
        "latitude": linha["latitude"],
        "longitude": linha["longitude"],
    }


# ==================== ROTAS DA API REST ====================


@app.route("/api/atual", methods=["GET"])
def obter_leitura_atual():
    """Retorna a leitura mais recente cadastrada no banco estacao.db."""
    cur = get_db().cursor()
    cur.execute("SELECT * FROM leituras_sensores ORDER BY id DESC LIMIT 1")
    linha = cur.fetchone()
    if not linha:
        return jsonify({"erro": "Nenhuma leitura encontrada no banco"}), 404
    return jsonify(formatar_para_frontend(linha))


@app.route("/api/historico", methods=["GET"])
def obter_historico():
    """Retorna o histórico recente em ordem cronológica para o Chart.js."""
    cur = get_db().cursor()
    # Busca as últimas 60 leituras
    cur.execute("SELECT * FROM leituras_sensores ORDER BY id DESC LIMIT 60")
    linhas = cur.fetchall()
    # Inverte a lista para ficar em ordem cronológica (da mais antiga para a mais recente)
    historico = [formatar_para_frontend(r) for r in reversed(linhas)]
    return jsonify(historico)


# ==================== ROTA PARA SERVIR O FRONTEND ====================


@app.route("/")
def index():
    """Serve a página principal do Dashboard se os arquivos estiverem na mesma pasta."""
    return app.send_static_file("index.html")


if __name__ == "__main__":
    print("🚀 API do Dashboard rodando em http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)