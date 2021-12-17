import serial
import sys
import glob
from serial.tools import list_ports
from threading import Thread
import csv
from datetime import datetime
from tkinter import messagebox



class Reader(): #class Reader(Thread):
    def __init__(self, update_period):
        #Thread.__init__(self)
        self.serial_object = None
        self.serial_data = -0.1
        self.filter_data = -1
        self.value_from_MS = -1
        self.temperature = -1
        self.update_period = update_period
        self.thread = None
        self.csv_file = None
        self.isRun = True
        self.ports = []
        self.avalaiblePorts = []
        self.UV_LED = -1
        self.Oven = -1
        # self.ports = list(list_ports.comports())
        # for p in self.ports:
        #     print(p, "in ", p.device)
        #https://habr.com/ru/post/443326/
        """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
        """
        
    #-----------------------------------------------------------------------------------
    def __Initialization(self):
        if sys.platform.startswith('win'):
            self.ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            self.ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            self.ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        self.avalaiblePorts = []
        for port in self.ports:
            try:
                s = serial.Serial(port)
                s.close()
                self.avalaiblePorts.append(port)
            except (OSError, serial.SerialException):
                pass
        self.csv_file =  open('data.csv', 'w')
    #-----------------------------------------------------------------------------------

    def GetData(self):
        return(12345)
    #-----------------------------------------------------------------------------------


    def GetPorts(self):
        self.__Initialization()
        return(self.avalaiblePorts)
    #-----------------------------------------------------------------------------------

    def Connect(self, port):

        try:
            self.serial_object = serial.Serial(port, 9600, timeout=self.update_period)
            print("Serial port is open " + str(self.serial_object.is_open))
        except:
            messagebox.showwarning("Warning", "Please, connect device to port \n and give permission to it by \n sudo chmod a+rw /dev/ttyACM0")
    #-----------------------------------------------------------------------------------            

    def ReadData(self):
        if self.thread == None:
            self.thread = Thread(target=self._getData)
            self.thread.daemon = True
            self.thread.start()
    #-----------------------------------------------------------------------------------

    def _getData(self):
        if self.serial_object:
            #self.serial_object.open()
            #self.serial_object.close()
            #self.serial_object.open()
            self.serial_object.flush()
            
            #with open ('data.csv', 'w') as my_csv_file:
            csv_writer = csv.writer(self.csv_file)
            while (True):
                if self.serial_object.in_waiting > 0:
                    self.serial_data = self.serial_object.readline().decode('utf-8').rstrip()
                    self.filter_data = self.serial_data.split(',')
                    self.value_from_MS = float(self.filter_data[0])
                    self.temperature = float(self.filter_data[1])
                    self.UV_LED = int(self.filter_data[2])
                    self.Oven   = int(self.filter_data[3])
                    csv_writer.writerow([datetime.now().time(), self.value_from_MS])
                    #my_csv_file.flush()
                    print(self.value_from_MS,  " Temperature ---", self.temperature, " UV_LED --- ", self.UV_LED, " OVEN --- ", self.Oven)
                if(self.isRun == False):
                    self.csv_file.close()
                    self.serial_object.close()
                    break

                    
        else:
            return 0
    #-----------------------------------------------------------------------------------
    def SendData(self, myUV_LED, my_Oven):
        stringToArduino = (str(int(myUV_LED)) + '\n' + str(int(my_Oven)) + '\n')
        '''if myUV_LED == False:
            self.serial_object.write(str(0).encode() )
        else:
            self.serial_object.write(str(1).encode() )'''
        #self.serial_object.write( b'%d%d\r\n' % myUV_LED % my_Oven)
        self.serial_object.write(stringToArduino.encode())

        pass
    #-----------------------------------------------------------------------------------