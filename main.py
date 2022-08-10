### Set grow parameters
### Humidity level at which the fogger turns on
SETLOWHUM = 61

### Humidity level at which the fogger turns off
SETHIGHHUM = 62

### Set time for lights to turn on.  Format is 24hr clock hhmm in GMT
LIGHTSONTIME = 0800

### Set time for lights to turn off.  Format is 24hr clock hhmm in GMT
LIGHTSOFFTIME = 2000

### Set time for UV sterilizer to turn on.  Format is 24hr clock hhmm in GMT
UVONTIME = 2000

### Set time for UV sterilizer to turn off.   Format is 24hr clock hhmm in GMT
UVOFFTIME = 2200

from machine import Pin, I2C
import dht
import ssd1306
import network
from time import sleep
import time
import ntptime
import utime

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

### LED Light relay pin assignment
LEDRELAY = Pin(13, Pin.OUT)

### UV Light realy pin assignment
UVRELAY = Pin(12, Pin.OUT)

### ESP32 Pin assignment
i2c = I2C(scl=Pin(5), sda=Pin(4))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

### Main loop
while 1 == 1:

  # Get current time from internet
  try:
    ntptime.settime()
  except:
    print('error setting time')

  # Unpack time into variables
  year, month, day, hour, minute, second, ms, dayinyear = utime.localtime()
  NOW = str(hour) + str(minute)
  NOWSECONDS = str(hour) + ":" + str(minute) + ":" + str(second)

  ### Take measurements from DHT22 sensor
  sensor.measure()
  HUMIDITY = sensor.humidity()
  TEMP = sensor.temperature()
  
  ### Convert temp to F
  TEMP = TEMP * 1.8 + 32

  ### Clear screen then display temp and humidity to OLED screen
  ### Turn on and off fog relay based on humidity
  if HUMIDITY >= SETHIGHHUM:
    FOGRELAY.value(0)  # Turn on fog relay
    FANRELAY.value(0)  # Turn on fan relay
  if HUMIDITY <= SETLOWHUM:
    FOGRELAY.value(1) # Turn off fog relay
    FANRELAY.value(1) # Turn off fan relay

  ### Turn lights on or off based on time set above
  if (int(NOW) > LIGHTSONTIME) and (int(NOW) < LIGHTSOFFTIME):
    LEDRELAY.value(0) # Turn on LED relay
  else:
    LEDRELAY.value(1) # Turn off LED relay

  ### Turn UV sterilizer on or off based on time set above
  if (int(NOW) > UVONTIME) and (int(NOW) < UVOFFTIME):
    UVRELAY.value(0) # Turn on LED relay
  else:
    UVRELAY.value(1) # Turn off LED relay


  ### Display info on OLED screen
  oled.fill(0)
  oled.show()
  oled.text('MycoHut', 0, 0, 16)
  oled.text('Temp: {}F'.format(TEMP), 0, 20)
  oled.text('RH: {}%'.format(HUMIDITY), 0, 30)
  oled.text('IP: {}'.format(IP), 0, 40)
  oled.text('Time: {}'.format(NOWSECONDS), 0, 50)
  oled.show()
  sleep(10)

