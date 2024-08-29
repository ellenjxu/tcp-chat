import socket
import subprocess
import time
import helper
import os
import rsa
import threading
import sys

# AF_INET defines the socket to be for internet communication
# (as opposed to bluetooth or something)
# SOCK_STREAM means it is a stream based socket;
# connection oriented using TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# We use a UDP socket to broadcast the IP and port of the server
# The client is set up to listen to the server's broadcast on a specific port
server_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# set a fixed port for both client and server
# to communicate the server's IP and port
broadcast_port = 64667

bound_port = 0

# global variable to indicate when the connection is complete
done = False

ipv4_address = helper.get_non_loopback_ip()
print("IP Address: ", ipv4_address)

ports = helper.known_ports()
print("Attempting commonly open ports... ")
bound = False

# controls communication between client and server
def client_server_flow():
    global done
    server.listen()

    client, addr = server.accept()
    
    # receive public key from client
    client_pubkey = eval(client.recv(1024).decode('utf-8')) # back to tuple
    print("Client public key: ", client_pubkey)
    
    # send public key to client
    pubkey, privkey = rsa.generate(10)
    client.send(str(pubkey).encode('utf-8'))
    print("Public key sent to client")
    time.sleep(1)

    # test encryption
    # 1. server sends encrypted message to client
    # 2. client decrypts message and sends it back to server
    test_msg = "Hello world"
    test_msg_enc = str(rsa.encrypt(test_msg, client_pubkey))
    client.send(test_msg_enc.encode('utf-8'))
    # print("Encrypted message sent to client")
    
    if client.recv(1024).decode('utf-8') == test_msg:
        client.send("ENC_TRUE".encode('utf-8'))
        enc = True
    else:
        client.send("ENC_FALSE".encode('utf-8'))
        enc = False

    done = False

    # receive and send messages
    while not done:
        msg = client.recv(1024).decode('utf-8')
        if enc:
            msg = rsa.decrypt(eval(msg), privkey)
        if msg == 'quit' or msg == '':
            done = True
            sys.exit()
        else:
            print("[Client]", msg)

        input_msg = input("[Me] ")
        if enc:
            input_msg = str(rsa.encrypt(input_msg, client_pubkey))
        client.send(input_msg.encode('utf-8'))

    client.close()
    server.close()

# Broadcast the IP and port of the server
def broadcast_for_new_clients(name, ip, port):
    global done
    while not done:
        message = f"Name: {name}, Server IP address: {ip}, Port: {port}"
        server_broadcast_socket.sendto(message.encode(), ("<broadcast>", broadcast_port))
        time.sleep(5)
    sys.exit()

# Kill any processes that are using the port we want to use
# and bind the server to the port
# additionally, begin the broadcast thread once port is established
def kill_and_bind(port_to_attempt):
    subprocess.run(["bash", "kill.sh", str(port_to_attempt)])
    server.bind((ipv4_address, port_to_attempt))
    bound_port = port_to_attempt
    room_name = str(input("Enter a name for the chat room: "))
    broadcast_thread = threading.Thread(target=broadcast_for_new_clients, args=(room_name, ipv4_address, bound_port))
    broadcast_thread.start()

    print("Running server on port", port_to_attempt, "!")
    print("IP: ", ipv4_address, "  Port: ", port_to_attempt)

# try to bind to any of the ports we know are generally free
for port in ports:
    try:
        if helper.validate_port(port):
            kill_and_bind(port)
            bound = True
            break
    except Exception as e:
        pass

# if not, do something a bit more malicious and 
# try to bind to any port that is in use but can be killed
# at user discretion
if not bound:
    print("Failed. Analyzing processes... ")
    last_resort_ports = helper.extract_port_numbers(ipv4_address)
    for port in last_resort_ports:
        try:
            if helper.validate_port(port):
                kill_and_bind(port)
                bound = True
                client_server_flow()
                break
        except Exception as e:
            pass
else:
    client_server_flow()


    

    