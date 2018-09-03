import sys, json
sys.stdout = sys.stderr

from homeslice import app as application
from homeslice import configure
configure('/homeslice/homeslice.json')
