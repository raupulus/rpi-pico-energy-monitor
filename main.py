from machine import Pin, SPI
import time, _thread, gc
from Models.DisplayST7735_128x160 import DisplayST7735_128x160
from Models.Sensor_Intensity import Sensor_Intensity
from Models.Sensor_Voltage import Sensor_Voltage
from Models.RpiPico import RpiPico
from Models.ADS1115 import ADS1115
from Models.Api import Api
from Data.Channels import Channels

# Importo variables de entorno
import env

# Habilito recolector de basura
gc.enable()

TIME_TO_UPLOAD = 10  # Cada cuantos segundos se suben los datos a la api
TIME_TO_SHOW_DATA = 5  # Cada cuantos segundos se muestran los datos en la pantalla

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
    28, 0.5, controller.voltage_working, controller.adc_voltage_correction, debug=env.DEBUG)

channelSensors = []

for channel in Channels(controller, adcWrapper, adcWrapper1, debug=env.DEBUG).getSensors():
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

# Primeras lecturas de sensores integrados
time.sleep(1)
controller.readSensorTemp()
time.sleep(1)
SENSOR_VOLTAGE.readSensor()
time.sleep_ms(100)

# Variables para el manejo de bloqueo con el segundo core
thread_lock = _thread.allocate_lock()
thread_lock_acquired = False


def thread0():
    """
    Primer hilo para lecturas y envío de datos a las acciones del segundo hilo.
    """

    # Inicializo el contador de lecturas
    counter = 0

    # Momento de la última subida a la api.
    last_upload_at = time.time()

    # Momento de la última vez que se mostró por pantalla.
    last_show_display_at = time.time()

    while True:
        time.sleep_ms(10)

        if env.DEBUG:
            print('.')

        # Aquí se almacenará información final para subir a la api o mostrar por pantalla
        read_data = None

        if not controller.locked:
            controller.readSensorTemp()

            time.sleep_ms(20)

            SENSOR_VOLTAGE.readSensor()

        # Almaceno si se ha pasado el tiempo para subir los datos a la api
        need_upload = True if time.time() - last_upload_at >= TIME_TO_UPLOAD and env.UPLOAD_API else False

        # Almaceno si se ha pasado el tiempo para mostrar los datos por pantalla
        need_show_display = time.time() - last_show_display_at >= TIME_TO_SHOW_DATA

        # Aquí se almacenan los datos de los sensores de intensidad
        intensity = []

        for channel in channelSensors:
            sensor = channel.get('sensor')

            if sensor.controller.locked:
                time.sleep_ms(20)
                continue

            time.sleep_ms(20)
            sensor.readSensor()

            # Solo almaceno los datos cuando se va a subir a la api o se va a mostrar por pantalla
            if need_upload or need_show_display:
                intensity.append({
                    'pos': channel.get('pos'),
                    'current': channel.get('sensor').current,
                    'max': channel.get('sensor').max,
                    'min': channel.get('sensor').min,
                    'avg': channel.get('sensor').avg,
                    'reads': channel.get('sensor').reads,
                })

            if need_upload:
                # Reseteo los valores de los sensores
                sensor.resetStats()


        # Compruebo si la pantalla se enciende o si ha pasado el tiempo para apagarla
        display.loop()

        # Preparo datos solo si hay subida de datos o si hay que mostrarlos por pantalla
        if need_show_display or need_upload:
            # Prepara los datos para ser enviados al segundo hilo
            read_data = {
                'cpu_current': controller.current,
                'cpu_max': controller.max,
                'cpu_min': controller.min,
                'cpu_avg': controller.avg,
                'voltage_current': SENSOR_VOLTAGE.current,
                'voltage_max': SENSOR_VOLTAGE.max,
                'voltage_min': SENSOR_VOLTAGE.min,
                'voltage_avg': SENSOR_VOLTAGE.avg,
                'intensity': intensity,
            }

        # Compruebo si ha pasado el tiempo para mostrar datos por pantalla
        if need_show_display and display and display.display_on:
            last_show_display_at = time.time()

            global thread_lock
            global thread_lock_acquired

            # Levanta un hilo independiente para mostrar los datos en la pantalla y subirlos a la api
            if not thread_lock_acquired and read_data:
                thread_lock_acquired = True
                _thread.start_new_thread(thread1, (read_data,))

        if need_upload and read_data and len(read_data):
            controller.locked = True

            # Recorre todos los datos y los muestra por consola
            for key in read_data:
                print(key, read_data[key])
                print()


            try:
                if controller.wifiIsConnected() == False:
                    controller.wifiConnect()

                controller.ledOn()

                api.upload(read_data)
            except Exception as e:
                if env.DEBUG:
                    print('Error al subir api: ', e)
            finally:
                time.sleep_ms(20)

                last_upload_at = time.time()
                controller.locked = False
                controller.ledOff()


def thread1(datas):
    """
    Segundo hilo para acciones secundarias.
    """
    global thread_lock
    global thread_lock_acquired

    thread_lock.acquire()

    # TODO: Crear tabla para que puedan caber todos los datos en la pantalla a partir de recibir "datas"
    time.sleep_ms(200)

    try:
        display.printStat(1, 'CPU/MAX: ', str(controller.current) + '/' + str(controller.max), 'C')

        display.printStat(
            3, 'VCC/AVG: ', str(SENSOR_VOLTAGE.current) + '/' + str(SENSOR_VOLTAGE.avg), 'V')

        display.printStat(
            4, 'V.MIN/V.MAX: ', str(SENSOR_VOLTAGE.min) + '/' + str(SENSOR_VOLTAGE.max), 'V')


        i1 = channelSensors[0].get('sensor')
        i2 = channelSensors[1].get('sensor')
        i3 = channelSensors[2].get('sensor')

        time.sleep_ms(100)

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
    except Exception as e:
        if env.DEBUG:
            print('Error al mostrar datos en pantalla: ', e)
    finally:
        if env.DEBUG:
            print('Memoria antes de liberar: ', gc.mem_free())

        gc.collect()

        if env.DEBUG:
            print("Memoria después de liberar:", gc.mem_free())
            print('Hilo 2 finalizado')

        thread_lock_acquired = False

        thread_lock.release()

while True:
    try:
        thread0()
    except Exception as e:
        if env.DEBUG:
            print('Error: ', e)
    finally:
        if env.DEBUG:
            print('Memoria antes de liberar: ', gc.mem_free())

        gc.collect()

        if env.DEBUG:
            print("Memoria después de liberar:", gc.mem_free())

        time.sleep(5)
