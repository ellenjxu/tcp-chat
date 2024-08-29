import socket
import helper

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_ip = helper.get_non_loopback_ip()
devices = helper.find_devices_on_network(client_ip)
print("IPs on this network:" , devices)
ports = helper.known_ports()

server_ip = str(input("Server IP: "))

connected = False
for port in ports:
    try:
        client.connect((server_ip, port))
        connected = True
    except:
        pass

if not connected:
    port = int(input("Port: "))
    client.connect((server_ip, port))

done = False

while not done:
    client.send(input("[Me] ").encode('utf-8'))
    msg = client.recv(1024).decode('utf-8')
    if msg == 'quit':
        done = True
    else:
        print("[Server]", msg)

client.close()