# Name: Charles R. Whealton
# Project: Physical Programming Simulator
#
# Description:  This program simulates a small Raspberry Pi-type of unit where students can look for
# button pushes, monitor climate statistics in the form of temperature, humidity, and pressure, use
# a sensor to detect daylight or night time, and manipulate LED devices (red, yellow, green, and blue).
# It requires that students import the bridge / emulator code in order to interface with it.
#
# This is based on Jason Silverstein's work (v1.0)
#
# Version       Date        Initials        Description
# 2.00          08/28/20    CRW             Initial version, get UDP client server portion going, this
#                                           code will serve as the simulator, complete rewrite of GUI
#                                           using up to 3 levels of boxes for placement to rid this of
#                                           grid layout, added two more sliders for humidity and barometric
#                                           pressure, utilized a 4x1 waffle widget for LED devices, same
#                                           4 PushButtons, read_values() function on this and the bridge
#                                           code are both threaded now.  The sys.exit() function along with
#                                           threading as a daemon are used in an effort to more effectively
#                                           cleanup the thread after a shutdown by clicking the 'x' on teh GUI.
#
# 2.01          08/31/20    EM, CRW         Convert waffle dotty location coordinates to CONSTANTS, added
#                                           padding between buttons.  Reorganized GUI code for better grouping
#                                           and readability.  Relocated pygame mixer init to it's own function
#                                           defined as init_mixer() and called from main().
# 2.02          09/01/20    CRW             Converted PushButton widget definitions into array within for loop.
#                                           Converted slider creation to use for loop with zip for parallel iteration.
#                                           Reduced photos for light sensor (day/night) and buzzer into to 175 x 130
#                                           resolution which is the size they display in anyway in the hopes of faster
#                                           loading / switching.  Added reset_devices() function to reset all LEDS,
#                                           light sensor, and values for temperature, humidity, and pressure sliders.
#                                           Note that reset_devices() is executed from the bridge side when the
#                                           student's program begins, called from the constructor sending reset, reset.
#                                           Removed leftover console message indicating blue LED on / off. Added
#                                           try/except for read_values().
# 2.022         09/12/20    CRW             Incremental numbering update for packaging stuff on pypi test.
# 2.023         09/14/20    CRW             Path separator stuff.
# 2.024         09/14/20    CRW             Realized that JPG files are only supported if an addon library such as
#                                           PILLOW has been installed. Resized and converted JPG images to PNG for
#                                           built in support.
# 2.025         09/14/20    CRW             Yet another update trying to make pathing work on Windows and Linux, added
#                                           the os.sep parameter to stop hard coding separators.

import socket
import sys
import pygame
from guizero import App, Box, Picture, PushButton, Text, Slider, Waffle
from threading import Thread
from os import path, sep

# Global constants
DEBUG = False  # Set to True to aid in debugging

RED_LED = 0, 0
YELLOW_LED = 0, 1
GREEN_LED = 0, 2
BLUE_LED = 0, 3

# Global variables
os_sep = sep
here = path.abspath(path.dirname(__file__)) + os_sep # Allows us to get the current directory for images / buzzer sound
led_waffle = None  # Directly accessed from a function defined prior to it's creation, so no choice
climate_dials = []  # List for temperature, humidity, and pressure sliders

# Images for the light sensor, used in multiple functions
light_toggle = None
day_image = here + 'Day.png'
night_image = here + 'Night.png'

host = '127.0.0.1'  # Standard loopback interface address (localhost)
r_port = 6666  # Receive port
s_port = 6665  # Send Port

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Open a socket for communication to the bridge code


def init_mixer():
    pygame.mixer.init()
    pygame.mixer.music.load(here + 'buzzer.wav')


def led_set(device, value, led_array):  # Turns out LED devices on or off

    if DEBUG:
        print("In the led_set function, values are device {} and status {}.".format(device, value))
    if value == 'on':
        if device == 'rled':
            led_array[RED_LED].color = 'red'

        elif device == 'yled':
            led_array[YELLOW_LED].color = 'yellow'

        elif device == 'gled':
            led_array[GREEN_LED].color = 'green'

        elif device == 'bled':
            led_array[BLUE_LED].color = 'blue'

    elif value == 'off':
        if device == 'rled':
            led_array[RED_LED].color = 'black'

        elif device == 'yled':
            led_array[YELLOW_LED].color = 'black'

        elif device == 'gled':
            led_array[GREEN_LED].color = 'black'

        elif device == 'bled':
            led_array[BLUE_LED].color = 'black'


def read_values():  # Reads incoming device values from the student programs for LED and buzzer devices

    s.bind((host, r_port))

    while True:

        try:
            data, addr = s.recvfrom(1024)  # buffer size, see if we can shrink
            data = str(data)
            data = data.strip('b')
            data = data.strip("\'")
            data = data.strip("\'")
            data = list(data.split(" "))

            if data[0] in {'rled', 'yled', 'gled', 'bled'}:
                led_set(data[0], data[1], led_waffle)
            elif data[0] == 'buzz':
                pygame.mixer.music.play()
            elif data[0] == 'reset':
                reset_devices()
            if DEBUG:
                print("\nReceived UDP data of {} from IP address {}, port {}.".format(data, addr[0], addr[1]))
        except ConnectionResetError:
            print("No connection to client.")


