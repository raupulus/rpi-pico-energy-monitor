
from machine import ADC, Pin


class RpiPico():
    INTEGRATED_TEMP_CORRECTION = 27  # Temperatura interna para corregir lecturas
    adc_voltage_correction = 0.706
    voltage_working = 3.3

    max = 0
    min = 0
    avg = 0
    current = 0

    def __init__(self):
        self.TEMP_SENSOR = ADC(4)  # Sensor interno de raspberry pi pico.

        # Definición de GPIO
        self.LED_INTEGRATED = Pin("LED", Pin.OUT)

        # 16bits factor de conversión, aunque la lectura real en raspberry pi pico es de 12bits.
        self.adc_conversion_factor = self.adc_conversion_factor = self.voltage_working / 65535

    def resetStats(self):
        """Reset Statistics"""
        temp = self.readSensorTemp()
        self.max = temp
        self.min = temp
        self.avg = temp
        self.current = temp

    def readSensorTemp(self):
        reading = (self.TEMP_SENSOR.read_u16() * self.adc_conversion_factor) - \
            self.adc_voltage_correction

        value = self.INTEGRATED_TEMP_CORRECTION - reading / \
            0.001721  # Formula given in RP2040 Datasheet

        return round(float(value), 1)

    def getTemp(self):
        cpu_temp = self.readSensorTemp()

        self.current = cpu_temp

        # Estadísticas
        if cpu_temp > self.max:
            self.max = cpu_temp
        if cpu_temp < self.min:
            self.min = cpu_temp

        self.avg_cpu_temp = round(float((self.avg + cpu_temp) / 2), 1)

        return round(float(cpu_temp), 1)

    def ledOn(self):
        self.LED_INTEGRATED.on()

    def ledOff(self):
        self.LED_INTEGRATED.off()

    def getStats(self):
        """ Get Statistics formated as a dictionary"""

        self.getTemp()

        return {
            'max': round(float(self.max), 1),
            'min': round(float(self.min), 1),
            'avg': round(float(self.avg), 1),
            'current': round(float(self.current), 1)
        }

    def wifiStatus(self):
        """ Get wifi status"""
        return "Not implemented"

    def wifiConnect(self, ssid, password):
        """ Connect to wifi"""
        return "Not implemented"

    def wifiDisconnect(self):
        """ Disconnect from wifi"""
        return "Not implemented"

    def bluetoothStatus(self):
        """ Get bluetooth status"""
        return "Not implemented"

    def bluetoothConnect(self):
        """ Connect to bluetooth"""
        return "Not implemented"

    def bluetoothDisconnect(self):
        """ Disconnect from bluetooth"""
        return "Not implemented"
