import socket

# Define the port number the server is running on
port = 5000

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Enable broadcasting option
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Get the local IP address
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

# Broadcast the IP address and port
message = f"Server IP address: {ip_address}, Port: {port}"
server_socket.sendto(message.encode(), ("<broadcast>", port))

# Rest of your server code goes here
