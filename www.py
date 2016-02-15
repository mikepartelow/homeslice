# -*- coding: utf-8 -*-

from flask import Flask, g
import os, sys, json, subprocess

PATH_TO_WEMO = 'wemo'

class Wemo(object):
    def __init__(self, name):
        self.name = name

    def on(self):
        subprocess.check_output("""{} switch "{}" on""".format(PATH_TO_WEMO, self.name), shell=True)

    def off(self):
        subprocess.check_output("""{} switch "{}" off""".format(PATH_TO_WEMO, self.name), shell=True)

# FIXME: why this? just an array of Wemo objs. merge them.
#

class Wemos(object):
    def __init__(self, config):
        self.wemos = {}

        # FIXME: it would be nice to use ouimeaux lib but it really doesn't want to coexist with flask.
        #
        out = subprocess.check_output("{} list".format(PATH_TO_WEMO), shell=True)
        wemos_found = [ line.split(':')[1].strip() for line in out.splitlines() ]

        for wemo_name in wemos_found:
            for entry in config:
                if wemo_name == entry.get('wemo switch'):
                    wemo_id=entry['id']
                    self.wemos[wemo_id] = dict(name=wemo_name, kind='switch', wemo=Wemo(wemo_name))

app = Flask(__name__)

def get_wemos():
    if not hasattr(g, 'wemos'):
        g.wemos = Wemos(app.config['homeslice']).wemos
    return g.wemos

def wemo_dict(wemo_id, wemo_info):
    return dict(id=wemo_id, name=wemo_info['name'], kind=wemo_info['kind'])

@app.route('/')
def root():
    return 'Homeslice!'

@app.route('/api/v0/wemos/', methods=('GET',))
def api_v0_wemos():
    wemos = [ wemo_dict(wemo_id, wemo_info) for (wemo_id, wemo_info) in get_wemos().iteritems() ]

    return json.dumps(wemos)

@app.route('/api/v0/wemos/switches/', methods=('GET',))
def api_v0_wemos_switches():
    wemos = [ wemo_dict(wemo_id, wemo_info) for (wemo_id, wemo_info) in get_wemos().iteritems() if wemo_info['kind'] == 'switch' ]

    return json.dumps(wemos)

@app.route('/api/v0/wemos/switches/<switch_id>/on/', methods=('POST',))
def api_v0_wemo_on(switch_id):
    get_wemos()[switch_id]['wemo'].on()

    return('OK')

@app.route('/api/v0/wemos/switches/<switch_id>/off/', methods=('POST',))
def api_v0_wemo_off(switch_id):
    get_wemos()[switch_id]['wemo'].off()

    return('OK')

if __name__ == '__main__':
    with open(sys.argv[1]) as config_file:
        config = json.loads(config_file.read())
        # FIXME: validate config
        app.config['homeslice'] = config

    app.run(host='0.0.0.0', debug=True)