#!/usr/bin/env python3
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
from paws.paws import get
from paws.pahttp import HttpRequest
from time import time
import signal
import uvloop
from multiprocessing import Process

start = 0.0
finish = 0.0
count = 100000
num_procs = 4
num = int(count/num_procs)

async def do_get():
    data = await get(url='http://localhost/hello', port=8080, ssl_context=False, 
        headers={}, debug=False)
    req = HttpRequest(data)
    #finish = clock()
    #print("req complete...")


def do_test():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    for i in range(num):
        foo = asyncio.ensure_future(do_get())
        loop.run_until_complete(foo)

def main():
    procs = []

    def finished(signum, frame):
        total = finish-start
        print("total time: {} ms/req".format(total * 1000))
        
        for proc in procs:
            if proc:
                proc.terminate()
    
    
    signal.signal(signal.SIGINT, finished)
    
    start = time()

    for i in range(num_procs):
        p = Process(target=do_test)
        procs.append(p)
        p.start()

    for proc in procs:
        proc.join()
    
    finish = time()

    total = finish-start
    print("total time: {} ms".format((total * 1000)))
    print("reqs per sec: {}".format((num*num_procs)/total))

if __name__ == '__main__':
    main()