def reset_devices():
    global light_toggle
    if DEBUG:
        print("Resetting Simulator GUI, LEDS (all=off), Light Sensor (not light), and Sliders (0, 0, 29)")
    for i in {'rled', 'yled', 'gled', 'bled'}:
        led_set(i, 'off', led_waffle)
    for i, v in zip([0, 1, 2], [0, 0, 29]):
        climate_dials[i].value = v
    light_toggle.image = night_image


def pressure_set(slider_value):
    message_to_send = 'press' + ' ' + slider_value
    s.sendto(message_to_send.encode('utf-8'), (host, s_port))


def humidity_set(slider_value):
    message_to_send = 'humid' + ' ' + slider_value
    s.sendto(message_to_send.encode('utf-8'), (host, s_port))


def temperature_set(slider_value):
    message_to_send = 'temp' + ' ' + slider_value
    s.sendto(message_to_send.encode('utf-8'), (host, s_port))


def day_night_toggle(device, light_toggle):
    if light_toggle.image == day_image:
        message_to_send = device + ' ' + '0'
        light_toggle.image = night_image
        s.sendto(message_to_send.encode('utf-8'), (host, s_port))
    else:
        message_to_send = device + ' ' + '1'
        light_toggle.image = day_image
        s.sendto(message_to_send.encode('utf-8'), (host, s_port))


def button_toggle(device):
    message_to_send = device + ' ' + '1'
    s.sendto(message_to_send.encode('utf-8'), (host, s_port))


def launch_simulator():
    global led_waffle
    global light_toggle
    global climate_dials
    button = []

    if DEBUG:
        print("In launch_simulator function...")

    simulator = App(title='Physical Programming Simulator v2.0', layout='auto', bg='tan', height=600, width=420)

    # Setup LEDs - Only incoming from student program

    upper_box = Box(simulator, border=1, height=240, width=410)
    led_box = Box(upper_box, border=1, height=240, width=200, align='left')
    Text(led_box, text='Lights', width='fill')
    led_left_box = Box(led_box, height=240, width=100, align='left')
    Text(led_left_box, text='rled', align='top', size=27, color='red')
    Text(led_left_box, text='yled', align='top', size=27, color='yellow')
    Text(led_left_box, text='gled', align='top', size=27, color='green')
    Text(led_left_box, text='bled', align='top', size=27, color='blue')
    led_right_box = Box(led_box, height=240, width=100, align='right')
    led_waffle = Waffle(led_right_box, height=4, width=1, dim=40, color='black', dotty='True')

    # Setup Buttons - Only outgoing to student program and needs timeout value / function

    button_box = Box(upper_box, border=1, height=240, width=200, align='right')
    Text(button_box, text='Push Buttons', width='fill')

    for i in range(4):
        button.append(PushButton(button_box, height=1, width=6, padx=13, pady=11, text='Button_' + str(i + 1)))
        button[i].bg = 'gray'
        button[i].update_command(button_toggle, args=['Button_' + str(i + 1)])
        Box(button_box, width=10, height=4)

    # Setup sliders for temperature in °F, humidity, and barometric pressure - Only outgoing to student program
    # Converted slider creation to use zip for parallel iteration in an effort to reduce code

    lower_box = Box(simulator, border=1, height=350, width=410)
    climate_box = Box(lower_box, border=1, height=350, width=200, align='left')
    Text(climate_box, text='Climate Statistics')
    Text(climate_box, text='    Temp °F   Humidity    Pressure', size=10)
    Text(climate_box, text='   temp        humid       press', size=10)

    # The following code creates three sliders for temperature, humidity and pressure using zip for parallel iteration

    for st, en, cmd in zip([150, 100, 31], [-50, 0, 29], [temperature_set, humidity_set, pressure_set]):
        Text(climate_box, width=1, align='left')
        climate_dials.append(Slider(climate_box, start=st, end=en, height=275, width=20,
                                    horizontal=False, align='left', command=cmd))

    misc_box = Box(lower_box, border=1, height=350, width=200, align='right')
    misc_upper_box = Box(misc_box, border=1, height=170, width=200)
    Text(misc_upper_box, text='Light Sensor (light)')
    light_toggle = PushButton(misc_upper_box, image=night_image, height=130, width=175)
    misc_lower_box = Box(misc_box, border=1, height=170, width=200)
    Text(misc_lower_box, text='Obnoxious Buzzer (buzz)')
    Picture(misc_lower_box, image=here + 'Ouch.png', height=130, width=175)
    light_toggle.update_command(day_night_toggle, args=['light', light_toggle])

    simulator.display()


def main():
    t1 = Thread(target=read_values)
    t1.daemon = True
    t1.start()
    init_mixer()
    launch_simulator()
    sys.exit()


# if __name__ == '__main__':  # Let the interpreter know to execute this main()
main()
