# TCP chat

A TCP chat room with RSA encryption and UDP device discovery. It's simple, and bypasses network firewall restrictions (e.g. for chatting on school wifi when discord/social media is blocked :) ).

## Installation
```shell
cd chat
```

```shell
pip install -r requirements.txt
```

## Usage

### Start Server

```shell
python multi_server.py
# python server.py  # OR single client
```


### Start GUI Client

```shell
python gui_multi_client.py
# python gui_client.py  # OR single client
```

## Troubleshooting

NOTE: UDP broadcasts will not work with WSL2 on Windows. WSL2 uses a virtual network interface, which means which means it doesn't have the same network visibility by default. (See [Microsoft docs](https://learn.microsoft.com/en-us/windows/wsl/networking#accessing-a-wsl-2-distribution-from-your-local-area-network-lan) for workarounds or run direclty on Windows instead).

If the client is not detecting the server broadcasts, make sure that UDP traffic is allowed on the broadcast port (in this case, 64667). For example, on Linux: `sudo ufw allow 64667/udp`
