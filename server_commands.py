""" PURPOSE:

	Each method in this file can be called with /[command] from a client.


	for example, /quit will cause the code in quit to be run.

   USAGE:

	Any command in this file MUST accept a server object, client, address
	and command_args. They need not use them, but they must accept them.

	Thus, this shall act as the docstring for each of those commands:

	Args:
		server_object(socket): The server that is being run. This is here to allow
					access to things in the server.
		client(socket): The client that made the command request.
		address(tuple): The IP and port of the client.
		command_args(list): A list of the arguments passed with the command.

	Finally, The /command command will show the client all available commands.
	Further, the docstring of each function will also be shown to the user, so
	that they have a better understanding of what each function does.
"""

def quit(server_object, client, address, command_args):
	"""
		Closes the connection to the chatroom.
	"""
	server_object.close_client(client, address, "quit command")

def commands(server_object, client, address, command_args):
	"""
		Lists out all of the commands for the client.
	"""

	msg = ""
	for command in server_object.command_list.keys():
		msg += "\n/" + command + " - "
		msg += server_object.command_list[command].__doc__

	client.send(msg.encode())

