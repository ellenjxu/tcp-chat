import tkinter as tk
import socket
import threading
import helper
import rsa
import os
import sys

# TCP client to receive and send messages to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# UDP socket to receive the IP and port of the server from broadcast
client_receive_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_receive_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
broadcast_port = 64667 # can be any port, typically greater than 1024 (reserved)

server_ip_address = "0.0.0.0" # placeholder
server_port = 0

server_info = {}

closing = False
nickname = ""

pubkey, privkey = rsa.generate(10)
global server_pubkey

enc = False


# update the textbox content while keeping it
# in a disabled state for the user
def populate_text(data, text):
    text.config(state="normal")
    text.insert(tk.END, data)
    text.see(tk.END)
    text.config(state="disabled")


# Display IP and port that server broadcasted
def display_received_broadcast():
    global server_ip_address
    global server_port
    client_receive_broadcast_socket.bind(("", broadcast_port))
    while True:
        data, address = client_receive_broadcast_socket.recvfrom(1024)
        message = data.decode()
        name = message.split(",")[0].split(":")[1].strip()
        server_ip_address = message.split(",")[1].split(":")[1].strip()
        server_port = int(message.split(",")[2].split(":")[1].strip())
        flag = False
        if name in server_info:
            flag = True
        if not flag:
            populate_text(name + " | " + "IP: " + str(server_ip_address) + "  Port: " + str(server_port) + "\n", text_devices)
            # create dictionary of server info
            server_info[name] = [server_ip_address, server_port]


# threading to improve startup time
display_received_broadcast_thread = threading.Thread(target=display_received_broadcast)
display_received_broadcast_thread.start()


# flow after connection is established
def submit(event=None):
    global nickname
    nickname = str(nickname_input.get())
    name = str(room_input.get())
    server_ip = server_info[name][0]
    port = server_info[name][1]

    connected = False

    try:
        client.connect((server_ip, port))
        connected = True
    except:
        pass 

    result_label.config(text="IP: " + server_ip + "\nPort: " + str(port))

    if not connected:
        pass

    label_room_input.destroy()
    room_input.destroy()

    label_text_devices.destroy()

    text_devices.destroy()
    submit_button.destroy()

    text_box = tk.Text(root, width=50, height=10, state="disabled", highlightcolor="red", highlightthickness=2)
    text_box.pack()

    frame = tk.Frame(root)
    frame.pack()

    space = tk.Label(frame, height=1)
    space.pack()

    input_message_to_send = tk.Entry(root, width=35)
    input_message_to_send.pack()

    # handle incoming messages from the server
    def receive_message():
        global pubkey, privkey, enc, server_pubkey
        while not closing:
            # decoded message
            incoming_message = client.recv(1024).decode('utf-8')
            print(incoming_message)

            # handle exit cases and
            # add valid message to textbox
            if incoming_message == 'quit' or '':
                client.close()
                break
            if incoming_message == 'NICK':
                client.send(nickname.encode('utf-8'))
            elif incoming_message == 'RSA':
                client.send(str(pubkey).encode('utf-8'))
                populate_text("Public key sent to server\n", text_box)

                # receive public key from server
                server_pubkey = client.recv(1024).decode('utf-8')
                print(server_pubkey)
                server_pubkey = eval(server_pubkey)
                populate_text("Server public key: " + str(server_pubkey) + "\n", text_box)

                # ******* TEST DECRYPTION *******
                test_msg = client.recv(1024).decode('utf-8')
                test_msg_dec = rsa.decrypt(eval(test_msg), privkey)
                print("Test message: " + test_msg_dec)
                client.send(test_msg_dec.encode('utf-8'))

                status = client.recv(1024).decode('utf-8')
                print("staus: " + status)

                if status == "ENC_TRUE":
                    populate_text("Using RSA encryption\n", text_box)
                    enc = True
                else:
                    populate_text("Unable to use RSA encryption. Unencrypted messages will be sent\n", text_box)
                    enc = False

                client.send("200".encode('utf-8'))
            else: 
                populate_text(incoming_message + "\n", text_box)

    # handle sending messages to the server
    def send_message(event=None):
        data = input_message_to_send.get()
        msg = "[" + nickname + "] " + data
        if enc:
            msg = str(rsa.encrypt(msg, server_pubkey))
        if data != "":
            input_message_to_send.delete(0, tk.END)
            client.send(msg.encode('utf-8'))

    input_message_to_send.bind("<Return>", send_message)

    # start thread to receive messages
    receive_thread = threading.Thread(target=receive_message)
    receive_thread.start()


# Create a Tkinter window
root = tk.Tk()
root.title("Chat Client")

label_text_devices = tk.Label(root, text="Devices on the network: ", justify="center", anchor="center")
label_text_devices.pack()
text_devices = tk.Text(root, width=50, height=6, state="disabled")
text_devices.pack()

label_nickname_input = tk.Label(root, text="Nickname:", justify="center", anchor="center")
label_nickname_input.pack()

nickname_input = tk.Entry(root, width=20, justify="center")
nickname_input.pack()

# label_ip_input = tk.Label(root, text="IP:", justify="center", anchor="center")
# label_ip_input.pack()

# ip_input = tk.Entry(root, width=20, justify="center")
# ip_input.pack()

# label_port_input = tk.Label(root, text="Port:", justify="center", anchor="center")
# label_port_input.pack()

# port_input = tk.Entry(root, width=20, justify="center")
# port_input.pack()

label_room_input = tk.Label(root, text="Chat room:", justify="center", anchor="center")
label_room_input.pack()

room_input = tk.Entry(root, width=20, justify="center")
room_input.pack()

submit_button = tk.Button(root, text="Connect", command=submit)
submit_button.pack()

result_label = tk.Label(root, text="")
result_label.pack()



# handle closing of the window
def on_closing():
    closing = True
    if client:
        client.close()  # Close the socket connection if it exists
        os._exit(0)
    root.destroy()


# Start the GUI main loop
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
