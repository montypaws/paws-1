#Python Async Web Server (paws) 🐾
A stupidly simple and insanely fast multi-process asyncronous python web server powered by Python 3.5 asyncio

Installation
------------
if just using stock python:
```
pip3 install jinja2
python3 setup.py install
```
if using uvloop:
```
pip3 install uvloop jinja2
python3 setup.py install
```


What's New:
-----------
PAWS now has the ability to perform asyncronous requests via new `get`, `put`, `post`, and `delete` connection methods. Additionally, experimental SSL support exists within these methods, but not the main server (yet).

Older News:
-----------
PAWS has support for [uvloop](http://github.com/magicstack/uvloop) allowing increased speed by replacing the default asyncio loop construct with one running on top of libuv. By default uvloop is NOT used. To use it, pass `use_uvloop=True` in the arguments for `run_server()`

Example
-------

```
from paws.paws import run_server

async def root(req, res):
  res.body = "hello world!"
  return res

def routing(app):
  app.add_route("/", root)

run_server(routing_cb=routing, host="127.0.0.1", port=8080, processes=4)
```

Requirements
------------
default:
- Python >= 3.5
- Jinja2 https://pypi.python.org/pypi/jinja2

if using uvloop:
- libuv
- [uvloop](http://github.com/magicstack/uvloop) >= 0.4.11

License
-------
paws is offered under the MIT license
