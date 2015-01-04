from distutils.core import setup
import py2exe

setup(
    console=['wagon.py'],
    options={'py2exe':{'bundle_files':1,'compressed':1},},
    zipfile=None
)