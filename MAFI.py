import threading
from tkinter import *
import tkinter.messagebox
import customtkinter 
import serial
import time
import serial.tools.list_ports
import os
import sys
import ctypes
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import datetime as dt
import csv
from pathlib import Path

app = customtkinter.CTk()

downloads_path = str(Path.home() / "Downloads")
#plt.style.use('_mpl-gallery')
#dataListp = []
class State:
    def __init__(self, Buttontext, connected, message, console, command, active):
        self.Buttontext = Buttontext
        self.connected = connected
        self.message = message
        self.console = console 
        self.command = command
        self.active = active

def on_closing(event=0):
    closed = True
    app.destroy()  
    return closed 
  
###################################################################################################
#====================================== GUI Dynamics =============================================#
###################################################################################################

#--------------------------------- Button Initialization -----------------------------------------#
IPX34text = "IPX3&4"  
IPX5Text = "IPX5"
IPX1Text = "IPX1"
IPX2Text = "IPX2"

def IPX34TestSelected():
    IPX34selected = True
    app.messageConsole.get() 
    app.messageConsole.delete(0, END)
    app.messageConsole.insert(0, buttonIPX34.console)
    app.buttonStart.configure(command = startTest34)
    app.messageCenter.configure(text = "IPX3 and IPX4: 10 liters/min")
    return IPX34selected 

def IPX5TestSelected():
    IPX5selected = True
    app.messageConsole.get() 
    app.messageConsole.delete(0, END)
    app.messageConsole.insert(0, "IPX5 test selected")
    app.buttonStart.configure(command = startTest34)
    app.messageCenter.configure(text = "IPX5: 12.5 liters/min")
    return IPX5selected 

def change_appearance_mode(new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)
    
def change_screen_size(new_screen_size):
    if new_screen_size == 'Fullscreen':
        app.attributes('-fullscreen', True)
    else:
        app.attributes('-fullscreen', False)

def button_event():
    print("Button pressed")
       
def nullState():
    app.messageConsole.get() 
    app.messageConsole.delete(0, END)
    app.messageConsole.insert(0, "ERROR: Please select a test from the menu")
    
###################################################################################################
#================================== arduino connection ===========================================#
###################################################################################################

# Restart Function
def restart():
    os.execl(sys.executable, 'python', __file__, *sys.argv[1:])
    
# Get ports 
def get_ports():
    ports = serial.tools.list_ports.comports()
    return ports

# Find the Arduino
def findArduino(portsFound):
    commPort = 'None'
    numConnection = len(portsFound)
        
    for i in range(0, numConnection):
        port = portsFound[i]
        strPort = str(port)
        
        if 'Arduino' in strPort:
            splitPort = strPort.split(' ')
            commPort = (splitPort[0])
    return commPort

# Connect to Arduino if found in ports
foundPorts = get_ports()
connectPort = findArduino(foundPorts)
#connectPort = 'None' # Troubleshooting code
if connectPort != 'None':
    ser = serial.Serial(connectPort, baudrate = 9600, timeout = 1)
    print(f"Arduino found on {connectPort}")
    state = State("Start Test", True, "Mechanical and Fluid Ingress Test System", "Message Console", nullState, "normal")
    buttonIPX34 = State(IPX34text, None, None, "IPX3&4 test selcected", IPX34TestSelected, "normal")
    buttonIPX5 = State("IPX5", None, None, "IPX5 test selected", IPX5TestSelected, "normal")
    buttonIPX1 = State(IPX1Text, None, None, "IPX1 test selected", IPX5TestSelected, "normal")
    buttonIPX2 = State(IPX2Text, None, None, "IPX2 test selected", IPX5TestSelected, "normal")
    buttonStopState = State("Stop", None, None, None, None, 'normal')

else:
    print("Connection Issue")
    state = State("Connect", False, "Connection to controller cannot be made.\nCheck connection and click connect.", "ERROR: Controller not connected, check USB connection.", restart, "normal")
    buttonIPX34 = State(IPX34text, None, None, "IPX3&4 test selcected", IPX34TestSelected, "disabled")
    buttonIPX5 = State(IPX5Text, None, None, "IPX5 test selected", IPX5TestSelected, "disabled")
    buttonIPX1 = State(IPX1Text, None, None, "IPX1 test selected", IPX5TestSelected, "disabled")
    buttonIPX2 = State(IPX2Text, None, None, "IPX2 test selected", IPX5TestSelected, "disabled")
    buttonStopState = State("Stop", None, None, None, None, 'disabled')

###################################################################################################
#================================== arduino commands =============================================#
###################################################################################################

