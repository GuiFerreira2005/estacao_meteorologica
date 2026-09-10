import network
import ujson
from umqtt.simple import MQTTClient

# Configuração do Broker Público
MQTT_BROKER = "broker.hivemq.com"
PORTA = 1883
TOPICO_DADOS = "unip/estacao_meteorologica/dados"
CLIENT_ID = "estacao_unip_esp32_ponta_a_ponta"

def publicar_dados_climaticos(payload):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("[MQTT] Erro de transmissão: Wi-Fi desconectado!")
        return False
        
    try:
        # Instancia e conecta o cliente umqtt.simple na nuvem
        client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=PORTA)
        print(f"[MQTT] Conectando ao Broker {MQTT_BROKER}...")
        client.connect()
        
        # Transforma o dicionário Python em uma String compacta JSON
        mensagem_json = ujson.dumps(payload)
        
        print(f"[MQTT] Publicando payload dinâmico no tópico '{TOPICO_DADOS}'...")
        client.publish(TOPICO_DADOS, mensagem_json)
        
        # Encerramento limpo do socket de rede para evitar erros LmacRxBlk
        client.disconnect()
        print("[MQTT] Transmissão concluída com sucesso!")
        return True
        
    except Exception as e:
        print("[MQTT] Erro crítico na transmissão da mensagem:", e)
        return False