from machine import ADC


class Sensor_Intensity():
    max = 0
    min = 0
    avg = 0
    current = 0

    # Diferencia máxima al estar desconectado 65535/2, para debug
    debug_max_voltage_on_disconnect = 0

    def __init__(self, adc_pin=26, sensibility=0.1, min_amperes=0.15, voltage_working=3.3, ):
        """
        @param adc_pin: ADC pin
        @param sensibility: Sensibility of the sensor (5A = 0.185mv/A, 20A = 100mv/A, 30A = 66mv/A)
        @param min_amperes: Minimum amperes to detect
        @param voltage_working: Working voltage of the sensor
        """
        self.SENSOR = ADC(adc_pin)
        self.adc_pin = adc_pin
        self.voltage_working = voltage_working
        self.min_amperes = min_amperes
        self.sensibility = sensibility

        # 16bits factor de conversión, aunque la lectura real en raspberry pi pico es de 12bits.
        self.adc_conversion_factor = adc_conversion_factor = voltage_working / 65535

        self.resetStats()

    def resetStats(self):
        """Reset Statistics"""
        intensity = self.getIntensity()
        self.max = intensity
        self.min = intensity
        self.avg = intensity
        self.current = intensity

    def readSensor(self):
        """ Read sensor and return amperes"""

        # Lectura del ADC a 16 bits (12bits en raspberry pi pico, traducido a 16bits)
        reading = self.SENSOR.read_u16()

        if (reading - (65535/2)) > self.debug_max_voltage_on_disconnect:
            self.debug_max_voltage_on_disconnect = (reading - (65535/2))

        readingParse = (reading / 65535) * self.voltage_working

        calc = (readingParse - (self.voltage_working/2))

        amperes = calc / self.sensibility

        if amperes <= self.min_amperes:
            return 0.00

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
