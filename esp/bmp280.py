# bmp280.py - Driver MicroPython para o BMP280 (I2C 0x76)
from machine import I2C
import time
import ustruct

class BMP280:
    def __init__(self, i2c, address=0x76):
        self.i2c = i2c
        self.addr = address

        # Leitura do Chip ID (0xD0) - extrai o byte como número inteiro (int)
        raw_id = self.i2c.readfrom_mem(self.addr, 0xD0, 1)
        self.chip_id = raw_id[0]

        # Validação do Chip ID (0x58 para BMP280 ou 0x60 para BME280)
        if self.chip_id not in (0x58, 0x60):
            raise OSError(f"BMP280 não encontrado em 0x{address:02x}. Chip ID lido: 0x{self.chip_id:02x}")

        self._ler_calibracao()
        # Configura modo normal, amostragem x1 para temperatura e pressão
        self.i2c.writeto_mem(self.addr, 0xF4, b'\x27')
        time.sleep_ms(100)

    def _ler_calibracao(self):
        cal = self.i2c.readfrom_mem(self.addr, 0x88, 24)
        (self.dig_T1, self.dig_T2, self.dig_T3,
         self.dig_P1, self.dig_P2, self.dig_P3, self.dig_P4, self.dig_P5,
         self.dig_P6, self.dig_P7, self.dig_P8, self.dig_P9) = ustruct.unpack('<HHhHhHhHhhhh', cal)

    def ler_dados(self):
        data = self.i2c.readfrom_mem(self.addr, 0xF7, 6)

        # Extração dos 20 bits indexando os bytes individuais da leitura I2C
        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

        # Compensação de Temperatura (Bosch)
        var1 = ((adc_t >> 3) - (self.dig_T1 << 1)) * self.dig_T2 >> 11
        var2 = (((((adc_t >> 4) - self.dig_T1) * ((adc_t >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        t_fine = var1 + var2
        temp = (t_fine * 5 + 128) >> 8
        temperatura_c = round(temp / 100.0, 1)

        # Compensação de Pressão (Bosch)
        var1 = t_fine - 128000
        var2 = var1 * var1 * self.dig_P6 + ((var1 * self.dig_P5) << 17) + (self.dig_P4 << 35)
        var1 = ((var1 * var1 * self.dig_P3) >> 8) + ((var1 * self.dig_P2) << 12)
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33

        if var1 == 0:
            pressao_hpa = 0.0
        else:
            p = 1048576 - adc_p
            p = (((p << 31) - var2) * 3125) // var1
            var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
            var2 = (self.dig_P8 * p) >> 19
            p = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)
            pressao_hpa = round((p / 256.0) / 100.0, 1)

        return temperatura_c, pressao_hpa
    
    @property
    def temperature(self):
        temp, _ = self.ler_dados()
        return temp

    @property
    def pressure(self):
        _, press = self.ler_dados()
        return press