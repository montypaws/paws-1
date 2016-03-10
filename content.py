#!/usr/local/bin/python3

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
