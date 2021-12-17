#!/usr/bin/env python3
from typing import Type
import serial
from serial.tools import list_ports

from threading import Thread
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk 

import csv
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
plt.style.use('seaborn-pastel')

from pandas import DataFrame
import collections

class MainGUI():
    def __init__(self, master, myTitle) -> None:
        global df1, df2, df3
        #Thread.__init__(self)
        # Variables for holding temperature data
        self.temp_c = tk.DoubleVar()
        self.value_from_MassSpectrometer = tk.DoubleVar() # updated in main function update_gui
        self.statusText = tk.StringVar()
        self.statusText.set("Setting up")
        self.plotTimer = 0
        self.previousTimer = 0
        self.plotMaxLength = 100
        self.data = collections.deque([0] * self.plotMaxLength, maxlen = self.plotMaxLength)
        self.thread = None
        self.animation = None
        self.UV_LED = False
        self.oven   = False

        # LAYOUT
        self.master = master
        master.title(myTitle)

        # Create the main container
        self.frame = Frame(master, relief = 'groove')
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Frame with real time plot
        self.frame_canvas = Frame(self.frame, relief = 'groove')# Lay out the main container, specify that we want it to grow with window size
        #figure1 = plt.Figure(figsize=(6,5), dpi=100)
        #ax1 = figure1.add_subplot(111)
        #line1 = FigureCanvasTkAgg(figure1, self.frame_canvas)
        #line1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
        #df2 = df2[['Year','Unemployment_Rate']].groupby('Year').sum()
        #df2.plot(kind='line', legend=True, ax=ax1)
        #ax1.set_title('Year Vs. Unemployment Rate')

         #Layout of canvas
        self.frame_canvas.grid(row=0, column=3, rowspan=3,  padx=5, pady=5, sticky=tk.E)

        # PORTS
        self.label_ports         = Label(self.frame, text="Ports")
        self.lbox_ports          = ttk.Combobox(self.frame, values=[])
        self.button_refresh      = Button(self.frame, text="Refresh")

        # Layouts of ports
        self.label_ports.grid   (row=0, column=0, padx=5, pady=5)
        self.lbox_ports.grid    (row=0, column=1, padx=5, pady=5)
        self.button_refresh.grid(row=0, column=2, padx=5, pady=5)

        #

        # Labels for mass spectometer value
        self.label_text_fromMC   = Label(self.frame, text="Value from mass spectometer")
        self.label_signal_fromMS = Label(self.frame, font = ("", 30, 'bold'), textvariable=self.value_from_MassSpectrometer)
        self.label_unitMC        = Label(self.frame, text="units")
        
        # Lay out widgets for voltage from MS
        self.label_text_fromMC.grid  (row=1, column=0, padx=5, pady=5)
        self.label_signal_fromMS.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.label_unitMC.grid       (row=1, column=2, padx=5, pady=5, sticky=tk.E)

        # Labels for temperature value
        self.label_text_temperture = tk.Label(self.frame, text="Temperature in the box")
        self.label_signal_temperature = tk.Label(self.frame, textvariable=self.temp_c, font = ("", 20, 'bold'),)
        self.label_temperature_unit = tk.Label(self.frame, text="°C")

        # Lay out widgets
        self.label_text_temperture.grid(row=2, column=0, padx=5, pady=5)
        self.label_signal_temperature.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.label_temperature_unit.grid(row=2, column=2, padx=5, pady=5, sticky=tk.E)

        # Buttons
        self.button_start = tk.Button(self.frame, text="Start", command=self.Start)
        self.button_stop = tk.Button(self.frame, text="Stop", command=self.Stop)
        self.button_exit = tk.Button(self.frame, text="Exit", command=self.Exit)

        self.button_UV_LED = tk.Button(self.frame, text="UV LED - OFF", command=self.UV_LED, bg='red')

        self.button_Oven = tk.Button(self.frame, text="OVEN - OFF", command=self.Oven, bg='red')
        # Layout of buttons
        self.button_start.grid(row=4, column=0, padx=5, pady=5, sticky=tk.S)
        self.button_stop.grid(row=4, column=1, padx=5, pady=5, sticky=tk.S)
        self.button_exit.grid(row=4, column=2, padx=5, pady=5, sticky=tk.S)
        self.button_UV_LED.grid(row=3, column=0, padx=5, pady=5, sticky=tk.S)
        self.button_Oven.grid(row=3, column=1, padx=5, pady=5, sticky=tk.S)

        # Info about serial port status bar
        self.status_bar = Label(master, textvariable=self.statusText, relief=SUNKEN, anchor="w")
        self.status_bar.pack(side=BOTTOM, fill=X)
        #label_text_temperture = tk.Label(frame, text="Temperature in the box")

