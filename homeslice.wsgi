activate_this = '/opt/code/venv.homeslice/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys, json
sys.stdout = sys.stderr
sys.path.insert(0, '/opt/code/venv.homeslice/bin/')
sys.path.insert(0, '/opt/code/homeslice/')

from www import app as application
with open('/opt/code/homeslice/homeslice.json') as config_file:
    config = json.loads(config_file.read())
    # FIXME: validate config
    application.config['homeslice'] = config

