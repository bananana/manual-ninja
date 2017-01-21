import subprocess

MANPATH = subprocess.check_output('manpath').strip().split(':')
DEFAULT_MANPATH = '/usr/share/man'
MANPATH_OVERRIDE = []
