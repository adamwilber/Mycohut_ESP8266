from machine import Pin, I2C
import dht
import ssd1306
from time import sleep

#Sensor Pin assignment & take measurement
sensor = dht.DHT22(Pin(14))
sensor.measure()
HUMIDITY = sensor.humidity()
TEMP = sensor.temperature()

# ESP32 Pin assignment
i2c = I2C(scl=Pin(5), sda=Pin(4))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.text('MycoHut', 0, 0)
oled.text('Temp: {}'.format(TEMP), 0, 10)
oled.text('RH:  {}'.format(HUMIDITY), 0, 20)

oled.show()
