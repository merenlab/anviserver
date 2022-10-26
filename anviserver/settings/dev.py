from anviserver.settings.base import *

#Override base.py settings here

try:
    from anviserver.settings.local import *
except:
    pass