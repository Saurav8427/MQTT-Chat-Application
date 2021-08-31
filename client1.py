import paho.mqtt.client as mqtt
from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox #Tkinter Python Module for GUI  
import time
import tkinter as tk

##########Defining all call back functions###################

class GUI:
    def on_connect(self,client,userdata,flags,rc):# called when the broker   responds to our connection request
        print("Connected - rc:",rc)
    def on_message(self,client,userdata,message):#Called when a message has been     received on a topic that the client has subscirbed to.
        if str(message.topic) != self.topicone:
            msg = str(message.payload.decode("utf-8"))
            if "joined" in msg:
                user = msg.split(":")[0]
                msg = user + " has joined"
                self.chat_transcript_area.insert('end', msg + '\n')
                self.chat_transcript_area.yview(END)
            elif "left" in msg:
                user = msg.split(":")[0]
                msg = user + " has left"
                self.chat_transcript_area.insert('end', msg + '\n')
                self.chat_transcript_area.yview(END)
            else:
                self.chat_transcript_area.insert('end', msg + '\n')
                self.chat_transcript_area.yview(END)

    def on_subscribe(self, client, userdata,mid,granted_qos):##Called when the    broker responds to a subscribe request.
        print("Subscribed:", str(mid),str(granted_qos))
    def on_unsubscirbe(self, client,userdata,mid):# Called when broker responds   to an unsubscribe request.
        print("Unsubscribed:",str(mid))
    def on_disconnect(self, client,userdata,rc):#called when the client   disconnects from the broker
        if rc !=0:
            print("Unexpected Disconnection")

    def initialize(self):
        broker = '1b8edb4435b64ca9b3f81b0b3e550d4c.s1.eu.hivemq.cloud'
        port = 8883
        username = 'stoicall'
        password = 'Abcd@1234'

        self.client = mqtt.Client()
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscirbe
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
        self.client.username_pw_set(username, password)
        self.client.connect(broker,port)

        time.sleep(1)
        self.client.loop_start()
        self.client.subscribe(self.topictwo)
        time.sleep(1)

    def __init__(self,master):
        self.root = master
        self.chat_transcript_area = None
        self.name_widget = None 
        self.enter_text_widget = None
        self.join_button = None
        self.topicone = "Friend/" #1
        self.topictwo = "Friend/#" #2
        self.initialize()
        self.display_chat_box()
        self.display_name_section()
        self.display_chat_entry_box()

    def display_name_section(self):
        frame = Frame()
        # self.photo = Image.open("C:/Users/LENOVO/Desktop/-/GUI/landscape.png")     
        # self.image = ImageTk.PhotoImage(self.photo)
        Label(frame, text='Enter your name:', font=("Fantasque Sans Mono", 12)).pack(side='left', padx=10)
        self.name_widget = Entry(frame, width=45, borderwidth=2)
        self.name_widget.pack(side='left', anchor='e')
        self.name_widget.focus_set()
        self.join_button = Button(frame, text="J o i n", width=8,bg="black",fg="white", command=self.on_join).pack(side='left')
        frame.pack(side='top', anchor='nw')

    def display_chat_box(self):
        frame = Frame()
        Label(frame, text='  Chat Box:',font=("Fantasque Sans Mono", 12)).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=60, height=10, font=("Fantasque Sans Mono", 12),bg = "lightblue1" )
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')

    def display_chat_entry_box(self):
        frame = Frame()
        Label(frame, text='Enter message:', font=("Fantasque Sans Mono", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Fantasque Sans Mono", 12), bg="darkseagreen1")
        self.enter_text_widget.pack(side='left', pady=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')

    def on_enter_key_pressed(self, event):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror("Enter your name", "Enter your name to send a message")
            return
        self.send_chat()
        self.clear_text()

    def on_join(self):
        if len(self.name_widget.get()) == 0:    
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        print("Someone joined")
        self.topicone = self.topicone + self.name_widget.get()
        self.name_widget.config(state='disabled')
        self.client.publish(self.topicone,(self.name_widget.get() + ": " + "has joined").encode('utf-8'))

    
    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        senders_name = self.name_widget.get().strip() + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.client.publish(self.topicone, message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.on_quit()
            self.root.destroy()
            exit(0)

    def on_quit(self):
        print("Someone left")
        if len(self.name_widget.get()) != 0:
            self.client.publish(self.topicone,(self.name_widget.get() + ": " + "has left").encode('utf-8'))

frame = tk.Tk()
frame.title("CallFlower Chat") 
g = GUI(frame)
#The window created is not resizable
frame.resizable(0, 0)
#On closing window on_close_window() is called.
frame.protocol("WM_DELETE_WINDOW", g.on_close_window)
frame.mainloop()
