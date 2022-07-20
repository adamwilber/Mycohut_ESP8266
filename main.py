import dht
import machine
sensor1 = dht.DHT22(machine.Pin(4))


while True:
  temp1 = sensor1.temperature()
  humidity1 = sensor1.humidity()
  