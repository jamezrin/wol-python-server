#!/usr/bin/env python

import yaml

APP_ADDRESS = "0.0.0.0"
APP_PORT = 5080

def main():
    print yaml.load(open('devices.conf'))
    print 'This has not been implemented yet.'


if __name__ == '__main__':
  main()
