# 🌦️ Mini Estação Meteorológica Inteligente (ESP32 + IoT)

> **Projeto Integrador — Ciência da Computação (2º Semestre)**  
> Sistema computacional embarcado de baixo custo para monitoramento microclimático urbano em tempo real, fundamentado nos conceitos de **Cidades Inteligentes (Smart Cities)** e **Internet das Coisas (IoT)**.

---

## 🎥 Demonstração em Vídeo (End-to-End)

Assista à demonstração completa da estação meteorológica operando na bancada, enviando telemetria via MQTT, gravando no banco de dados relacional e atualizando o Dashboard Web em tempo real:

👉 **[Acessar Pasta com o Vídeo de Demonstração (Google Drive)](https://drive.google.com/drive/folders/16mUkOfseDTz8MFLSGQTXc_80uOtTwf-6?usp=drive_link)**

---

## 📋 Sobre o Projeto

A ausência de monitoramento microclimático localizado dificulta a identificação de ilhas de calor e a tomada de decisões sustentáveis na gestão urbana. Este projeto soluciona esse problema por meio de uma arquitetura IoT distribuída e de baixo acoplamento, dividida em três camadas principais:

1. **Camada de Borda (Hardware/Firmware):** Coleta de variáveis ambientais via microcontrolador **ESP32** programado em **MicroPython**, com envio assíncrono via protocolo **MQTT**.
2. **Camada de Transporte e Persistência (Backend):** Recepção dos pacotes JSON por um *Subscriber* Python (`paho-mqtt` v2.0+), filtragem de inconsistências, atribuição de carimbo temporal (*timestamp*) e gravação segura em banco relacional **SQLite 3** (`db_estacao.db`).
3. **Camada de Visualização (API REST + Dashboard Web):** Exposição dos dados via **API Flask** desacoplada e exibição pública interativa com gráficos dinâmicos, alertas climáticos e geolocalização espacial aplicando **Geometria Analítica**.

---

## 🏗️ Arquitetura do Sistema

```text
+----------------------------------- ESP32 (Borda) -----------------------------------+
| [boot.py] -> [sensores.py] -> [bmp280.py] -> [mqtt_client.py] -> [main.py] (Maestro) |
+-------------------------------------------------------------------------------------+
                                           |
                                    (JSON via Wi-Fi)
                                           v
                             +---------------------------+
                             |     Broker MQTT Público   |
                             | (broker.hivemq.com:1883)  |
                             +---------------------------+
                                           |
                                     (Se inscreve)
                                           v
+----------------------------- Servidor (Backend Python) -----------------------------+
|  1. [conexao_mqtt.py]: Subscriber MQTT -> Valida JSON -> INSERT Parametrizado       |
|  2. [db_estacao.db]: Banco Relacional SQLite 3 (Modelado em 3FN)                    |
|  3. [rota_db.py]: API REST Flask (/api/atual e /api/historico) com CORS             |
+-------------------------------------------------------------------------------------+
                                           |
                                   (Requisição HTTP)
                                           v
+-------------------------------- Dashboard Web (Site) -------------------------------+
|  [index.html] + [api.js] + [charts.js] (Chart.js) + [map.js] (Leaflet / Vetores)    |
+-------------------------------------------------------------------------------------+
```

---

## 🔌 Mapeamento de Hardware e Pinagem

O circuito eletrônico foi prototipado em protoboard separando as linhas de alimentação lógica (**3.3V**) e dos módulos que exigem maior corrente (**5V**).

| Componente / Sensor | Variável Medida | Protocolo / Interface | Pino no ESP32 | Observações Técnicas |
| :--- | :--- | :--- | :--- | :--- |
| **DHT22** | Temperatura (°C) e Umidade (%) | Digital (1-Wire) | `GPIO 15` | Leitura climática primária |
| **BMP280** | Pressão Atmosférica (hPa) | Barramento I2C | `GPIO 21` (SDA)<br>`GPIO 22` (SCL) | Endereço físico `0x76` com driver customizado (`bmp280.py`) |
| **LDR** | Luminosidade | Analógico (ADC) | `GPIO 35` | Divisor de tensão + atenuação `11 dB` (faixa 0V a 3.3V) |
| **MQ-135** | Qualidade do Ar / Gases | Analógico (ADC) | `GPIO 34` | Saída analógica + atenuação `11 dB` (faixa 0V a 3.3V) |
| **Pluviômetro** *(Opcional)* | Precipitação (mm) | Interrupção (IRQ) | `GPIO 13` | Borda de descida com pull-up interno e *debounce* |

---

## 📡 Contrato de Dados (Payload JSON)

O ESP32 serializa as leituras em uma string JSON compacta antes de publicar no tópico MQTT (`unip/estacao_meteorologica/dados`).  
*Nota: O timestamp não é gerado na placa para economizar memória RAM e energia; ele é atribuído pelo servidor Python no exato instante da persistência.*

```json
{
  "estacao_id": "estacao_01",
  "dht22": {
    "temperatura_c": 24.5,
    "umidade_pct": 60.2
  },
  "bmp180": {
    "pressao_hpa": 1013.25,
    "temperatura_c": 24.8
  },
  "ldr": {
    "luminosidade_raw": 3045
  },
  "mq": {
    "gas_raw": 1200
  }
}
```
*(A chave `"bmp180"` é mantida no contrato JSON para compatibilidade retroativa com o parser do backend e a estrutura do banco de dados).*

---

## 🗄️ Modelagem do Banco de Dados (`db_estacao.db`)

O banco de dados foi remodelado na **Terceira Forma Normal (3FN)**, separando os dados cadastrais estáticos da estação das leituras transacionais periódicas.

### Tabela `estacao` (Entidade Estática)
| Atributo | Tipo | Restrição / Descrição |
| :--- | :--- | :--- |
| `id_estacao` | `INT` | `PK, Auto Increment` — Identificador único da estação |
| `latitude` | `FLOAT` | Coordenada $y$ (Aplicação de Geometria Analítica) |
| `longitude` | `FLOAT` | Coordenada $x$ (Aplicação de Geometria Analítica) |

### Tabela `leitura` (Entidade Transacional)
| Atributo | Tipo | Restrição / Descrição |
| :--- | :--- | :--- |
| `id_leitura` | `BIGINT` | `PK, Auto Increment` — Identificador único do registro |
| `id_estacao` | `INT` | `FK` referenciando `estacao(id_estacao)` |
| `temperatura` | `FLOAT` | Temperatura ambiente em Graus Celsius (°C) |
| `umidade` | `FLOAT` | Umidade relativa do ar (%) |
| `pressao` | `FLOAT` | Pressão atmosférica (hPa) |
| `qualidade_ar` | `INT` | Concentração relativa de gases (ADC / PPM) |
| `luminosidade` | `INT` | Intensidade luminosa bruta (ADC) |
| `pluviometria` | `FLOAT` | Acúmulo de chuva em milímetros (mm) |
| `data_hora` | `TIMESTAMP` | Data e hora da coleta atribuída pelo servidor |

---

## 📂 Estrutura do Repositório

```text
estacao_meteorologica/
├── esp/                        # Firmware embarcado em MicroPython (Memória Flash do ESP32)
│   ├── boot.py                 # Inicialização e conexão Wi-Fi em modo Station (STA)
│   ├── bmp280.py               # Driver I2C de baixo nível e equações de compensação Bosch
│   ├── sensores.py             # Abstração dos pinos GPIO/ADC/I2C e tratamento de falhas
│   ├── mqtt_client.py          # Cliente MQTT resiliente para publicação do JSON
│   └── main.py                 # Orquestrador principal, coleta e gerenciamento de memória (gc)
│
├── computador/                 # Serviços de Backend e Persistência em Python
│   ├── conexao_mqtt.py         # Subscriber Paho-MQTT v2.0+ com INSERT parametrizado (anti-SQLi)
│   └── rota_db.py              # API REST em Flask (/api/atual e /api/historico) com CORS
│
├── site/                       # Frontend Web (Dashboard Público Interativo)
│   ├── index.html              # Estrutura semântica do painel de monitoramento
│   ├── css/
│   │   └── style.css           # Estilização responsiva com suporte a temas Claro/Escuro
│   └── js/
│       ├── api.js              # Consumo da API Flask (suporta modo real e simulado/mock)
│       ├── alertas.js          # Lógica matemática de verificação de faixas (Normal/Atenção/Crítico)
│       ├── charts.js           # Renderização dinâmica de histórico com Chart.js
│       ├── map.js              # Plotagem geoespacial com Leaflet JS e Geometria Analítica
│       └── main.js             # Sincronização periódica da interface
│
├── db_estacao.db               # Arquivo de banco de dados relacional SQLite 3
└── README.md                   # Documentação oficial do projeto
```

---

## 🚀 Como Executar o Projeto

### 1. Firmware no ESP32 (`esp/`)
1. Instale o firmware **MicroPython** na placa ESP32 e abra a **Thonny IDE**.
2. Edite as credenciais de rede no arquivo `boot.py` (`WIFI_SSID` e `WIFI_PASSWORD`).
3. Faça o upload de todos os arquivos da pasta `esp/` (`boot.py`, `bmp280.py`, `sensores.py`, `mqtt_client.py` e `main.py`) para a raiz do dispositivo (`MicroPython Device`).
4. Execute o `main.py` (ou reinicie a placa) para iniciar a telemetria autônoma.

### 2. Backend e API REST (`computador/`)
Certifique-se de ter o **Python 3.9+** instalado e instale as dependências necessárias:
```bash
pip install paho-mqtt flask flask-cors
```
Inicie o receptor MQTT (em um terminal) para gravar os dados recebidos no SQLite:
```bash
python computador/conexao_mqtt.py
```
Inicie o servidor da API Flask (em outro terminal) na porta `8000`:
```bash
python computador/rota_db.py
```
*Endpoints disponíveis:*
* `GET http://localhost:8000/api/atual` — Retorna a leitura mais recente e as coordenadas da estação.
* `GET http://localhost:8000/api/historico` — Retorna a série histórica para renderização dos gráficos.

### 3. Dashboard Web (`site/`)
1. Verifique em `site/js/api.js` se a configuração está apontando para a API local (`USAR_MOCK: false` e `URL_BASE: "http://localhost:8000"`).
2. Abra o arquivo `site/index.html` utilizando um servidor web local (como a extensão *Live Server* no VS Code ou `python -m http.server` dentro da pasta `site/`).

---

## 🧪 Plano de Testes e Validação

| ID | Componente | Descrição do Teste | Resultado Esperado | Status |
| :--- | :--- | :--- | :--- | :--- |
| **CT01** | Hardware / Firmware | Leitura dos sensores com variação ambiental na bancada | Leitura atualizada e JSON válido no terminal REPL sem travamentos | ✅ Aprovado |
| **CT02** | Comunicação | Desconexão forçada da rede Wi-Fi / Broker MQTT | Firmware trata exceções e tenta reconectar automaticamente | ✅ Aprovado |
| **CT03** | Backend / Lógica | Envio de leitura inconsistente ou fora de faixa | Backend/Dashboard filtra anomalias e classifica níveis de alerta | ✅ Aprovado |
| **CT04** | Dashboard Web | Renderização da localização da estação no mapa | Marcador plotado com precisão nas coordenadas $(x, y)$ | ✅ Aprovado |

---

## 🔧 Limitações Atuais e Evoluções Futuras

* **Vulnerabilidades da Protoboard:** A montagem atual em matriz de contatos está sujeita a ruídos eletromagnéticos nas portas analógicas (ADC) e eventuais maus contatos mecânicos nos jumpers.
* **Próximos Passos:**
  1. Desenvolvimento de uma **Placa de Circuito Impresso (PCB)** dedicada para eliminar ruídos e garantir robustez elétrica.
  2. Construção de um **encapsulamento com proteção IP65** para instalação externa resistente à chuva e poeira, aliado à alimentação autônoma por bateria e painel solar utilizando o modo `machine.deepsleep()` do ESP32.