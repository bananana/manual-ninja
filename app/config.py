import subprocess

SITE_TITLE = 'manual ninja'
DEFAULT_MANPATH = '/usr/share/man'
MANPATH = subprocess.check_output('manpath').strip().split(':')
