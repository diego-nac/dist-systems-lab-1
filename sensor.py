import socket
import time
import random
import struct

MCAST_GROUP = '224.0.0.1'  
MCAST_PORT = 5000          

def get_temperature():
    return round(random.uniform(20.0, 30.0), 2)

def send_temperature_data(device_id, device_ip, device_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    group = socket.inet_aton(MCAST_GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        temperature = get_temperature()
        message = f"Sensor {device_id}, IP: {device_ip}, Porta: {device_port}, Temperatura: {temperature}°C"
        print(f"Enviando dados para o gateway: {message}")
        sock.sendto(message.encode(), (MCAST_GROUP, MCAST_PORT))
        time.sleep(10)

def main():
    device_id = "sensor_1"
    device_ip = "192.168.0.11"  
    device_port = 6001  
    send_temperature_data(device_id, device_ip, device_port)

if __name__ == "__main__":
    main()
