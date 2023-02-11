# Adaptador de i2c a ADC (analógico a digital) ADS1115
from machine import ADC, Pin


class ADS1115():
    adc_voltage_correction = 0.706
    voltage_working = 3.3

    def __init__(self, sda_pin, scl_pin, adc_voltage_correction=0.15, voltage_working=3.3,):
        self.sda_pin = sda_pin
        self.scl_pin = scl_pin
        self.adc_voltage_correction = adc_voltage_correction
        self.voltage_working = voltage_working

    def readAnalogInput(self, pin):
        """
        Read analog value from pin, Los valores válidos son 0-3
        Lectura del ADC a 16 bits, igual que micropython (rpi solo 12)
        """

        # TODO: Analizar como funciona el ADC de adicional, devolver lectura

        return 0
        #reading = ADC(pin).read_u16()

        # return (reading / 65535) * self.voltage_working
