#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from machine import Pin, SPI
from time import sleep
from Library.ST7735 import ST7735
#import Library.lcd_gfx

# ST7735.ST7735_TFTHEIGHT = 160 # Establece la altura de la pantalla


class DisplayST7735_128x160():

    def __init__(self, spi, rst=9, ce=13, dc=12, offset=0, c_mode='RGB'):
        self.display = ST7735(spi, rst, ce, dc, offset, c_mode)

        self.display.reset()
        self.display.begin()
        self.display._bground = 0x0000
        self.display.fill_screen(self.display._bground)

    def printStat(self, line, title, value, unity):
        """
        Imprime estadísticas en la pantalla
        @param line: Linea donde se imprime
        @param title: Titulo de la estadística
        @param value: Valor de la estadística
        @param unity: Unidad de la estadística
        """
        self.display._color = 0x07e0
        self.display.set_rotation(3)

        line_size = 10  # Altura dónde inicia cada línea

        y = line * line_size  # Posición de inicio
        x = 5

        # TODO: poner valor y unidad de medida en otro color
        self.display.p_string(x, y, title + str(value) + unity)

    def printMessage(self, message):
        """
        Dibuja un mensaje en la pantalla.
        WIP
        """
        pass

    def example(self):
        """
        Método para probar la pantalla y depurar problemas que puedan
        encontrarse, esto solo es para pruebas y debug.
        """
        print('In display example')
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
