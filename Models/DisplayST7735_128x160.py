#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from time import sleep
from time import time
from Library.ST7735 import ST7735
from machine import Pin
import _thread


class DisplayST7735_128x160():
    TIME_TO_OFF = 10  # Tiempo en minutos para apagar la pantalla

    # TODO: dinamizar letras y añadir más
    fonts = {
        'small': {
            'h': 7,  # Alto de la letra
            'w': 5,  # Ancho de la letra
            'font': 'font5x7.fnt'  # Fuente
        },
        'medium': {
            'h': 7,
            'w': 5,
            'font': 'font5x7.fnt'
        },
        'big': {
            'h': 7,
            'w': 5,
            'font': 'font5x7.fnt'
        }
    }

    def __init__(self, spi, rst=9, ce=13, dc=12, offset=0, c_mode='RGB', btn_display_on=None):
        self.display = ST7735(spi, rst, ce, dc, offset, c_mode)

        # Estado inicial de la pantalla
        self.reset()

        # Tiempo en el que se encendió la pantalla por primera vez
        self.display_on_at = time()
        self.display_on = True  # Indica si la pantalla está encendida o apagada

        if (btn_display_on is not None):
            sleep(1)
            self.btn_display_on = Pin(btn_display_on, Pin.IN, Pin.PULL_DOWN)

            sleep(0.5)

            # Deja en un hilo independiente el control de la pantalla
            _thread.start_new_thread(self.loop, ())

        # ST7735.ST7735_TFTHEIGHT = 160 # Establece la altura de la pantalla

    def reset(self):
        """
        Prepara el estado inicial de la pantalla.
        """

        self.display.reset()

        sleep(0.2)

        self.display.begin()

        sleep(0.2)

        self.display.set_rotation(3)

        sleep(0.2)

        self.display._bground = 0x0000
        self.display.fill_screen(self.display._bground)

        sleep(0.2)

        self.cleanDisplay()

    def cleanDisplay(self):
        sleep(0.2)
        self.display.fill_screen(self.display._bground)
        sleep(0.2)

        height = self.display._height  # Altura dónde inicia cada línea
        width = self.display._width

        print('DisplayST7735_128x160: cleanDisplay: height: ' + str(height))
        print('DisplayST7735_128x160: cleanDisplay: width: ' + str(width))

        self.display.draw_block(0, 0, width, height, self.display._bground)
        sleep(0.2)

    def loop(self):
        """
        Mientras la pantalla esté encendida, comprobar si se apaga cada 10 segundos
        """

        print('DisplayST7735_128x160: loop')

        while True:
            diffSeconds = time() - self.display_on_at
            diffMinutes = diffSeconds / 60

            print('DisplayST7735_128x160: loop: diffMinutes: ' + str(diffMinutes))

            if diffMinutes > self.TIME_TO_OFF:
                print('Entro en apagar la pantalla')

                self.display_on = False

                sleep(0.2)

                self.reset()

                sleep(1)

                # TODO: Apagar la pantalla, LED de pantalla debería ser controlado por un GPIO

                self.callbackDisplayOn()
            else:
                print('No apago la pantalla. Tiempo restante: ',
                      self.TIME_TO_OFF - diffMinutes)

                sleep(10)

    def callbackDisplayOn(self):
        """
        Callback para encender la pantalla, se dispara al pulsar el botón de encendido
        """
        while True:
            if self.btn_display_on.value() == 1:
                self.reset()
                self.display_on = True
                self.display_on_at = time()
                break

    def printStat(self, line, title, value, unity):
        """
        Imprime las estadísticas por la pantalla
        @param line: Línea donde se imprime
        @param title: Título de la estadística
        @param value: Valor de la estadística
        @param unity: Unidad de la estadística
        """

        self.display.set_rotation(3)

        line_size = 10  # Altura dónde inicia cada línea

        y = line * line_size  # Posición de inicio
        x = 5

        # Limpio a partir del título
        allLength = len(title) + len(str(value)) + len(unity)
        self.display.draw_block(len(title) * 6, y, allLength - len(title),
                                line_size, self.display._bground)

        # Muestro título
        self.display._color = 0xF800
        self.display.p_string(x, y, title)

        # Muestro Valor
        self.display._color = 0x07E0
        self.display.p_string(x + (len(title) * 6), y, str(value))

        # Muestro unidad de medida
        self.display._color = 0xFFE0
        self.display.p_string(
            x + ((len(title) * 6) + (len(str(value)) * 6)), y, ' ' + str(unity))

    def printMessage(self, message):
        pass

    def example(self):
        print('in display example')
        self.display.reset()
        self.display.begin()
        self.display._bground = 0x0fff
        self.display.fill_screen(self.display._bground)

        sleep(1)

        self.display.reset()
        self.display.begin()
        self.display._bground = 0x00ff
        self.display.fill_screen(self.display._bground)

        sleep(1)

        self.display.reset()
        self.display.begin()
        self.display._bground = 0x000f
        self.display.fill_screen(self.display._bground)

        sleep(1)

        self.display.reset()
        self.display.begin()
        self.display._bground = 0x0000
        self.display.fill_screen(self.display._bground)

        sleep(1)

        self.display._color = 0
        self.display.set_rotation(0)
        self.display.p_string(10, 10, 'Hello World 1')

        self.display._color = 0xf100
        self.display.set_rotation(1)
        self.display.p_string(10, 10, 'Hello World 2')

        self.display._color = 0x07e0
        self.display.set_rotation(2)
        self.display.p_string(10, 10, 'Hello World 3')

        self.display._color = 0x001f
        self.display.set_rotation(3)
        self.display.p_string(10, 10, 'Hello World 4')

        """
        sleep(1)
        x = int(self.display._width/2)
        y = int(self.display._height/2)
        r = int(min(x,y)/2)
        self.display.fill_screen(self.display.rgb_to_565(255,255,255))
        color = self.display.rgb_to_565(0,36,125)
        lcd_gfx.drawfillCircle(x,y,r,d,color)
        r = int(r*2/3)
        color = self.display.rgb_to_565(255,255,255)
        lcd_gfx.drawfillCircle(x,y,r,d,color)
        r = int(r/2)
        color = self.display.rgb_to_565(206,17,38)
        lcd_gfx.drawfillCircle(x,y,r,d,color)
        """
