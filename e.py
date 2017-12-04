import os
import subprocess

import threading
import sys
import re
import signal
from IPy import IP



from subprocess import Popen, PIPE, check_output

import tkinter as tk

from time import sleep  
test = 1
T=threading.Thread
STOREOK = False
store = ""
test = ""
process = 0
#pipe = Popen(path, stdout=PIPE)
#text = pipe.communicate()[0]
#out = check_output(["ntpq", "-p"])


def create_widgets():
    global process
    #var = StringVar(master)
    #var.set("Ping Target") # initial value
    target = tk.StringVar()
    target.set("Router(dg)")
    store = tk.StringVar()
    test = tk.StringVar()
    pingnumber = tk.StringVar()
    
    testbutton = tk.Checkbutton(text="Test Backup", variable=test, onvalue="secondary", offvalue="primary",)
    testbutton.deselect()
    testbutton.grid(row=2, column=2)
    
    pingtxt = tk.Label(text="Ping Number")
    pingtxt.grid(row=0, column=2)
    
    storetxt = tk.Label(text="Store Number")
    storetxt.grid(row=0, column=1)

    ping = tk.Button(text="Start Ping", command = lambda:startasthread(lambda:startping(store.get(), test.get(), pingnumber.get(), ping, cancelping, target.get(), options, storetxt)))
    ping.grid(row=1, column=3)
    
    
    cancelping = tk.Button(text="Cancel Ping", command=lambda:killthread(cancelping, ping, store.get()))
    cancelping['state'] = 'disabled'
    cancelping.grid(row=1, column=4)
    
    options = {"Router(dg)":"dg", "Switch US(ussw010)":"ussw010", "Switch Canada(casw010)":"casw010", "Workstation(mws)":"mws", "IP address":""}
    dropdown = tk.OptionMenu(root, target, *options)
    dropdown.grid(row=1, column=0)
    
    exit = tk.Button(text="exit", fg="red", command=root.destroy)
    exit.grid(row=2, column=1)
    
    pingentry = tk.Entry(text="Number of Pings", textvariable = pingnumber)
    pingentry.grid(row=1, column=2)
    
    storeentry = tk.Entry(text="Store Number", textvariable = store)
    storeentry.grid(row=1, column=1)
    
    textdaemon = T(target = updatetext, args = [target, storetxt])
    textdaemon.setDaemon(True)
    textdaemon.start()

    def func(event):
        startasthread(lambda:startping(store.get(), test.get(), pingnumber.get(), ping, cancelping, target.get(), options, storetxt))
    root.bind('<Return>', func)

        
#def onclick(event=None):
#    startasthread(lambda:startping(store.get(), test.get(), pingnumber.get(), ping, cancelping, target.get(), options, storetxt))
    
def updatetext(button1, button2):
    while True:
        sleep(0.05)
        #print('checking text button')
        if button1.get() == "IP address":
            button2['text']="IP Address"
        if button1.get() != "IP address":
            button2['text']="Store Number"
    
def startasthread(funct):
    thread = T(target = funct)
    thread.start()

    
def killthread(buttondis, buttonen, store):
    #print("store is {}".format(store))
    storeip = IP(store)
    #print("storeip is {}".format(storeip))
    if storeip != store:
        store = store.zfill(5)
    else:
        store = storeip
    print("store is {}".format(store))
    buttondis['state'] = 'disabled'
    buttonen['state'] = 'normal'
    global process
    print("pid is {} ".format(process))
    #print(pingthread.poll())
    os.system("TASKKILL /F /PID {} /T > nul".format(process))
    #print('waiting timeout')
    openfile = open("temp{}.txt".format(store), 'r')
    openfile.close()
    os.system("del temp{}.txt".format(store))
    print("Ping ended, start a new ping when ready")



def startping(store, test, pingnumber, buttondis, buttonen, prefix, options, storetxt):
    
    prefixconverted = options[prefix]
    if prefixconverted == "":
        store = IP(store)
    buttonen['state'] = 'normal'
    buttondis['state'] = 'disabled'
    pingsize = 0
    if test == "primary":
        pingsize = "1345"
    else:
        pingsize = "4000"
    if prefixconverted == "":
        print("IP Ping:")
        
    if testpingnumber(pingnumber) == True:
        if prefixconverted != "":
            store = store.zfill(5) 
            print('Pinging {}{} with {} bytes {} times.'.format(options[prefix], store, pingsize, pingnumber))
        if prefixconverted == "":
            try:
                IP(store)
                print(IP(store))
                print('Pinging ip address {} with {} bytes {} times.'.format(IP(store), pingsize, pingnumber))
            except:
                raise
        pingnumber = int(pingnumber)
        
        pingthread = T(target = pinger, args = [store, pingnumber, test, buttondis, buttonen, prefixconverted])
        pingthread.start()

    else:
        print('Number of pings was not a number.')


