import utime
import machine
import pycom
from network import WLAN
from keychain1 import *

__all__ = ['connect_to_WLAN',
           'setup_rtc',
           ]

retries = 5

def connect_to_WLAN():
    wlan = WLAN(mode=WLAN.STA)
    if not wlan.isconnected():
        wlan = __connect_to_WLAN(wlan, wifi_ssid, wifi_pw)
    return wlan


def __connect_to_WLAN(wlan, ssid, passkey):
    tries = 1
    while not wlan.isconnected():
        try:
            wlan.connect(wifi_ssid, auth=(WLAN.WPA2, wifi_pw), timeout=10000)
            utime.sleep_ms(500)
        except TimeoutError:
            print('Failed WiFi connection attempt #{}, reattempting...')
            utime.sleep_ms(500)
    print('WLAN connection succeeded!\n')
    return wlan


def setup_rtc():
    rtc = machine.RTC()
    rtc.ntp_sync("pool.ntp.org")
    while not rtc.synced():
        utime.sleep_ms(100)
    utime.timezone(-25200)  # GMT-7, Arizona (no DST)
    print('Clock synced, current time {}.\n'.format(utime.time()))


def flash_led(color, n=1):
    for _ in range(n):
        pycom.rgbled(color)
        utime.sleep_ms(20)
        pycom.rgbled(0x000000)
        if n != 1:
            utime.sleep_ms(200)
