import subprocess

DEFAULT_MANPATH = '/usr/share/man'
MANPATH = subprocess.check_output('manpath').strip().split(':')
