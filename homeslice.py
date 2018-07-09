# -*- coding: utf-8 -*-

from flask import Flask, g, jsonify, Response, request, jsonify, send_from_directory, render_template
import os, sys, json, subprocess
import time
import soco
import soco.snapshot
import requests
from sqlite3 import dbapi2 as sqlite3
import json
from datetime import datetime

PATH_TO_DATABASE   = '/var/tmp/homeslice.sqlite3'

class SmartSwitch(object):
    def __init__(self, id, name, kind):
        self.id, self.name, self.kind = id, name, kind

    def to_dict(self):
        return dict(id=self.id, name=self.name, kind=self.kind)

    def on(self):
        return subprocess.call(self.on_cmd, shell=True)

    def off(self):
        return subprocess.call(self.off_cmd, shell=True)

    def toggle(self):
        if self.is_on():
            self.off()
        else:
            self.on()

    @classmethod
    def from_dict(cls, d):
        if 'wemo' in d['kind']:
            return Wemo(d['id'], d['name'], d['kind'].replace('wemo', '').strip())
        elif 'kasa' in d['kind']:
            return Kasa(d['id'], d['ip'], d['name'], d['kind'].replace('kasa', '').strip())

class Kasa(SmartSwitch):
    PATH_TO_KASA = 'pyhs100'
    
    def __init__(self, id, ip, name, kind):
        super(Kasa, self).__init__(id, name, kind)
        self.ip = ip

        self.on_cmd  = "LANG=C.UTF-8 {} --{} --ip {} on".format(self.PATH_TO_KASA, self.kind, self.ip)
        self.off_cmd = "LANG=C.UTF-8 {} --{} --ip {} off".format(self.PATH_TO_KASA, self.kind, self.ip)

    def is_on(self):
        cmd = "LANG=C.UTF-8 {} --{} --ip {} state".format(self.PATH_TO_KASA, self.kind, self.ip)
        out = subprocess.check_output(cmd, shell=True).decode('UTF-8')
        return u"Device state: ON" in out

class Wemo(SmartSwitch):
    PATH_TO_WEMO = 'wemo'
    PATH_TO_WEMO_CACHE = '/var/www/.wemo/cache'

    def __init__(self, id, name, kind):
        super(Wemo, self).__init__(id, name, kind)

        self.on_cmd  = """rm -f {} ; {} {} "{}" on 2>&1""".format(self.PATH_TO_WEMO_CACHE, self.PATH_TO_WEMO, self.kind, self.name)
        self.off_cmd = """rm -f {} ; {} {} "{}" off""".format(self.PATH_TO_WEMO_CACHE, self.PATH_TO_WEMO, self.kind, self.name)

    def is_on(self):
        cmd = """rm -f {} ; {} {} "{}" status""".format(self.PATH_TO_WEMO_CACHE, self.PATH_TO_WEMO, self.kind, self.name)
        out = subprocess.check_output(cmd, shell=True).decode('UTF-8')
        return '1' in out

app = Flask(__name__)

def connect_db():
    rv = sqlite3.connect(os.path.join(PATH_TO_DATABASE))
    rv.row_factory = sqlite3.Row
    return rv

@app.cli.command('initdb')
def initdb_command():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    print('Initialized the database.')

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def reboot_sonos(z):
    r = requests.get("http://{}:1400/reboot".format(z.ip_address))
    token = r.text.split('csrfToken')[1].split('"')[2]
    requests.post("http://{}:1400/reboot".format(z.ip_address), data=dict(csrfToken=token))

def get_switches():
    return app.config['switches']

def get_sonos():
    if not hasattr(g, 'sonos'):
        g.sonos = soco.discover()
    return g.sonos

@app.route('/')
def root():
    return "Homeslice!"

@app.route('/doorbell.mp3')
def doorbell_mp3():
    return send_from_directory('/var/www/html', 'doorbell.mp3', as_attachment=True)

@app.route('/sonos/', methods=('GET',))
def sonos_plural():
    sonos = [ dict(name=z.player_name,
                   group=z.group.uid,
                   volume=z.volume,
                   is_coordinator=z.is_coordinator,
                   mute=z.mute,
                   current_track=z.get_current_track_info()['title']) for z in get_sonos() ]
    return render_template('sonos.html', sonos=sonos)
    
@app.route('/api/v0/clocktime/', methods=('GET',))
def api_v0_clocktime():
    return datetime.today().strftime("%-I%M")

@app.route('/api/v0/doorbell/', methods=('POST',))
def api_v0_doorbell():
    snapshots = []
    for sonos in get_sonos():
    	if sonos.is_coordinator and len(sonos.group.members) > 1:
            for member in sonos.group.members:
                snap = soco.snapshot.Snapshot(member)
                snap.snapshot()
                snapshots.append(snap)
                if member.is_coordinator and \
                  member.get_current_transport_info()['current_transport_state'] == 'PLAYING':
                    member.pause()
            for member in sonos.group.members:
                if not member.mute:
                    member.volume = 40
            sonos.play_uri(app.config['doorbell_url'], title="ding dong")
            time.sleep(6)
            for snap in snapshots:
                snap.restore(fade=False)
    return 'OK'

@app.route('/api/v0/switches/', methods=('GET',))
def api_v0_switches():
    switches = map(lambda v: v.to_dict(), get_switches().values())
    return Response(json.dumps(switches),  mimetype='application/json')

@app.route('/api/v0/switches/<switch_id>/on/', methods=('POST',))
def api_v0_switch_on(switch_id):
    get_switches()[switch_id].on()
    return('OK')

@app.route('/api/v0/switches/<switch_id>/off/', methods=('POST',))
def api_v0_switch_off(switch_id):
    get_switches()[switch_id].off()
    return('OK')

@app.route('/api/v0/switches/<switch_id>/toggle/', methods=('POST',))
def api_v0_switch_toggle(switch_id):
    get_switches()[switch_id].toggle()
    return('OK')

@app.route('/api/v0/buttontimes/<button_name>/', methods=('GET',))
def api_v0_button_time(button_name):
    onoff = api_v0_button(button_name)
    time  = api_v0_clocktime()

    return onoff + ":" + time

@app.route('/api/v0/buttons/<button_name>/', methods=('GET',))
def api_v0_button(button_name):    
    if request.method == 'GET':
        db = get_db()
        cur = db.execute('SELECT status FROM buttons WHERE name = ?', [button_name,])
        entry = cur.fetchone()
        return entry[0]

@app.route('/api/v0/buttons/<button_name>/on/', methods=('POST',))
def api_v0_button_on(button_name):    
    if request.method == 'POST':
        db = get_db()
        db.execute("UPDATE buttons SET status='ON' WHERE name = ?", [button_name,])
        db.commit()
    return 'OK'

@app.route('/api/v0/buttons/<button_name>/off/', methods=('POST',))
def api_v0_button_off(button_name):    
    if request.method == 'POST':
        db = get_db()
        db.execute("UPDATE buttons SET status='OFF' WHERE name = ?", [button_name,])
        db.commit()
    return 'OK'

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
       cfg = json.loads(config_file.read())

    app.config['switches'] = dict( (d['id'], SmartSwitch.from_dict(d)) for d in cfg['switches'] )
    app.config['doorbell_url'] = cfg['doorbell_url']
    
if __name__ == '__main__':
    port = int(os.environ.get('HOMESLICE_PORT', 80))
    configure(sys.argv[1])
    app.run(host='0.0.0.0', port=port, debug=True)
