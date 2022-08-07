### Set grow parameters
### Humidity level at which the fogger turns on
SETLOWHUM = 61

### Humidity level at which the fogger turns off
SETHIGHHUM = 62

from machine import Pin, I2C
import dht
import ssd1306
import network
from time import sleep

### Some delay to allow aquisition of IP
sleep(10)

### Get IP address and set to variable
sta_if = network.WLAN(network.STA_IF)
IP = sta_if.ifconfig()[0]

### Sensor Pin assignment
sensor = dht.DHT22(Pin(14))

### Fog relay pin assignment
FOGRELAY = Pin(3, Pin.OUT)

### Fan relay pin assignment
FANRELAY = Pin(15, Pin.OUT)

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
  ### Turn on and off fog relay based on humidity
  if HUMIDITY >= SETHIGHHUM:
    FOGRELAY.value(0)  #Turn on fog relay
    FANRELAY.value(0)  # Turn on fan relay
  if HUMIDITY <= SETLOWHUM:
    FOGRELAY.value(1) #Turn off fog relay
    FANRELAY.value(1) # Turn off fan relay
  oled.fill(0)
  oled.show()
  oled.text('MycoHut', 0, 0, 16)
  oled.text('Temp: {}F'.format(TEMP), 0, 20)
  oled.text('RH: {}%'.format(HUMIDITY), 0, 30)
  oled.text('IP: {}'.format(IP), 0, 40)
  oled.show()
  sleep(10)

