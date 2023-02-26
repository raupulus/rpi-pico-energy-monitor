
from machine import ADC, Pin
import network
from time import sleep


class RpiPico():
    INTEGRATED_TEMP_CORRECTION = 27  # Temperatura interna para corregir lecturas
    adc_voltage_correction = 0.706
    voltage_working = 3.3

    max = 0
    min = 0
    avg = 0
    current = 0
    locked = False

    # Wireless
    wifi = None

    def __init__(self, ssid=None, password=None, debug=False, country="BO"):

        self.DEBUG = debug

        self.SSID = ssid
        self.PASSWORD = password
        self.COUNTRY = country

        # Código de país para el Wireless
        #rp2.country(country)

        self.TEMP_SENSOR = ADC(4)  # Sensor interno de raspberry pi pico.

        # Definición de GPIO
        self.LED_INTEGRATED = Pin("LED", Pin.OUT)

        # 16bits factor de conversión, aunque la lectura real en raspberry pi pico es de 12bits.
        self.adc_conversion_factor = self.voltage_working / 65535

        # print('Tiene ssid y pass:', ssid and password)

        # Si recibe credenciales para conectar por wifi, se conecta al instanciar.
        if ssid and password:
            print('Comienza conexión a wireless')
            self.wifiConnect(ssid, password)

        # Realizo primera lectura de temperatura para inicializar variables y no comenzar a evaluar con 0 en estadísticas.
        sleep(0.100)
        self.resetStats()

    def resetStats(self, temp=None):
        """Reset Statistics"""

        temp = temp if temp else self.readSensorTemp()
        self.max = temp
        self.min = temp
        self.avg = temp
        self.current = temp

    def readSensorTemp(self):
        if self.locked:
            return self.current

        reading = (self.TEMP_SENSOR.read_u16() * self.adc_conversion_factor) - \
            self.adc_voltage_correction

        value = self.INTEGRATED_TEMP_CORRECTION - reading / 0.001721  # Formula given in RP2040 Datasheet

        cpu_temp = round(float(value), 1)
        self.current = cpu_temp

        # Estadísticas
        if cpu_temp > self.max:
            self.max = cpu_temp
        if cpu_temp < self.min:
            self.min = cpu_temp

        self.avg_cpu_temp = round(float((self.avg + cpu_temp) / 2), 1)

        return round(float(cpu_temp), 1)

    def getTemp(self):
        cpu_temp = self.readSensorTemp()

        return round(float(cpu_temp), 1)

    def ledOn(self):
        self.LED_INTEGRATED.on()

    def ledOff(self):
        self.LED_INTEGRATED.off()

    def getStats(self):
        """ Get Statistics formated as a dictionary"""

        return {
            'max': round(float(self.max), 1),
            'min': round(float(self.min), 1),
            'avg': round(float(self.avg), 1),
            'current': round(float(self.current), 1)
        }

    def wifiStatus(self):
        """ Get wifi status"""
        return self.wifi.status() if self.wifi else 0

    def wifiIsConnected(self):
        """ Get wifi is connected """
        return bool(self.wifi and self.wifi.isconnected and self.wifi.status() == 3)

    def wifiDebug(self):
        print('Conectado a wifi:', self.wifiIsConnected())
        print('Wifi Status:', self.wifiStatus())
        print('Wifi IP:', self.wifi.ifconfig())
        print('Canal: ', self.wifi.config('channel'))
        print('ESSID: ', self.wifi.config('essid'))
        print('TXPOWER:', self.wifi.config('txpower'))

        import ubinascii
        import network

        mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
        print(mac)

    def wifiConnect(self, ssid = None, password = None):
        """ Connect to wifi"""

        if ssid is None and self.SSID is None and self.PASSWORD is None and password is None:
            if self.DEBUG:
                print('No se ha definido credenciales para conectar a wifi')
            return False

        self.wifi = network.WLAN(network.STA_IF)
        self.wifi.active(True)

        # Desactivo el ahorro de energía.
        self.wifi.config(pm = 0xa11140)

        #self.wifi.config(txpower=20, channel=2, ssid=ssid, security=4, password=password)

        self.wifi.connect(ssid, password)

        sleep(1)

        tryConnections = 3

        while self.wifiIsConnected() == False and tryConnections > 0:
            tryConnections -= 1

            sleep(3)

            self.wifi.connect(ssid, password)

        if (self.DEBUG):
            while self.wifiIsConnected() == False:
                print('')

                sleep(3)

                self.wifi.connect(ssid, password)

                sleep(1)

                print("Waiting to connect:")
                self.wifiDebug()
                print('SSID: ', ssid)

                sleep(3)

                print(self.wifi.scan())
                sleep(3)


            print('')
            sleep(1)

            print("Waiting to connect:")
            self.wifiDebug()
            print('SSID: ', ssid)

            sleep(3)

            print(self.wifi.scan())
            sleep(3)

        return self.wifiIsConnected()

    def wifiDisconnect(self):
        """ Disconnect from wifi"""
        self.wifi.disconnect()

    def readAnalogInput(self, pin):
        """
        Read analog value from pin
        Lectura del ADC a 16 bits (12bits en raspberry pi pico, traducido a 16bits)
        """

        reading = ADC(pin).read_u16()

        #print("Lectura pin :" + str(pin))

        #readingParse = ((reading - self.adc_voltage_correction)
        #                * self.adc_conversion_factor)
        #print("Lectura pin :" + str(pin),
        #      (reading / 65535) * self.voltage_working)

        #print("Lectura parseada: " + str(readingParse))

        #print("raw: " + str(reading))
        #print("adc_voltage_correction: " + str(self.adc_voltage_correction))

        #print("voltaje: " + str(self.voltage_working -
        #                        ((reading / 65535) * self.voltage_working)))

        return self.voltage_working - ((reading / 65535) * self.voltage_working)
        # return (reading / 65535) * self.voltage_working
