# Sensor de intensidad

from machine import ADC


class ACS712():

    def __init__(self, adc_pin=26, sensibility=0.1, min_amperes=0.15, voltage_working=3.3, ):
        self.adc_pin = adc_pin
        self.min_amperes = min_amperes
        self.sensibility = sensibility
        self.voltage_working = voltage_working

    def readAnalogInput(self, value16bits):
        readingParse = (value16bits - (self.voltage_working/2))

        amperes = readingParse / self.sensibility

        if amperes <= self.min_amperes:
            return 0.00

        return amperes
