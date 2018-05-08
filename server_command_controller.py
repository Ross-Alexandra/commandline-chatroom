"""PURPOSE:

	Using from server_commands import command_list will give
	a dictionary of all the commands in the server_commands.py file.

"""

#: Import the commands file so we can see what commands exist
import server_commands as commands

#: Import all of the commands from server_commands.
from server_commands import *

def get_server_commands():
	server_commands = [f for f in dir(commands) if '__' not in f]
	return server_commands

#: Create a dictionary of server commands.
command_list = {f: eval(f) for f in get_server_commands()}

