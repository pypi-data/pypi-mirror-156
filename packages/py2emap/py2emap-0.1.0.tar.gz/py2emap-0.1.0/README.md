# py2emap
py2emap is a module that converts Python objects to Emap.

[Emap](https://github.com/rheniumNV/json2emap) is designed to be useful for exchange data between [Neos VR](https://wiki.neos.com/Main_Page) and external applications. 

## Installation
```bash
$ pip install py2emap
```

## How to use?
```python
import py2emap

pydata = {
    "name": "John",
    "age": 30,
    "address": {
        "street": "Main Street",
        "city": "New York",
        "state": "NY"
    }
}

string = py2emap.dumps(pydata)
print(string)
# =>
# l$#5$#v$#k0$#name$#v0$#John$#t0$#string$#k1$#age$#v1$#30$#t1$#number$#k2$#address.street$#v2$#Main Street$#
# t2$#string$#k3$#address.city$#v3$#New York$#t3$#string$#k4$#address.state$#v4$#NY$#t4$#string$#
```

Also, you can convert json to emap in command line.

```bash
$ python -m py2emap '{"key1": "value1", "key2":"value2"}'
l$#2$#v$#k0$#key1$#v0$#value1$#t0$#string$#k1$#key2$#v1$#value2$#t1$#string$#
```

It can take stdin.

```bash
$ echo '{"key1": "value1", "key2":"value2"}' | python -m py2emap -
l$#2$#v$#k0$#key1$#v0$#value1$#t0$#string$#k1$#key2$#v1$#value2$#t1$#string$#
```

By bringing these converted strings into Neos, objects can be easily restored and handled through LogiX.
Please see the [proposer's repository](https://github.com/rheniumNV/json2emap) for more details on how to handle this in Neos.