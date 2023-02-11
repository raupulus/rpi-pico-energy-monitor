from machine import ADC
from Models.Sensors.ACS712 import ACS712
from Models.ADS1115 import ADS1115


class Sensor_Intensity():

    min = 0
    max = 0
    avg = 0
    current = 0

    def __init__(self, origin, sensor_type, adc_pin=26, sensibility=0.1, min_amperes=0.15):
        """
        @param origin: Fuente (Wrapper) de donde se accede al sensor (Controlador o interfaz)
        @param adc_pin: ADC pin
        @param sensibility: Sensibility of the sensor (5A = 0.185mv/A, 20A = 100mv/A, 30A = 66mv/A)
        @param min_amperes: Minimum amperes to detect
        @param voltage_working: Working voltage of the sensor
        """
        self.ORIGIN = origin
        #self.adc_pin = adc_pin
        #self.min_amperes = min_amperes
        #self.sensibility = sensibility

        #  TODO: Sensor de intensidad
        if sensor_type.upper() == 'ACS712':
            self.SENSOR = ACS712(adc_pin, sensibility,
                                 min_amperes, origin.voltage_working)
        elif False:
            self.SENSOR = ADS1115()

        # Esto sirve??? quizás mejor dentro de la clase que representa al sensor?
        # self.resetStats()

    def resetStats(self):
        """Reset Statistics"""
        intensity = self.getIntensity()
        self.max = intensity
        self.min = intensity
        self.avg = intensity
        self.current = intensity

    def readSensor(self):
        """ Read sensor and return amperes"""
        read = self.ORIGIN.readAnalogInput(self.SENSOR.adc_pin)

        amperes = self.SENSOR.readAnalogInput(read)

        return round(float(amperes), 2)

    def getIntensity(self, samples=50):
        """
        Read sensor and return voltage
        @param samples: Number of samples to read
        """

        sum = 0

        for read in range(samples):
            intensity = self.readSensor()

            self.current = intensity

            sum += intensity

            # Estadísticas
            if intensity > self.max:
                self.max = intensity
            if intensity < self.min:
                self.min = intensity
            self.avg = round(float((self.avg + intensity) / 2), 2)

        return round(float(sum/samples), 2)

    def getStats(self, samples=50):
        """ Get Statistics formated as a dictionary"""

        self.getIntensity(samples)

        return {
            'max': round(float(self.max), 2),
            'min': round(float(self.min), 2),
            'avg': round(float(self.avg), 2),
            'current': round(float(self.current), 2)
        }
