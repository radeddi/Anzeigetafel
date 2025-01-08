#!/usr/bin/env python3

import time
import socket
import datetime
import screeninfo
import json
import tkinter as tk
from pygame import mixer

# Konfigurationsvariablen
UDP_IP = ""
UDP_PORT = 5005
DEFAULT_TIME = "0:00"

# Initialisiere UDP-Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)
sock.bind((UDP_IP, UDP_PORT))

# Sound-Konfiguration
sound_active = True
try:
    mixer.init()
    sound = mixer.Sound("bing.wav")
    schnaps_sound = mixer.Sound("schnaps.wav")
except Exception as e:
    print(f"Sound konnte nicht initialisiert werden: {e}")
    sound_active = False

# Globale Variablen
last_log = datetime.datetime.now()
time_str = DEFAULT_TIME
anzeige_tauschen = False

# Funktionen

def reconnect_socket():
    try:
        print("Reconnecting...")
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock2.sendto(b"Hello, I need data", ("255.255.255.255", 5006))
    except Exception as e:
        print(f"Fehler beim Reconnect: {e}")

def update_display(data):
    global time_str, last_log

    anzeige = json.loads(data)
    zeit_anzeige.config(text=f"{anzeige['minutes']}:{anzeige['seconds']}")

    if anzeige['minutes'] + ":" + anzeige['seconds'] == DEFAULT_TIME and time_str != DEFAULT_TIME:
        time_str = DEFAULT_TIME
        if sound_active:
            sound.play()
        print("bing")
    elif anzeige.get("schnaps"):
        zeit_anzeige.config(text=f"{anzeige['schnapszahl']}!!!")
        if sound_active and not mixer.get_busy():
            schnaps_sound.play()
    else:
        time_str = f"{anzeige['minutes']}:{anzeige['seconds']}"

    team1_anzeige.config(text=anzeige.get('team1', ""))
    team2_anzeige.config(text=anzeige.get('team2', ""))
    tore1_anzeige.config(text=anzeige.get('tore1', ""))
    tore2_anzeige.config(text=anzeige.get('tore2', ""))
    next_anzeige.config(text=anzeige.get('next', ""))

    last_log = datetime.datetime.now()


def show():
    try:
        data, addr = sock.recvfrom(1024)  # Puffergröße: 1024 Bytes
        update_display(data)
    except socket.timeout:
        zeit_anzeige.config(text="no data")
        team1_anzeige.config(text="")
        team2_anzeige.config(text="")
        tore1_anzeige.config(text="")
        tore2_anzeige.config(text="")
        next_anzeige.config(text="")
        reconnect_socket()
    except Exception as e:
        print(f"Fehler beim Empfang: {e}")

    root.after(10, show)

# GUI-Initialisierung
root = tk.Tk()
mon_count = 0
height = 0

for m in screeninfo.get_monitors():
    height = m.height
    mon_count += 1

if mon_count == 1:
    root.configure(bg='black', cursor='none')
    root.attributes("-fullscreen", True)
else:
    monitor = screeninfo.get_monitors()[0]
    root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
    root.configure(bg='black', cursor='none')
    root.wm_overrideredirect(True)

# GUI-Widgets
small = int(-0.15 * height)
big = int(-0.28 * height)
pad_x = int(0.03 * height)
pad_y = int(0.111 * height)

zeit_anzeige = tk.Label(root, font=('times', big, 'bold'), bg='black', fg='white', pady=pad_y)
zeit_anzeige.grid(row=2, column=0, columnspan=4, sticky="nesw")
zeit_anzeige.config(text="no data")

team1_anzeige = tk.Label(root, font=('times', small, 'bold'), bg='black', fg='white', padx=pad_x, pady=1.3 * pad_y)
team2_anzeige = tk.Label(root, font=('times', small, 'bold'), bg='black', fg='white', padx=pad_x, pady=1.3 * pad_y)
tore1_anzeige = tk.Label(root, font=('times', big, 'bold'), bg='black', fg='white', pady=pad_y)
tore2_anzeige = tk.Label(root, font=('times', big, 'bold'), bg='black', fg='white', pady=pad_y)
next_anzeige = tk.Label(root, font=('times', small, 'bold'), bg='black', fg='grey', pady=pad_y)

team1_anzeige.grid(row=0, column=0, columnspan=2, sticky="nsw")
team2_anzeige.grid(row=0, column=3, columnspan=2, sticky="nsw")
teams = (team1_anzeige, team2_anzeige)
tore1_anzeige.grid(row=1, column=0, columnspan=2, sticky="nesw")
tore2_anzeige.grid(row=1, column=2, columnspan=2, sticky="nesw")
next_anzeige.grid(row=3, column=0, columnspan=4, sticky="nesw")

for i in range(4):
    root.grid_rowconfigure(i, weight=1)
    root.grid_columnconfigure(i, weight=1)

# Starte die Datenanzeige
root.after(100, show)
root.mainloop()
