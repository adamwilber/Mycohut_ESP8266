import RPi.GPIO as GPIO
import Adafruit_DHT
import mysql.connector
import datetime
import time as sleeptime

### Set variables
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
TRIG = 23
ECHO = 24
RELAY1 = 17  ### Humidity relay
RELAY2 = 27  ### Fan relay
RELAY3 = 26 ### Light Relay
waterlvl = 5  ### Test variable while ultrasonic sensor is not working
dist = 6  ### test variable - see above
i = 0  ### Increment variable

### User variables
SETHIHUM = 94  ### Humidity at which the atomizer stops
SETLOWHUM = 83  ### Humidity at which the atomizer starts
LOWH2O = 15  ### Water level to send alert

### Use GPIO numbers
GPIO.setmode(GPIO.BCM)

### Set up GPIO pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(RELAY1, GPIO.OUT)
GPIO.setup(RELAY2, GPIO.OUT)
GPIO.setup(RELAY3, GPIO.OUT)

### Set default output of GPIO pins
GPIO.output(TRIG, False)
GPIO.output(RELAY1, GPIO.LOW)
GPIO.output(RELAY2, GPIO.HIGH)
GPIO.output(RELAY3, GPIO.HIGH)

mydb = mysql.connector.connect(
    host="localhost",
    user="db_user",
    password="SQLPASSWORD",
    database="main"
)
mycursor = mydb.cursor()

while True:

    ### Figure out if the lights need to be on
    now = datetime.datetime.now() #Get current date and time
    LIGHTSON = now.replace(hour=6, minute=30, second=0)
    LIGHTSOFF = now.replace(hour=22, minute=0, second=0)
    if now > LIGHTSON:
        GPIO.output(RELAY3, GPIO.HIGH)
    if now > LIGHTSOFF:
        GPIO.output(RELAY3, GPIO.LOW)


    ### Read temp and humidity from sensor
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    ### Set temp to F
    temperature = temperature * 1.8 + 32

    ### Set atomizer relay state based on humidity level
    if int(humidity) <= SETLOWHUM:
        GPIO.output(RELAY1, GPIO.HIGH)
    if int(humidity) >= SETHIHUM:
        GPIO.output(RELAY1, GPIO.LOW)

    ### Trigger ultrasonic sensor
    # sleeptime.sleep(2)
    # GPIO.output(TRIG, True)
    # sleeptime.sleep(0.00001)
    # GPIO.output(TRIG, False)

    ### Take reading from ultrasonic sensor
    # while GPIO.input(ECHO) == 0:
    #    pulse_start = sleeptime.time()

    # while GPIO.input(ECHO) == 1:
    #    pulse_end = sleeptime.time()

    # pulse_duration = pulse_end - pulse_start

    ### Do math on distance from ultrasonic sensor to figure out % full of reservoir
    # dist = pulse_duration * 17150
    # dist = float(dist) - 1
    # dist = (26 - int(dist)) * 100
    # dist = dist / 26
    # dist = round(dist, 2)
    # dist = str(dist)
    # print ("Reservoir Level:",dist,"%")

    if humidity is not None and temperature is not None:
        time = datetime.datetime.now()
        nowdate = time.strftime("%m/%d/%Y")
        nowtime = time.strftime("%H:%M:%S")
        print("Temp={0:0.1f}*F  Humidity={1:0.1f}%".format(temperature, humidity))
        if i == 12:
            sqlstmt = "insert into main (date, time, temp, humidity, waterlvl) values (%s, %s, %s, %s, %s);"
            temperature = round(temperature, 1)
            temperature = str(temperature) + "*F"
            humidity = round(humidity, 1)
            humidity = str(humidity) + "%"
            data = (nowdate, nowtime, temperature, humidity, dist)
            mycursor.execute(sqlstmt, data)
            mydb.commit()
            i = 0
    else:
        print("Failed to retrieve data from humidity sensor")
    sleeptime.sleep(5)
    i += 1
