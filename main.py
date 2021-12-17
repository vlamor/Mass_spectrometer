#!/usr/bin/env python3
from os import times
import serial
import sys
import glob
from GUI import MainGUI
from Reader import Reader
from threading import Thread

import tkinter as tk
from tkinter import *
from tkinter import ttk 

import csv
import time


# Parameters and global variables
serial_object = None
serial_data   = '' # String with data from arduino
# Parameters
update_interval = 100 # Time (ms) between polling/animation updates
thread = None
is_UV_LED = False
is_Oven = False

def start(event,  my_gui, my_reader, port):
    #if not port:
    port = my_gui.GetPortCombobox()
    if port:
        my_gui.statusText.set("Start reading data...")
        my_reader.Connect(port)
        #if my_reader.isRun == False:
        my_reader.isRun = True
        updateGuiInThread(my_gui, my_reader)
        time.sleep(1.0) # Wait while connection is established
        my_reader.ReadData()

    print("myReader = ", my_reader, "Selected port = ", port)

def update_gui(myG, myR):
    #myG.statusText.set("Reading data...")
    while True:
        myG.value_from_MassSpectrometer.set(myR.value_from_MS)
        myG.temp_c.set(myR.temperature)
        

def updateGuiInThread(my_gui, my_reader):
    global thread
    if thread == None:
        thread = Thread(target=lambda myG = my_gui, myR = my_reader: update_gui(myG, myR))
        thread.daemon = True
        thread.start()

def stop(event, my_gui, my_reader):
    my_gui.statusText.set("Stop reading data...")
    
    #my_gui.thread.join()
    my_reader.serial_data = -0.1
    my_reader.isRun = False
    #my_reader.serial_object.close()
    
    #my_reader.thread.join()
    #global thread
    #thread.join()
    print("stop was pressed")

def exit_clicked(event, my_gui, my_reader):
    # Switching off UV_LED and OVEN
    my_reader.SendData(False, False) 
    # time.sleep(10)
    my_gui.statusText.set("Exiting...")
    
    #my_gui.thread.join()
    my_reader.serial_data = -0.1
    my_reader.isRun = False

def SelectPort(my_gui, my_reader):
    ports = my_reader.GetPorts()
    selectedPort =''
    if not ports: #if ports list is empty
        my_gui.SetPortsCombobox(["Please, connect device to port"])
        my_gui.statusText.set("Please, connect device to port")
    else:
        my_gui.SetPortsCombobox(ports)
        selectedPort = my_gui.GetPortCombobox()

    return selectedPort

def refresh(event, my_gui, my_reader, selected_port):
    selectedPort = SelectPort(my_gui, my_reader)

def UV_LED_clicked(event, my_gui, my_reader):
    global is_UV_LED
    global is_Oven
    is_UV_LED = not is_UV_LED

    if is_UV_LED:
        my_gui.button_UV_LED.configure(background = 'green', text="UV LED - ON", fg = "white")
    else:
        my_gui.button_UV_LED.configure(background = 'red', text="UV LED - OFF", fg = "blue")
    my_reader.SendData(is_UV_LED, is_Oven)
    pass

def Oven_clicked(event, my_gui, my_reader):
    global is_Oven
    global is_UV_LED
    is_Oven = not is_Oven

    if is_Oven:
        my_gui.button_Oven.configure(background = 'green', text="OVEN - ON", fg = "white")
    else:
        my_gui.button_Oven.configure(background = 'red', text="OVEN - OFF", fg = "blue")

    my_reader.SendData(is_UV_LED, is_Oven)
    pass

# --------------------------------------------------------------
if __name__ == "__main__":
    selectedPort =''

    root = tk.Tk()
    myReader = Reader(update_interval)
    myGUI = MainGUI(root, "Mass Spectrometer")
    
    selectedPort = SelectPort(my_gui=myGUI, my_reader=myReader)
    
    print("Selected port ", selectedPort)
    
        

    myGUI.button_start.bind('<ButtonRelease-1>', lambda event, my_gui = myGUI, my_reader=myReader, port = selectedPort: 
                            start(event, my_gui, my_reader, port))

    myGUI.button_stop.bind('<ButtonRelease-1>', lambda event, my_gui = myGUI , my_reader = myReader: 
                            stop(event, my_gui, my_reader))
    myGUI.button_refresh.bind('<ButtonRelease-1>', lambda event, my_gui = myGUI , my_reader = myReader: 
                            refresh(event, my_gui, my_reader, selected_port = selectedPort))

    myGUI.button_exit.bind('<ButtonRelease-1>', lambda event, my_gui = myGUI , my_reader = myReader: 
                            exit_clicked(event, my_gui, my_reader))     

    myGUI.button_UV_LED.bind('<ButtonRelease-1>', lambda event, my_gui = myGUI , my_reader = myReader: 
                            UV_LED_clicked(event, my_gui, my_reader))

    myGUI.button_Oven.bind('<ButtonRelease-1>', lambda event, my_gui = myGUI , my_reader = myReader: 
                            Oven_clicked(event, my_gui, my_reader))

    myGUI.MakeAnimationInThread()
    
    #updateGuiInThread(myGUI, myReader)
    
    root.mainloop()