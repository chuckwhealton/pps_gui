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
# 2.0           08/28/20    CRW             Initial version, get UDP client server portion going, this
#                                           code will serve as the simulator, complete rewrite of GUI
#                                           using up to 3 levels of boxes for placement to rid this of
#                                           grid layout, added two more sliders for humidity and barometric
#                                           pressure, utilized a 4x1 waffle widget for LED devices, same
#                                           4 PushButtons, read_values() function on this and the bridge
#                                           code are both threaded now.  The sys.exit() function along with
#                                           threading as a daemon are used in an effort to more effectively
#                                           cleanup the thread after a shutdown by clicking the 'x' on teh GUI.

import socket
import sys
import pygame
from guizero import App, Box, Picture, PushButton, Text, Slider, Waffle
from threading import Thread
from os import path


# Global variables

DEBUG = False       # Set to True to aid in debugging
here = path.abspath(path.dirname(__file__))  # Allows us to get the current directory for images / buzzer sound
led_waffle = ""  # Directly accessed from a function defined prior to it's creation

# Images for the light sensor, used in multiple functions
day_image = here + '/Day.jpg'
night_image = here + '/Night.jpg'

host = '127.0.0.1'  # Standard loopback interface address (localhost)
r_port = 6666       # Receive port
s_port = 6665       # Send Port

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Open a socket for communication to the bridge code


def led_set(device, value):  # Turns out LED devices on or off

    if DEBUG:
        print("In the led_set function, values are device {} and status {}.".format(device, value))
    if value == 'on':
        if device == 'rled':
            led_waffle[0, 0].color = 'red'
        elif device == 'yled':
            led_waffle[0, 1].color = 'yellow'
        elif device == 'gled':
            led_waffle[0, 2].color = 'green'
        elif device == 'bled':
            led_waffle[0, 3].color = 'blue'
    elif value == 'off':
        if device == 'rled':
            led_waffle[0, 0].color = 'black'
        elif device == 'yled':
            led_waffle[0, 1].color = 'black'
        elif device == 'gled':
            led_waffle[0, 2].color = 'black'
        elif device == 'bled':
            led_waffle[0, 3].color = 'black'


def read_values():  # Reads incoming device values from the student programs for LED and buzzer devices

    s.bind((host, r_port))
    pygame.mixer.init()
    pygame.mixer.music.load(here + '/buzzer.wav')

    while True:

        data, addr = s.recvfrom(1024)  # buffer size, see if we can shrink
        data = str(data)
        data = data.strip('b')
        data = data.strip("\'")
        data = data.strip("\'")
        data = list(data.split(" "))

        if data[0] in {'rled', 'yled', 'gled', 'bled'}:
            led_set(data[0], data[1])
        elif data[0] == 'buzz':
            pygame.mixer.music.play()

        if DEBUG:
            print("\nReceived UDP data of {} from IP address {}, port {}.".format(data, addr[0], addr[1]))


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

    global day_image
    global night_image

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
    button_1 = PushButton(button_box, height=1, width=6, padx=13, pady=11, text='Button_1')
    button_2 = PushButton(button_box, height=1, width=6, padx=13, pady=11, text='Button_2')
    button_3 = PushButton(button_box, height=1, width=6, padx=13, pady=11, text='Button_3')
    button_4 = PushButton(button_box, height=1, width=6, padx=13, pady=11, text='Button_4')
    button_1.bg = 'gray'
    button_2.bg = 'gray'
    button_3.bg = 'gray'
    button_4.bg = 'gray'
    button_1.update_command(button_toggle, args=['Button_1'])
    button_2.update_command(button_toggle, args=['Button_2'])
    button_3.update_command(button_toggle, args=['Button_3'])
    button_4.update_command(button_toggle, args=['Button_4'])

    # Setup sliders for temperature in °F, humidity, and barometric pressure - Only outgoing to student program

    lower_box = Box(simulator, border=1, height=350, width=410)
    climate_box = Box(lower_box, border=1, height=350, width=200, align='left')
    Text(climate_box, text='Climate Statistics')
    Text(climate_box, text='    Temp °F   Humidity    Pressure', size=10)
    Text(climate_box, text='   temp        humid       press', size=10)
    Text(climate_box, width=1, align='left')
    temperature_slider = Slider(climate_box, start=150, end=-50, height=275, width=20, horizontal=False, align='left')
    Text(climate_box, width=1, align='left')
    humidity_slider = Slider(climate_box, start=100, end=0, height=275, width=20, horizontal=False, align='left')
    Text(climate_box, width=1, align='left')
    pressure_slider = Slider(climate_box, start=31, end=29, height=275, width=20, horizontal=False, align='left')
    temperature_slider.update_command(temperature_set)
    humidity_slider.update_command(humidity_set)
    pressure_slider.update_command(pressure_set)

    # Setup light sensor and the obnoxious buzzer - Light sensor outgoing, but buzzer is for documentation only

    misc_box = Box(lower_box, border=1, height=350, width=200, align='right')
    misc_upper_box = Box(misc_box, border=1, height=170, width=200)
    Text(misc_upper_box, text='Light Sensor (light)')
    light_toggle = PushButton(misc_upper_box, image=night_image, height=130, width=175)
    misc_lower_box = Box(misc_box, border=1, height=170, width=200)
    Text(misc_lower_box, text='Obnoxious Buzzer (buzz)')
    Picture(misc_lower_box, image='Obnoxious Sound.jpg', height=130, width=175)
    light_toggle.update_command(day_night_toggle, args=['light', light_toggle])
    simulator.display()


def main():

    t1 = Thread(target=read_values)
    t1.daemon = True
    t1.start()
    launch_simulator()
    sys.exit()


if __name__ == '__main__':  # Let the interpreter know to execute this main()
    main()
