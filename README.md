# commandline-chatroom
A basic command line chatroom application utilising sockets and multi-threading.

Running python3 host.py will setup the chatroom server on the host computer.
Default is to broadcast over port 34343, however this can be changed easilly.

Running python3 client.py will give access to this chatroom as a client. 
In order to connect remotely (once ports have been forwarded), the client
needs to connect to you IP address rather than 'localhost'

server_commands_controller.py is used internally to handle getting
server commands from server_commands.py

Finally, server_commands.py is simply a file containing all of the server commands.
Each function in this file represents a command of the same name that will do what
the function does. Neccessary restrictions are explained in the docstring at the
top of server_commands.py.
