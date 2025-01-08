#!/usr/bin/env python3
import time
import socket
import datetime 
import os
import json

from functools import partial

schnapsszahl = 11
schnapsaktiv = False # nur für Spassturniere
#UDP_IP = ["127.0.0.1"]
UDP_IP = ["127.0.0.1", "192.168.4.1","192.168.1.10"]
#UDP_IP = "129.13.1"

UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
	# Python2
	import Tkinter as tk
except ImportError:
	# Python3
	import tkinter as tk
from tkinter import Listbox
import tkinter.messagebox
started = 0
spielzeit= 0 #7 * 60
remaining= datetime.timedelta(seconds=spielzeit)
endtime = datetime.datetime.now()+datetime.timedelta(seconds=spielzeit)
tore1 = 0
tore2 = 0
gesamttore = 0

team1='Mannschaft 1'
team2='Mannschaft 2'
teams=[]
selected_team1=0
selected_team2=0
class control:
	
	def __init__(self, value=datetime.timedelta(seconds=0)):
		self.delta = value
		self.started=0
		self.remaining=datetime.timedelta(seconds=0)
	def stop(self,event=None):
		if self.started==1:
			print ("stop!")
			stop_button.configure(state='disable', bg='grey')
			start_button.configure(state='active', bg='white',fg="black")
			self.started = 0
			self.remaining=endtime-datetime.datetime.now()
			if self.remaining < datetime.timedelta(seconds=0):
				self.remaining = datetime.timedelta(seconds=0)
			
	def start(self,event=None):
		
		
		if self.started == 2:
			self.remaining=datetime.timedelta(seconds=spielzeit)
			self.started = 0
		if self.started == 0:
			print ("start!")
			stop_button.configure(state='active', bg='white',fg="black")
			start_button.configure(state='disable', bg='grey')
			break_button.configure(state='disable', bg='grey')
			win1.unbind('h')
			self.started = 1
			global endtime
			endtime = datetime.datetime.now()+self.remaining

	def start_break(self,event=None):
			
		global endtime	
		if self.started == 0:
			self.started = 2
			endtime=datetime.datetime.now()+datetime.timedelta(seconds=120)
	def reset(self,event=None):
		
		if self.started == 2:
			self.started=0
		if self.started == 0:
			stop_button.configure(state='disable', bg='grey')
			start_button.configure(state='active', bg='white',fg="black")
			break_button.configure(state='normal', bg='grey')
			win1.bind('h', ctl.start_break)	
			self.remaining=datetime.timedelta(seconds=spielzeit)
	
	def t1p(self,event=None):
		global tore1
		tore1+=1
		ctl.checkSchnaps()
	def t1m(self,event=None):
		global tore1
		if tore1 > 0:
			tore1-=1
	def t2p(self,event=None):
		global tore2
		tore2+=1
		ctl.checkSchnaps()

	def t2m(self,event=None):
		global tore2
		if tore2 > 0:
			tore2-=1
	def checkSchnaps (self,event=None):
		if schnapsaktiv and (gesamttore + tore1 + tore2) > 0 and (gesamttore + tore1 + tore2) % schnapsszahl == 0:
			print("Schnapszahl!")
			ctl.stop()
			schnapszeit(zahl= gesamttore + tore1 + tore2)
	def sw(self,event=None):		
		global team1
		global team2
		global tore1
		global tore2
		if self.remaining <= datetime.timedelta(seconds=0):
			self.remaining = datetime.timedelta(seconds=spielzeit)
		temp1=team1
		team1=team2
		team2=temp1	
		Mannschaft1.config(text=team1)
		Mannschaft2.config(text=team2)
		temp2=tore2
		tore2 = tore1
		tore1 = temp2
	def rsz(self,event=None):	
		if self.started == 0:
			win1.pack_forget()
			#win2.wm_attributes("-topmost", 1)
			#win2.configure(bg="black",fg="white")
			win2.pack(expand=1, fill=tk.BOTH)
			win2.focus_set()
			
			self.remaining2=self.remaining
			
			rem=self.remaining
			minutes = (rem.seconds % 3600) // 60
			seconds = rem.seconds % 60
			neu_minutes = (self.remaining2.seconds % 3600) // 60
			neu_seconds = self.remaining2.seconds % 60
			
			
			alt = tk.Label(win2, font=('times', 30, 'bold'),bg='black', fg='white')
			alt.grid(row=1, column=2, sticky="nsew",padx=10, pady=15)
			alt_label = tk.Label(win2, font=('times', 30, 'bold'),bg='black', fg='white', text= "alt:")
			alt_label.grid(row=1, column=1, sticky="nsew",padx=10, pady=15)
			
			alt.config(text=str(minutes)+":"+str(seconds).rjust(2,"0"))

			neu.grid(row=2, column=2, sticky="nsew",padx=10, pady=15)
			neu_label = tk.Label(win2, font=('times', 30, 'bold'),bg='black', fg='white', text= "neu:")
			neu_label.grid(row=2, column=1, sticky="nsew",padx=10, pady=15)
			
			neu.config(text=str(neu_minutes)+":"+str(neu_seconds).rjust(2,"0"))

			p1m = tk.Button(win2, text='+1 min\n(a)', font=('times',20,'bold'), command=ctl.p1m)
			win2.bind('a',ctl.p1m)
			m1m = tk.Button(win2, text='-1 min\n(y)', font=('times',20,'bold'), command=ctl.m1m)
			win2.bind('y',ctl.m1m)
			p10s = tk.Button(win2, text='+10 sek\n(s)', font=('times',20,'bold'), command=ctl.p10s)
			win2.bind('s',ctl.p10s)
			m10s = tk.Button(win2, text='-10 sek\n(x)', font=('times',20,'bold'), command=ctl.m10s)
			win2.bind('x',ctl.m10s)
			p1s = tk.Button(win2, text='+1 sek\n(d)', font=('times',20,'bold'), command=ctl.p1s)
			win2.bind('d',ctl.p1s)
			m1s = tk.Button(win2, text='-1 sek\n(c)', font=('times',20,'bold'), command=ctl.m1s)
			win2.bind('c',ctl.m1s)
			p1m.grid(row=3, column=1, sticky="nsew",padx=10, pady=15)
			m1m.grid(row=4, column=1, sticky="nsew",padx=10, pady=15)
			p10s.grid(row=3, column=2, sticky="nsew",padx=10, pady=15)
			m10s.grid(row=4, column=2, sticky="nsew",padx=10, pady=15)
			p1s.grid(row=3, column=3, sticky="nsew",padx=10, pady=15)
			m1s.grid(row=4, column=3, sticky="nsew",padx=10, pady=15)
			#time.sleep(10)
			set_button = tk.Button(win2, text='Zeit setzen\n(Leertaste)', font=('times',20,'bold'), command=ctl.set_time)
			set_button.grid(row=3, column=4, columnspan = 4, sticky="nsew",padx=10, pady=15)
			win2.bind('<space>',ctl.set_time)
			
			back_button = tk.Button(win2, text='Verwerfen\n(r)', font=('times',20,'bold'), command=ctl.back)
			back_button.grid(row=4, column=5, columnspan = 1, sticky="nsew",padx=10, pady=15)
			win2.bind('r',ctl.back)

			
			diff.config(text=str(0)+":"+str(0).rjust(2,"0"),fg="red")
			diff.grid(row=2, column=3, sticky="nsew",padx=10, pady=15)
			
			
			tk.Grid.rowconfigure(win2, 0, weight=1)
			tk.Grid.rowconfigure(win2, 1, weight=1)
			tk.Grid.rowconfigure(win2, 2, weight=1)
			tk.Grid.rowconfigure(win2, 3, weight=1)
			tk.Grid.rowconfigure(win2, 4, weight=1)


			tk.Grid.columnconfigure(win2, 0, weight=1)
			tk.Grid.columnconfigure(win2, 1, weight=1)
			tk.Grid.columnconfigure(win2, 2, weight=1)
			tk.Grid.columnconfigure(win2, 3, weight=1)
			tk.Grid.columnconfigure(win2, 4, weight=1)
			tk.Grid.columnconfigure(win2, 5, weight=1)
	def p1m(self,event=None):
		if self.remaining2+datetime.timedelta(seconds=(60))>datetime.timedelta(seconds=(0)):
			self.remaining2=self.remaining2+datetime.timedelta(seconds=(60))
			ctl.update_diff()
	def m1m(self,event=None):
		if self.remaining2-datetime.timedelta(seconds=(60))>datetime.timedelta(seconds=(0)):
			self.remaining2=self.remaining2-datetime.timedelta(seconds=(60))
			ctl.update_diff()
	def p10s(self,event=None):
		if self.remaining2+datetime.timedelta(seconds=(10))>datetime.timedelta(seconds=(0)):
			self.remaining2=self.remaining2+datetime.timedelta(seconds=(10))
			ctl.update_diff()
	def m10s(self,event=None):
		if self.remaining2-datetime.timedelta(seconds=(10))>datetime.timedelta(seconds=(0)):
			self.remaining2=self.remaining2-datetime.timedelta(seconds=(10))
			ctl.update_diff()
	def p1s(self,event=None):

		if self.remaining2+datetime.timedelta(seconds=(1))>datetime.timedelta(seconds=(0)):
			self.remaining2=self.remaining2+datetime.timedelta(seconds=(1))
			ctl.update_diff()
	def m1s(self,event=None):
		
		if self.remaining2-datetime.timedelta(seconds=(1))>datetime.timedelta(seconds=(0)):
			self.remaining2=self.remaining2-datetime.timedelta(seconds=(1))
			ctl.update_diff()
		
	def update_diff(self,event=None):
		
		
		diff_time=self.remaining2-self.remaining
		minutes = (diff_time.seconds % 3600) // 60
		seconds = diff_time.seconds % 60
		if diff_time<datetime.timedelta(seconds=0):
			minutes = ((-diff_time).seconds % 3600) // 60
			seconds = (-diff_time).seconds % 60
			diff.config(text="-"+str(minutes)+":"+str(seconds).rjust(2,"0"))
		else:
			diff.config(text="+"+str(minutes)+":"+str(seconds).rjust(2,"0"))
		neu_minutes = (self.remaining2.seconds % 3600) // 60
		neu_seconds = self.remaining2.seconds % 60
		neu.config(text=str(neu_minutes)+":"+str(neu_seconds).rjust(2,"0"))


	def set_time(self,event=None):
		
		#self.remaining=datetime.timedelta(seconds=(60*int(eingabe_min.get())+int(eingabe_sec.get())))
		self.remaining=self.remaining2
		win2.pack_forget()
		win1.pack(expand=1, fill=tk.BOTH)
		win1.focus_set()
	def back(self,event=None):
		win2.pack_forget()
		win1.pack(expand=1, fill=tk.BOTH)
		win1.focus_set()
	def save_game(self,event=None):
		if self.started == 0 or self.started == 2:
			msg_result=tkinter.messagebox.askyesnocancel('Übernehmen?','Spielstand speichern', default="yes")
			print(msg_result)
			if msg_result==True:
				f_ergebnis.write(str(team1)+" - "+str(team2)+"\t"+str(tore1)+":"+str(tore2)+"\n")
				print(str(team1)+" - "+str(team2)+"\t"+str(tore1)+":"+str(tore2)+"\n")
				global gesamttore
				gesamttore += tore1 + tore2
				f_ergebnis.flush()
				ctl.new_game()
			elif msg_result==False:
				ctl.new_game()
	def new_game(self,event=None):
		
			for widget in radiobuttonFrame.winfo_children():
				widget.destroy()
			win1.pack_forget()
			win5.pack_forget()

			win3.pack(expand=1, fill=tk.BOTH)
			win3.focus_set()
			i=0
			global teams
			global u
			global v
			global w
			check=[]
			team_shortcut1=['q','w','e','r','t','z','u','i','o']
			team_shortcut2=['a','s','d','f','g','h','j','k','l']
			but1=[]
			but2=[]
			if len(teams)<10:
				for team in teams:
					print(i)
					tk.Radiobutton(radiobuttonFrame,text=team+"\n("+team_shortcut1[i]+")", padx = 10,pady = 15,variable=u,value=i, bg='grey',fg="black",activebackground="light grey",indicatoron="false",command= partial(ctl.sel1, team)).grid(row=i,column=0,sticky="nsew",padx=15, pady=7)
					tk.Radiobutton(radiobuttonFrame,text=team+"\n("+team_shortcut2[i]+")", padx = 10,pady = 15,variable=v,value=i, bg='grey',fg="black",activebackground="light grey",indicatoron="false",command= partial(ctl.sel2, team)).grid(row=i,column=1,sticky="nsew",padx=15, pady=7)
					win3.bind(team_shortcut1[i], lambda throw_away=0,i=i: ctl.sel1(teams[i]))
					
					win3.bind(team_shortcut2[i], lambda throw_away=0,i=i: ctl.sel2(teams[i]))
					
					print(i)
					i+=1
					print(i)
				
			else:
				for team in teams:
					
					tk.Radiobutton(radiobuttonFrame,text=team, padx = 10,pady = 15,variable=u,value=i, bg='grey',fg="black",activebackground="light grey",indicatoron="false",command= partial(ctl.sel1, team)).grid(row=i,column=0,sticky="nsew",padx=15, pady=7)
					tk.Radiobutton(radiobuttonFrame,text=team, padx = 10,pady = 15,variable=v,value=i, bg='grey',fg="black",activebackground="light grey",indicatoron="false",command= partial(ctl.sel2, team)).grid(row=i,column=1,sticky="nsew",padx=15, pady=7)
					i+=1
					print(i)
				
			if i!=0:
				tk.Label(radiobuttonFrame, bg="black").grid(row=i+1)
				tk.Label(radiobuttonFrame, bg="black").grid(row=i+5)
				tk.Radiobutton(radiobuttonFrame,text="5 min\n(5)", padx = 10,pady = 15,variable=w,value=1, bg='grey',fg="black",activebackground="light grey",indicatoron="false",command= partial(ctl.setTime, 5)).grid(row=i+2,column=0,columnspan=2,sticky="nsew",padx=5, pady=15)
				win3.bind("5", lambda throw_away=0,i=i: ctl.setTime(5))
				tk.Radiobutton(radiobuttonFrame,text="6 min\n(6)", padx = 10,pady = 15,variable=w,value=2, bg='grey',fg="black",activebackground="light grey",indicatoron="false",command= partial(ctl.setTime, 6)).grid(row=i+3,column=0,columnspan=2,sticky="nsew",padx=5, pady=15)
				win3.bind("6", lambda throw_away=0,i=i: ctl.setTime(6))
				
				tk.Radiobutton(radiobuttonFrame,text="7 min\n(7)", padx = 10,pady = 15,variable=w,value=3, bg='grey',fg="black",activebackground="light grey",indicatoron="false",command= partial(ctl.setTime, 7)).grid(row=i+4,column=0,columnspan=2,sticky="nsew",padx=5, pady=15)
				win3.bind("7", lambda throw_away=0,i=i: ctl.setTime(7))
				
				tk.Button(radiobuttonFrame, text='gespeicherte Ergebnisse anzeigen', width=30,padx=10, pady=15, font=('times',20,'bold'),command=ctl.show_games, bg='grey',fg="white" ).grid(row=i+6, column=0,sticky="nsew",padx=10, pady=15)
				tk.Button(radiobuttonFrame, text='übernehmen\n(Leertaste)', width=30,padx=10, pady=15, font=('times',20,'bold'), command=ctl.cls, bg='grey',fg="white" ).grid(row=i+7, column=0,sticky="nsew",padx=10, pady=15)
				win3.bind('<space>',ctl.cls)
			tk.Button(radiobuttonFrame, text='Mannschaften definieren\n(F1)',width=30,padx=10, pady=15,  font=('times',20,'bold'), command=ctl.new_teams, bg='grey',fg="white" ).grid(row=i+7, column=1,sticky="nsew",padx=10, pady=15)
			win3.bind('<F1>',ctl.new_teams)
			for y in range(i+5):
				radiobuttonFrame.grid_rowconfigure(y, weight=1)
	def cls(self):
		
		global selected_team1
		global selected_team2
		global team1
		global team2
		global spielzeit
		print(spielzeit)
		team1=selected_team1
		team2=selected_team2
		Mannschaft1.config(text=team1)
		Mannschaft2.config(text=team2)
		global tore1
		global tore2
		tore1 = 0
		tore2 = 0
		self.remaining=datetime.timedelta(seconds=spielzeit)
		win3.pack_forget()
		win1.pack(expand=1, fill=tk.BOTH)
		win1.focus_set()

		
		
	def new_teams(self):
		win3.pack_forget()
		win4.pack(expand=1, fill=tk.BOTH)
		text.focus_set()
		text.bind('<F1>', ctl.save_teams)

		text.delete(1.0, tk.END)
		for team in teams:
			print (tk.END)
			text.insert(tk.END, team+ "\n")
	def sel1(self,selected_team=""):
		global selected_team1
		global u
		global teams
		u.set(teams.index(selected_team))
		selected_team1=selected_team
		print (selected_team)
	def sel2(self,selected_team=""):
		global selected_team2
		global v
		global teams
		
		v.set(teams.index(selected_team))
		selected_team2=selected_team
		print (selected_team)
	def save_teams(self,event=None):
		global teams
		f=open("teams.conf","w")
		f.write(text.get(1.0, tk.END))
		teams=text.get(1.0, tk.END).split("\n")
		teams=list(filter(None, teams))
		win4.pack_forget()
		ctl.new_game()
	def setTime(self,timeset):
		print(timeset)
		global spielzeit
		global w
		
		spielzeit=60*timeset
		
		self.remaining= datetime.timedelta(seconds=spielzeit)
		print(type(w))
		print((w))
		w.set(timeset-4)
		
	def show_games(self,event=None):
		win3.pack_forget()
		win5.pack(expand=1, fill=tk.BOTH)
		win5.focus_set()
		
		f_ergebnis=open("ergebnis.conf","r")
		ergebnis=f_ergebnis.readlines()
		print(ergebnis)
		for a in range(len(ergebnis)):
			ergebnis[a]=ergebnis[a].replace("\n","")
		list(filter(None, ergebnis))
		print("Ergebnisse:")
		tk.Button(frame5, text='zurück\n(Leertaste)', width=30,padx=10, pady=15, font=('times',20,'bold'), command=ctl.new_game, bg='grey',fg="white" ).grid(row=1, column=0,sticky="nsew",padx=10, pady=15)
		win5.bind('<space>',ctl.new_game)
		count=1
		for a in ergebnis:
			count +=1
			tk.Label(frame5,text=a).grid(row=count, column=0,sticky="nsew",padx=10, pady=15)
			
