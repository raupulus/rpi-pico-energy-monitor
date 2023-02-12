from machine import Pin, ADC, SPI
import utime
from Models.DisplayST7735_128x160 import DisplayST7735_128x160
from Models.Sensor_Intensity import Sensor_Intensity
from Models.Sensor_Voltage import Sensor_Voltage
from Models.RpiPico import RpiPico
from Models.ADS1115 import ADS1115

# Importo variables de entorno
import env

# Rpi Pico Model
controller = RpiPico(ssid=env.AP_NAME, password=env.AP_PASS)

# ADS1115 Model (i2c to ADC)
adcWrapper = ADS1115(4, 5, 0.601, 3.3)

# Sensor de voltage
SENSOR_VOLTAGE = Sensor_Voltage(
    28, 0.5, controller.voltage_working, controller.adc_voltage_correction)

#  Integrado en Rpi Pico
SENSOR_INTENSITY_1 = Sensor_Intensity(controller, 'acs712', 27, 0.1, 0.20)
SENSOR_INTENSITY_2 = Sensor_Intensity(controller, 'acs712', 26, 0.66, 0.20)

#  Mediante ACS712 (Entiendo que los pines van de 0-3)
SENSOR_INTENSITY_3 = Sensor_Intensity(adcWrapper, 'MAX471', 0, 0.1, 0.05)

# Pantalla principal 128x160px
cs = Pin(13, Pin.OUT)
reset = Pin(9, Pin.OUT)

spi1 = SPI(1, baudrate=8000000, polarity=0, phase=0,
           firstbit=SPI.MSB, sck=Pin(10), mosi=Pin(11), miso=None)


display = DisplayST7735_128x160(spi1, rst=9, ce=13, dc=12, btn_display_on=8)


def setReadOn():
    """
    Preparar lectura, enciende el led integrado.
    TODO: Iniciar conexión al wifi, para que cargue mientras estamos leyendo datos.
    """
    controller.ledOn()

    #print('Wifi ON:', controller.wifi.isconnected())
    #print('Estado del wifi:', controller.wifiStatus())
    #print('ifconfig', controller.wifi.ifconfig())


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
    intensity3 = SENSOR_INTENSITY_3.getStats(5)

    if display.display_on:
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

        display.printStat(
            12, 'I3/AVG: ', str(intensity3.get('current')) + '/' + str(intensity3.get('avg')), 'A')

        display.printStat(
            13, 'I3.MIN/I3.MAX: ', str(intensity3.get('min')) + '/' + str(intensity3.get('max')), 'A')

    else:
        print()
        print('La pantalla está apagada, presiona el botón para encenderla.')

    # TODO: if UPLOAD_API: conectar wifi, esperar wifi conectado, enviar datos a la API cada 1 minuto.
    # TODO: PLANTEAR si tiene sentido: Separar flujo para el hilo que enciende la pantalla, cuando suba a la api salir del loop

    print()
    print('cpu_temp: ' + str(cpu.get('current')) + ' C')
    print('voltage: ' + str(voltage.get('current')) + ' V')
    print('intensity1: ' + str(intensity1.get('current')) + ' A')
    print('intensity2: ' + str(intensity2.get('current')) + ' A')
    print('intensity3: ' + str(intensity3.get('current')) + ' A')
    #print('DEBUG I1: ' + str(SENSOR_INTENSITY_1.debug_max_voltage_on_disconnect))
    #print('DEBUG I2: ' + str(SENSOR_INTENSITY_2.debug_max_voltage_on_disconnect))
    print()

    utime.sleep(0.5)
    setReadOff()

    utime.sleep(3)
