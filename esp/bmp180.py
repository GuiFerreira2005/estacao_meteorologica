import time
from machine import I2C

class BMP180:
    def __init__(self, i2c, address=0x77):
        self.i2c = i2c
        self.address = address
        try:
            self._load_calibration()
        except OSError:
            raise OSError("BMP180 nao detectado no barramento I2C!")

    def _read_word(self, reg, signed=True):
        # Lê exatamente 2 bytes do registrador de calibracao
        buf = self.i2c.readfrom_mem(self.address, reg, 2)
        # Converte os bytes em inteiro de 16 bits (MSB primeiro) de forma nativa e segura
        val = int.from_bytes(buf, 'big')
        if signed and val > 32767:
            val -= 65536
        return val

    def _load_calibration(self):
        # Leitura dos 11 coeficientes de calibração gravados de fábrica
        self.AC1 = self._read_word(0xAA, True)
        self.AC2 = self._read_word(0xAC, True)
        self.AC3 = self._read_word(0xAE, True)
        self.AC4 = self._read_word(0xB0, False)
        self.AC5 = self._read_word(0xB2, False)
        self.AC6 = self._read_word(0xB4, False)
        self.B1 = self._read_word(0xB6, True)
        self.B2 = self._read_word(0xB8, True)
        self.MB = self._read_word(0xBA, True)
        self.MC = self._read_word(0xBC, True)
        self.MD = self._read_word(0xBE, True)

    def read_raw_temp(self):
        self.i2c.writeto_mem(self.address, 0xF4, b'\x2E')
        time.sleep_ms(5)
        buf = self.i2c.readfrom_mem(self.address, 0xF6, 2)
        # Conversão nativa sem uso de colchetes de indexação
        return int.from_bytes(buf, 'big')

    def read_raw_pressure(self):
        oss = 0
        self.i2c.writeto_mem(self.address, 0xF4, b'\x34')
        time.sleep_ms(5)
        buf = self.i2c.readfrom_mem(self.address, 0xF6, 3)
        # Converte os 3 bytes de pressão diretamente em um inteiro de 24 bits
        val = int.from_bytes(buf, 'big')
        return val >> (8 - oss)

    @property
    def temperature(self):
        UT = self.read_raw_temp()
        X1 = ((UT - self.AC6) * self.AC5) // 32768
        X2 = (self.MC * 2048) // (X1 + self.MD)
        B5 = X1 + X2
        t = (B5 + 8) // 16
        return t / 10.0 # Temperatura final em °C

    @property
    def pressure(self):
        UT = self.read_raw_temp()
        UP = self.read_raw_pressure()
        
        X1 = ((UT - self.AC6) * self.AC5) // 32768
        X2 = (self.MC * 2048) // (X1 + self.MD)
        B5 = X1 + X2
        
        B6 = B5 - 4000
        X1 = (self.B2 * ((B6 * B6) // 4096)) // 2048
        X2 = (self.AC2 * B6) // 2048
        X3 = X1 + X2
        B3 = (((self.AC1 * 4 + X3) + 2) // 4)
        
        X1 = (self.AC3 * B6) // 8192
        X2 = (self.B1 * ((B6 * B6) // 4096)) // 65536
        X3 = ((X1 + X2) + 2) // 4
        B4 = (self.AC4 * (X3 + 32768)) // 32768
        B7 = (UP - B3) * 50000
        
        if B7 < 0x80000000:
            p = (B7 * 2) // B4
        else:
            p = (B7 // B4) * 2
            
        X1 = (p // 256) * (p // 256)
        X1 = (X1 * 3038) // 65536
        X2 = (-7357 * p) // 65536
        p = p + ((X1 + X2 + 3791) // 16)
        return p / 100.0 # Pressão atmosférica em hPa
