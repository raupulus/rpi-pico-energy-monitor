# Sensor de intensidad

from machine import ADC


class ACS712():

    def __init__(self, adc_pin=26, sensibility=0.1, min_amperes=0.15, voltage_working=3.3, ):
        self.adc_pin = adc_pin
        self.min_amperes = min_amperes
        self.sensibility = sensibility
        self.voltage_working = voltage_working

    def readAnalogInput(self, value16bits):
        """
        El valor 0 corresponde a la mitad de la tensión de trabajo del sensor (5v/2 = 2.5v = 0amperes, 3.3v/2 = 1.65v = 0amperes))
        """
        #readingParse = (value16bits - (self.voltage_working/2))
        #readingParse = (self.voltage_working/2) - value16bits
        #readingParse = value16bits - (2.575 - (self.voltage_working/2))

        # debe dar sobre 1v (0,925v concretamente)
        #readRange = 2.575 - (self.voltage_working/2)

        # De lo que recibo se lo resto a 1,65v y obtengo la diferencia
        #readingParse = 1.65 + (1.65 - value16bits)

        readingParse = (self.voltage_working/2) - value16bits

        #print("")
        #print("pin: ", self.adc_pin)
        #print("readingParse: ", readingParse)
        #print("value16bits: ", value16bits)
        #print("")

        # 1.65 + (1.65 - 1.58)

        # 1.65 - 2.575 = -1.025
        # 2.575 - 3.3/2 = 1.025

        # 1.65 = 0
        # 1.56 = x

        amperes = readingParse / self.sensibility

        if amperes <= self.min_amperes:
            return 0.00

        return amperes
