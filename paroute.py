#!/usr/local/bin/python3

"""
uses a similar dynamic process as aiohttp
"""
import re

class Route:
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
    match=None
    route=None

    def __init__(self, match, route):
        self.match = match
        self.route = route


class Router:

    DYN = re.compile(r'^\{(?P<var>[a-zA-Z][_a-zA-Z0-9]*)\}$')
    DYN_WITH_RE = re.compile(
        r'^\{(?P<var>[a-zA-Z][_a-zA-Z0-9]*):(?P<re>.+)\}$')
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

                '''
                match = DYN_WITH_RE.match(part)
                if match:
                    pattern += '(?P<{var}>{re})'.format(**match.groupdict())
                    formatter += '{' + match.group('var') + '}'
                    continue
                '''

                if '{' in part or '}' in part:
                    raise ValueError("Invalid path '{}'['{}']".format(path, part))

                formatter += part
                pattern += re.escape(part)

        compiled = re.compile('^' + pattern + '$')

        route = Route(compiled, formatter, call_back)
        self.routes.append(route)



    def parse_route(self, path):
        for route in self.routes:
            match = route.match(path)
            if match:
                return Match(match, route)
            else:
                continue

        return None


    def traverse_route(self, route_string):
        pass
