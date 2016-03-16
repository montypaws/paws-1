#!/usr/bin/python3

#constants
CRLF = '\r\n'
HTTP_STANDARD = 'HTTP/1.1'
SP = ' '
STATUS_DICT = {'200':'OK',
               '404':'Not Found'}
SEP = ':'

class HttpResponse:
    raw = None
    text = None
    headers_dict = {'content-type':'text/html'}
    status = ''
    body = ""

    def __init__(self, status=200):
        self.status = str(status)

    def add_header(self, key, value):
        self.headers_dict[key] = value

    def _render(self):
        start_line = HTTP_STANDARD + SP + self.status + SP + STATUS_DICT[self.status] + CRLF

        headers=''
        for key, value in self.headers_dict.items():
            headers += key + SEP + value + CRLF

        self.text = start_line + headers + CRLF + self.body
        self.raw = self.text.encode()


class HttpRequest:
    raw = None
    text = None
    headers_dict = {}
    status = None
    body = ''
    resource = ''
    request_type = ''
    params= {}
    wildcards={}

    def __init__(self, raw=None):
        if raw:
            self.parse(raw)
        else:
            pass

    def parse(self, raw):
        self.raw = raw

        if type(self.raw) is bytes:
            data = self.raw.decode()
        else:
            data = self.raw

        #print(data)

        #determine type of request, and resource requested
        self.start_line = data.split(CRLF)[0]
        self.request_type = self.start_line.split(SP)[0].strip(SP)
        self.resource = self.start_line.split(SP)[1].strip(SP)

        #process parameters
        if '?' in self.resource:
            self.resource, params = self.resource.split('?')
            for param in params.split('&'):
                key,token = param.split('=')
                self.params[key]=token

        #if ends with a / remove it
        if self.resource.endswith('/') and len(self.resource) > 1:
            self.resource = self.resource[:-1]

        #process headers and body
        in_headers = True
        for item in data.split(CRLF)[1:]:
            if in_headers:
                index = item.find(':')
                k = item[:index]
                if k:
                    v = item[index+1:].strip(SP)
                    self.headers_dict[k] = v
                else:
                    in_headers = False
            else:
                self.body = item
                break

        #print('start_line:\n{}'.format(self.start_line))
        #print('headers:\n{}'.format(self.headers_dict))
        #print('body:\n{}'.format(self.body))
        #print('length: {}'.format(len(self.body)))
