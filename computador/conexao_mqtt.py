import sqlite3
import json
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import os

# CONEXÃO COM O BANCO DE DADOS
db_name = "db_estacao.db"
id_estacao_padrao = 1 # ID da estação cadastrada na tabela 'estacao'
broker_mqtt = "broker.hivemq.com"  # Configurado para o broker estável HiveMQ
porta_mqtt = 1883
topico_leitura = "unip/estacao_meteorologica/dados"

# CALLBACK SUCESSO [Repo]
def on_connect(client, userdata, flags, reason_code, properties=None):
    if hasattr(reason_code, "is_failure") and reason_code.is_failure:
        print(f"Falha na conexão: {reason_code}")
    elif reason_code == 0 or (hasattr(reason_code, "value") and reason_code.value == 0):
        print("Conectado com sucesso ao Broker HiveMQ!")
        client.subscribe(topico_leitura)
        print(f"Inscrito no tópico: {topico_leitura}")
        print("Aguardando mensagens...\n")
    else:
        print(f"Falha na conexão: código de retorno {reason_code}")

# CALLBACK RECEBE MENSAGEM [Repo]
def on_message(client, userdata, msg):
    try:
        # decodifica o payload para string e converte para dicionário
        dados_json = msg.payload.decode('utf-8')
        payload = json.loads(dados_json)
        print(f"Mensagem recebida no tópico {msg.topic}:")
        print(json.dumps(payload, indent=2))

        # Extração defensiva com tratamento de dados nulos
        dht_temp = payload.get("dht22", {}).get("temperatura_c")
        dht_umid = payload.get("dht22", {}).get("umidade_pct")
        bmp_press = payload.get("bmp180", {}).get("pressao_hpa")
        ldr_lum = payload.get("ldr", {}).get("luminosidade_raw")
        mq_gas = payload.get("mq", {}).get("gas_raw")

        # [MANUTENÇÃO PREVENTIVA] Verifica se o banco realmente existe no diretório atual
        if not os.path.exists(db_name):
            print(f"⚠️ ERRO CRÍTICO: O arquivo de banco de dados '{db_name}' não foi encontrado nesta pasta!")
            print(f"Diretório atual de execução do terminal: {os.getcwd()}")
            print("A gravação foi abortada para evitar a criação de um banco fantasma vazio.\n")
            return

        # Se o arquivo existe, prossegue com a conexão segura
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # SQL Parametrizado ajustado para a tabela 'leitura' (sem pluviometria)
        query = """
        INSERT INTO leitura (
            id_estacao, temperatura, umidade, pressao, 
            qualidade_ar, luminosidade
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            id_estacao_padrao, dht_temp, dht_umid, bmp_press, mq_gas, ldr_lum
        ))

        conn.commit()
        conn.close()
        print("Dados ambientais gravados no SQLite com sucesso!\n")

    except json.JSONDecodeError:
        print("Erro: Payload corrompido ou formato JSON inválido.")
    except Exception as e:
        print(f"Erro no fluxo de dados: {e}")

# INICIALIZAÇÃO DO CLIENTE [Repo]
mqttc = mqtt.Client(CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

print("Iniciando conexão com o broker MQTT...")
mqttc.connect(broker_mqtt, porta_mqtt, 60)

# Loop ativo para escuta de pacotes
mqttc.loop_forever()