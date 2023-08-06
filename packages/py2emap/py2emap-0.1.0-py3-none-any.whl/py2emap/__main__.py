import sys
import json
from . import py2emap

if sys.argv[1] == '-':
    print(py2emap.dumps(json.loads(sys.stdin.read())))
else:
    print(py2emap.dumps(json.loads(sys.argv[1])))
