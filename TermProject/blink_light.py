import time
from machine import Pin


def blink_light(pin, time_on, time_off):
    p = Pin(pin, mode=Pin.OUT)
    start_time = time.time()
    elapsed_time = 0
    while elapsed_time < 10:
        p.on()
        time.sleep(time_on)
        p.off()
        time.sleep(time_off)
        elapsed_time = time.time() - start_time