# -*- coding: utf-8 -*-

from ouimeaux.environment import Environment
from flask import Flask, g
import os, sys, json, subprocess

class Wemos(object):
    def __init__(self, config):
        self.wemos = {}

        out = subprocess.check_output("wemo list", shell=True)
        wemos_found = [ line.split(':')[1].strip() for line in out.splitlines() ]
        for wemo_name in wemos_found:
            for entry in config:
                if wemo_name == entry.get('wemo switch'):
                    wemo_id=entry['id']
                    self.wemos[wemo_id] = dict(name=wemo_name)

app = Flask(__name__)

def get_wemos():
    if not hasattr(g, 'wemos'):
        g.wemos = app.config['wemos']
    return g.wemos

@app.route('/')
def root():
    return 'Homeslice!'

@app.route('/api/v0/wemos/', methods=('GET',))
def api_v0_wemos():
    wemos = [ dict(id=wemo_id, name=wemo_info['name']) for (wemo_id, wemo_info) in get_wemos().wemos.iteritems() ]

    return json.dumps(wemos)

if __name__ == '__main__':
    with open(sys.argv[1]) as config_file:
        config = json.loads(config_file.read())
        # FIXME: validate config
        app.config['homeslice'] = config
        app.config['wemos'] = Wemos(config)

    app.run(host='0.0.0.0', debug=True)