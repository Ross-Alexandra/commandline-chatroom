from tkinter import *

import tkinter.scrolledtext as tkst
from chatroom.host import chatroomServer

import threading
import time

class serverGUI:

	def __init__(self):

		#: Draw the original page.
		root = Tk()
		root.attributes('-topmost', -1)
		root.geometry("500x250+600+100")
		#root.overrideredirect(True)

		#root.wm_attributes('-alpha', 0.8)

		chat = tkst.ScrolledText(root, height=10, width=50)
		chat.place(x=50, y=20, anchor="nw")
		chat.config(state=DISABLED)

		input_box = Entry(root, width=46)
		input_box.place(x=50, y=190)
		input_box.bind('<Return>', self.send)

		close_button = Button(root, text="Close Window", command=self.stop)
		close_button.place(x=50, y=220, anchor="nw")

		send_button = Button(root, text="Send", command= self.send)
		send_button.place(x=420, y=220, anchor="ne")

		self.input_box = input_box
		self.root = root
		self.chat = chat

	def screen_write(self, msg: str, end: str=""):
		self.chat.config(state=NORMAL)
		self.chat.insert(END, msg + end.strip() + "\n")
		self.chat.config(state=DISABLED)

		#: TODO:
		#: Have the scroll bar scroll to END iff the user hasn't clicked into
		#: this widget.
		self.chat.see(END)

	def send(self, event=None):
		cmd = self.input_box.get().strip()
		cmd_args = cmd.split(" ")
		self.input_box.delete(0, END)

		print(cmd_args)

		try:
			self.host.server_command_list[cmd_args[0].replace("!", '')](self.host, cmd_args)
		except Exception as e:

			#: For debugging use, if a ! is in a command,
			#: a traceback will be printed if an error occurs.
			if '!' in cmd_args[0]:
				self.screen_write(str(e))
			else:
				self.screen_write("Invalid command, please try again. Append '!' to the command to see a traceback.")

	def start(self, host='', port=34343):

		self.host = chatroomServer(print_to = self.screen_write)
		self.host.start(inactivity_timeout=60, max_connections=5, no_console=True)

		self.root.mainloop()

	def stop(self):
		self.host.stop()
		self.root.destroy()
