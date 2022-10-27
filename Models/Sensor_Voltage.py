#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from machine import ADC


class Sensor_Voltage():

    max_voltage = 0
    min_voltage = 0
    avg_voltage = 0
    current_voltage = 0

    def __init__(self, adc_pin=28, voltage_working=3.3, adc_voltage_correction=0.706):

        self.SENSOR = ADC(adc_pin)
        self.adc_pin = adc_pin
        self.voltage_working = voltage_working
        self.adc_voltage_correction = adc_voltage_correction

        # 16bits factor de conversión, aunque la lectura real en raspberry es 12bits.
        self.adc_conversion_factor = voltage_working / 65535

        # Estado inicial para estadísticas
        self.resetStats()

    def resetStats(self):
        """Reset statistics"""
        voltage = self.readVoltage()
        self.max_voltage = voltage
        self.min_voltage = voltage
        self.avg_voltage = voltage
        self.current_voltage = voltage

    def readVoltage(self):
        """
        Read sensor and return voltage
        """
        reading = self.SENSOR.read_u16()  # Lectura del ADC a 16 bits
        readingParse = ((reading - self.adc_voltage_correction)
                        * self.adc_conversion_factor)

        return 5 * readingParse

    def getVoltage(self, samples=50):
        """
        Read sensor and return voltage
        @param samples: Number of samples to read
        """
        sum = 0

        for read in range(samples):
            voltage = self.readVoltage()

            self.current_voltage = voltage

            sum += voltage

            # Estadísticas
            if voltage > self.max_voltage:
                self.max_voltage = voltage
            if voltage < self.min_voltage:
                self.min_voltage = voltage
            self.avg_voltage = (self.avg_voltage + voltage) / 2

        return sum/samples

    def getStats(self, samples=50):
        """Get statistics"""
        self.getVoltage(samples)

        return {
            'max': round(float(self.max_voltage), 2),
            'min': round(float(self.min_voltage), 2),
            'avg': round(float(self.avg_voltage), 2),
            'current': round(float(self.current_voltage), 2),
        }

    def debug(self):
        """Debug Sensor_Voltage to console"""
        pass
