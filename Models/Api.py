#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import urequests
import json
from time import sleep

class Api():
    def __init__(self, controller, sensors, url, path, token, debug=False):
        self.URL = url
        self.TOKEN = token
        self.URL_PATH = path
        self.CONTROLLER = controller
        self.SENSORS = sensors
        self.DEBUG = debug

    def upload(self, data):
        if self.CONTROLLER.wifiIsConnected() == False:
            self.CONTROLLER.wifiConnect()

        sleep(1)

        if self.CONTROLLER.wifiIsConnected() == False:
            return False

        url = self.URL
        url_path = self.URL_PATH
        full_url = url + '/' + url_path
        token = self.TOKEN

        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + str(token),
        }

        try:
            response = urequests.post(
                full_url,
                headers=headers,
                data=json.dumps(data)
            )
        except Exception as e:
            if self.DEBUG:
                print('Error: ', e)

            return False

        if self.DEBUG:
            print('payload: ', response.json())
            print('status code:', response.status_code)
            print('wifi status: ', self.CONTROLLER.wifiIsConnected())

        response.close()

        self.CONTROLLER.wifiDisconnect()

    def prepare_sensors_and_upload(self):
        """
        Une toda la información de sensores y los sube a la api en un solo lote.
        """
        sensors = self.SENSORS

        payload = []

        # TODO: Ver como preparar los datos que recibiré en la api, revisar parte para energía solar.

        #print('sensors', sensors)

        for c in sensors:
            sensor = c.get('sensor')

            ready = False

            while not ready:
                try:
                    sensor.block = True
                    ready = True
                except Exception as e:
                    print('error', e)
                    sleep(0.1)

            stats = {
                "pos": c.get('pos'),
                "max": sensor.max,
                "min": sensor.min,
                "avg": sensor.avg,
                "current": sensor.current,
            }

            print('stats', stats)


            sleep(0.1)

            payload.append(stats)

            sensor.block = False


            sensor.resetStats()

        print('antes de subir')

        self.upload(payload)


    def getDevicesInfo(self):
        """Get devices info from API"""
        pass

    def postReadings(self, readings):
        """Post readings to API"""
        pass

    def debug(self, msg):
        """Debug Api connection to console"""
        pass
