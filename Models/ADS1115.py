# Adaptador de i2c a ADC (analógico a digital) ADS1115
from machine import I2C, Pin
from Library.Ads1x15 import *

class ADS1115():
    adc_voltage_correction = 0
    voltage_working = 3.3
    locked = False

    def __init__(self, sda_pin, scl_pin, adc_voltage_correction=0.0, voltage_working=3.3, address=0x48):
        self.adc_voltage_correction = adc_voltage_correction
        self.voltage_working = voltage_working

        i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin))

        self.adc = ADS1115Lib(i2c, address)
        self.adc.setVoltageRange_mV(ADS1115_RANGE_4096)
        # self.adc.setCompareChannels(ADS1115_COMP_0_GND)
        self.adc.setMeasureMode(ADS1115_SINGLE)

    def readAnalogInput(self, pin):
        """
        Read analog value from pin, Los valores válidos son 0-3
        Lectura del ADC a 16 bits, igual que micropython (rpi solo 12)
        """

        if self.locked:
            return None

        self.locked = True

        reading = None

        try:
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
        except Exception as e:
            print("Error: ", e)
            reading = 0
        finally:
            self.locked = False

        #print("reading: ", reading)
        #print("getRawResult: ", self.adc.getRawResult())
        # print("reading - adc_voltage_correction: ",
        #      reading - self.adc_voltage_correction)

        # print("")

        # 3.3v
        # 1.49
        # Tengo que devolver mayor a 1.65v
        # 1.65v = 0amperes
        # 0.185 = 1A
        # El rango es de 0-2v
        # 2v = 3.3v: 1.5v
        # Sin carga: 0,7v
        # Consumo de 1,65A devuelve 1,51v

        # 3,3v - 1,51v = 1,79v
        # 3,3v + 0,7v = 4v; 4v - 1,79v = 2,21v; 2,21 - 1,65 = 0,56v; 0,56v / 0,185 = 3A;
        # 3v + 0,7 = 3,7v; 3,7v - 1,79v = 1,91v; 1,91v / 0,185 = 1,04A
        # 3,3 + 0,7 = 4v; 4v - 1.65v = 2,35v; 2,35v / 0,185 = 3,2A
        # 2v - 1,5v = 0,5v; (0,5v * 2v) / 3,3v = 0,33v; 0,33v / 0,185 = 1,78A

        # 3.3v - 0.33v = 2.97v
        # 2.97v - 1.65v = 1.32v
        # 3.3v - 1.32v = 1.98v; 1.98v / 0.185 = 10.7A

        # result = (reading - self.adc_voltage_correction) * \
        #    self.voltage_working / 2

        #result = 3 - (reading - self.adc_voltage_correction)

        #print("result: ", result)

        return reading - self.adc_voltage_correction if reading else None
        # return 1.65 + ((2 - reading) * 2) / self.voltage_working
        # return 3.3 - (2 - (reading - self.adc_voltage_correction))
