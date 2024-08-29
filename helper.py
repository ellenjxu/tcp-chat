import subprocess
import netifaces
import socket
import re


def get_non_loopback_ip():
    interface = netifaces.gateways()['default'][netifaces.AF_INET][1] # get name of the "default" gateway interface (e.g. (ip addr, interface name)))
    ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr'] # get ip address associated with interface
    return ip


def extract_port_numbers(ip_address):
    command = f"netstat -a | awk '$6 == \"ESTABLISHED\" && $4 ~ /^{ip_address}/ {{print $4}}'"
    output = subprocess.check_output(command, shell=True, universal_newlines=True)
    port_numbers = [int(port.split('.')[4]) for port in output.strip().split('\n')]
    return port_numbers


def validate_port(port):
    bad_ports = [63342]
    if port not in bad_ports:
        return True
    return False


def known_ports():
    possible_allowed = [64692, 64691, 64690, 64689, 64688, 64685, 64675, 64674]
    return possible_allowed


def find_devices_on_network(ip_address):
    command = f"arp -a | grep {ip_address.split('.')[0]}"
    output = subprocess.check_output(command, shell=True, universal_newlines=True)
    device_ip_list = [re.findall(r'\((.*?)\)', ip)[0] for ip in output.strip().split('\n')]
    return device_ip_list
    
