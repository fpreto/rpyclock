"""
Controls the LED Matrix MAX7219.
"""

#
# Imports
#
from daemonhttp import Config
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.legacy import text, textsize, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT, SEG7_FONT
from luma.core.render import canvas


class LedMatrix:
    def __init__(self, config: Config):
        self.config = config
        self.font = proportional(SINCLAIR_FONT)
        # Prepare SPI device
        serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(serial, cascaded=4, block_orientation=-90, rotate=0)

        # Set Initial contrast
        self.device.contrast(self.config.getint('led_intensity'))


    def display_scrolling_text(self, text):
        show_message(self.device, text, fill="white", font=self.font)


    def display_centered_text(self, output):
        with canvas(self.device) as draw:
            dw, dh = self.device.width, self.device.height
            tw, th = textsize(output, font=self.font)
            w = max((dw - tw + 1) / 2, 0)
            h = max((dh - th + 1) / 2, 0)
            text(draw, (w, h), output, fill="white", font=self.font)

