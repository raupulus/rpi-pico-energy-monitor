from machine import Pin, ADC, SPI
from time import sleep
import utime
from Models.DisplayST7735_128x160 import DisplayST7735_128x160
from Models.Sensor_Intensity import Sensor_Intensity
from Models.Sensor_Voltage import Sensor_Voltage
from Models.RpiPico import RpiPico

voltage_working = 3.3

# Corrección de voltaje al leer ADC, en rpi pico según datasheet es 0.706
adc_voltage_correction = 0.706

# Rpi Pico Model
controller = RpiPico()

# Sensor de voltage
SENSOR_VOLTAGE = Sensor_Voltage(
    28, 0.5, voltage_working, adc_voltage_correction)

# Sensores de intensidad
SENSOR_INTENSITY_1 = Sensor_Intensity(27, 0.1, 0.20, voltage_working)
SENSOR_INTENSITY_2 = Sensor_Intensity(26, 0.66, 0.20, voltage_working)

# Pantalla principal 128x160px
cs = Pin(13, Pin.OUT)
reset = Pin(9, Pin.OUT)

spi1 = SPI(1, baudrate=8000000, polarity=0, phase=0,
           firstbit=SPI.MSB, sck=Pin(10), mosi=Pin(11), miso=None)


display = DisplayST7735_128x160(spi1, rst=9, ce=13, dc=12)


def setReadOn():
    """
    Preparar lectura, enciende el led integrado.
    TODO: Iniciar conexión al wifi, para que cargue mientras estamos leyendo datos.
    """
    controller.ledOn()


def setReadOff():
    """
    Termina lectura, apaga led integrado.
    TODO: Al terminar la lectura, enviar datos por wifi a la API.
    """

    controller.ledOff()


while True:
    setReadOn()

    cpu = controller.getStats()
    voltage = SENSOR_VOLTAGE.getStats(50)
    intensity1 = SENSOR_INTENSITY_1.getStats(500)
    intensity2 = SENSOR_INTENSITY_2.getStats(500)

    display.printStat(1, 'CPU/MAX: ', str(cpu.get('current')
                                          ) + '/' + str(cpu.get('max')), 'C')

    display.printStat(
        3, 'VCC/AVG: ', str(voltage.get('current')) + '/' + str(voltage.get('avg')), 'V')

    display.printStat(
        4, 'V.MIN/V.MAX: ', str(voltage.get('min')) + '/' + str(voltage.get('max')), 'V')

    display.printStat(
        6, 'I1/AVG: ', str(intensity1.get('current')) + '/' + str(intensity1.get('avg')), 'A')

    display.printStat(
        7, 'I1.MIN/I1.MAX: ', str(intensity1.get('min')) + '/' + str(intensity1.get('max')), 'A')

    display.printStat(
        9, 'I2/AVG: ', str(intensity2.get('current')) + '/' + str(intensity2.get('avg')), 'A')

    display.printStat(
        10, 'I2.MIN/I2.MAX: ', str(intensity2.get('min')) + '/' + str(intensity2.get('max')), 'A')

    display.printStat(8, '', '', '')

    print()
    print('cpu_temp: ' + str(cpu.get('current')) + ' C')
    print('voltage: ' + str(voltage.get('current')) + ' V')
    print('intensity1: ' + str(intensity1.get('current')) + ' A')
    print('intensity2: ' + str(intensity2.get('current')) + ' A')
    #print('DEBUG I1: ' + str(SENSOR_INTENSITY_1.debug_max_voltage_on_disconnect))
    #print('DEBUG I2: ' + str(SENSOR_INTENSITY_2.debug_max_voltage_on_disconnect))
    print()

    utime.sleep(0.5)
    setReadOff()

    utime.sleep(3)
