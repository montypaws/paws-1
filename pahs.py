#!/usr/local/bin/python3

import multiprocessing as mp
import asyncio
from jinja2 import Environment, FileSystemLoader
import config
import json
from pahttp import HttpRequest, HttpResponse
from paroute import Router

env = Environment(loader=FileSystemLoader('templates'))

def render_template(template, context):
    template = env.get_template(template)
    return template.render(context)



class InjestServer:
    pool = None
    router = None
    loop = None
    is_running=False
    task_queue=[]

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.router = Router()

    def run(self):
        # Each client connection will create a new protocol instance
        coro = self.loop.create_server(lambda: InjestProtocol(self.loop, self.handle_request), '127.0.0.1', 8080)
        server = self.loop.run_until_complete(coro)

        # Serve requests until Ctrl+C is pressed
        print('listening on {}'.format(server.sockets[0].getsockname()))

        try:
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
        if self.is_running:
            asyncio.ensure_future(task())
        else:
            self.task_queue.append(task)

    def add_route(self, route, call_back):
        #self.routes[route] = call_back
        self.router.add_route(route, call_back)

    async def handle_request(self, raw=None, transport=None):
        request = HttpRequest(raw)
        response = HttpResponse()

        response = await self.process_route(request, response)

        #build response
        response._render()

        #send response and close connection
        transport.write(response.raw)
        transport.close()

    async def process_route(self, request, response):
        """basic routing processing
        """

        match = self.router.parse_route(request.resource)

        if match:
            request.wildcards = match.match.groupdict()
            return await match.route.call_back(request, response)
        else:
            return self.bad_route(request, response)



    def bad_route(self, request,response):
        response.status = '404'
        response.body = '<h1>404 Not Found - BAD ROUTE</h1>'
        return response




class InjestProtocol(asyncio.Protocol):
    def __init__(self, loop, request_handler):
        self.loop = loop
        self.request_handler = request_handler

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        #handle the request
        asyncio.ensure_future(self.request_handler(raw=data, transport=self.transport))



def main():

    server = InjestServer()
    server.run()

if __name__ == '__main__':
    main()
