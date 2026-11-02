import machine
import network
import esp
import time
import gc

#LIMPEZA NO TERMINAL
esp.osdebug(None) #biblioteca esp

#CONEXAO WIFI
wifi_ssid = "Wokwi-GUEST"
wifi_senha= ""

def conectar_wifi(): #Biblioteca Network
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)

  if wlan.isconnected():
    print("Conectado a rede wifi")
    print("configurações do ip:", wlan.ipconfig('addr4'))
    return True
  
  #tentando conectar na rede
  print(f"Tentando conectar a rede: {wifi_ssid}")
  wlan.connect(wifi_ssid, wifi_senha)
  limite_tentativas = 15
  tentativa_atual = 0

  #limitando a quantidade de tentativas
  while not wlan.isconnected() and tentativa_atual < limite_tentativas:
    print(f"Aguardando conexão... ({tentativa_atual + 1}/{limite_tentativas})")
    tentativa_atual += 1
    machine.idle()
    time.sleep(2)

  if wlan.isconnected():
    print("\nConexão Wi-Fi estabelecida com sucesso!")
    # Exibe os detalhes de rede obtidos
    print("Configurações de IP:", wlan.ipconfig('addr4'))
    return True
  else:
    print("\nNão foi possível conectar ao Wi-Fi.")
    print("Verifique se as credenciais estão corretas e reinicie a placa.")
    return False
    
#inicia quando a placa liga
conectar_wifi()

#limpa a memoria ram da maquina
gc.collect()
print("Memória RAM otimizada para o início do programa principal.\n")