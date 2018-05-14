"""PURPOSE:

	Using from server_commands import command_list will give
	a dictionary of all the commands in the server_commands.py file.

"""

#: Import the commands file so we can see what commands exist
import server_commands

#: Import all of the commands from server_commands.
from server_commands import *

def get_server_commands():

	#: Import inpsect to get the docstring from each function.
	import inspect

	#: Import re to find permission_level of each function.
	import re

	cmds = []

	#: Loop over every function in server_commands that is not a
	#: built in python function (one that is surrounded by __)
	for f in [f for f in dir(server_commands) if '__' not in f]:

		#: Get the docstring for each function.
		docstring = inspect.getdoc(eval(f))

		#: Use a regex to find the permission level specified in the docstring.
		vals = re.findall(r'Permission_level\s*=\s*(\d+)', docstring, re.I)

		#: Append the string of the function, and the permission level to do it
		cmds.append((f, int(vals[0])))

	#: Return this
	return cmds

#: Create a dictionary relating strings of command names to their respective functions
#: and permission level.
command_list = {f: (eval(f), perm) for f, perm in get_server_commands()}
