from machine import ADC


class Sensor_Voltage():
    max = 0
    min = 0
    avg = 0
    current = 0

    def __init__(self, adc_pin=28, min_voltage=0.5, voltage_working=3.3, adc_voltage_correction=0.706):
        self.SENSOR = ADC(adc_pin)
        self.adc_pin = adc_pin
        self.min_voltage = min_voltage
        self.voltage_working = voltage_working
        self.adc_voltage_correction = adc_voltage_correction

        # 16bits factor de conversión, aunque la lectura real en raspberry pi pico es de 12bits.
        self.adc_conversion_factor = adc_conversion_factor = voltage_working / 65535

        self.resetStats()

    def resetStats(self):
        """Reset Statistics"""
        voltage = self.getVoltage()
        self.max = voltage
        self.min = voltage
        self.avg = voltage
        self.current = voltage

    def readVoltage(self):
        """ Read sensor and return voltage"""

        # Lectura del ADC a 16 bits (12bits en raspberry pi pico, traducido a 16bits)
        reading = self.SENSOR.read_u16()

        readingParse = ((reading - self.adc_voltage_correction)
                        * self.adc_conversion_factor)

        voltage = 5 * readingParse

        if readingParse < self.min_voltage:
            return 0.00

        return round(float(voltage), 2)

    def getVoltage(self, samples=50):
        """
        Read sensor and return voltage
        @param samples: Number of samples to read
        """

        sum = 0

        for read in range(samples):
            voltage = self.readVoltage()

            self.current = round(voltage, 2)

            sum += voltage

            # Estadísticas
            if voltage > self.max:
                self.max_voltage = voltage
            if voltage < self.min:
                self.min = voltage
            self.avg = round(float((self.avg + voltage) / 2), 2)

        return round(float(sum/samples), 2)

    def getStats(self, samples=50):
        """ Get Statistics formated as a dictionary"""

        self.getVoltage(samples)

        return {
            'max': round(float(self.max), 2),
            'min': round(float(self.min), 2),
            'avg': round(float(self.avg), 2),
            'current': round(float(self.current), 2)
        }
