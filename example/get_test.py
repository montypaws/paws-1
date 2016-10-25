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


async def do_get():
	#{'Host':'172.56.29.245'}
	data = await get(url='https://www.reddit.com/', port=443, ssl_context=True, headers={}, debug=True)
	req = HttpRequest(data)
	print(req.headers)

def main():
	loop = asyncio.get_event_loop()	
	task = asyncio.ensure_future(do_get())
	loop.run_until_complete	(task)
	loop.close()


if __name__ == '__main__':
	main()