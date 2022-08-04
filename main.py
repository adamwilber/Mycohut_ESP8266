### Set grow parameters
### Humidity level at which the fogger turns on
SETLOWHUM = 75

### Humidity level at which the fogger turns off
SETHIGHHUM = 93

from machine import Pin, I2C
import dht
import ssd1306
from time import sleep

### Sensor Pin assignment
sensor = dht.DHT22(Pin(14))

### Fog relay pin assignment
FOGRELAY = Pin(3, Pin.OUT)

### ESP32 Pin assignment
i2c = I2C(scl=Pin(5), sda=Pin(4))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

### Main loop
while 1 == 1:
  ### Take measurements from DHT22 sensor
  sensor.measure()
  HUMIDITY = sensor.humidity()
  TEMP = sensor.temperature()
  
  ### Convert temp to F
  TEMP = TEMP * 1.8 + 32

  ### Clear screen then display temp and humidity to OLED screen
  ### Turn on fog relay (just for testing)
  FOGRELAY.value(0)
  oled.fill(0)
  oled.show()
  oled.text('MycoHut', 0, 0, 16)
  oled.text('Temp: {}F'.format(TEMP), 0, 20)
  oled.text('RH:  {}%'.format(HUMIDITY), 0, 30)
  oled.show()
  sleep(5)
  ###Turn off fog relay ### just for testing 
  FOGRELAY.value(1)
  sleep(3)


