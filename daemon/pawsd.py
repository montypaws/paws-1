#!/usr/bin/env python3

from docopt import docopt
from paws import pahttp, render_template, run_server
import json

opts = """
Python Asyncronous Web Server Daemon

Usage:
    pawsd

Options:
    -h --help       Show this screen

"""

__all__ = ()

async def root(request, response):
    foo = {}
    foo['hello'] = 'world'
    foo['queries'] = request.params
    response.body = json.dumps(foo)
    return response

async def app_start(request, response):
    response.body = json.dumps(request.wildcards)
    return response

def routing(app):
    app.add_route('/', root)
    app.add_route('/app/start/{app}',app_start)

def main(args):
    run_server(routing_cb=routing, host='127.0.0.1', port=8080, processes=1)


if __name__ == "__main__":
    args = docopt(opts)
    print(args)
    main(args)