def testpingnumber(pingnumber):
    if pingnumber == "":
        return False
    try:
        int(pingnumber)
        return True
    except:
        return False 


def pinger(store, num, primsec, buttondis, buttonen, prefix):
    #print(prefix)
    '''Takes a store number, index as INT, primsec as STRING sets primary or secondary test'''
    global process
    print("\n")
    
    if primsec == "primary":
        #print("ping -n {} -l 1345 {}{} > temp{}.txt".format(num, prefix, store, store))
        pingthread = Popen("ping -n {} -l 1345 {}{} > temp{}.txt".format(num, prefix, store, store), shell=True)
    if primsec == "secondary":
        #print("ping -n {} -l 4000 {}{} > temp{}.txt".format(num, prefix, store, store))
        pingthread = Popen("ping -n {} -l 4000 {}{} > temp{}.txt".format(num, prefix, store, store), shell=True)
    process = pingthread.pid  
    print(process)
    #os.system("TASKKILL /F /PID {} /T > nul".format(pingthread.pid))
    process = pingthread.pid  
    print(process)
    outputthread = T(target = printoutput, args = [pingthread, store, prefix])
    outputthread.start()
    while True:
        threadalive = bool(pingthread.poll())
        threadalive2 = bool(outputthread.is_alive())
        sleep(0.05)
        #print("pingthread is {}".format(threadalive))
        #print("outputthread is {}".format(threadalive2))
        if threadalive2 == False:
            #print("pid is {} ".format(pingthread.pid))
            #print(pingthread.poll())
            #os.system("TASKKILL /F /PID {} /T > nul".format(pingthread.pid))
            #print('waiting timeout')
            if threadalive == False:
                
                sleep(0.05)
                print("\nPing Complete. Start a new ping with the GUI.")
                buttondis['state'] = 'normal' #reenables buttons when ping completes.
                buttonen['state'] = 'disabled'
                os.system("del temp{}.txt".format(store))
                break


def printoutput(monitoredthread, store, prefix):
    
    outputstring = ""
    pingcount = 0
    sleep(1)
    while True:
        sleep(0.05)
        openfile = open("temp{}.txt".format(store), 'r')
        openstring = str(openfile.read())
        if openstring == "Ping request could not find host {}{}. Please check the name and try again.\n".format(prefix, store):
            print("Ping request could not find host {}{}. Is your prefix correct? Please start ping again when ready.\n".format(prefix, store))
            openfile.close()
            break
        len1 = len(openstring)
        len2 = len(outputstring)
        #print("len 1 is {}".format(len1))
        #print("len 2 is {}".format(len2))
        if len1 > len2:
            outputstring = openstring
            len3 = (len(outputstring.split('\n')))
            #if pingcount > 0:
                #print("{} pings sent".format(pingcount))
            outsplit = outputstring.splitlines()[len3-2]
            if outsplit[0] != " ":
                print("{} {}".format((pingcount+1), outputstring.splitlines()[len3-2]))
            if outsplit[0] == " ":
                print("{} {}".format((pingcount+1), outputstring.splitlines()[len3-7]))
                #print("{} pings sent".format(pingcount+1))
            #print(outputstring)
            pingcount = pingcount + 1
        #print("moni thread{}".format(monitoredthread.poll()))
        th1 = monitoredthread.poll()
        #print("TH1 {}".format(th1))
        if th1 != None:
            #print("monitoredthread.poll() was {}".format(monitoredthread.poll()))
            #print("lines = {}".format(len(outputstring.split('\n'))))
            print("\n")
            print(outputstring.splitlines()[len3-5])
            print(outputstring.splitlines()[len3-4])
            print(outputstring.splitlines()[len3-3])
            print(outputstring.splitlines()[len3-2])
            openfile.close()
            #print("output file closed")
            sleep(0.05)
            break
                
root = tk.Tk()
create_widgets()
root.mainloop()


