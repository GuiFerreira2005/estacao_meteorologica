import time
import gc
import sensores
import mqtt_client

print("=" * 60)
print("MINI ESTAÇÃO METEOROLÓGICA INTELIGENTE - MODO AUTÔNOMO")
print("=" * 60)

# Intervalo seguro de atualização entre leituras (15 segundos)
INTERVALO_LEITURA_S = 15

while True:
    print("\n--- Iniciando Novo Ciclo de Monitoramento ---")
    
    # 1. Coleta os dados limpos e formatados da RAM do ESP32
    dados = sensores.coletar_todos_os_dados("estacao_unip_norte_01")
    print("[MAESTRO] Leituras consolidadas na RAM:", dados)
    
    # 2. Despacha o pacote pela internet para o Broker MQTT
    mqtt_client.publicar_dados_climaticos(dados)
    
    # 3. Otimização de Memória RAM (Essencial para evitar travamentos de hardware)
    gc.collect()
    print(f"[MAESTRO] Memória RAM livre após limpeza: {gc.mem_free()} bytes")
    
    # 4. Coloca a placa em repouso controlado antes do próximo ciclo
    print(f"[MAESTRO] Aguardando {INTERVALO_LEITURA_S} segundos...")
    time.sleep(INTERVALO_LEITURA_S)