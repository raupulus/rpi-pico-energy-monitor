from machine import Pin, ADC, SPI
from time import sleep
import utime
import Models.ST7735
# import Models/DisplayST7735_128x160


ST7735.ST7735_TFTHEIGHT = 160  # Establece la altura de la pantalla
cs = machine.Pin(13, machine.Pin.OUT)
reset = machine.Pin(9, machine.Pin.OUT)

spi1 = machine.SPI(1, baudrate=8000000, polarity=0, phase=0,
                   firstbit=machine.SPI.MSB, sck=machine.Pin(10), mosi=machine.Pin(11), miso=None)
#display = DisplayST7735_128x160(spi1, rst=9, ce=13, dc=12)

# display.example()


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


def getVoltage(samples):
    sum = 0

    for read in range(samples):
        reading = adc2.read_u16()  # Lectura del ADC a 16 bits
        readingParse = ((reading - adc_voltage_correction)
                        * adc_conversion_factor)

        sum += 5 * readingParse

    return sum/samples


def getRpiPicoTemp():
    reading = (adc3.read_u16() * adc_conversion_factor) - \
        adc_voltage_correction
    cpu_temp = INTEGRATED_TEMP_CORRECTION - reading / \
        0.001721  # Formula given in RP2040 Datasheet

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

    return intensity/10


def sendDisplay(message):
    pass


while True:
    setReadOn()

    voltage = round(getVoltage(1), 4)
    intensity = round(getIntensity(50, 0.1), 4)
    cpu_temp = round(getRpiPicoTemp(), 2)

    print()
    print('voltage: ' + str(voltage) + ' V')
    print('intensity: ' + str(intensity) + ' A')
    print('cpu_temp: ' + str(cpu_temp) + ' ºC')
    print()

    utime.sleep(0.5)
    setReadOff()

    utime.sleep(1.5)
