#!/usr/bin/env python3

import time
import socket
import json
import screeninfo
import tkinter as tk
import tkinter.font as tkFont
from pygame import mixer

# ------------------------------------------------------------------------
# 1) KONFIGURATION
# ------------------------------------------------------------------------
UDP_IP = ""
UDP_PORT = 5005
DEFAULT_TIME = "0:00"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)  # Non-blocking Socket

sound_active = True
try:
    mixer.init()
    sound = mixer.Sound("bing.wav")
    schnaps_sound = mixer.Sound("schnaps.wav")
except Exception as e:
    print(f"Sound konnte nicht initialisiert werden: {e}")
    sound_active = False

time_str = DEFAULT_TIME
last_data_received = time.monotonic()

# Merkt sich den zuletzt angezeigten Text (Teamnamen),
# damit wir nur dann neu skalieren, wenn es sich ändert
prev_team1_text = ""
prev_team2_text = ""

# Cache für bereits berechnete Fonts, damit nicht jedes Mal neu skaliert wird
TEAM_FONT_CACHE = {}  # dictionary: text -> tkFont.Font

def reconnect_socket():
    """Schickt einen Broadcast, damit der Sender weiß, dass wir Daten brauchen."""
    try:
        print("Reconnecting...")
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock2.sendto(b"Hello, I need data", ("255.255.255.255", 5006))
        sock2.close()
    except Exception as e:
        print(f"Fehler beim Reconnect: {e}")

# ------------------------------------------------------------------------
# 2) FUNKTIONEN
# ------------------------------------------------------------------------

def split_team_name(name: str) -> str:
    """
    Sucht nach Slash oder Bindestrich und bricht dort (beim ersten Vorkommen)
    in eine zweite Zeile um.
    """
    slash_index = name.find("/")
    dash_index = name.find("-")

    if slash_index != -1:
        return name[:slash_index + 1] + "\n" + name[slash_index + 1:]
    elif dash_index != -1:
        return name[:dash_index + 1] + "\n" + name[dash_index + 1:]
    else:
        return name

def measure_text_width(text: str, font: tkFont.Font) -> int:
    """Misst die maximale Breite (in Pixel) der (ggf. mehrzeiligen) Zeichenkette."""
    lines = text.split("\n")
    widths = [font.measure(line) for line in lines]
    return max(widths) if widths else 0

def auto_shrink_font(text: str, max_width: int, base_font_size: int,
                     min_size: int = 10, font_family="times", weight="bold") -> tkFont.Font:
    """
    Verkleinert die Schriftgröße so lange, bis 'text' in 'max_width' Pixel passt.
    Nutzt TEAM_FONT_CACHE, damit wir nicht wiederholt berechnen.
    """
    # Schon im Cache?
    if text in TEAM_FONT_CACHE:
        return TEAM_FONT_CACHE[text]

    # Falls base_font_size negativ ist (pixelbasiert in tkinter),
    # arbeiten wir intern nur mit dem absoluten Wert.
    size = abs(base_font_size)
    current_font = tkFont.Font(family=font_family, size=-size, weight=weight)

    while size >= min_size:
        w = measure_text_width(text, current_font)
        if w <= max_width:
            break
        size -= 1
        current_font.configure(size=-size)

    # Im Cache speichern
    TEAM_FONT_CACHE[text] = current_font
    return current_font

def update_display(data: bytes):
    """Bekommt neue Daten, aktualisiert Zeit, Teamnamen etc."""
    global time_str, last_data_received
    global prev_team1_text, prev_team2_text

    try:
        anzeige = json.loads(data)
    except json.JSONDecodeError:
        return

    # Zeitstempel updaten (wir haben gültige Daten)
    last_data_received = time.monotonic()

    # Zeit-Anzeige
    current_time_str = f"{anzeige['minutes']}:{anzeige['seconds']}"
    zeit_anzeige.config(text=current_time_str)

    # bing oder schnaps
    if current_time_str == DEFAULT_TIME and time_str != DEFAULT_TIME:
        time_str = DEFAULT_TIME
        if sound_active:
            sound.play()
        print("bing")
    elif anzeige.get("schnaps"):
        zeit_anzeige.config(text=f"{anzeige['schnapszahl']}!!!")
        if sound_active and not mixer.get_busy():
            schnaps_sound.play()
    else:
        time_str = current_time_str

    # Teamnamen
    new_team1_text = split_team_name(anzeige.get('team1', ""))
    new_team2_text = split_team_name(anzeige.get('team2', ""))

    # Nur aktualisieren, wenn sich der Text ändert
    if new_team1_text != prev_team1_text:
        font_for_team1 = auto_shrink_font(
            text=new_team1_text,
            max_width=TEAM_LABEL_MAX_WIDTH,
            base_font_size=small,  # Startgröße (z.B. -108)
            min_size=10
        )
        team1_anzeige.config(text=new_team1_text, font=font_for_team1)
        prev_team1_text = new_team1_text

    if new_team2_text != prev_team2_text:
        font_for_team2 = auto_shrink_font(
            text=new_team2_text,
            max_width=TEAM_LABEL_MAX_WIDTH,
            base_font_size=small,
            min_size=10
        )
        team2_anzeige.config(text=new_team2_text, font=font_for_team2)
        prev_team2_text = new_team2_text

    # Tore & Next
    tore1_anzeige.config(text=anzeige.get('tore1', ""))
    tore2_anzeige.config(text=anzeige.get('tore2', ""))
    next_anzeige.config(text=anzeige.get('next', ""))

