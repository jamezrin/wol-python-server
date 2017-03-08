#!/usr/bin/env python

import socket
import binascii
import logging.config
import yaml
import sys
import os
from textwrap import wrap
from wakeonlan import wol

BIND_ADDRESS="0.0.0.0"
BIND_PORT=5009

def read_payload(payload):
    try:
        frame = payload[:12]
    
        if frame == 'ffffffffffff':
            repetitions = payload[12:]
            list = wrap(repetitions, 12)

            if len(list) == 16:
                return list[0]

    except Exception:
        pass

    raise ValueError("Received payload is not valid")

def main():
    logging.config.dictConfig(yaml.load(open('logging.conf')))
    logger = logging.getLogger('replicator')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((BIND_ADDRESS, BIND_PORT))

    while(1):
        try:
            data, addr = sock.recvfrom(102)
            logger.debug("Received packet from %s:%s" % (addr[0], addr[1]))
            
            payload = binascii.hexlify(data)
            logger.debug("Received payload: %s" % payload)
            
            try:
                target = read_payload(payload)
        
                logger.debug("Waking up: %s" % target)
                wol.send_magic_packet(target)

            except ValueError as error:
                logger.debug(error)

        except KeyboardInterrupt:
            sys.exit()


if __name__ == '__main__':
    main()

