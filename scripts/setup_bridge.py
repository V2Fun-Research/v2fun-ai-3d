"""Legacy bridge to the runtime bundled in this skill."""
from pathlib import Path
import runpy
import sys

def setup_root():
    return Path(__file__).resolve().parent.parent

def run_script(name):
    scripts = setup_root() / 'scripts'
    sys.path.insert(0, str(scripts))
    runpy.run_path(str(scripts / name), run_name='__main__')