def startTest34():
    try:
        global ser, serialData, stop_threads
        serialData = True
        app.buttonStop.configure(state = 'normal', fg_color='#B6412C', text_color='#FFFFFF', command=stopIPX34)
        app.buttonStart.configure(state = "disabled", text="Running..")
        app.messageConsole.get() 
        app.messageConsole.delete(0, END)
        app.messageConsole.insert(0, "IPX3&4 test is running!") 
        x.start()
    except:
        restart()
        
def stopIPX34():
    app.messageCenterData.configure(text='')
    app.buttonStart.configure(state = "normal", text="Restart")
    app.messageConsole.get() 
    app.messageConsole.delete(0, END)
    app.messageConsole.insert(0, "IPX3&4 test stopped")
    app.buttonStop.configure(state = 'normal', fg_color=None, command=stopIPX34)
    ser.close()

#with graph
def readSerialData():
    global serialData
    f = open(f'{downloads_path}/data.csv', 'a', newline ='')
    writer = csv.writer(f)
    while serialData:
        global stop_threads
        ser.write(b'B')
        data = ser.readline()
        timeStamp = dt.datetime.now().strftime('%H:%M:%S.%f')
        if len(data) > 0:
            #sensor = float(data.decode('utf8'))
            app.messageCenterData.configure(text=data)
            writer.writerow(data)
            print(data)
    f.close()    
    #with open(f'{downloads_path}/data.csv')
      

###################################################################################################
#===================================== Initialize ================================================#
###################################################################################################
# Initialize the GUI to dark mode with dark-blue theme. Find the USF logo path to be used in the window.
# initialize GUI
customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Find the USF logo icon
dirname = os.path.dirname(__file__)
os.path.join(dirname, "icons", "USFlogo.ico")
x = threading.Thread(target=readSerialData)
#-------------------------------------------------------------------------------------------------#
#------------------------------------Create Window -----------------------------------------------#
#-------------------------------------------------------------------------------------------------#
# Create an WIDTH x HEIGHT window with custome title and USF logo
WIDTH = 800
HEIGHT = 520

app.title("Mechanical and Fluid Ingress Protection Spray Test")
app.state('zoomed')
app.minsize(WIDTH, HEIGHT)
app.protocol("WM_DELETE_WINDOW", on_closing)  # call .on_closing() when app gets closed
app.iconbitmap(f"{dirname}/icons/USFlogo.ico")

#-------------------------------------------------------------------------------------------------#
#------------------------------------ Create Frames ----------------------------------------------#
#-------------------------------------------------------------------------------------------------#
# 2 frames are made. left frame to host the menu and a right frame to host messages and options

# Configure a 2x1 grid layout
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

# This is the left frame that will host the menu
app.frame_left = customtkinter.CTkFrame(master=app, 
                                        width = 180,
                                        corner_radius=2,)
app.frame_left.grid(row=0, column=0, sticky="nswe", padx=10, pady=0)

# This is the right frame that will host the messages and options
app.frame_right = customtkinter.CTkFrame(master=app)
app.frame_right.grid(row=0, column=1, sticky="nswe", padx=10, pady=0)

# Configure a 1x11 grid layout in the left frame
app.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
app.frame_left.grid_rowconfigure(4, minsize=50)   # empty row with minsize as spacing
app.frame_left.grid_rowconfigure(7, weight=1)  # empty row as spacing
app.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
app.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing


#-------------------------------------------------------------------------------------------------#
#------------------------------------ Creating items in frames -----------------------------------#
#-------------------------------------------------------------------------------------------------#
#---------------- The menu text and buttons are added to the left frame --------------------------#
#-------------------------------------------------------------------------------------------------#
# Add 'menu' into the left frame
app.label_Menu = customtkinter.CTkLabel(master=app.frame_left,
                                         text="Menu",
                                         text_font=("Roboto Medium", -16))  # font name and size in px
app.label_Menu.grid(row=1, column=0, pady=10, padx=10)

# Add IPX3&4 Test button
app.buttonIPX34 = customtkinter.CTkButton(master=app.frame_left,
                                        text=IPX34text,
                                        state = buttonIPX34.active,
                                        command=buttonIPX34.command)
app.buttonIPX34.grid(row=2, column=0, pady=10, padx=20)

# Add IPX5 Test button
app.buttonIPX5 = customtkinter.CTkButton(master=app.frame_left,
                                        text=IPX5Text,
                                        state = buttonIPX5.active,
                                        command=buttonIPX5.command)
app.buttonIPX5.grid(row=3, column=0, pady=5, padx=20)

