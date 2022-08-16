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

### Initializes the lists used for data logging
humidityLog = []
tempLog = []
timeLog = []
fanStatusLog = []
fogStatusLog = []
LEDStatusLog = []
UVStatusLog = []

### Initializes the booleans used for cycling the hardware as well as 
### reaching out for NTP
hasNTP = False
fogStatus = False
lightStatus = False
UVStatus = False

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

### Sets the width and height of the LCD and initializes the object
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

### Attempts to get network time, sets the flag for this to not run on every clock cycle if succcessful
def getNetworkTime():
      # Get current time from internet
  try:
    ntptime.settime()
    hasNTP = True
  except Exception as e:
    print('error setting time')

### formats the time and returns the current hour
def getTime():
  global nowseconds
  # Unpack time into variables
  year, month, day, hour, minute, second, ms, dayinyear = utime.gmtime(time.time() + time_offset)

  ### If the current hour is evenly divisible by 4 and is within the first 15 seconds of the hour,
  ### sets up for the next cycle to renew NTP
  if ( hour mod 4 == 0 ) and ( minute < 1 ) and ( second < 15 ):
    hasNTP = False

  ###print(hour,minute)  ### for testing, can remove
  ### Formatting correction for display
  if len(str(minute)) == 1:
    minute = "0" + str(minute)
  nowseconds = str(hour) + ":" + str(minute) + ":" + str(second)
  timeLog.append(nowseconds)
  return hour

### Reads information from the sensor and adds the information to the log
def readSensor():
  global temp
  global humidity
  global sensor
  sensor.measure()
  humidity = sensor.humidity()
  temp = sensor.temperature() * 1.8 + 32
  tempLog.append(temp)
  humidityLog.append(humidity)

### Cycles the fan and fog relay
def cycleHumidifier(status):
  global fog_relay
  global fan_relay
  if(status):
    fog_relay.value(0) # Turn on fog relay
    fan_relay.value(0) # Turn on fan relay
  else:
    fog_relay.value(1)  # Turn off fog relay
    fan_relay.value(1)  # Turn off fan relay

### Cycles the UV light
def cycleSanitizer(status):
  global uv_relay
  ### Turn lights on or off based on time set above
  if(status):
    uv_relay.value(0) # Turn on LED relay
  else:
    uv_relay.value(1) # Turn off LED relay

### Cycles the lighting system
def cycleLights(status):
  global led_relay
  if(status):
    led_relay.value(0)
  else:
    led_relay.value(1)

### Writes information to the LC
def writeToLCD(temp, hum, addr, time):
  ### Display info on OLED screen
  oled.fill(0)
  oled.show()
  oled.text('MycoHut', 0, 0, 16)
  oled.text('Temp: {}F'.format(temp), 0, 20)
  oled.text('RH: {}%'.format(hum), 0, 30)
  oled.text('IP: {}'.format(addr), 0, 40)
  oled.text('Time: {}'.format(time), 0, 50)
  oled.show()

### Purges the logs
### Need to dream up the logic to dump all but the last 10 or so,
### depending on the amount of memory used by the lists
def purgeLogs():
  humidityLog = []
  tempLog = []
  timeLog = []
  fanStatusLog = []
  fogStatusLog = []
  LEDStatusLog = []
  UVStatusLog = []

### Main loop
while 1 == 1:

  ### If NTP failed or is out of date, attempts the NTP pull again
  if not hasNTP:
    getNetowrkTime()

  ### Call the method to retreive the time from the system and format the output, 
  ### receives the current hour into a global variable
  hour = getTime()

  ### Call the method to read the sensor
  readSensor()

  ### Turn on and off fog relay based on humidity
  if (humidity >= set_high_hum) and not (fogStatus):
    fogStatus = True
    cycleHumidifier(fogStatus)
  if (humidity <= set_low_hum) and (fogStatus):
    fogStatus = False
    cycleHumidifier(fogStatus)

  ### Turn lights on or off based on time set above
  ### If it is after the hour to turn on the lights and before the hour to turn them off,
  ### and not already running the lights, cycles the lights on
  if (hour >= lights_on_hour) and (hour < lights_off_hour) and not (lightStatus):
    lightStatus = True
    cycleLights(lightStatus)
  ### If it is before the hour to turn on the lights and after the hour to turn them off,
  ### and already running the lights, cycles them off
  else if (hour <= lights_on_hour) and (hour > lights_off_hour) and (lightStatus):
    lightStatus = False
    cycleLights(lightStatus)

  ### Turn UV sterilizer on or off based on time set above
  ### If it is after the hour to turn on the sanitizer and before the time to turn it off,
  ### and not already running the sanitizer, cycles it on
  if (hour >= uv_on_hour) and (hour < uv_off_hour) and not (UVStatus):
    UVStatus = True
    cycleSanitizer(UVStatus)
  ### If it is before the hour to turn on the sanitizer and after the time to turn it off,
  ### and is currently running the sanitizer, cycles it off
  else if (hour <= uv_on_hour) and (hour > uv_off_hour) and (UVStatus):
    UVStatus = False
    cycleSanitizer(UVStatus)

  ### Logs the status of the fogger, lights, and sanitizer
  fogStatusLog.append(fogStatus)
  lightStatusLog.append(lightStatus)
  UVStatusLog.append(UVStatus)

  ### If the logs get longer than 50 entries, calls the purge method
  if (len(timeLog) > 50):
    purgeLogs()

  ### Calls the method to write information to the LED
  writeToLCD(temp, humidity, IP, nowseconds)

  ### Delays for 10 seconds, making the loop run six times per minute.
  ### Can be adjusted if moving the NTP to a separate bit of logic helps with latency on the controller.
  sleep(10)