class tick:		
	udp_dict={}
	udp_dict["schnaps"] = False
	udp_dict["schnapszalh"] = 0
	
	def calc(event=None):
		global endtime
		
		Tore1.config(text=str(tore1))
		Tore2.config(text=str(tore2))
		
		#udp_string=(";"+str(team1)+";"+str(team2)+";"+str(tore1)+";"+str(tore2))
		tick.udp_dict ["team1"] = str(team1)
		tick.udp_dict ["team2"] = str(team2)
		tick.udp_dict ["tore1"] = str(tore1)
		tick.udp_dict ["tore2"] = str(tore2)
		
		if ctl.started == 0:
			#print (self.remaining)
			rem=ctl.remaining
			if int(rem.microseconds/100000)>=5:
				ssek=1
			else:
				ssek=0
			#print (rem)
			#print ((rem.seconds) % 3600//60)
			#print ((rem.seconds) % 60)
			minutes = ((rem.seconds+ssek) % 3600) // 60
			seconds = (rem.seconds+ssek) % 60
			if rem > datetime.timedelta(seconds=0) and rem < datetime.timedelta(seconds=10):
				minutes = (rem.seconds % 3600) // 60
				seconds = rem.seconds % 60
				#print(int(rem.microseconds/100000))
				clock.config(text=(" "+str(seconds).rjust(2, '0')+"."+str(int(rem.microseconds/100000))), fg = "red")
				tick.udp_dict ["minutes"] = str(minutes) 
				tick.udp_dict ["seconds"] = (str(seconds).rjust(2, '0')+"."+str(int(rem.microseconds/100000)))
				
				#udp_send("   "+str(minutes)+":"+str(seconds).rjust(2, '0')+"."+str(int(rem.microseconds/100000)) +udp_string)
			
			else:
				clock.config(text=(str(minutes)+":"+str(seconds).rjust(2, '0')), fg = "white")
				tick.udp_dict ["minutes"] = str(minutes)
				tick.udp_dict ["seconds"] = str(seconds).rjust(2, '0')
				
			
		if ctl.started == 1:
			rem=(endtime-datetime.datetime.now())
			if int(rem.microseconds/100000)>=5:
				ssek=1
			else:
				ssek=0
			if rem > datetime.timedelta(seconds=10):
				minutes = ((rem.seconds+ssek) % 3600) // 60
				seconds = (rem.seconds+ssek) % 60
				clock.config(text=(str(minutes)+":"+str(seconds).rjust(2, '0')), fg = "white")
				tick.udp_dict ["minutes"] = str(minutes)
				tick.udp_dict ["seconds"] = str(seconds).rjust(2, '0')
			elif rem > datetime.timedelta(seconds=0):
				minutes = (rem.seconds % 3600) // 60
				seconds = rem.seconds % 60
				#print(int(rem.microseconds/100000))
				clock.config(text=(" "+str(seconds).rjust(2, '0')+"."+str(int(rem.microseconds/100000))), fg = "red")
				tick.udp_dict ["minutes"] = str(minutes) 
				tick.udp_dict ["seconds"] = (str(seconds).rjust(2, '0')+"."+str(int(rem.microseconds/100000))) 
			elif rem <= datetime.timedelta(seconds=0):
				ctl.remaining = datetime.timedelta(seconds=0)
				ctl.stop()
				break_button.configure(state='normal', bg='grey')
				win1.bind('h', ctl.start_break)
				tick.udp_dict ["minutes"] = str(0)
				tick.udp_dict ["seconds"] = str(0).rjust(2, '0')
		if ctl.started == 2:
			rem=(endtime-datetime.datetime.now())
			#print (rem)
			if rem < datetime.timedelta(seconds=0):
				ctl.reset()
			else:
				em=ctl.remaining
				minutes = (rem.seconds % 3600) // 60
				seconds = rem.seconds % 60
				clock.config(text=(str(minutes)+":"+str(seconds).rjust(2, '0')), fg = "white")
				
				tick.udp_dict ["minutes"] = str(minutes)
				tick.udp_dict ["seconds"] = str(seconds).rjust(2, '0')
		#print("..")
		udp_send(json.dumps(tick.udp_dict))

		clock.after(100, tick.calc)

	def enable_schnaps(event=None, zahl=0):
		tick.udp_dict["schnaps"] = True
		tick.udp_dict["schnapszahl"] = zahl
	def disable_schnaps(event=None):
		tick.udp_dict["schnaps"] = False

