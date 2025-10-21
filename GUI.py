import numpy as np
import tkinter as Tk
### Functions
from MyFunctions import setMACD
from MyFunctions import setStoch
from MyFunctions import setMAs
from MyFunctions import setRSI
from MyFunctions import setMFI
from MyFunctions import setSymbolList
from MyFunctions import setCurrentData
from MyFunctions import setLSS
from MyFunctions import configPull
from MyFunctions import listPull
from MyFunctions import currentPull
from MyFunctions import statData


### MAIN WINDOW FUNCTIONS
### Search Stock
def searchStock(*args):
    x = custName.get()
    if x:
        symbol = symbolName.get()
        symbolName.delete(0, Tk.END)
        statData(symbol)


### Search Set List
def searchListStock():
    listVar = listPull()
    for i in range(len(listVar)):
            statData(listVar[i])


### Configure Background
def configure(event):
    canvas1.delete('all')
    w, h = event.width, event.height
    ### Background Placement
    canvas1.create_image(w / 2, h / 2, image=bImage)
    ### Button Placement
    canvas1.create_window(w / 2, h / 2 + 199, window=button1)
    ### Text Image Button Placement
    canvas1.create_window(w / 2, h / 2 - 40, window=button2)
    ### Text Box Placement
    canvas1.create_window(w / 2, h / 2 + 158, window=symbolName)
    ### Version Label Placement
    canvas1.create_window(w / 2 + 150, h / 2 + 200, window=versionLabel)


### Disable Button Without Entry Text
def disButton(*args):
    x = custName.get()
    if x:
        button1.config(state='normal')
    else:
        button1.config(state='disabled')


### Keep Button Flat When Clicked
def keepFlat(Event):
    if Event.widget is button1:
        Event.widget.config(relief=Tk.FLAT)


### MAIN WINDOW
### Start of GUI
root = Tk.Tk()
root.geometry('400x500+200+100')
### Initial Definitions
canvas1 = Tk.Canvas(root, bg='black')
bImage = Tk.PhotoImage(file='Zephyr Limit 1.4/Images/Login.gif')
buttonImage = Tk.PhotoImage(file='Zephyr Limit 1.4/Images/Button.gif')
textImage = Tk.PhotoImage(file='Zephyr Limit 1.4/Images/Text.gif')
custName = Tk.StringVar()
menu = Tk.Menu(root)
subMenu = Tk.Menu(menu)
indSetMenu = Tk.Menu(menu)
statsTF = Tk.IntVar(root)
versionLabelVal = Tk.StringVar(root, 'V 0.1')
versionLabel = Tk.Label(root, textvariable=versionLabelVal, fg='white', bg='black')

### Stats Check Box Variable From configVar
configVar = configPull()

### Title Bar
root.title('Zephyr')
root.iconbitmap('Zephyr Limit 1.4/Images/Favicon.ico')

### Background
canvas1.pack(fill=Tk.BOTH, expand=Tk.YES)
canvas1.bind('<Configure>', configure)

### Buttons
button1 = Tk.Button(root, image=buttonImage, command=searchStock, relief=Tk.FLAT, bg='black', cursor='hand2', bd=0)
button1.config(state='disabled')
button2 = Tk.Button(root, image=textImage, command=searchListStock, relief=Tk.FLAT, bg='black', cursor='hand2', bd=0)
root.bind('<Button-1>', keepFlat)

### Text Box
symbolName = Tk.Entry(root, textvariable=custName, font='bold', width=22, justify=Tk.CENTER, relief=Tk.FLAT, bd=0)
custName.trace_add('write', disButton)
root.bind('<Return>', searchStock)

### Options Menu
root.config(menu=menu)
menu.add_cascade(label='Options', menu=subMenu)
menu.add_command(label='Quit', command=root.quit)
subMenu.config(tearoff=False)
subMenu.add_command(label='Stock List', command=setSymbolList)
subMenu.add_command(label='Current Data', command=setCurrentData)
subMenu.add_command(label='LSS', command=setLSS)
subMenu.add_cascade(label='Indicator Settings', menu=indSetMenu)
indSetMenu.config(tearoff=False)
indSetMenu.add_command(label='MACD', command=setMACD)
indSetMenu.add_command(label='Stochastic', command=setStoch)
indSetMenu.add_command(label='Moving Averages', command=setMAs)
indSetMenu.add_command(label='RSI', command=setRSI)
indSetMenu.add_command(label='MFI', command=setMFI)


root.mainloop()