# Add IPX1-2 Test button
app.buttonIPX1 = customtkinter.CTkButton(master=app.frame_left,
                                        text=IPX1Text,
                                        state = buttonIPX1.active,
                                        command=buttonIPX1.command)
app.buttonIPX1.grid(row=5, column=0, pady=5, padx=20)

app.buttonIPX2 = customtkinter.CTkButton(master=app.frame_left,
                                        text=IPX2Text,
                                        state = buttonIPX2.active,
                                        command=buttonIPX2.command)
app.buttonIPX2.grid(row=6, column=0, pady=5, padx=20)




#-------------------------------------------------------------------------------------------------#
#-------------------------- Configure the grid within the right frame ----------------------------#
#-------------------------------------------------------------------------------------------------#
# configure grid layout (3x7)
app.frame_right.rowconfigure((0, 1, 2, 3), weight=1)
app.frame_right.grid_rowconfigure(2, minsize=10)   # empty row with minsize as spacing
app.frame_right.rowconfigure(7, weight=10)
app.frame_right.columnconfigure((0, 1), weight=1)
app.frame_right.columnconfigure(2, weight=0)

app.frame_info = customtkinter.CTkFrame(master=app.frame_right)
app.frame_info.grid(row=0, column=0, columnspan=2, rowspan=9, pady=20, padx=20, sticky="nsew")

# ============ frame_info ============
# configure grid layout (1x1)
app.frame_info.rowconfigure(2, weight=1)
app.frame_info.columnconfigure(0, weight=1)

#Create center interface
app.messageCenter = customtkinter.CTkLabel(master=app.frame_info,
                                            text=state.message,
                                            height=80,
                                            corner_radius=6,  # <- custom corner radius
                                            fg_color=("white", "gray38"),  # <- custom tuple-color
                                            justify=tkinter.CENTER)
app.messageCenter.grid(column=0, row=0, sticky="nwe", padx=15, pady=15)

app.messageCenterData = customtkinter.CTkLabel(master=app.frame_info,
                                            text='',
                                            height=300,
                                            corner_radius=6,  # <- custom corner radius
                                            fg_color=("white", "gray38"),  # <- custom tuple-color
                                            justify=tkinter.CENTER)
app.messageCenterData.grid(column=0, row=1, sticky="nwe", padx=15, pady=4)

# Add Appearance Mode button
app.label_mode = customtkinter.CTkLabel(master=app.frame_right, text="Appearance Mode:")
app.label_mode.grid(row=0, column=2, columnspan=1, pady=0, padx=20, sticky="we")

app.optionmenu_theme = customtkinter.CTkOptionMenu(master=app.frame_right,
                                                values=["Light", "Dark", "System"],
                                                command=change_appearance_mode)
app.optionmenu_theme.grid(row=1, column=2, columnspan=1, pady=0, padx=20, sticky="we")

# Set default Appearance mode:
app.optionmenu_theme.set("Dark")

app.optionmenu_size = customtkinter.CTkOptionMenu(master=app.frame_right,
                                                values=["Windowed", "Fullscreen"],
                                                command=change_screen_size)
app.optionmenu_size.grid(row=2, column=2, columnspan=1, pady=0, padx=20, sticky="we")
app.optionmenu_size.set("Windowed")

#-------------------------------------------------------------------------------------------------#
#-------------------------- Creating inputs and message console------ ----------------------------#
#-------------------------------------------------------------------------------------------------#
#Create message console 
app.messageConsole = customtkinter.CTkEntry(master=app.frame_right,
                                    width=120,
                                    placeholder_text=state.console)
app.messageConsole.grid(row=8, column=0, columnspan=2, rowspan=2, pady=0, padx=20, sticky="we")

# Create Start Test Button
app.buttonStart = customtkinter.CTkButton(master=app.frame_right,
                                        text = state.Buttontext,
                                        border_width=2,  # <- custom border_width
                                        fg_color=None,  # <- no fg_color
                                        state = state.active,
                                        command=state.command)
app.buttonStart.grid(row=8, column=2, columnspan=1, pady=0, padx=20, sticky="we")

# Create Stop Test Button
app.buttonStop = customtkinter.CTkButton(master=app.frame_right, text=buttonStopState.Buttontext,
                                                border_width=2,  # <- custom border_width
                                                fg_color=None,  # <- no fg_color
                                                state = buttonStopState.active,
                                                command=button_event)
app.buttonStop.grid(row=9, column=2, pady=10, padx=20, sticky="n")


if __name__ == "__main__":
    app.mainloop()
        
