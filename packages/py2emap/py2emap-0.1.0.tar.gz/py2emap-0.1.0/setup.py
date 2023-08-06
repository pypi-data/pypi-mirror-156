# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['py2emap']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'py2emap',
    'version': '0.1.0',
    'description': 'Convert Python objects to Emap which is friendly data exchange format for Neos VR',
    'long_description': '# py2emap\npy2emap is a module that converts Python objects to Emap.\n\n[Emap](https://github.com/rheniumNV/json2emap) is designed to be useful for exchange data between [Neos VR](https://wiki.neos.com/Main_Page) and external applications. \n\n## Installation\n```bash\n$ pip install py2emap\n```\n\n## How to use?\n```python\nimport py2emap\n\npydata = {\n    "name": "John",\n    "age": 30,\n    "address": {\n        "street": "Main Street",\n        "city": "New York",\n        "state": "NY"\n    }\n}\n\nstring = py2emap.dumps(pydata)\nprint(string)\n# =>\n# l$#5$#v$#k0$#name$#v0$#John$#t0$#string$#k1$#age$#v1$#30$#t1$#number$#k2$#address.street$#v2$#Main Street$#\n# t2$#string$#k3$#address.city$#v3$#New York$#t3$#string$#k4$#address.state$#v4$#NY$#t4$#string$#\n```\n\nAlso, you can convert json to emap in command line.\n\n```bash\n$ python -m py2emap \'{"key1": "value1", "key2":"value2"}\'\nl$#2$#v$#k0$#key1$#v0$#value1$#t0$#string$#k1$#key2$#v1$#value2$#t1$#string$#\n```\n\nIt can take stdin.\n\n```bash\n$ echo \'{"key1": "value1", "key2":"value2"}\' | python -m py2emap -\nl$#2$#v$#k0$#key1$#v0$#value1$#t0$#string$#k1$#key2$#v1$#value2$#t1$#string$#\n```\n\nBy bringing these converted strings into Neos, objects can be easily restored and handled through LogiX.\nPlease see the [proposer\'s repository](https://github.com/rheniumNV/json2emap) for more details on how to handle this in Neos.',
    'author': 'Nemnomi',
    'author_email': 'dev@nemnomi.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pluser/py2emap',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
