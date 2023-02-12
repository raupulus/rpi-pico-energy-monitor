# Adaptador de i2c a ADC (analógico a digital) ADS1115
from machine import I2C, Pin
from Library.Ads1x15 import *


class ADS1115():
    adc_voltage_correction = 0.559
    voltage_working = 3.3

    def __init__(self, sda_pin, scl_pin, adc_voltage_correction=0.559, voltage_working=3.3, address=0x48):
        self.adc_voltage_correction = adc_voltage_correction
        self.voltage_working = voltage_working

        i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin))

        self.adc = ADS1115Lib(i2c, address)
        self.adc.setVoltageRange_mV(ADS1115_RANGE_2048)
        # self.adc.setCompareChannels(ADS1115_COMP_0_GND)
        self.adc.setMeasureMode(ADS1115_SINGLE)

    def readAnalogInput(self, pin):
        """
        Read analog value from pin, Los valores válidos son 0-3
        Lectura del ADC a 16 bits, igual que micropython (rpi solo 12)
        """

        if pin == 0:
            self.adc.setCompareChannels(ADS1115_COMP_0_GND)
        elif pin == 1:
            self.adc.setCompareChannels(ADS1115_COMP_1_GND)
        elif pin == 2:
            self.adc.setCompareChannels(ADS1115_COMP_2_GND)
        elif pin == 3:
            self.adc.setCompareChannels(ADS1115_COMP_3_GND)

        self.adc.startSingleMeasurement()

        while self.adc.isBusy():
            pass

        reading = self.adc.getResult_V()

        print("reading: ", reading)
        print("getVoltageRange_mV: ", self.adc.getVoltageRange_mV())
        print("getRawResult: ", self.adc.getRawResult())
        print("getResult_mV: ", self.adc.getResult_mV())

        print("reading - adc_voltage_correction: ",
              reading - self.adc_voltage_correction)
        print("adc_voltage_correction: ", self.adc_voltage_correction)

        return reading - self.adc_voltage_correction
