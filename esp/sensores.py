from machine import Pin, ADC, I2C
import dht

# 1. Variáveis Globais de Controle
sensor_bmp = None
HAS_BMP = False

# 2. Tenta importar o driver do BMP280
try:
    import bmp280
    HAS_BMP = True
except ImportError:
    print("Aviso: Driver 'bmp280.py' não encontrado na placa física.")

# 3. Configuração do Barramento I2C (SDA=GPIO 21, SCL=GPIO 22)
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)

# 4. Inicialização Inicial do BMP280 em 0x76
if HAS_BMP:
    try:
        sensor_bmp = bmp280.BMP280(i2c, address=0x76)
        print("✓ BMP280 inicializado com sucesso em 0x76!")
    except Exception as e:
        print("Erro ao conectar BMP280:", e)
        sensor_bmp = None

# 5. Configuração do DHT22 (GPIO 15)
sensor_dht = dht.DHT22(Pin(15))

# 6. Configuração dos ADCs (LDR em GPIO 35, MQ em GPIO 34) - Escala 0V a 3.3V
adc_ldr = ADC(Pin(35))
adc_ldr.atten(ADC.ATTN_11DB)
adc_mq = ADC(Pin(34))
adc_mq.atten(ADC.ATTN_11DB)

def ler_bmp():
    """Lê os dados de temperatura e pressão do BMP280 com reconexão automática."""
    global sensor_bmp
    
    # Tenta reconectar caso a variável tenha ficado vazia (None)
    if sensor_bmp is None and HAS_BMP:
        try:
            sensor_bmp = bmp280.BMP280(i2c, address=0x76)
        except Exception:
            sensor_bmp = None
            
    if sensor_bmp is not None:
        try:
            return sensor_bmp.ler_dados()
        except Exception:
            return None, None
            
    return None, None

def coletar_todos_os_dados(estacao_id="estacao_01"):
    """Coleta todas as leituras da estação meteorológica e monta o dicionário JSON."""
    # Coleta do DHT22
    try:
        sensor_dht.measure()
        dht_temp = round(sensor_dht.temperature(), 1)
        dht_umid = round(sensor_dht.humidity(), 1)
    except Exception:
        dht_temp, dht_umid = None, None

    # Coleta do BMP280
    bmp_temp, bmp_press = ler_bmp()

    # Retorno estruturado no contrato JSON
    return {
        "estacao_id": estacao_id,
        "dht22": {
            "temperatura_c": dht_temp,
            "umidade_pct": dht_umid
        },
        "bmp180": {  # Chave mantida como 'bmp180' para compatibilidade com o contrato
            "temperatura_c": bmp_temp,
            "pressao_hpa": bmp_press
        },
        "ldr": {
            "luminosidade_raw": adc_ldr.read()
        },
        "mq": {
            "gas_raw": adc_mq.read()
        }
    }