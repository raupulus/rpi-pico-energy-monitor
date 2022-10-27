#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from machine import Pin, ADC, SPI
from time import sleep
import utime
from Models.DisplayST7735_128x160 import DisplayST7735_128x160

cs = machine.Pin(13, machine.Pin.OUT)
reset = machine.Pin(9, machine.Pin.OUT)

spi1 = machine.SPI(1, baudrate=8000000, polarity=0, phase=0,
                   firstbit=machine.SPI.MSB, sck=machine.Pin(10), mosi=machine.Pin(11), miso=None)

# Pantalla principal 128x160px
display = DisplayST7735_128x160(spi1, rst=9, ce=13, dc=12)


voltage_working = 3.3
adc_conversion_factor = voltage_working / 65535  # 16/bits: raspberry 12bits.
# Corrección de voltaje al leer ADC, en rpi pico según datasheet es 0.706
adc_voltage_correction = 0.706

INTEGRATED_TEMP_CORRECTION = 27  # Temperatura interna para corregir lecturas

# Definición de GPIO
LED_INTEGRATED = Pin("LED", Pin.OUT)


# Pines analógicos
adc0 = machine.ADC(26)  # Sensor de intensidad.
adc1 = machine.ADC(27)  # Sensor de intensidad.
adc2 = machine.ADC(28)  # Sensor de tensión.
adc3 = machine.ADC(4)  # Sensor interno de raspberry pi pico.


# Guardo estadísticas

max_voltage = 0
max_intensity = 0
max_cpu_temp = 0
min_voltage = 0
min_intensity = 0
min_cpu_temp = 0
avg_voltage = 0
avg_intensity = 0
avg_cpu_temp = 0


def getVoltage(samples):
    global max_voltage, min_voltage, avg_voltage
    sum = 0

    for read in range(samples):
        reading = adc2.read_u16()  # Lectura del ADC a 16 bits
        readingParse = ((reading - adc_voltage_correction)
                        * adc_conversion_factor)

        voltage = 5 * readingParse

        sum += voltage

        # Estadísticas
        if voltage > max_voltage:
            max_voltage = voltage
        if voltage < min_voltage:
            min_voltage = voltage
        avg_voltage = (avg_voltage + voltage) / 2

    return sum/samples


def getRpiPicoTemp():
    global max_cpu_temp, min_cpu_temp, avg_cpu_temp

    reading = (adc3.read_u16() * adc_conversion_factor) - \
        adc_voltage_correction
    cpu_temp = INTEGRATED_TEMP_CORRECTION - reading / \
        0.001721  # Formula given in RP2040 Datasheet

    # Estadísticas
    if cpu_temp > max_cpu_temp:
        max_cpu_temp = cpu_temp
    if cpu_temp < min_cpu_temp:
        min_cpu_temp = cpu_temp
    avg_cpu_temp = (avg_cpu_temp + cpu_temp) / 2

    return cpu_temp


def setReadOn():
    """
    Preparar lectura, enciende el led integrado.
    TODO: Iniciar conexión al wifi, para que cargue mientras estamos leyendo datos.
    """
    LED_INTEGRATED.on()


def setReadOff():
    """
    Termina lectura, apaga led integrado.
    TODO: Al terminar la lectura, enviar datos por wifi a la API.
    """

    LED_INTEGRATED.off()


def getIntensity(samples, sensibility_5v=0.1):
    """
    Recibe la sensibilidad para 5v, se calcula por si la tensión de trabajo es otra.
    """

    global max_intensity, min_intensity, avg_intensity

    # Revisar: La sensibilidad, de 100mv/a es para 5v. Sacar método para pasarlo a 3,3v
    sensibility = ((sensibility_5v / 5) * voltage_working) * voltage_working

    sum = 0  # Almaceno el total de valores a partir de todos los samples

    for read in range(samples):
        reading = adc2.read_u16()  # Lectura del ADC a 16 bits
        readingParse = ((reading - adc_voltage_correction)
                        * adc_conversion_factor)

        if readingParse <= (voltage_working/2):
            readingParse = voltage_working/2

        sum += readingParse

    average = sum/samples

    # Calcula la intensidad en ma?
    intensity = (average - (voltage_working/2)) / sensibility

    # Estadísticas
    if intensity > max_intensity:
        max_intensity = (intensity / 10)
    if intensity < min_intensity:
        min_intensity = (intensity / 10)
    avg_intensity = (avg_intensity + (intensity / 10)) / 2

    return intensity/10


while True:
    setReadOn()

    voltage = round(getVoltage(1), 4)
    intensity = round(getIntensity(50, 0.1), 4)
    cpu_temp = round(getRpiPicoTemp(), 2)

    display.printStat(1, 'Voltaje: ', round(voltage, 2), 'V')
    display.printStat(2, 'Int: ', round(intensity, 2), 'A')
    display.printStat(3, 'Cpu: ', round(cpu_temp, 2), 'C')

    display.printStat(4, '', '', '')
    display.printStat(5, 'Voltaje AVG: ', round(avg_voltage, 2), 'V')
    display.printStat(6, 'Intensidad AVG: ', round(avg_intensity, 2), 'A')

    display.printStat(7, '', '', '')
    display.printStat(8, 'Voltaje Min.: ', round(min_voltage, 2), 'V')
    display.printStat(9, 'Intensidad Min: ', round(min_intensity, 2), 'A')
    display.printStat(10, 'Voltaje Max.: ', round(max_voltage, 2), 'V')
    display.printStat(11, 'Intensidad Max: ', round(max_intensity, 2), 'A')

    print()
    print('voltage: ' + str(voltage) + ' V')
    print('intensity: ' + str(intensity) + ' A')
    print('cpu_temp: ' + str(cpu_temp) + ' C')
    print()

    utime.sleep(0.5)
    setReadOff()

    utime.sleep(1.5)