class close:
	def root_closing():
		if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
			root.destroy()
			quit()
	def win2_closing():
		win2.pack_forget()
		win1.pack(expand=1, fill=tk.BOTH)
		win1.focus_set()

	def win3_closing():
		win3.pack_forget()
		win1.pack(expand=1, fill=tk.BOTH)
		win1.focus_set()

	def win4_closing():
		win4.pack_forget()
		win1.pack(expand=1, fill=tk.BOTH)
		win1.focus_set()


def udp_send(sendstring):
	for i in UDP_IP:
		try:
			#print (i)
			sock.sendto(bytes(sendstring, 'utf-8'), (i, UDP_PORT))
		except:
			print("network error")

def schnapszeit(zahl = 0):
    top = tk.Toplevel()
    top.title('Shotrunde')
    tk.Message(top, text="Bitten sofort die Spieler versorgen", padx=300, pady=300, font=('times',50,'bold')).pack()
    tick.enable_schnaps(zahl=zahl)
    top.after(3000, top.destroy)
    clock.after(7000, tick.disable_schnaps)

ctl=control(datetime.timedelta(seconds=0))

		
root = tk.Tk()
root.configure(bg='black')
root.title('RadballAnzeige')

win1 = tk.Frame(root, bg='black')
win2 = tk.Frame(root, bg='black')
win3 = tk.Frame(root, bg='black')
win4 = tk.Frame(root, bg='black')
win5 = tk.Frame(root, bg='black')

