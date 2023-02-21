from machine import Pin, SPI
from sys import exit
import time
import _thread
from Models.DisplayST7735_128x160 import DisplayST7735_128x160
from Models.Sensor_Intensity import Sensor_Intensity
from Models.Sensor_Voltage import Sensor_Voltage
from Models.RpiPico import RpiPico
from Models.ADS1115 import ADS1115
from Models.Api import Api
from Data.Channels import Channels

# Importo variables de entorno
import env

# Rpi Pico Model
controller = RpiPico(ssid=env.AP_NAME, password=env.AP_PASS, debug=env.DEBUG)

# Pantalla principal 128x160px
cs = Pin(13, Pin.OUT)
reset = Pin(9, Pin.OUT)

spi1 = SPI(1, baudrate=8000000, polarity=0, phase=0,
           firstbit=SPI.MSB, sck=Pin(10), mosi=Pin(11), miso=None)


display = DisplayST7735_128x160(spi1, rst=9, ce=13, dc=12, btn_display_on=8)


# ADS1115 Model (i2c to ADC)
adcWrapper = ADS1115(4, 5, 0, 3.3)
time.sleep_ms(120)
adcWrapper1 = ADS1115(4, 5, 0, 3.3, 0x49)

# Sensor de voltage
SENSOR_VOLTAGE = Sensor_Voltage(
    28, 0.5, controller.voltage_working, controller.adc_voltage_correction)

CHANNELS = Channels(controller, adcWrapper, adcWrapper1, debug=env.DEBUG).getSensors()

channelSensors = []

for channel in CHANNELS:
    if channel.get('active'):

        time.sleep_ms(120)

        channelSensors.append({
            'pos': channel.get('pos'),
            'sensor': Sensor_Intensity(
                channel.get('controller'),
                channel.get('sensor'),
                int(channel.get('pin')),
                float(channel.get('sensibility')),
                float(channel.get('min_amperes'))
            )
        })


# Instancia de la api
api = Api(controller, channelSensors, env.API_URL, env.API_PATH, env.API_TOKEN, debug=env.DEBUG)

time.sleep(1)

def callbackRead():
    counter = 0
    while True:
        time.sleep_ms(10)

        cpu = controller.readSensorTemp()

        time.sleep_ms(10)

        voltage = SENSOR_VOLTAGE.readSensor()

        time.sleep_ms(10)

        for channel in channelSensors:
            channel.get('sensor').readSensor()

        # Compruebo si la pantalla se enciende o si ha pasado el tiempo para apagarla
        display.loop()

# Deja en un hilo independiente el control de la pantalla
_thread.start_new_thread(callbackRead, ())

TIME_TO_UPLOAD = 10  # Cada cuantos segundos se suben los datos a la api

last_upload_at = time.time()

def loop():

    if env.DEBUG:
        print()
        print('cpu_temp: ' + str(controller.current) + ' C')
        print('voltage: ' + str(SENSOR_VOLTAGE.current) + ' V')

        for channel in channelSensors:
            sensor = channel.get('sensor')

            print('intensity' + str(channel.get('pos')) + ': ' + str(sensor.current) + ' A')

        print()


    if display.display_on and display:
        # Muestra los datos en la pantalla
        #display.showData(channelSensors, controller.readSensorTemp(), SENSOR_VOLTAGE.readSensor())

        # TODO: Crear tabla para que puedan caber todos los datos en la pantalla

        display.printStat(1, 'CPU/MAX: ', str(controller.current) + '/' + str(controller.max), 'C')

        display.printStat(
            3, 'VCC/AVG: ', str(SENSOR_VOLTAGE.current) + '/' + str(SENSOR_VOLTAGE.avg), 'V')

        display.printStat(
            4, 'V.MIN/V.MAX: ', str(SENSOR_VOLTAGE.min) + '/' + str(SENSOR_VOLTAGE.max), 'V')


        """
        for channel in channelSensors:
            sensor = channel.get('sensor')

            print('intensity' + sensor.pos + str(sensor.get('current')) + ' A')
        """


        i1 = channelSensors[0].get('sensor')
        i2 = channelSensors[1].get('sensor')
        i3 = channelSensors[2].get('sensor')

        display.printStat(
            6, 'I1/AVG: ', str(i1.current) + '/' + str(i1.avg), 'A')

        display.printStat(
            7, 'I1.MIN/I1.MAX: ', str(i1.min) + '/' + str(i1.max), 'A')

        display.printStat(
            9, 'I2/AVG: ', str(i2.current) + '/' + str(i2.avg), 'A')

        display.printStat(
            10, 'I2.MIN/I2.MAX: ', str(i2.min) + '/' + str(i2.max), 'A')

        display.printStat(
            12, 'I3/AVG: ', str(i3.current) + '/' + str(i3.avg), 'A')

        display.printStat(
            13, 'I3.MIN/I3.MAX: ', str(i3.min) + '/' + str(i3.max), 'A')


    global last_upload_at
    diff_in_seconds = time.time() - last_upload_at

    print('diff_in_seconds', diff_in_seconds)

    if env.UPLOAD_API and diff_in_seconds > TIME_TO_UPLOAD:
        controller.ledOn()
        # TODo: Subimos los datos a la api
        # Si ha pasado el tiempo necesario para subir datos a la api, conectamos al wifi y subimos los datos. Borramos los datos en el sensor (reset de datos)




        api.prepare_sensors_and_upload()


        try:
            #api.prepare_sensors_and_upload()
            pass
        except Exception as e:
            if env.DEBUG:
                print('Error al subir api: ', e)
        finally:
            controller.ledOff()

        global last_upload_at
        last_upload_at = time.time()


    time.sleep(5)


while True:
    try:
        loop()
    except Exception as e:
        if env.DEBUG:
            print('Error: ', e)
    finally:
        time.sleep(5)
