#!/usr/bin/env python

from flask import Flask, request, render_template, flash
import netaddr
from netaddr import AddrFormatError
from wakeonlan import wol
from wtforms.fields.core import StringField
from wtforms.validators import InputRequired, ValidationError
from flask_wtf import Form
import logging.config, yaml

APP_ADDRESS = "0.0.0.0"
APP_PORT = 5080

app = Flask(__name__)
app.secret_key = b'\xf4\x8f\x98>\xdd\x80Y{\xf7M\x163s|A_\xec\x1a\x04\xcf\xb4\x14\xf0\x14'

file = open('devices.yml')
config = yaml.load(file)
file.close()


def get_devices_safe():
    result = {}

    devices = config['devices']
    for name in devices:
        device = devices[name]

        address = None
        if 'address' in device:
            address = device['address']

        result[name] = {
            'alias': device['alias'],
            'address': address
        }

    return result


def get_device(address):
    devices = config['devices']
    bare = convert_to_bare(address)

    for name in devices:
        device = devices[name]
        if 'address' in device:
            if bare == device['address']:
                return device

    for name in devices:
        device = devices[name]
        if 'address' not in device:
            return device


def convert_to_bare(address):
    mac = netaddr.EUI(address)
    mac.dialect = netaddr.mac_bare
    return str(mac)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        address = request.form['address']
        secret = request.form['secret']

        try:
            bare = convert_to_bare(address)
            device = get_device(bare)
            if secret == device['secret']:
                flash("Waking up...")
                wol.send_magic_packet(bare)
                app.logger.debug("Waking up %s" % address)
            else:
                flash("Incorrect secret")
                app.logger.debug("Tried to auth with %s" % secret)
        except AddrFormatError:
            flash("Format error...")

    return render_template('base.html', devices=get_devices_safe())


if __name__ == '__main__':
    with open('logging.yml') as logfile:
        logconfig = yaml.load(logfile)
        logging.config.dictConfig(logconfig)
    app.run(debug=True, host=APP_ADDRESS, port=APP_PORT)