win1.pack(expand=1, fill=tk.BOTH)
win1.focus_set()


	
		

Mannschaft1 = tk.Label(win1, font=('times', 30, 'bold'), bg='black', fg='white')
Mannschaft1.grid(row=0, column=0)
Mannschaft1.config(text=team1)

Tore1 = tk.Label(win1, font=('times', 40, 'bold'), bg='black', fg='white')
Tore1.grid(row=1, column=0)
Tore1.config(text="0")

frame1= tk.Frame(win1, bg='black')
frame1.grid(row=2, column=0, sticky="nsew")
Tore1_p = tk.Button(frame1, text='+\n(q)', width=10, font=('times',20,'bold'), command=ctl.t1p, bg='grey',fg="white" )
Tore1_p.grid(row=0, column=0,sticky="nsew",padx=10, pady=15)
win1.bind('q', ctl.t1p)
Tore1_m = tk.Button(frame1, text='-\n(a)', width=10, font=('times',20,'bold'), command=ctl.t1m, bg='grey',fg="white" )
Tore1_m.grid(row=0, column=1,sticky="nsew",padx=10, pady=15)
win1.bind('a', ctl.t1m)
tk.Grid.rowconfigure(frame1, 0, weight=1)
tk.Grid.columnconfigure(frame1, 0, weight=1)
tk.Grid.columnconfigure(frame1, 1, weight=1)

