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
from dateutil import tz

PATH_TO_THE_WEMO_CACHE_WE_HATE = '/var/www/.wemo/cache'
PATH_TO_WEMO_CACHE = '/var/cache/homeslice/homeslice.cache.json'
PATH_TO_DATABASE   = '/var/cache/homeslice/db/homeslice.sqlite3'
HOMESLICE_IP_ADDR  = '192.168.2.5'

class Wemo(object):
    PATH_TO_WEMO = 'wemo'

    def __init__(self, id, name, kind):
        self.id, self.name, self.kind = id, name, kind

    def on(self):
        subprocess.check_output("""rm -f {} ; {} {} "{}" on 2>&1""".format(PATH_TO_THE_WEMO_CACHE_WE_HATE, self.PATH_TO_WEMO, self.kind, self.name), shell=True)

    def off(self):
        subprocess.check_output("""rm -f {} ; {} {} "{}" off""".format(PATH_TO_THE_WEMO_CACHE_WE_HATE, self.PATH_TO_WEMO, self.kind, self.name), shell=True)

    def toggle(self):
        cmd = """rm -f {} ; {} {} "{}" status""".format(PATH_TO_THE_WEMO_CACHE_WE_HATE, self.PATH_TO_WEMO, self.kind, self.name)
        o = subprocess.check_output(cmd, shell=True)

        if "'state': 'False'" in o or "'state': '0'" in o:
            self.on()
        else:
            self.off()

    def to_dict(self):
        return dict(id=self.id, name=self.name, kind=self.kind)

    @classmethod
    def find_configured(cls, config):
        wemos = {}

        # FIXME: it would be nice to use ouimeaux lib but it really doesn't want to coexist with flask.
        #
        out = subprocess.check_output("{} list".format(cls.PATH_TO_WEMO), shell=True)
        # ('Light:', 'Garage North')
        wemos_found = [ line.split(',')[1].split("'")[1].strip() for line in out.splitlines() ]

        for wemo_name in wemos_found:
            for entry in config:
                if wemo_name == entry.get('wemo switch'):
                    wemo_id=entry['id']
                    wemos[wemo_id] = Wemo(wemo_id, wemo_name, 'switch')
                elif wemo_name == entry.get('wemo light'):
                    wemo_id=entry['id']
                    wemos[wemo_id] = Wemo(wemo_id, wemo_name, 'light')
        return wemos

app = Flask(__name__)

def connect_db():
    rv = sqlite3.connect(os.path.join(PATH_TO_DATABASE))
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def gmt_to_local(timestr):
    utc = datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=gmt_to_local.from_zone)
    return utc.astimezone(gmt_to_local.to_zone).isoformat()

gmt_to_local.from_zone = tz.tzutc()
gmt_to_local.to_zone = tz.tzlocal()

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def reboot_sonos(z):
    r = requests.get("http://{}:1400/reboot".format(z.ip_address))
    token = r.text.split('csrfToken')[1].split('"')[2]
    requests.post("http://{}:1400/reboot".format(z.ip_address), data=dict(csrfToken=token))

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

@app.route('/api/v0/clocktime/', methods=('GET',))
def api_v0_clocktime():
    return datetime.today().strftime("%-I%M")

@app.route('/doorbell.mp3')
def doorbell_mp3():
    return send_from_directory('/var/www/html', 'doorbell.mp3', as_attachment=True)

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
            sonos.play_uri("http://{}/doorbell.mp3".format(HOMESLICE_IP_ADDR), title="ding dong")
            time.sleep(6)
            for snap in snapshots:
                snap.restore(fade=False)
    return 'OK'

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

@app.route('/api/v0/wemos/lights/<light_id>/toggle/', methods=('POST',))
def api_v0_wemo_toggle(light_id):
    get_wemos()[light_id].toggle()

    return('OK')

@app.route('/api/v0/buttontimes/<button_name>/', methods=('GET',))
def api_v0_button_time(button_name):
    onoff = api_v0_button(button_name)
    time  = api_v0_clocktime()

    return onoff + ":" + time

@app.route('/api/v0/buttons/<button_name>/', methods=('GET',))
def api_v0_button(button_name):
    db = get_db()
    if request.method == 'GET':
        cur = db.execute('SELECT status FROM buttons WHERE name = ?', [button_name,])
        entry = cur.fetchone()
        return entry[0]

@app.route('/api/v0/buttons/<button_name>/on/', methods=('POST',))
def api_v0_button_on(button_name):
    db = get_db()
    if request.method == 'POST':
        db.execute("UPDATE buttons SET status='ON' WHERE name = ?", [button_name,])
        db.commit()
    return 'OK'

@app.route('/api/v0/buttons/<button_name>/off/', methods=('POST',))
def api_v0_button_off(button_name):
    db = get_db()
    if request.method == 'POST':
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

@app.route('/sonos/', methods=('GET',))
def sonos_plural():
    sonos = [ dict(name=z.player_name,
                   group=z.group.uid,
                   volume=z.volume,
                   is_coordinator=z.is_coordinator,
                   mute=z.mute,
                   current_track=z.get_current_track_info()['title']) for z in get_sonos() ]
    return render_template('sonos.html', sonos=sonos)

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

@app.route('/api/v0/logs/<log_name>/', methods=('GET', 'POST',))
def api_v0_logs(log_name):
    db = get_db()
    if request.method == 'GET':
        cur = db.execute('SELECT json, timestamp FROM log_entries WHERE log_name = ? ORDER BY id DESC', [log_name,])
        entries = cur.fetchall()
        return jsonify([ dict(entry=json.loads(e[0]), timestamp=gmt_to_local(e[1])) for e in entries ])

    elif request.method == 'POST':
        the_json = request.get_json()
        sys.stderr.write("POST\n")
        sys.stderr.write("POST: {}::{}\n".format(log_name, the_json))
        db.execute('INSERT INTO log_entries (log_name, json) VALUES (?, ?)', [log_name, json.dumps(the_json),])
        sys.stderr.write("POST2\n")
        db.commit()
        return jsonify(dict(result='OK'))

    return('OK')

@app.route('/api/v0/logs/<log_name>/homebridge/', methods=('GET',))
def api_v0_logs_last(log_name):
    db = get_db()
    if request.method == 'GET':
        cur = db.execute('SELECT json, timestamp FROM log_entries WHERE log_name = ? ORDER BY id DESC LIMIT 1', [log_name,])
        entry = json.loads(cur.fetchone()[0])
        tempC = (float(entry['tempF']) - 32) / (9.0/5.0)
        return jsonify(dict(temperature=tempC, humidity=float(entry['relhum'])))

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
    port = int(os.environ.get('HOMESLICE_PORT', 80))
    configure(sys.argv[1])
    app.run(host='0.0.0.0', port=port, debug=True)
