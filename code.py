#
# Line following program
# Adafruit CircuitPython 6.2.0
# Board: Metro ESP32 S2 BETA
# Sensoren: KY-033 mit TCRT5000 (3x Digital)
# 28.06.21 - wb
# v0.2
#
import board
import time
from motor import Motor, Vehicle
from driver import Driver, Line
from sensor import *
import neopixel


max_execution_time = 0.05


# SensorArray from left to right
sensor_array = SensorArray([Sensor(board.IO9), Sensor(board.IO8), Sensor(board.IO7), Sensor(board.IO6), Sensor(board.IO5)])
vehicle = Vehicle(motor_l= Motor(io_pin_fwd= board.IO14, io_pin_bwd= board.IO13), motor_r= Motor(io_pin_fwd= board.IO15, io_pin_bwd= board.IO16))
driver = Driver(sensor_array, vehicle= vehicle, alarm_sec= max_execution_time)
timer = 0
last_second = 0

pixel_onboard = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel_onboard.brightness = 0.5

def sens_update_callback(sav: SensorArrayValue):
    driver.hard_update()
    corner = ""
    if driver.get_corner():
        corner = "corner"
    print("SENS:", sav, "{:.1f}".format(Line.get_bar_position(sav)), "\t" , "{:.0f}".format(Line.get_bar_width(sav)), corner)


while True:
    do_print = False
    if time.monotonic()-last_second > 1:
        last_second = time.monotonic()
        do_print = True
    # choose direction
    sensor_array.update(sens_update_callback)
    driver.update() #force regular updates
    vehicle.update()

    if time.monotonic() - timer > max_execution_time:
        pixel_onboard[0] = (255, 0, 0)
    else:
        pixel_onboard[0] = (0, 0, 0)
        #pixel_onboard[0] = (0, 0, 255 - math.floor(((time.monotonic() - timer)/max_execution_time)*255))

    if do_print and False:
        print("- - - - - - - - - - - - - - - - - - -")
        print("CPU: ", ((time.monotonic() - timer)/max_execution_time)*100, "%")
        print("MOT:","left: " + str(vehicle.motor_l.__target), "right: " + str(vehicle.motor_r.__target))
        for id,val in enumerate(reversed(list(map(str,sensor_array.history)))): 
            if id < 10:
                print(-id,"\t",val)
            else:
                continue
        print()

    if driver.get_corner():
        pixel_onboard[0] = (0, 128, 0)
    elif driver.sensor_array.history[-1] == SensorValue.WHITE:
        pixel_onboard[0] = (0,0,128)
    else:
        pixel_onboard[0] = (0,0,0)
    timer = time.monotonic()
    