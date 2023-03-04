from machine import Pin, SPI
import _thread, gc
from time import sleep_ms, sleep, time
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

TIME_TO_UPLOAD = 30  # Cada cuantos segundos se suben los datos a la api
TIME_TO_SHOW_DATA = 5  # Cada cuantos segundos se muestran los datos en la pantalla

# Rpi Pico Model
if env.UPLOAD_API and env.AP_NAME and env.AP_PASS:
    controller = RpiPico(ssid=env.AP_NAME, password=env.AP_PASS, debug=env.DEBUG)
else:
    controller = RpiPico(debug=env.DEBUG)

# Pantalla principal 128x160px
cs = Pin(13, Pin.OUT)
reset = Pin(9, Pin.OUT)

spi1 = SPI(1, baudrate=8000000, polarity=0, phase=0,
           firstbit=SPI.MSB, sck=Pin(10), mosi=Pin(11), miso=None)


display = DisplayST7735_128x160(spi1, rst=9, ce=13, dc=12, btn_display_on=8, orientation=env.DISPLAY_ORIENTATION, debug=env.DEBUG, timeout=env.DISPLAY_TIMEOUT)

# ADS1115 Model (i2c to ADC)
adcWrapper = ADS1115(4, 5, 0, 3.3)
sleep_ms(120)
adcWrapper1 = ADS1115(4, 5, 0, 3.3, 0x49)

# Sensor de voltage
SENSOR_VOLTAGE = Sensor_Voltage(
    28, 0.5, controller.voltage_working, controller.adc_voltage_correction, debug=env.DEBUG)

sleep_ms(10)

channelSensors = []

for channel in Channels(controller, adcWrapper, adcWrapper1, debug=env.DEBUG).getSensors():
    if channel.get('active'):

        sleep_ms(10)

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

#gc.collect()

# Instancia de la api
api = Api(controller, channelSensors, env.API_URL, env.API_PATH, env.API_TOKEN, debug=env.DEBUG)

# Primeras lecturas de sensores integrados
sleep_ms(50)
controller.readSensorTemp()
sleep_ms(100)
SENSOR_VOLTAGE.readSensor()
sleep_ms(100)

## Crea base de la pantalla
display.displayHeadInfo(wifi_status=controller.wifiStatus(), voltage=SENSOR_VOLTAGE.current)
sleep_ms(display.DELAY)
display.displayFooterInfo()
sleep_ms(display.DELAY)
display.tableCreate(len(channelSensors), demo=True)

# Variables para el manejo de bloqueo con el segundo core
thread_lock = _thread.allocate_lock()
thread_lock_acquired = False

#gc.collect()

def thread0():
    """
    Primer hilo para lecturas y envío de datos a las acciones del segundo hilo.
    """

    # Inicializo el contador de lecturas
    #counter = 0

    # Momento de la última subida a la api.
    last_upload_at = time()

    # Momento de la última vez que se mostró por pantalla.
    last_show_display_at = time()

    while True:
        if env.DEBUG:
            print('.')

        #counter += 1

        # Aquí se almacenará información final para subir a la api o mostrar por pantalla
        read_data = None

        if not controller.locked:
            controller.readSensorTemp()

            sleep_ms(10)

            SENSOR_VOLTAGE.readSensor()

        # Almaceno si se ha pasado el tiempo para subir los datos a la api
        duration = time() - last_upload_at
        need_upload = True if duration >= TIME_TO_UPLOAD and env.UPLOAD_API else False

        # Almaceno si se ha pasado el tiempo para mostrar los datos por pantalla
        need_show_display = time() - last_show_display_at >= TIME_TO_SHOW_DATA

        # Aquí se almacenan los datos de los sensores de intensidad
        intensity = []

        for channel in channelSensors:
            sensor = channel.get('sensor')

            if sensor.controller.locked:
                sleep_ms(10)
                continue

            sleep_ms(10)
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
            last_show_display_at = time()

            global thread_lock
            global thread_lock_acquired

            # Levanta un hilo independiente para mostrar los datos en la pantalla y subirlos a la api
            if not thread_lock_acquired and read_data:
                thread_lock_acquired = True

                _thread.start_new_thread(thread1, (read_data.get('intensity'), controller.wifiStatus(), read_data['voltage_current']))

            #if (read_data and len(read_data)):
            #    thread1(read_data.get('intensity'), controller.wifiStatus(), read_data['voltage_current'])

        if need_upload and read_data and len(read_data):
            controller.locked = True

            # Recorre todos los datos y los muestra por consola
            if env.DEBUG:
                for key in read_data:
                    print(key, read_data[key])
                    print()

            try:
                if controller.wifiIsConnected() == False:
                    controller.wifiConnect()

                controller.ledOn()

                read_data['hardware_device'] = env.DEVICE_ID
                read_data['duration'] = duration

                api.upload(read_data)
            except Exception as e:
                if env.DEBUG:
                    print('Error al subir api: ', e)
            finally:
                sleep_ms(20)

                last_upload_at = time()
                controller.locked = False
                controller.ledOff()


def thread1(sensors, wifi_status, voltage):
    """
    Segundo hilo para acciones secundarias.
    """
    global thread_lock
    global thread_lock_acquired

    thread_lock.acquire()

    gc.collect()

    try:
        display.displayHeadInfo(wifi_status, voltage)

        for sensor in sensors:

            ## TODO: Extraer a función para redondear los valores

            current = round(sensor['current'], 2) if sensor['current'] > 0 and sensor['current'] < 10 else round(sensor['current'], 1)
            avg = round(sensor['avg'], 2) if sensor['avg'] > 0 and sensor['avg'] < 10 else round(sensor['avg'], 1)
            min = round(sensor['min'], 2) if sensor['min'] > 0 and sensor['min'] < 10 else round(sensor['min'], 1)
            max = round(sensor['max'], 2) if sensor['max'] > 0 and sensor['max'] < 10 else round(sensor['max'], 1)

            display.tableAddValue(sensor['pos'], current, avg, min, max)

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

        sleep(5)
