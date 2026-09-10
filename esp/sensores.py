from machine import Pin, I2C, ADC
import dht
import time

#Contagem do Pluviômetro (RAM)
chuva_pulsos = 0
ULTIMO_PULSO_MS = 0
DEBOUNCE_DELAY_MS = 200  # Evita falsas contagens causadas por ruído mecânico

# Inicializa o sensor de umidade e temperatura na porta digital GPIO 15 [1].
dht_sensor = dht.DHT22(Pin(15))


# Inicializa o hardware I2C0 ( Requer o arquivo externo de driver "bmp180.py")
i2c_bus = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)

try:
    from esp.bmp180 import BMP180
    bmp_sensor = BMP180(i2c_bus)
except ImportError:
    print("Aviso: Driver 'bmp180.py' não encontrado na placa física.")
    bmp_sensor = None

# Inicializa a porta analógica e ajusta a atenuação para ler até 3.3V
ldr_adc = ADC(Pin(35))
ldr_adc.atten(ADC.ATTN_11DB)  # Configuração obrigatória do ESP32 para ler até 3.6V [10]

# Inicializa a porta analógica para medição de qualidade do ar [1].
mq_adc = ADC(Pin(34))
mq_adc.atten(ADC.ATTN_11DB)

def registrar_pulso_chuva(pin):
    """
    Função de interrupção executada pelo processador em segundo plano sempre que
    o pluviômetro de báscula oscila (GPIO 13 vai de nível ALTO para BAIXO) 
    """
    global chuva_pulsos, ULTIMO_PULSO_MS
    tempo_atual = time.ticks_ms()
    
    # Aplica o debounce: ignora pulsos extremamente rápidos causados por vibrações mecânicas
    if time.ticks_diff(tempo_atual, ULTIMO_PULSO_MS) > DEBOUNCE_DELAY_MS:
        chuva_pulsos += 1
        ULTIMO_PULSO_MS = tempo_atual

# Configura o pino GPIO 13 com resistor interno de Pull-up
pin_pluviometro = Pin(13, Pin.IN, Pin.PULL_UP)
pin_pluviometro.irq(trigger=Pin.IRQ_FALLING, handler=registrar_pulso_chuva)

def ler_dht22():
    """
    Executa a leitura do sensor DHT22.
    Se o sensor for desconectado fisicamente, retorna valores nulos (None) 
    impedindo que a placa inteira trave por um erro de barramento.
    """
    try:
        dht_sensor.measure()  # Dispara a medição física do sensor [4]
        return {
            "temperatura_c": round(dht_sensor.temperature(), 1),
            "umidade_pct": round(dht_sensor.humidity(), 1)
        }
    except OSError:
        print("Erro de Hardware: DHT22 não está respondendo.")
        return {"temperatura_c": None, "umidade_pct": None}

def ler_bmp180():
    """
    Executa a leitura de pressão e temperatura redundante do BMP180.
    """
    if bmp_sensor is None:
        return {"pressao_hpa": None, "temperatura_c": None}
    try:
        # Lê a temperatura e converte a pressão de Pascal (Pa) para Hectopascal (hPa)
        temp = round(bmp_sensor.temperature, 1)
        pressao = round(bmp_sensor.pressure / 100.0, 2)
        return {
            "pressao_hpa": pressao,
            "temperatura_c": temp
        }
    except Exception as e:
        print(f"Erro de Hardware: Falha na leitura I2C do BMP180: {e}")
        return {"pressao_hpa": None, "temperatura_c": None}

def ler_luminosidade():
    """
    Lê a luminosidade bruta capturada pelo ADC.
    No ESP32, o retorno é de 0 (escuro completo) a 65535 (luminosidade máxima) [8].
    """
    try:
        return ldr_adc.read_u16()  # Executa a conversão analógico-digital de 16 bits [8]
    except Exception:
        return None

def ler_qualidade_ar():
    """
    Lê a concentração de gases do sensor MQ de forma analógica.
    """
    try:
        return mq_adc.read_u16()
    except Exception:
        return None

def obter_chuva_acumulada():
    """
    Calcula o volume de chuva baseado no número de pulsos registrados.
    Cada pulso mecânico de báscula equivale a aproximadamente 0.25 mm de água.
    Retorna o volume total e zera a contagem para o próximo intervalo de leitura.
    """
    global chuva_pulsos
    FATOR_PLUVIOMETRO_MM = 0.25  # Constante padrão de conversão
    
    chuva_total_mm = round(chuva_pulsos * FATOR_PLUVIOMETRO_MM, 2)
    chuva_pulsos = 0  # Reseta o acumulador após descarregar o dado
    return chuva_total_mm

def coletar_todos_os_dados(estacao_id="estacao_01"):
    """
    Função centralizadora: Coleta de todos os blocos de sensores e organiza
    no formato do contrato JSON acordado para envio via MQTT.
    """
    dados_dht = ler_dht22()
    dados_bmp = ler_bmp180()
    
    return {
        "estacao_id": estacao_id,
        "dht22": dados_dht,
        "bmp180": dados_bmp,
        "ldr": {
            "luminosidade_raw": ler_luminosidade()
        },
        "mq": {
            "gas_raw": ler_qualidade_ar()
        },
        "pluviometro": {
            "chuva_mm": obter_chuva_acumulada()
        }
    }
