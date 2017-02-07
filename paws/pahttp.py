'''
The MIT License (MIT)

Copyright (c) 2016, 2017 Erika Jonell (xevrem)

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

__all__ = ('HttpData', 'http_data_create', 'http_data_parse', 'http_data_add_header', 'http_data_render_request', 'http_data_render_response')

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

class HttpData:
    '''simple HTTP Data Holder
    '''
    raw = None
    text = None
    http_standard = HTTP_STANDARD
    headers = {}
    status = "200"
    body = ''
    resource = ''
    method = ''
    params= {}
    wildcards={}

def http_data_create(raw_data=None):
    if raw_data:
        return http_data_parse(HttpData(), raw_data)
    else:
        return HttpData()

def http_data_add_header(http_data, key, value):
    '''add a key-value pair to the headers
    '''
    http_data.headers[key] = value
    return http_data

def http_data_parse(http_data, raw):
    '''attempts to parse the raw request data
    '''
    http_data.raw = raw

    #if data supplied as raw bytes, decode
    if type(http_data.raw) is bytes:
        data = http_data.raw.decode()
    else:
        data = http_data.raw

    #determine type of request, and resource requested
    http_data.start_line = data.split(CRLF)[0]
    http_data.method = http_data.start_line.split(SP)[0].strip(SP)
    http_data.resource = http_data.start_line.split(SP)[1].strip(SP)

    #process parameters
    if QM in http_data.resource:
        http_data.resource, params = http_data.resource.split(QM)
        for param in params.split(AP):
            key,token = param.split(EQ)
            http_data.params[key]=token

    #if resource ends with a / remove it
    if http_data.resource.endswith('/') and len(http_data.resource) > 1:
        http_data.resource = http_data.resource[:-1]

    #process headers and body
    in_headers = True
    for item in data.split(CRLF)[1:]:
        if in_headers:
            index = item.find(':')
            k = item[:index]
            if k:
                v = item[index+1:].strip(SP)
                http_data.headers[k] = v
            else:
                in_headers = False
        else:
            http_data.body = item
            break

    return http_data

def http_data_render_request(http_data):
    '''renders all textual information into raw bytes
    '''
    start_line = http_data.method + SP + http_data.resource + SP + http_data.http_standard + CRLF

    hdrs=''
    for key, value in http_data.headers.items():
        hdrs += key + SEP + value + CRLF

    http_data.text = start_line + hdrs + CRLF + http_data.body + CRLF
    http_data.raw = http_data.text.encode()

    return http_data

def http_data_render_response(http_data):
    '''renders all textual information into raw bytes
    '''
    start_line = HTTP_STANDARD + SP + http_data.status + SP + STATUS_DICT[http_data.status] + CRLF

    hdrs=''
    for key, value in http_data.headers.items():
        hdrs += key + SEP + value + CRLF

    http_data.text = start_line + hdrs + CRLF + http_data.body
    http_data.raw = http_data.text.encode()

    return http_data
