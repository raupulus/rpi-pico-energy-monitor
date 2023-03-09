#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from time import time
from time import sleep_ms
from Library.ST7735_Small import ST7735
from machine import Pin
from math import floor

class DisplayST7735_128x160():
    TIME_TO_OFF = 10  # Tiempo en minutos para apagar la pantalla
    DISPLAY_ORIENTATION = 3  # Orientación de la pantalla
    DEBUG = False

    DELAY = 0x80

    DISPLAY_WIDTH = 160
    DISPLAY_HEIGHT = 128

    sensors_quantity = 10 # Cantida de sensores a mostrar

    locked = False

    # Colores por secciones (de más claro a más oscuro)
    COLORS = {
        'white': 0xFFFF,
        'black': 0x0000,

        # Rojos
        'red1': 0xF800,
        'red2': 0xD800,
        'red3': 0xB800,
        'red4': 0x9000,
        'red5': 0x7800,

        # Amarillos
        'yellow1': 0xFFE0,
        'yellow2': 0xEE20,
        'yellow3': 0xC618,
        'yellow4': 0x8400,
        'yellow5': 0x7C00,

        # Verdes
        'green1': 0x07E0,
        'green2': 0x06E0,
        'green3': 0x04E0,
        'green4': 0x02E0,
        'green5': 0x01E0,

        # Azules
        'blue1': 0x001F,
        'blue2': 0x003F,
        'blue3': 0x005F,
        'blue4': 0x007F,
        'blue5': 0x009F,

        # Rosas
        'pink1': 0xFC9F,
        'pink2': 0xF81F,
        'pink3': 0xD69A,
        'pink4': 0xBDF7,
        'pink5': 0xA953,

        # Grises
        'gray1': 0x7BEF,
        'gray2': 0x739C,
        'gray3': 0x6318,
        'gray4': 0x4A49,
        'gray5': 0x2104,

        'orange1': 0xFD60,
        'orange2': 0xFD20,
        'orange3': 0xFB80,
        'orange4': 0xFAE0,
        'orange5': 0xFA60
    }

    # TODO: Añadir más fuentes y controlar bloques para no solapar, hacer grid almacenado
    FONTS = {
        'normal': {
            'h': 7,  # Alto de la letra
            'w': 5,  # Ancho de la letra
            'font': 'font5x7.fnt',  # Fuente
            'line_height': 9,  # Alto de la línea
            'font_padding': 1  # Espacio entre carácteres
        },
    }

    def __init__(self, spi, rst=9, ce=13, dc=12, offset=0, c_mode='RGB', btn_display_on=None, orientation=3, timeout=10, debug=False, color=0, background=0x000):
        self.display = ST7735(spi, rst, ce, dc, offset, c_mode, color=color, background=background)
        self.display.set_rotation(orientation)

        # Estado inicial de la pantalla
        self.reset()

        # Tiempo en el que se encendió la pantalla por primera vez
        self.display_on_at = time()
        self.display_on = True  # Indica si la pantalla está encendida o apagada
        self.DEBUG = debug

        self.DISPLAY_ORIENTATION = orientation
        self.TIME_TO_OFF = timeout

        if self.DISPLAY_ORIENTATION == 1:
            self.DISPLAY_WIDTH = 160
            self.DISPLAY_HEIGHT = 128
        elif self.DISPLAY_ORIENTATION == 2:
            self.DISPLAY_WIDTH = 128
            self.DISPLAY_HEIGHT = 160
        elif self.DISPLAY_ORIENTATION == 3:
            self.DISPLAY_WIDTH = 160
            self.DISPLAY_HEIGHT = 128
        elif self.DISPLAY_ORIENTATION == 4:
            self.DISPLAY_WIDTH = 128
            self.DISPLAY_HEIGHT = 160

        if (btn_display_on is not None):
            self.btn_display_on = Pin(btn_display_on, Pin.IN, Pin.PULL_DOWN)

            sleep_ms(100)

    def reset(self):
        """
        Prepara el estado inicial de la pantalla.
        """

        while self.locked:
            sleep_ms(10)

        self.locked = True

        self.display.reset()
        self.display.begin()
        self.display.set_rotation(self.DISPLAY_ORIENTATION)

        self.locked = False

        self.cleanDisplay()

    def cleanDisplay(self):

        while self.locked:
            sleep_ms(10)

        try:
            self.locked = True

            black = self.COLORS['black']
            self.display._bground = black
            self.display.set_rotation(self.DISPLAY_ORIENTATION)
            self.display.fill_screen(black)
            self.display.draw_block(0, 0, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT, black)
        except Exception as e:
            if self.DEBUG:
                print('Error en cleanDisplay(): {}'.format(e))
        finally:
            self.locked = False

    def loop(self):
        """
        Mientras la pantalla esté encendida, comprobar si se apaga cada 10 segundos
        """

        diffSeconds = time() - self.display_on_at
        diffMinutes = diffSeconds / 60

        if diffMinutes > self.TIME_TO_OFF and self.display_on:
            self.display_on = False

            # TODO: Apagar la pantalla, LED de pantalla debería ser controlado por un GPIO

            self.cleanDisplay()

        elif not self.display_on:
            self.callbackDisplayOn()

    def callbackDisplayOn(self):
        """
        Callback para encender la pantalla, se dispara al pulsar el botón de encendido
        """
        if self.btn_display_on.value() == 1:
            while self.locked:
                if self.DEBUG:
                    print('Esperando a que se desbloquee la pantalla en callbackDisplayOn()')

                sleep_ms(10)

            try:
                #self.reset()
                # TODO: Encender backlight de la pantalla
                self.reset()
                self.display_on = True
                self.display_on_at = time()

                self.displayHeadInfo(0, 0)
                self.displayFooterInfo()
                self.tableCreate(self.sensors_quantity)
            except Exception as e:
                if self.DEBUG:
                    print('Error al encender la pantalla: {}'.format(e))
            finally:
                self.locked = False

    def printChar(self, x, y, ch, color, bg_color):
        if not self.display_on:
            return

        while self.locked:
            if self.DEBUG:
                print('Esperando a que se desbloquee la pantalla en printChar()')

            sleep_ms(10)

        try:
            self.locked = True

            font = self.FONTS['normal']  ## Fuente
            font_height = font['h']  # Alto de la letra
            font_width = font['w']  # Ancho de la letra
            font_padding = font['font_padding']

            fp = (ord(ch)-0x20) * font_width
            f = open(font['font'], 'rb')
            f.seek(fp)
            b = f.read(font_width)
            char_buf = bytearray(b)
            char_buf.append(0)

            font_height_padding = font_height + font_padding
            font_width_padding = font_width + font_padding

            # Creo la imagen del carácter teniendo en cuenta padding
            char_image = bytearray()
            for bit in range(font_height_padding):
                for c in range(font_width_padding):
                    if ((char_buf[c] >> bit) & 1) > 0:
                        char_image.append(color >> font_height_padding)
                        char_image.append(color & 0xff)
                    else:
                        char_image.append(bg_color >> font_height_padding)
                        char_image.append(bg_color & 0xff)

            self.display.draw_bmp(x, y, font_width_padding, font_height_padding, char_image)
        except Exception as e:
            if self.DEBUG:
                print('Error en printChar(): {}'.format(e))
        finally:
            self.locked = False

    def printByPos(self, line, pos, content, length = None, color = 0xFFE0, background = 0x0000):
        """
        Imprime contenido en una posición determinada borrando previamente el contenido si recibe longitud

        line: integer, línea en eje vertical dónde se imprimirá el contenido
        pos: integer, posición en eje horizontal dónde se imprimirá el contenido
        content: string, contenido a dibujar
        length: integer, longitud del contenido a borrar (cantidad de carácteres). Esto es para no dejar residuos de contenido anterior
        """

        font = self.FONTS['normal']  ## Fuente
        font_width = font['w']  # Ancho de la letra

        # Espacio entre carácteres teniendo en cuenta el paddding
        font_total_width = font_width + (font['font_padding'] * 2)
        line_height = font['line_height']  # Altura dónde inicia cada línea

        # Cantidad máxima de carácteres en la línea
        max_line_chars = floor(self.DISPLAY_WIDTH / (font_width + font['font_padding']))

        content = str(content)

        if len(content) > max_line_chars:
            content = content[0:max_line_chars]

        pixels_x = pos * font_total_width # Posición en eje horizontal para iniciar a dibujar
        pixels_y = line * line_height # Posición en eje vertical para iniciar a dibujar

        # Si recibo la longitud, borro el contenido previo
        if length:
            clean_length_width = int(length) * font_total_width

            self.display.draw_block(pixels_x, pixels_y, clean_length_width, line_height, background)

        pixels_x_counter = pixels_x

        for ch in (content):
            self.printChar(pixels_x_counter, pixels_y, ch, color, background)
            pixels_x_counter += font_width + font['font_padding']


    def displayHeadInfo(self, wifi_status, voltage):
        """
        La primera fila de la pantalla será para mostrar información del estado en general. Esta información contempla:
        - Estado de la conexión wifi
        - Estado de la subida de datos a la API
        - ¿Título o logotipo?
        """

        while self.locked:
            if self.DEBUG:
                print('Esperando a que se desbloquee la pantalla en displayHeadInfo()')

            sleep_ms(10)

        font = self.FONTS['normal']  ## Fuente
        font_width = font['w']  # Ancho de la letra
        font_total_width = font_width + (font['font_padding'] * 2)

        # Cantidad máxima de carácteres en la línea
        max_line_chars = floor(self.DISPLAY_WIDTH / font_total_width)

        color = self.COLORS['yellow1']
        background = self.COLORS['red3']

        ## Dibujar fondo de dos líneas
        self.display.draw_block(0, 0, self.DISPLAY_WIDTH, font['line_height'] * 2, background)

        """
        INFORMACIÓN DEL VOLTAJE
        """
        block_voltaje_width = 8 # Ancho del bloque carácteres para la información del voltaje

        voltage_content = str(round(voltage, 2)) + 'V'

        self.printByPos(0, 0, voltage_content, block_voltaje_width, color, background)

        """
        INFORMACIÓN DEL WIFI
        """
        block_wireless_width = 9 # Ancho del bloque carácteres para la información del wifi

        # Posición del comienzo para el estado del wifi. Calculado desde la derecha de la pantalla
        pos_wireless_start = max_line_chars - block_wireless_width
        wifi_on = 'ON' if wifi_status >= 3 else 'OFF'
        content = '   W: ' + wifi_on # W: ON | W: OFF

        self.printByPos(0, pos_wireless_start, content, block_wireless_width, color, background)


        """
        INFORMACIÓN EN EL CENTRO
        """
        center_content = '     RASPBERRY PI PICO'
        start_x = floor((max_line_chars/2) - (len(center_content) / 2))

        self.printByPos(1, start_x, center_content, len(center_content), color, background)

    def displayFooterInfo(self, center = None):

        while self.locked:
            if self.DEBUG:
                print('Esperando a que se desbloquee la pantalla en displayFooterInfo()')

            sleep_ms(10)

        font = self.FONTS['normal']  ## Fuente
        font_width = font['w']  # Ancho de la letra
        font_total_width = font_width + font['font_padding']

        # Cantidad máxima de carácteres en la línea
        max_line_chars = floor(self.DISPLAY_WIDTH / font_total_width)

        """
        INFORMACIÓN EN EL CENTRO
        """

        if not center:
            center_content = 'MONITOR DE ENERGIA'

        ## TODO: Usar sensor RTC para obtener timestamps?
        #time_content = '07/11/2023 16:31:14'
        center_content = 'MONITOR DE ENERGIA'

        start_x = floor((max_line_chars/2) - (len(center_content) / 2))

        line = floor((self.DISPLAY_HEIGHT / font['line_height']) - 1)

        color = self.COLORS['black']
        background = self.COLORS['white']

        try:
            # TODO: Extraer el "draw_block" a un método de esta clase
            self.locked = True
            self.display.draw_block(0, line * font['line_height'], self.DISPLAY_WIDTH, font['line_height'], background)

        except Exception as e:
            if self.DEBUG:
                print('Error al dibujar el bloque de información en el footer: ' + str(e))
        finally:
            self.locked = False

        self.printByPos(line, start_x, center_content, len(center_content), color, background)

    def tableCreate(self, sensorsQuantity = None, demo = False):
        """
        sensorsQuantity: integer, cantidad de sensores para la tabla
        """

        while self.locked:
            if self.DEBUG:
                print('Esperando a que se desbloquee la pantalla en tableCreate()')

            sleep_ms(10)

        if sensorsQuantity:
            self.sensors_quantity = sensorsQuantity
        else:
            sensorsQuantity = self.sensors_quantity

        font = self.FONTS['normal']  ## Fuente
        font_width = font['w']  # Ancho de la letra

        # Cantidad máxima de carácteres en la línea
        max_line_chars = floor(self.DISPLAY_WIDTH / (font_width + font['font_padding']))

        # Colores
        colors = self.COLORS
        color_th = colors['white']
        color_th_bg = colors['blue4']
        color_separator = colors['yellow1']

        # Cabecera con los nombres de las columnas
        self.printByPos(2, 0, '     Ic    Avg   Min   Max', max_line_chars, color=color_th, background=color_th_bg)

        """
        Dibujo de la línea de separación, 2 píxeles de alto al final del bloque
        """
        self.display.draw_block(0, (font['line_height'] * 2) - 2, self.DISPLAY_WIDTH, 2, color_separator)

        current_line = 3
        iterations = sensorsQuantity if sensorsQuantity <= 10 else 10

        while iterations:
            title = 'I' + str((sensorsQuantity - iterations) + 1)

            if (iterations < 10):
                title += ' '

            if current_line % 2 == 0:
                color = colors['yellow1'] #0xFFE0
                background = colors['gray5'] #0x0000
            else:
                color = colors['yellow1'] #0xFFE0
                background = colors['black'] #0x0000

            self.printByPos(current_line, 0, title, max_line_chars, color=color, background=background)

            current_line += 1
            iterations -= 1

        if demo:
            for self.sensors_quantity in range(1, 11):
                self.tableAddValue(self.sensors_quantity, 0.00, 0.00, 0.00, 0.00)


    def tableAddValue(self, pos, current, avg, min, max):
        """
        pos: posición que ocupa el sensor, en el array de datos se establece
        value: float de una posición (3 carácteres, ej: 1.2)
        """

        if pos > 10:
            return

        line = int(pos) + 2 # Número de línea en vertical dónde comenzamos, saltamos la cabecera

        block_char_size = 5 # Cantidad de carácteres que ocupa un bloque
        margin_chars_left = 4 # Margen izquierdo para comenzar a dibujar los bloques

        colors = self.COLORS

        if line % 2 == 0:
            color = colors['green1'] #0x07E0
            background = colors['gray5'] #0x0000
        else:
            color = colors['green1']
            background = colors['black']

        self.printByPos(line, margin_chars_left, current, block_char_size, color=color, background=background)
        self.printByPos(line, margin_chars_left + block_char_size, avg, block_char_size, color=color, background=background)
        self.printByPos(line, margin_chars_left + (block_char_size * 2), min, block_char_size, color=color, background=background)
        self.printByPos(line, margin_chars_left + (block_char_size * 3), max, block_char_size, color=color, background=background)