Mannschaft2 = tk.Label(win1, font=('times', 30, 'bold'), bg='black', fg='white')
Mannschaft2.grid(row=0, column=2)
Mannschaft2.config(text=team2)

frame2= tk.Frame(win1, bg='black')
frame2.grid(row=2, column=2, sticky="nsew")
Tore2_p = tk.Button(frame2, text='+\n(o)', width=10, font=('times',20,'bold'), command=ctl.t2p, bg='grey',fg="white" )
Tore2_p.grid(row=0, column=0,sticky="nsew",padx=10, pady=15)	
win1.bind('o', ctl.t2p)
Tore2_m = tk.Button(frame2, text='-\n(l)', width=10, font=('times',20,'bold'), command=ctl.t2m, bg='grey',fg="white" )
Tore2_m.grid(row=0, column=1,sticky="nsew",padx=10, pady=15)
win1.bind('l', ctl.t2m)
tk.Grid.rowconfigure(frame2, 0, weight=1)
tk.Grid.columnconfigure(frame2, 0, weight=1)
tk.Grid.columnconfigure(frame2, 1, weight=1)


Tore2 = tk.Label(win1, font=('times', 40, 'bold'), bg='black', fg='white')
Tore2.grid(row=1, column=2)
Tore2.config(text="0")

