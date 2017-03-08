import socket
import binascii
from wakeonlan import wol

UDP_IP="0.0.0.0"
UDP_PORT=5009

def start():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))


    while(1):
        try:
            data, addr = sock.recvfrom(102)
            print "received packet from %s:%s" % (addr[0], addr[1])
            payload = binascii.hexlify(data)
            print "received payload:", payload
            target = read_payload(payload)
            print "waking up target:", target
            wol.send_magic_packet(target)
            
        except socket.error, msg:
            sys.exit()


# Returns the bare target MAC address of a WOL packet
# https://en.wikipedia.org/wiki/Wake-on-LAN
# http://serverfault.com/questions/632908/why-does-a-wake-on-lan-packet-contain-16-duplications-of-the-target-mac-address

def read_payload(payload):
    if not is_wol(payload):
        raise Exception('The defined parameter is not a valid wake-on-lan payload') 
    
    return payload[12:24]

# MAC address has 12 bytes (48 bits)
# First 12 bytes is the frame, ignore it
# Start from the frame and multiply by x + 1

def is_wol(payload):
    try:
        start = 0
        frame = payload[:12]
        if frame != 'ffffffffffff':
            start = 12
            return False
    
        list = []
        for x in range(16):
            rep = payload[start:start+12]
            start += 12
            list.append(rep)
    
        if len(list) != 16:
            return False
    
        return True
    except IndexError:
        return False

# Start the main function
if __name__ == '__main__':
    start()
