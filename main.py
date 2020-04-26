# main.py -- put your code here!
# See https://docs.pycom.io for more information regarding library specifics

import utime
import pycom
import machine

from pycoproc import Pycoproc
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2, ALTITUDE, PRESSURE
from helpers import setup_rtc, connect_to_WLAN
from datapoint import DataPoint
from thingspeak import send_to_thingspeak

# Turn off that blinking!
pycom.heartbeat(False)

# Start timer
rtc = machine.RTC()
alive_timer = machine.Timer.Chrono()
alive_timer.start()

# Used to sleep between sensor readings
def tear_down(timer, initial_time_remaining):
    timer.stop()
    elapsed_ms = int(timer.read()*1000)
    timer.reset()
    time_remaining = initial_time_remaining - elapsed_ms
    print('sleeping for {}ms ({})'.format(time_remaining, utime.mktime(rtc.now())))

    # deepsleep_pin = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
    # machine.pin_deepsleep_wakeup(pins=[deepsleep_pin], mode=machine.WAKEUP_ALL_LOW, enable_pull=True)
    machine.deepsleep(time_remaining)


# Set up sensor I2C bus
class Pysense(Pycoproc):

    def __init__(self, i2c=None, sda='P22', scl='P21'):
        Pycoproc.__init__(self, i2c, sda, scl)


# Initialize sensors
py = Pysense()
mp = MPL3115A2(py,mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
si = SI7006A20(py)
lt = LTR329ALS01(py)
li = LIS2HH12(py)

# Connect to WiFi
connect_to_WLAN()

# Setup up clock (after WiFI, we use NTP), above call is blocking
setup_rtc()

temp_mp = mp.temperature()
altitude = mp.altitude()
mpp = MPL3115A2(py, mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
pressure = mpp.pressure()
print("MPL3115A2 temperature: " + str(temp_mp))
print("Altitude: " + str(altitude))
print("Pressure: " + str(pressure))

temp_si = si.temperature()
humidity = si.humidity()
dewpoint = si.dew_point()
humid_ambient = si.humid_ambient(temp_si)
print("Temperature: " + str(temp_si)+ " deg C and Relative Humidity: " + str(humidity) + " %RH")
print("Dew point: "+ str(dewpoint) + " C")
print("Humidity Ambient for " + str(temp_si) + " C is " + str() + " %RH")

light = lt.light()
print("Light (channel Blue lux, channel Red lux): " + str(light[0]/2. + light[1]/2.))

print("Acceleration: " + str(li.acceleration()))
print("Roll: " + str(li.roll()))
print("Pitch: " + str(li.pitch()))

print("Battery voltage: " + str(py.read_battery_voltage()))

print("\nSending data to ThingSpeak...")
time_alive = alive_timer.read_ms()
timestamp = utime.time()

datapoint = DataPoint(timestamp=timestamp, 
                      temp_mp=temp_mp, 
                      temp_si=temp_si,
                      humidity=humidity,
                      altitude=altitude,
                      pressure=pressure,
                      dewpoint=dewpoint,
                      light=light[0]/2. + light[1]/2.)

send_to_thingspeak(datapoint)

print("done!\n")

# Go to sleep, 10 minutes minus 10 seconds
tear_down(alive_timer, 590*1000)
