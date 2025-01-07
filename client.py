#!/usr/bin/env python3


import time
import socket
import datetime 
import screeninfo 
import json

try:
  # Python2
  import Tkinter as tk
except ImportError:
  # Python3
  import tkinter as tk

try:
  from pygame import mixer
except:
  pass

UDP_IP = ""
UDP_PORT = 5005
time_str = "0:00"

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.settimeout(1)
sock.bind((UDP_IP, UDP_PORT))
last_log = datetime.datetime.now()

anzeige_tauschen = False

try:
  mixer.init()
  sound = mixer.Sound("bing.wav")
  schnpas = mixer.Sound("schnaps.wav")
except:
  pass


def show():
  try:

    #print("hello")
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    anzeige = json.loads(data)
    print(anzeige)
    
    zeit_anzeige.config(text=f"{anzeige['minutes']}:{anzeige['seconds']}")
    global time_str
    if f"{anzeige['minutes']}:{anzeige['seconds']}" == "0:00" and time_str != "0:00":
      time_str = "0:00"
      sound.play()
      print ("bing")
    elif anzeige["schnaps"]:
      zeit_anzeige.config(text=str(anzeige["schnapszahl"])+ "!!!" )
      if not mixer.get_busy():
        schnpas.play()
    else:
      time_str = f"{anzeige['minutes']}:{anzeige['seconds']}"
    team1_anzeige.config(text=anzeige['team1'])
    team2_anzeige.config(text=anzeige['team2'])
    tore1_anzeige.config(text=anzeige['tore1'])
    tore2_anzeige.config(text=anzeige['tore2'])
    next_anzeige.config(text=anzeige['next'])
    global last_log
    last_log = datetime.datetime.now()
    root.after(10, show)
  except socket.timeout:
    zeit_anzeige.config(text="no data")
    team1_anzeige.config(text="")
    team2_anzeige.config(text="")
    tore1_anzeige.config(text="")
    tore2_anzeige.config(text="")
    next_anzeige.config(text="")
    time_str = "0:00"
    try:
      sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
      sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      sock2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
      sock2.sendto(b"Hello, I need data", ("255.255.255.255", 5006))
    except:
      pass
    
    
    root.after(10, show)
    
print("Hello")



root = tk.Tk()
mon_count=0
height=0
for m in screeninfo.get_monitors():
  print(m.x)
  print(m.y)
  print(m.width)
  print(m.height)
  height=m.height
  mon_count+=1
  mon=(str(m.width)+"x"+str(m.height)+"+"+str(m.x)+"+"+str(m.y))
  print(str(mon))
  
if mon_count==1:
  root.configure(bg='black',cursor='none')
  root.attributes("-fullscreen", True)
else: 
   root.geometry(mon)
   root.configure(bg='black',cursor='none')
   #root.attributes("-fullscreen", True)
   #root.wm_attributes('-type', 'splash')
   #root.wm_overrideredirect(True)
small=int(-0.15*height)
big=int(-0.28*height)
pad_x=int(0.03*height)
pad_y=int(0.111*height)


zeit_anzeige = tk.Label(root, font=('times', big, 'bold'), bg='black', fg='white',pady=pad_y)
zeit_anzeige.grid(row=2, column=0, columnspan=4, sticky="nesw")
zeit_anzeige.config(text="no data")
if anzeige_tauschen:
  team2_anzeige = tk.Label(root, font=('times', small, 'bold'), bg='black', fg='white',padx=pad_x,pady=1.3*pad_y)
  team2_anzeige.grid(row=0, column=0,columnspan=4, sticky="nsw")
  team1_anzeige = tk.Label(root, font=('times', small, 'bold'), bg='black', fg='white',padx=pad_x,pady=1.3*pad_y)
  team1_anzeige.grid(row=0, column=0,columnspan=4, sticky="nes")
  tore2_anzeige = tk.Label(root, font=('times', big, 'bold'), bg='black', fg='white',pady=pad_y)
  tore2_anzeige.grid(row=1, column=0,columnspan=2, sticky="nesw")
  tore1_anzeige = tk.Label(root, font=('times', big, 'bold'), bg='black', fg='white',pady=pad_y)
  tore1_anzeige.grid(row=1, column=2,columnspan=2, sticky="nesw")
else:
  
  team1_anzeige = tk.Label(root, font=('times', small, 'bold'), bg='black', fg='white',padx=pad_x,pady=1.3*pad_y)
  team1_anzeige.grid(row=0, column=0,columnspan=4, sticky="nsw")
  team2_anzeige = tk.Label(root, font=('times', small, 'bold'), bg='black', fg='white',padx=pad_x,pady=1.3*pad_y)
  team2_anzeige.grid(row=0, column=0,columnspan=4, sticky="nes")
  tore1_anzeige = tk.Label(root, font=('times', big, 'bold'), bg='black', fg='white',pady=pad_y)
  tore1_anzeige.grid(row=1, column=0,columnspan=2, sticky="nesw")
  tore2_anzeige = tk.Label(root, font=('times', big, 'bold'), bg='black', fg='white',pady=pad_y)
  tore2_anzeige.grid(row=1, column=2,columnspan=2, sticky="nesw")

next_anzeige = tk.Label(root, font=('times', small, 'bold'), bg='black', fg='grey',pady=pad_y)
next_anzeige.grid(row=3, column=0, columnspan=4, sticky="nesw")
next_anzeige.config(text="Test1 vs Test2")

for i in range (4):
  root.grid_rowconfigure(i, weight=1)
for i in range(4):
  root.grid_columnconfigure(i, weight=1)



root.after(100, show)
root.mainloop()
  
