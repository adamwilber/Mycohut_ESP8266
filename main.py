from machine import Pin, I2C
import dht
import ssd1306
import network
from time import sleep
import time
import ntptime
import utime


### Set timezone offset
time_offset = -5
time_offset = time_offset * 60 * 60

### Set grow parameters
### humidity level at which the fogger turns on
set_low_hum = 80

### humidity level at which the fogger turns off
set_high_hum = 90

### Set time for lights to turn on.  
lights_on_hour = 9

### Set time for lights to turn off.  
lights_off_hour = 21

### Set time for UV sterilizer to turn on.  
uv_on_hour = 9

### Set time for UV sterilizer to turn off.   
uv_off_hour = 11

### Some delay to allow aquisition of IP
sleep(10)

### Get IP address and set to variable
sta_if = network.WLAN(network.STA_IF)
IP = sta_if.ifconfig()[0]

### Sensor Pin assignment
sensor = dht.DHT22(Pin(14))

### Fog relay pin assignment
fog_relay = Pin(3, Pin.OUT)

### Fan relay pin assignment
fan_relay = Pin(15, Pin.OUT)

### LED Light relay pin assignment
led_relay = Pin(13, Pin.OUT)

### UV Light realy pin assignment
uv_relay = Pin(12, Pin.OUT)

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
  except Exception as e:
    print('error setting time')

  # Unpack time into variables
  year, month, day, hour, minute, second, ms, dayinyear = utime.gmtime(time.time() + time_offset)
  print(hour,minute)  ### for testing, can remove



  # now = str(hour) + str(minute)


  ### Take measurements from DHT22 sensor
  sensor.measure()
  humidity = sensor.humidity()
  temp = sensor.temperature()

  ### Convert temp to F
  temp = temp * 1.8 + 32

  ### Clear screen then display temp and humidity to OLED screen
  ### Turn on and off fog relay based on humidity
  if humidity >= set_high_hum:
    fog_relay.value(1)  # Turn off fog relay
    fan_relay.value(1)  # Turn off fan relay
  if humidity <= set_low_hum:
    fog_relay.value(0) # Turn on fog relay
    fan_relay.value(0) # Turn on fan relay

  ### Turn lights on or off based on time set above
  if (hour >= lights_on_hour) and (hour < lights_off_hour):
    led_relay.value(0) # Turn on LED relay
  else:
    led_relay.value(1) # Turn off LED relay

  ### Turn UV sterilizer on or off based on time set above
  if (hour >= uv_on_hour) and (hour < uv_off_hour):
    uv_relay.value(0) # Turn on LED relay
  else:
    uv_relay.value(1) # Turn off LED relay

  ### Formatting correction for display
  if len(str(minute)) == 1:
    minute = "0" + str(minute)
  nowseconds = str(hour) + ":" + str(minute) + ":" + str(second)

  ### Display info on OLED screen
  oled.fill(0)
  oled.show()
  oled.text('MycoHut', 0, 0, 16)
  oled.text('Temp: {}F'.format(temp), 0, 20)
  oled.text('RH: {}%'.format(humidity), 0, 30)
  oled.text('IP: {}'.format(IP), 0, 40)
  oled.text('Time: {}'.format(nowseconds), 0, 50)
  oled.show()
  sleep(10)

