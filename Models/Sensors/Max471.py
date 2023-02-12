# SENSOR INTENSIDAD (quizás también lea tensión/voltaje)

class Max471():

    def __init__(self, adc_pin):
        self.adc_pin = adc_pin

    def readAnalogInput(self, value16bits):
        print("value16bits: ", value16bits)

        if value16bits >= 3:
            return 0

        if value16bits <= 0:
            return 3

        amperes = 3 - value16bits

        print("amperes: ", amperes)

        return amperes
