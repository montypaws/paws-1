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

__all__ = ('HttpResponse', 'HttpRequest')

#constants
CRLF = '\r\n'
HTTP_STANDARD = 'HTTP/1.1'
SP = ' '
STATUS_DICT = {'200':'OK',
               '201':'Created',
               '202':'Accepted',
               '203':'Non-Authoratative Information',
               '205':'Reset Content',
               '206':'Partial Content',
               '207':'Multi-Status',
               '208':'Already Reported',
               '226':'IM Used',
               '300':'Multiple Choices',
               '301':'Moved Permanently',
               '302':'Found',
               '303':'See Other',
               '304':'Not Modified',
               '305':'Use Proxy',
               '306':'Switch Proxy',
               '307':'Temporary Redirect',
               '308':'Permanent Redirect',
               '400':'Bad Request',
               '401':'Unauthorized',
               '402':'Payment Required',
               '403':'Forbidden',
               '404':'Not Found',
               '405':'Method Not Allowed',
               '406':'Not Acceptable',
               '407':'Proxy Authentication Required',
               '407':'Request Timeout',
               '409':'Conflict',
               '410':'Gone',
               '411':'Length Requried',
               '412':'Precondition Failed',
               '413':'Payload Too Large',
               '414':'URI Too Long',
               '415':'Unsupported Media Type',
               '416':'Range Not Satisfiable',
               '417':'Expectation Failed',
               '418':'I\'m a teapot',
               '421':'Misdirected Request',
               '422':'Unprocessable Entity',
               '423':'Locked',
               '424':'Failed Dependency',
               '425':'Upgrade Requried',
               '428':'Precondition Required',
               '429':'Too Many Requests',
               '431':'Request Header Fields Too Large',
               '451':'Unavailable For Legal Reasons',
               '500':'Internal Server Error',
               '501':'Not Implemented',
               '502':'Bad Gateway',
               '503':'Service Unabailable',
               '504':'Gateway Timeout',
               '505':'HTTP Version Not Supported',
               '506':'Variant Also Negotiates',
               '507':'Insufficient Storage',
               '508':'Loop Detected',
               '510':'Not Extended',
               '511':'Network AUthentication Required'}
SEP = ':'
AP = '&'
QM = '?'
EQ = '='

class HttpResponse:
    '''simple HTTP Response class
    '''
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
        '''renders all textual information into raw bytes
        '''
        start_line = HTTP_STANDARD + SP + self.status + SP + STATUS_DICT[self.status] + CRLF

        headers=''
        for key, value in self.headers_dict.items():
            headers += key + SEP + value + CRLF

        self.text = start_line + headers + CRLF + self.body
        self.raw = self.text.encode()


class HttpRequest:
    '''simple HTTP Request class
    '''
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
        '''attempts to parse the raw request data
        '''
        self.raw = raw

        #if data supplied as raw bytes, decode
        if type(self.raw) is bytes:
            data = self.raw.decode()
        else:
            data = self.raw

        #determine type of request, and resource requested
        self.start_line = data.split(CRLF)[0]
        self.request_type = self.start_line.split(SP)[0].strip(SP)
        self.resource = self.start_line.split(SP)[1].strip(SP)

        #process parameters
        if QM in self.resource:
            self.resource, params = self.resource.split(QM)
            for param in params.split(AP):
                key,token = param.split(EQ)
                self.params[key]=token

        #if resource ends with a / remove it
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
