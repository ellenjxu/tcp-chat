import socket

# Define the port number to listen for broadcasts
port = 5000

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Enable broadcasting option
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Bind the socket to the port
client_socket.bind(("", port))

# Receive the broadcast message
data, address = client_socket.recvfrom(1024)
message = data.decode()

# Extract the IP address and port from the message
ip_address = message.split(",")[0].split(":")[1].strip()
server_port = int(message.split(",")[1].split(":")[1].strip())

print(ip_address)
print(server_port)

# Rest of your client code goes here
