# -*- coding: utf-8 -*-

from flask import Flask, g, jsonify, Response
import os, sys, json, subprocess
import soco
import requests
PATH_TO_WEMO_CACHE = '/tmp/homeslice.cache.json'

class Wemo(object):
    PATH_TO_WEMO = 'wemo'

    def __init__(self, id, name, kind):
        self.id, self.name, self.kind = id, name, kind

    def on(self):
        subprocess.check_output("""{} switch "{}" on""".format(self.PATH_TO_WEMO, self.name), shell=True)

    def off(self):
        subprocess.check_output("""{} switch "{}" off""".format(self.PATH_TO_WEMO, self.name), shell=True)

    def to_dict(self):
        return dict(id=self.id, name=self.name, kind=self.kind)

    @classmethod
    def find_configured(cls, config):
        wemos = {}

        # FIXME: it would be nice to use ouimeaux lib but it really doesn't want to coexist with flask.
        #
        out = subprocess.check_output("{} list".format(cls.PATH_TO_WEMO), shell=True)
        wemos_found = [ line.split(':')[1].strip() for line in out.splitlines() ]

        for wemo_name in wemos_found:
            for entry in config:
                if wemo_name == entry.get('wemo switch'):
                    wemo_id=entry['id']
                    wemos[wemo_id] = Wemo(wemo_id, wemo_name, 'switch')
        return wemos

app = Flask(__name__)

def reboot_sonos(z):
    requests.get("http://{}:1400/reboot".format(z.ip_address))

def get_wemos():
    if not hasattr(g, 'wemos'):
        g.wemos = app.config['wemos']
    return g.wemos

def get_sonos():
    if not hasattr(g, 'sonos'):
        g.sonos = soco.discover()
    return g.sonos

@app.route('/')
def root():
    return "Homeslice!"

@app.route('/api/v0/wemos/', methods=('GET',))
def api_v0_wemos():
    wemos = [ wemo.to_dict() for wemo in get_wemos().values() ]

    return Response(json.dumps(wemos),  mimetype='application/json')

@app.route('/api/v0/wemos/switches/', methods=('GET',))
def api_v0_wemos_switches():
    wemos = [ wemo.to_dict() for wemo in get_wemos().values() if wemo.kind == 'switch' ]

    return Response(json.dumps(wemos),  mimetype='application/json')

@app.route('/api/v0/wemos/switches/<switch_id>/on/', methods=('POST',))
def api_v0_wemo_on(switch_id):
    get_wemos()[switch_id].on()

    return('OK')

@app.route('/api/v0/wemos/switches/<switch_id>/off/', methods=('POST',))
def api_v0_wemo_off(switch_id):
    get_wemos()[switch_id].off()

    return('OK')

@app.route('/api/v0/sonos/', methods=('GET',))
def api_v0_sonos_plural():
    sonos = [ dict(name=z.player_name,
                   group=z.group.uid,
                   volume=z.volume,
                   is_coordinator=z.is_coordinator,
                   mute=z.mute,
                   current_track=z.get_current_track_info()['title']) for z in get_sonos() ]
    return Response(json.dumps(sonos),  mimetype='application/json')

@app.route('/api/v0/sonos/reboot/', methods=('POST',))
def api_v0_sonos_reboot():
    for z in get_sonos():
        reboot_sonos(z)
    return('OK')

@app.route('/api/v0/sonos/<name>/', methods=('GET',))
def api_v0_sonos_singular(name):
    sonos = [ dict(name=z.player_name,
                   group=z.group.uid,
                   volume=z.volume,
                   is_coordinator=z.is_coordinator,
                   mute=z.mute,
                   current_track=z.get_current_track_info()['title']) for z in get_sonos()
                if z.player_name == name ][0]
    return Response(json.dumps(sonos),  mimetype='application/json')

@app.route('/api/v0/sonos/play/', methods=('POST',))
def api_v0_sonos_play():
    sonos = next((z for z in get_sonos() if z.is_coordinator), None)
    if sonos is not None:
        sonos.play()

    return('OK')

@app.route('/api/v0/sonos/pause/', methods=('POST',))
def api_v0_sonos_pause():
    sonos = next((z for z in get_sonos() if z.is_coordinator), None)
    if sonos is not None:
        sonos.pause()

    return('OK')

@app.route('/api/v0/sonos/volume/up/', methods=('POST',))
def api_v0_sonos_volume_up():
    for sonos in get_sonos():
        sonos.volume += 10

    return('OK')

@app.route('/api/v0/sonos/volume/down/', methods=('POST',))
def api_v0_sonos_volume_down():
    for sonos in get_sonos():
        sonos.volume -= 10

    return('OK')

def configure(path_to_config):
    with open(path_to_config) as config_file:
       config = json.loads(config_file.read())
       # FIXME: validate config
       app.config['homeslice'] = config

    if os.path.exists(PATH_TO_WEMO_CACHE):
        with open(PATH_TO_WEMO_CACHE, 'r') as f:
            wemo_dicts = json.loads(f.read())

        app.config['wemos'] = dict([ ( d['id'], Wemo(d['id'], d['name'], d['kind']) ) for d in wemo_dicts ])
    else:
        app.config['wemos'] = Wemo.find_configured(app.config['homeslice'])
        the_json = json.dumps([ wemo.to_dict() for wemo in app.config['wemos'].values() ])

        with open(PATH_TO_WEMO_CACHE, 'w') as f:
            f.write(the_json)

if __name__ == '__main__':
    configure(sys.argv[1])
    app.run(host='0.0.0.0', debug=True)
