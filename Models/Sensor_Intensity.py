from machine import ADC
from Models.Sensors.ACS712 import ACS712
from Models.Sensors.Max471 import Max471
from Models.ADS1115 import ADS1115
import time

class Sensor_Intensity():
    reads = 0 # Cantidad de lecturas realizadas desde el último reset
    min = 0
    max = 0
    avg = 0
    current = 0

    block = False # Indica si está bloqueado para no realizar lecturas

    def __init__(self, origin, sensor_type, adc_pin=26, sensibility=0.1, min_amperes=0.15):
        """
        @param origin: Fuente (Wrapper) de donde se accede al sensor (Controlador o interfaz)
        @param adc_pin: ADC pin
        @param sensibility: Sensibility of the sensor (5A = 0.185mv/A, 20A = 100mv/A, 30A = 66mv/A)
        @param min_amperes: Minimum amperes to detect
        @param voltage_working: Working voltage of the sensor
        """
        self.ORIGIN = origin

        if sensor_type.upper() == 'ACS712':
            self.SENSOR = ACS712(adc_pin, sensibility,
                                 min_amperes, origin.voltage_working)
        elif sensor_type.upper() == 'MAX471':
            self.SENSOR = Max471(adc_pin)

        self.resetStats()

    def resetStats(self):
        """Reset Statistics"""
        intensity = self.getIntensity()
        self.max = intensity
        self.min = intensity
        self.avg = intensity
        self.current = intensity
        self.reads = 0

    def readSensor(self):
        """ Read sensor and return amperes"""

        while self.block:
            time.sleep_ms(100)

        ready = False

        while not ready:
            try:
                read = self.ORIGIN.readAnalogInput(self.SENSOR.adc_pin)

                value = self.SENSOR.readAnalogInput(read)
                ready = True
            except Exception as e:
                print('Error de lectura, reintentando...', e)
                time.sleep_ms(20)
        read = self.ORIGIN.readAnalogInput(self.SENSOR.adc_pin)

        value = self.SENSOR.readAnalogInput(read)

        amperes = round(float(value), 2)

        self.current = amperes

        # Estadísticas
        if amperes > self.max:
            self.max = amperes
        if amperes < self.min:
            self.min = amperes


        self.reads += 1

        self.avg = round(float((self.avg + amperes) / self.reads), 2)

        return amperes

    def getIntensity(self, samples=50):
        """
        Read sensor and return voltage
        @param samples: Number of samples to read
        """

        sum = 0

        for read in range(samples):
            intensity = self.readSensor()

            sum += intensity

        return round(float(sum/samples), 2)

    def getStats(self, samples=50):
        """ Get Statistics formated as a dictionary"""

        return {
            'max': round(float(self.max), 2),
            'min': round(float(self.min), 2),
            'avg': round(float(self.avg), 2),
            'current': round(float(self.current), 2),
            'reads': self.reads
        }
