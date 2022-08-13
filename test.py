import utime
import time
import network
import ntptime
ntptime.settime()
year, month, mday, hour, minute, second, weekday, yearday = utime.localtime(time.time())
print(f'{hour}')