clock = tk.Label(win1, font=('times', 40, 'bold'), bg='black')
clock.grid(row=1, column=1)

sw_button = tk.Button(win1, text='Seitenwechsel\n(z)', width=25, font=('times',20,'bold'), command=ctl.sw, bg='grey',fg="white" )
win1.bind('z', ctl.sw)
sw_button.grid(row=2, column=1,sticky='nesw',padx=10, pady=15)



stop_button = tk.Button(win1, text='Stop\n(Leertaste)', width=25, font=('times',20,'bold'), command=ctl.stop, bg='grey',fg="white" )
win1.bind('<space>', ctl.stop)
stop_button.grid(row=3, column=0,sticky='nesw',padx=10, pady=15)

start_button = tk.Button(win1, text='Start\n(b)', width=25, font=('times',20,'bold'), command=ctl.start, bg='grey',fg="white")
win1.bind('b', ctl.start)
start_button.grid(row=3, column=1,sticky='nesw',padx=10, pady=15)

reset_button = tk.Button(win1, text='Zeit zurücksetzen\n(r)', width=25, font=('times',20,'bold'),command=ctl.reset, bg='grey',fg="white")
win1.bind('r', ctl.reset)
reset_button.grid(row=3, column=2,sticky='nesw',padx=10, pady=15)