def show():
    """
    Liest alle verfügbaren Pakete aus dem Socket (non-blocking) und aktualisiert die Anzeige.
    Zeigt ein Overlay an, wenn seit >1s keine Daten.
    """
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            update_display(data)
        except BlockingIOError:
            # keine weiteren Pakete
            break
        except Exception as e:
            print(f"Fehler beim Empfang: {e}")
            break

    now = time.monotonic()
    if now - last_data_received > 1.0:
        # Overlay einblenden
        if overlay.state() == "withdrawn":  # nur falls noch nicht eingeblendet
            overlay.deiconify()
        reconnect_socket()
    else:
        # Overlay ausblenden
        if overlay.state() != "withdrawn":
            overlay.withdraw()

    root.after(50, show)

# ------------------------------------------------------------------------
# 3) GUI-AUFBAU
# ------------------------------------------------------------------------
root = tk.Tk()

monitors = screeninfo.get_monitors()
if not monitors:
    print("Keine Monitore gefunden, Standardwerte setzen ...")
    screen_width, screen_height = 800, 600
else:
    monitor = monitors[0]
    screen_width = monitor.width
    screen_height = monitor.height

if len(monitors) == 1:
    root.configure(bg='black', cursor='none')
    root.attributes("-fullscreen", True)
else:
    root.geometry(f"{screen_width}x{screen_height}+{monitor.x}+{monitor.y}")
    root.configure(bg='black', cursor='none')
    root.wm_overrideredirect(True)

small = int(-0.15 * screen_height)
big   = int(-0.28 * screen_height)
pad_x = int(0.03  * screen_height)
pad_y = int(0.111 * screen_height)

TEAM_LABEL_MAX_WIDTH = int(screen_width * 0.50)

# Hauptelemente
zeit_anzeige = tk.Label(
    root, 
    font=('times', big, 'bold'), 
    bg='black', 
    fg='white', 
    pady=pad_y
)
zeit_anzeige.grid(row=2, column=0, columnspan=4, sticky="nsew")
zeit_anzeige.config(text="no data")

team1_anzeige = tk.Label(
    root, 
    font=('times', small, 'bold'), 
    bg='black', 
    fg='white',
    padx=pad_x, 
    pady=int(1.3 * pad_y),
    anchor='center'
)
team1_anzeige.grid(row=0, column=0, columnspan=2, sticky="nsew")

team2_anzeige = tk.Label(
    root, 
    font=('times', small, 'bold'), 
    bg='black', 
    fg='white',
    padx=pad_x, 
    pady=int(1.3 * pad_y),
    anchor='center'
)
team2_anzeige.grid(row=0, column=2, columnspan=2, sticky="nsew")

tore1_anzeige = tk.Label(
    root, 
    font=('times', big, 'bold'), 
    bg='black', 
    fg='white', 
    pady=pad_y
)
tore1_anzeige.grid(row=1, column=0, columnspan=2, sticky="nsew")

tore2_anzeige = tk.Label(
    root, 
    font=('times', big, 'bold'), 
    bg='black', 
    fg='white', 
    pady=pad_y
)
tore2_anzeige.grid(row=1, column=2, columnspan=2, sticky="nsew")

next_anzeige = tk.Label(
    root, 
    font=('times', small, 'bold'), 
    bg='black', 
    fg='grey', 
    pady=pad_y
)
next_anzeige.grid(row=3, column=0, columnspan=4, sticky="nsew")

# Grid-Konfiguration
root.grid_rowconfigure(0, weight=1, minsize=int(0.15 * screen_height))
root.grid_rowconfigure(1, weight=1, minsize=int(0.15 * screen_height))
root.grid_rowconfigure(2, weight=1, minsize=int(0.3  * screen_height))
root.grid_rowconfigure(3, weight=1, minsize=int(0.15 * screen_height))

for c in range(4):
    root.grid_columnconfigure(c, weight=1, minsize=0)

# ------------------------------------------------------------------------
# 4) OVERLAY: "NO DATA"
# ------------------------------------------------------------------------
overlay = tk.Toplevel(root)
overlay.title("No Data Overlay")
# Gleiche Größe/Auflösung wie root
overlay.geometry(f"{screen_width}x{screen_height}+{monitor.x}+{monitor.y}")
overlay.configure(bg='black')
# Ganz oben und ohne Rahmen
overlay.attributes("-topmost", True)
overlay.overrideredirect(True)

# Falls ein Monitor => fullscreen
if len(monitors) == 1:
    overlay.attributes("-fullscreen", True)

# Label im Overlay
overlay_label = tk.Label(
    overlay, 
    text="NO DATA", 
    font=('times', int(-0.2 * screen_height), 'bold'), 
    bg='black', 
    fg='red'
)
overlay_label.pack(expand=True, fill=tk.BOTH)

# Start: Overlay ausgeblendet
overlay.withdraw()

# ------------------------------------------------------------------------
# 5) LOOP START
# ------------------------------------------------------------------------
root.after(50, show)
root.mainloop()
