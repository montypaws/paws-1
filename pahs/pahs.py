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
SOFTWARE.o
'''

import asyncio
import json

from jinja2 import Environment, FileSystemLoader

from .pahttp import HttpRequest, HttpResponse
from .paroute import Router

__all__ = ('InjestServer', 'InjestProtocol', 'render_template')

#setup jinja2 env
env = Environment(loader=FileSystemLoader('templates'))

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

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.router = Router()

    def run(self, ip='127.0.0.1', port=8080):
        '''sets up the server and starts running it on the event loop
        '''
        # Each client connection will create a new protocol instance
        coro = self.loop.create_server(lambda: InjestProtocol(self.loop, self.handle_request), ip, port)
        server = self.loop.run_until_complete(coro)

        # Serve requests until Ctrl+C is pressed
        print('listening on {}'.format(server.sockets[0].getsockname()))

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
        '''queues a task for startup or issues it on active event loop'''
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
        request = HttpRequest(raw)
        response = HttpResponse()

        #process the response
        response = await self.process_route(request, response)

        #build response
        response._render()

        #send response and close connection
        transport.write(response.raw)
        transport.close()

    async def process_route(self, request, response):
        """basic routing processing
        """

        #attempt to match the route
        match = self.router.parse_route(request.resource)

        #execute the route if found or return bad-route
        if match:
            request.wildcards = match.match.groupdict()
            return await match.route.call_back(request, response)
        else:
            return self.bad_route(request, response)



    def bad_route(self, request, response):
        '''simple bad-route response
        '''
        response.status = '404'
        response.body = '<h1>404 Not Found - BAD ROUTE</h1>'
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
