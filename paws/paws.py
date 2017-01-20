'''
The MIT License (MIT)

Copyright (c) 2016 Erika Jonell (xevrem)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import asyncio
import json
import socket
from multiprocessing import Process
import signal
from urllib.parse import urlparse
import ssl

from jinja2 import Environment, FileSystemLoader

from .pahttp import HttpData, STATUS_DICT, http_data_create, http_data_render_response, http_data_render_request
from .paroute import Router
from .palog import AsyncLogger

__all__ = ('InjestServer', 'InjestProtocol', 'render_template', 'run_server', 'logger', 'get', 'put', 'post', 'delete')

global logger, env

env = Environment(loader=FileSystemLoader('templates'))
logger = AsyncLogger()


def render_template(template, **kwargs):
    #simple template render handler
    template = env.get_template(template)
    return template.render(**kwargs)


class InjestServer:
    '''main HTTP server
    '''
    router = None
    loop = None
    is_running=False
    task_queue=[]
    debug = False
    log = None

    def __init__(self, host='127.0.0.1', port=8080, sock=None, debug=False):
        self.router = Router()
        self.host = host
        self.port = port
        self.debug = debug

        if sock:
            self.sock = sock
        else:
            #if no socket specified create one
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.bind((host, port))
            sock.listen(1024)
            sock.setblocking(False)
            self.sock = sock

    def run(self):
        '''sets up the server and starts running it on the event loop
        '''
        self.loop = loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.log = AsyncLogger(loop=self.loop, debug=self.debug)

        # Each client connection will create a new protocol instance
        coro = self.loop.create_server(lambda: InjestProtocol(self.loop, self.handle_request), backlog=1024, sock=self.sock)
        server = self.loop.run_until_complete(coro)

        # Serve requests until Ctrl+C is pressed
        self.log.log('listening on {}'.format(server.sockets[0].getsockname()))

        try:
            #see if there are tasks to initialize
            if len(self.task_queue) > 0:
                for task in self.task_queue:
                    asyncio.ensure_future(task())

            self.is_running = True
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            # Close the server
            server.close()
            self.loop.run_until_complete(server.wait_closed())
            self.loop.close()

    def add_task(self, task):
        '''queues a task for startup or issues it on active event loop
        '''
        if self.is_running:
            asyncio.ensure_future(task())
        else:
            self.task_queue.append(task)

    def add_route(self, route, call_back):
        '''create a new route to handle
        '''
        self.router.add_route(route, call_back)


    async def handle_request(self, raw=None, transport=None):
        '''handles an incomming HTTP request
        '''
        #create the request and response from the raw data
        request = http_data_create(raw)
        response = HttpData()

        #process the response
        response = await self.process_route(request, response)

        self.log.log('{} [{} - {}]: {}'.format(request.method, response.status, STATUS_DICT[response.status], request.resource))

        #build response
        http_data_render_response(response)

        #send response and close connection
        transport.write(response.raw)
        transport.close()


    async def process_route(self, request, response):
        """basic routing processing
        """

        #attempt to match the request to a route
        route = self.router.match_request(request)

        #execute the route if found or return bad-route
        if route:
            return await route.call_back(request, response)
        else:
            return self.bad_route(request, response)


    def bad_route(self, request, response):
        '''simple bad-route response
        '''
        response.status = '404'
        response.body = STATUS_DICT['404']
        return response


class InjestProtocol(asyncio.Protocol):
    '''basic asyncio protocol for handling all incoming requests
    '''
    def __init__(self, loop, request_handler):
        self.loop = loop
        self.request_handler = request_handler

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        #handle the request
        asyncio.ensure_future(self.request_handler(raw=data, transport=self.transport))


async def get(url, port=80, ssl_context=False, headers={}, body="", debug=False):
    '''basic get request
    '''
    return await do_request(url, port, ssl_context, "GET", headers, body, debug)


async def post(url, port=80, ssl_context=False, headers={}, body="", debug=False):
    '''basic post request
    '''
    return await do_request(url, port, ssl_context, "POST", headers, body, debug)


async def delete(url, port=80, ssl_context=False, headers={}, body="", debug=False):
    '''basic delete request
    '''
    return await do_request(url, port, ssl_context, "DELETE", headers, body, debug)


async def put(url, port=80, ssl_context=False, headers={}, body="", debug=False):
    '''basic put request
    '''
    return await do_request(url, port, ssl_context, "PUT", headers, body, debug)


async def do_request(url, port, ssl_context, method, headers, body, debug):
    '''enacts a request
    '''
    global logger

    loop = asyncio.get_event_loop()

    parsed = urlparse(url)

    #set default headers
    default_headers = {"Host" : "127.0.0.1",
        "User-Agent" : "paws/1.0.0",
        "Content-Type" : "text/html; charset=utf-8",
        "Connection" : "close"}

    #merge headers
    for key in default_headers.keys():
        if key in headers.keys():
            continue
        else:
            headers[key] = default_headers[key]

    headers['Host'] = parsed.netloc

    logger.log("Path: " + parsed.path, force_log=debug)
    logger.log("Netloc: " + parsed.netloc, force_log=debug)
    logger.log("Method: " + method, force_log=debug)
    logger.log("Headers: {}".format(headers), force_log=debug)
    logger.log("Body: " + body, force_log=debug)

    #establish the connection
    conn = loop.create_connection(lambda: RequestProtocol(parsed.path, method=method, headers=headers, body=body), host=parsed.netloc, port=port, ssl=ssl_context, server_hostname=parsed.netloc if ssl_context else None)

    trans, proto = await loop.create_task(conn)

    #await for the request to complete
    data = await proto.request_complete()

    #return the data
    return data


class RequestProtocol(asyncio.Protocol):
    '''Main single-shot request protocol
    '''

    data_complete = False
    data = b''

    def __init__(self, resource, method="GET", headers={}, body=""):
        request = http_data_create()
        request.resource = resource
        request.method = method
        request.headers = headers
        request.body = body
        http_data_render_request(request)
        self.foo = request

    def connection_made(self, transport):
        self.transport = transport
        self.transport.write(self.foo.raw)


    def data_received(self, data):
        self.data += data


    def eof_received(self):
        self.data_complete = True
        self.transport.close()


    def connection_lost(self, ex):
        self.data_complete = True
        self.transport.close()


    @asyncio.coroutine
    def request_complete(self):
        while not self.data_complete:
            yield
            continue

        return self.data


def run_server(routing_cb=None, host='127.0.0.1', port=8080, processes=2, use_uvloop=False, debug=False):
    '''initializes and launches the PAWS server
    '''

    if use_uvloop:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    #setup logger
    logger = AsyncLogger(loop=asyncio.get_event_loop(), debug=debug)

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.bind((host, port))
    sock.listen(1024)
    sock.setblocking(False)

    procs = []

    def interupt_signal(signum, frame):
        #process interrupt signal
        print('PAWS Shutting Down...')

        for proc in procs:
            if proc:
                proc.terminate()
                print('process terminated...')

        print('PAWS Shut down...')

    #set intterupt signal catcher
    signal.signal(signal.SIGINT, interupt_signal)



    for i in range(processes):
        app = InjestServer(host=host, port=port, sock=sock, debug=debug)

        routing_cb(app)

        p = Process(target=app.run)
        procs.append(p)
        p.start()

    for proc in procs:
        proc.join()