rsz_button = tk.Button(win1, text='Restspielzeit ändern\n(m)', width=25, font=('times',20,'bold'),command=ctl.rsz, bg='grey',fg="white")
win1.bind('m', ctl.rsz)
rsz_button.grid(row=4, column=2,sticky='nesw',padx=10, pady=15)

newg_button = tk.Button(win1, text='Neues Spiel\n(c)', width=25, font=('times',20,'bold'),command=ctl.save_game, bg='grey',fg="white")
win1.bind('c', ctl.save_game)
newg_button.grid(row=4, column=1,sticky='nesw',padx=10, pady=15)

break_button = tk.Button(win1, text='Pause starten\n(h)', width=25, font=('times',20,'bold'),command=ctl.start_break, bg='grey',fg="white")

break_button.grid(row=4, column=0,sticky='nesw',padx=10, pady=15)


diff=tk.Label(win2, font=('times', 30, 'bold'),bg='black', fg='white')
neu = tk.Label(win2, font=('times', 30, 'bold'),bg='black', fg='white')
						

for i in range(5):
	tk.Grid.rowconfigure(win1, i, weight=1)
for i in range(3):
	tk.Grid.columnconfigure(win1, i, weight=1)


tick.calc()

u=tk.IntVar()
v=tk.IntVar()
w=tk.IntVar()

radiobuttonFrame = tk.Frame(win3, bg='black')
radiobuttonFrame.pack()



		
text = tk.Text(win4)
text.pack()

frame5 = tk.Frame(win5, bg='black')
frame5.pack()

save_teams_button = tk.Button(win4, text='Teams übernehmen\n(F1)', width=25, font=('times',20,'bold'),command=ctl.save_teams, bg='grey',fg="white")
save_teams_button.pack()

wide, height = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (wide, height))
root.protocol("WM_DELETE_WINDOW", close.root_closing)

if os.path.isfile("teams.conf"):
	if tkinter.messagebox.askyesno('Spieltag?','Mannschaften vom letzem Spieltag laden', default='no'):
		f=open("teams.conf","r")
		f_ergebnis=open("ergebnis.conf","a+")
		teams=f.readlines()
		for a in range(len(teams)):
			teams[a]=teams[a].replace("\n","")
		list(filter(None, teams))
		print(teams)
		f.close()
	else:
		f_ergebnis=open("ergebnis.conf","w+")
else:
	f_ergebnis=open("ergebnis.conf","w+")
root.mainloop()
