# wol.py
import socket

def send_wol(macaddress, broadcast="255.255.255.255"):
    mac = macaddress.replace(":", "").replace("-", "")
    if len(mac) != 12:
        raise ValueError("Неверный MAC-адрес")

    data = bytes.fromhex("FF" * 6 + mac * 16)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(data, (broadcast, 9))
    sock.close()
