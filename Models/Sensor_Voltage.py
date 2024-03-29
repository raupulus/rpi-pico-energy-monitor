from machine import ADC

class Sensor_Voltage():
    reads = 0 # Cantidad de lecturas realizadas desde el último reset
    max = 0
    min = 0
    avg = 0
    current = 0

    locked = False # Indica si está bloqueado para no realizar lecturas

    def __init__(self, adc_pin=28, min_voltage=0.5, voltage_working=3.3, adc_voltage_correction=0.706, debug=False):
        self.SENSOR = ADC(adc_pin)
        self.adc_pin = adc_pin
        self.min_voltage = min_voltage
        self.voltage_working = voltage_working
        self.adc_voltage_correction = adc_voltage_correction
        self.DEBUG = debug

        # 16bits factor de conversión, aunque la lectura real en raspberry pi pico es de 12bits.
        self.adc_conversion_factor = voltage_working / 65535

        self.resetStats()

    def resetStats(self, current=None):
        """Reset Statistics"""

        if self.locked:
            voltage = self.avg
        else:
            voltage = current if current else self.getVoltage()

        self.max = voltage
        self.min = voltage
        self.avg = voltage
        self.current = voltage
        self.reads = 0

    def readSensor(self):
        """ Read sensor and return voltage"""

        if self.locked:
            return self.current

        self.locked = True

        try:
            # Lectura del ADC a 16 bits (12bits en raspberry pi pico, traducido a 16bits)
            reading = self.SENSOR.read_u16()

            readingParse = ((reading - self.adc_voltage_correction)
                            * self.adc_conversion_factor)

            value = 5 * readingParse

            if readingParse < self.min_voltage:
                return 0.00


            voltage = float(value)
            self.current = voltage

            # Estadísticas
            if voltage > self.max:
                self.max_voltage = voltage
            if voltage < self.min:
                self.min = voltage

            self.reads += 1

            self.avg = float((self.avg + voltage) / 2)
        except Exception as e:
            if self.DEBUG:
                print('Error al leer sensor de voltaje', e)

            return self.avg
        finally:
            self.locked = False

        return value

    def getVoltage(self, samples=1):
        """
        Read sensor and return voltage
        @param samples: Number of samples to read
        """

        sum = 0

        for read in range(samples):
            voltage = self.readSensor()

            sum += voltage

        return float(sum/samples)

    def getStats(self):
        """ Get Statistics formated as a dictionary"""

        return {
            'max': float(self.max),
            'min': float(self.min),
            'avg': float(self.avg),
            'current': float(self.current),
            'reads': self.reads
        }
