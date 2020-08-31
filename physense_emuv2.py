# Name: Charles R. Whealton
# Project: Physical Programming Emulator (Bridge)
#
# Description:  This is the bridge code that students import into their Python programs
# in order to work with the Physical Programming Simulator.  This rewrite uses a dictionary
# to keep track of states, and there are startup states already embedded in it, so this
# can have the effort of providing erroneous information if the simulator has already been
# started before the program runs and sliders have already been changed or the light sensor
# has been switched from
#
# This is based on Jason Silverstein's work (v1.0)
#
# Version       Date        Initials        Description
# 2.00          08/28/20    CRW             Initial version, get UDP client server portion going, this
#                                           code will be imported into student's programs giving them
#                                           the input / output functions required to manipulate the LED
#                                           and buzzer devices (output) and receive data from the simulator
#                                           GUI representing the temperature, humidity, and pressure sliders,
#                                           as well as the four buttons, and light sensor toggle.  These
#                                           devices have their status stored in a state dictionary that
#                                           the input function reads from.  In the case of the buttons, it
#                                           first reads the value, then sets it to zero and returns 'pressed'
#                                           if the integer value is a 1, thus evaluating to a Boolean True.
#
# 2.01          08/31/20    CRW             Removed redundant debug statement from the read_values() while True
#                                           loop.

import socket
from threading import Thread


class Sensor:

    # Class variables available to all functions

    DEBUG = False       # Set to True to aid in debugging

    host = '127.0.0.1'  # Standard loopback interface address (localhost)
    r_port = 6665       # Receive port
    s_port = 6666       # Send Port

    lookup_table = {'Button_1': 0,  # Input state table
                    'Button_2': 0,
                    'Button_3': 0,
                    'Button_4': 0,
                    'light': 0,
                    'temp': 0,
                    'humid': 0,
                    'press': 29
                    }

    def __init__(self):  # Initialization where we open sockets based on the localhost ports above
        if self.DEBUG:
            print("In emulator / bridge constructor, setting up network connections.")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # For sending

        self.r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # For receiving
        self.r.bind((self.host, self.r_port))                       # Receive from the simulator GUI

        if self.DEBUG:
            print("In emulator / bridge constructor, launching read_values() thread.")
        t1 = Thread(target=self.read_values)                        # Thread this so it is constantly reading data
        t1.daemon = True                                            # This is an attempt to cleanup the thread on exit
        t1.start()

    def output(self, device, value):  # For output, which is the four LED devices and the sound device
        if self.DEBUG:
            print("Inside output() function with values of {} and {}.".format(device, value))
        message_to_send = device + ' ' + value
        self.r.sendto(message_to_send.encode('utf-8'), (self.host, self.s_port))

    def input(self, device):  # For input, but if a button, get the value, set it to 0 as read, send it, otherwise send
        if self.DEBUG:
            print("Inside input() function with {}".format(device))
        if device in {'Button_1', 'Button_2', 'Button_3', 'Button_4'}:
            button_value = self.lookup_table[device]     # First get button value
            self.lookup_table[device] = 0                # Then set it to not pressed
            if button_value:
                return 'pressed'
            else:
                return button_value
        else:
            return self.lookup_table[device]             # Otherwise, return the value

    def read_values(self):  # Get the data here and add it directly to our dictionary, works good but needs background
        if self.DEBUG:
            print("Waiting for data...")
        while True:
            data, addr = self.r.recvfrom(1024)  # buffer size, see if we can shrink
            data = str(data)
            data = data.strip('b')
            data = data.strip("\'")
            data = data.strip("\'")
            data = list(data.split(" "))
            self.lookup_table[data[0]] = int(data[1])

            if self.DEBUG:
                print("\nReceived UDP data of {} from IP address {}, port {}.".format(data, addr[0], addr[1]))
                print(self.lookup_table)
