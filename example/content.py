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

import config
import asyncio
import json

#stupid cache
CACHE = {}

async def check_cache(filename):
    if filename in CACHE.keys():
        #print('cache hit...')
        return CACHE[filename]
    else:
        #print('cache miss...')
        return False


async def get_file(filename):
    #check if it is in the cache
    data = await check_cache(filename)
    if data:
        return data

    #not in cache, retrieve asset
    loop = asyncio.get_event_loop()
    try:
        with open(filename, 'r') as f:
            data = await loop.run_in_executor(None,f.read)
            CACHE[filename] = data
            return data
    except:
        print('failed to find: {}'.format(filename))
        return None


async def get_json(filename):
    data = await get_file(filename)
    if data:
        return json.loads(data)
    else:
        return None


async def get_asset(aid):
    return await get_json(config.ASSET_DIR+aid)


async def get_html_asset(aid):
    return await get_file(config.ASSET_DIR+aid)


async def get_nav():
    nav = await get_json(config.STATIC_DIR +'nav_items.json')
    return nav['nav_items']


async def get_courses():
    courses = await get_json(config.STATIC_DIR+'courses.json')
    return courses['course_list']
