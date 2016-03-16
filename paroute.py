#!/usr/local/bin/python3
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

"""
uses a similar dynamic process as aiohttp
"""
import re

class Route:
    '''simple class representing a route and its handler call_back
    '''
    pattern=None
    call_back=None
    formatter=None

    def __init__(self, pattern, formatter, call_back):
        self.pattern = pattern
        self.formatter = formatter
        self.call_back = call_back

    def match(self, path):
        return self.pattern.match(path)

class Match:
    '''simple data structure representing a route match
    '''
    match=None
    route=None

    def __init__(self, match, route):
        self.match = match
        self.route = route


class Router:
    '''dynamic route builder with heavy influence from aiohttp
    '''
    DYN = re.compile(r'^\{(?P<var>[a-zA-Z][_a-zA-Z0-9]*)\}$')
    GOOD = r'[^{}/]+'
    ROUTE_RE = re.compile(r'(\{[_a-zA-Z][^{}]*(?:\{[^{}]*\}[^{}]*)*\})')

    routes=[]

    def __init__(self):
        pass

    def add_route(self, path, call_back):
        '''use the dyn route re to construct a unique re for this route
        '''
        pattern = ''
        formatter =''
        for part in self.ROUTE_RE.split(path):
                match = self.DYN.match(part)
                if match:
                    pattern += '(?P<{}>{})'.format(match.group('var'), self.GOOD)
                    formatter += '{' + match.group('var') + '}'
                    continue

                if '{' in part or '}' in part:
                    raise ValueError("Invalid path '{}'['{}']".format(path, part))

                formatter += part
                pattern += re.escape(part)

        compiled = re.compile('^' + pattern + '$')

        route = Route(compiled, formatter, call_back)
        self.routes.append(route)



    def parse_route(self, path):
        '''attempt to find a matching route and return a Match if successful
        '''
        for route in self.routes:
            match = route.match(path)
            if match:
                return Match(match, route)
            else:
                continue

        return None