#-----------------------------------------------------------------------------------
    def Start(self):
        #print("Start pressed")
        #self.animation.event_source.start()
        pass

#-----------------------------------------------------------------------------------
    def Stop(self):
        self.animation.event_source.stop()
        pass

#-----------------------------------------------------------------------------------
    def Exit(self):
        self.animation.event_source.stop()
        self.master.quit()
        pass

#-----------------------------------------------------------------------------------
    def UV_LED(self):
        self.UV_LED = not self.UV_LED
        if self.UV_LED:
            self.button_UV_LED.configure(background = 'green')
        else:
            self.button_UV_LED.configure(background = 'red')

        self.button_UV_LED.update()

#-----------------------------------------------------------------------------------
    def Oven(self):
        self.oven = not self.oven

#-----------------------------------------------------------------------------------
    def SetVoltage(self, value):
        self.value_from_MassSpectrometer.set(value)
    
#-----------------------------------------------------------------------------------
    def SetPortsCombobox(self, values):
        try:
            for p in values:
                #port = str(p.device)
                if p not in self.lbox_ports['values']:
                    self.lbox_ports['values'] = (*self.lbox_ports['values'], p)
                    print(type(p))

            self.lbox_ports.current(len(self.lbox_ports['values'])-1)
            self.statusText.set("Connected to " + self.lbox_ports.get() + " port")
        except:
            self.statusText.set( "Connect device to port" )
            print("Connect device to port")
        #print("Length", len(self.lbox_ports['values']))

#-----------------------------------------------------------------------------------        
    def GetPortCombobox(self):
        return self.lbox_ports.get()

#-----------------------------------------------------------------------------------
    def GetSerialData(self, frame, ax, lines, lineValueText, lineLabel, timeText):
        color = 'tab:red'
        currentTimer = time.perf_counter()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000)     # the first reading will be erroneous
        self.previousTimer = currentTimer
        timeText.set_text('Plot Interval = ' + str(self.plotTimer) + 'ms')
        value = float(self.value_from_MassSpectrometer.get())
        self.data.append(value)    # we get the latest data point and append it to our array
        lines.set_data(range(self.plotMaxLength), self.data)
        lineValueText.set_text('[' + lineLabel + '] = ' + str(value))       

#-----------------------------------------------------------------------------------
    def MakeAnimation(self):
        # plotting starts below
        pltInterval = 50    # Period at which the plot animation updates [ms]
        xmin = 0
        xmax = 100 # maxPlotLength
        ymin = 0
        ymax = 3.5
        fig = plt.figure()
        ax = plt.axes(xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))
        ax.set_title('Arduino Analog Read')
        ax.set_xlabel("time")
        ax.set_ylabel("AnalogRead Value")

        lineLabel = 'Potentiometer Value'
        timeText = ax.text(0.50, 0.95, '', transform=ax.transAxes)
        lines = ax.plot([], [], label=lineLabel)[0]
        lineValueText = ax.text(0.50, 0.90, '', transform=ax.transAxes)

        # canvas = FigureCanvasTkAgg(fig, master=self.frame_canvas) # A tk.DrawingArea.
        # canvas_plot = canvas.get_tk_widget()
        # canvas_plot.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        

        self.animation = FuncAnimation(fig, self.GetSerialData, fargs=(ax, lines, lineValueText, lineLabel, timeText), 
                            interval=pltInterval)    # fargs has to be a tuple
        

        plt.legend(loc="upper left")
        #canvas.draw()
        plt.show()
    
    #-----------------------------------------------------------------------------------
    def MakeAnimationInThread(self):
        if self.thread == None:
            self.thread = Thread(target=self.MakeAnimation)
            self.thread.daemon = True
            self.thread.start()
