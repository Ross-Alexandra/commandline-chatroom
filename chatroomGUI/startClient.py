from tkinter import *

import tkinter.scrolledtext as tkst
from chatroom.client import chatroomClient

import threading
import time

class clientGUI:

	def __init__(self):

		#: Draw the original page.
		root = Tk()
		root.attributes('-topmost', -1)
		root.geometry("500x250+100+100")
		root.overrideredirect(True)

		#root.wm_attributes('-alpha', 0.8)

		entry = Entry(root)

		chat = tkst.ScrolledText(root, height=10, width=50)
		chat.place(x=50, y=20, anchor="nw")
		chat.config(state=DISABLED)

		input_box = tkst.ScrolledText(root, height=3, width=50)
		input_box.place(x=50, y=150)
		input_box.config(state=NORMAL)

		close_button = Button(root, text="Close Window", command=self.stop)
		close_button.place(x=50, y=220, anchor="nw")

		send_button = Button(root, text="Send", command= self.send)
		send_button.place(x=420, y=220, anchor="ne")

		self.input_box = input_box
		self.root = root
		self.chat = chat

	def screen_write(self, msg: str, end: str=""):
		self.chat.config(state=NORMAL)
		self.chat.insert(END, "You:" + msg + end.strip() + "\n")
		self.chat.config(state=DISABLED)

		#: TODO:
		#: Have the scroll bar scroll to END iff the user hasn't clicked into
		#: this widget.
		self.chat.see(END)

	def send(self):
		msg = self.input_box.get('1.0', END).strip()
		self.input_box.delete('1.0', END)

		self.client.send(msg)
		if msg == "/quit":
			self.stop()

		time.sleep(.5)

	def start(self, server='localhost', port=34343):

		self.client = chatroomClient(print_to = self.screen_write)
		self.client.join(server, port, silent=True)

		self.root.mainloop()

	def stop(self):
		self.client.quit(False)
		self.root.destroy()
