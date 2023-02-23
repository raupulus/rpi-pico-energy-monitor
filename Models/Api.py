#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import urequests, gc
import json
from time import sleep

gc.enable()

class Api():
    def __init__(self, controller, sensors, url, path, token, debug=False):
        self.URL = url
        self.TOKEN = token
        self.URL_PATH = path
        self.CONTROLLER = controller
        self.SENSORS = sensors
        self.DEBUG = debug

    def upload(self, datas):
        if self.DEBUG:
            print('Api Uploading...')

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
                data=json.dumps(datas)
            )

        except Exception as e:
            if self.DEBUG:
                print('Error: ', e)

            return False
        finally:

            if self.DEBUG:
                print('Memoria antes de liberar: ', gc.mem_free())

            gc.collect()

            if self.DEBUG:
                print("Memoria después de liberar:", gc.mem_free())

        if self.DEBUG:
            print('payload: ', response.json())
            print('status code:', response.status_code)
            print('wifi status: ', self.CONTROLLER.wifiIsConnected())
