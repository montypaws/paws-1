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

import asyncio
import pahttp
from pahs import InjestServer, render_template
import config
import json
import content


async def root(request, response):
    response.body = render_template('root.html', nav_list= await content.get_nav())
    return response


async def index(req,res):
    res.body = render_template('index.html', nav_list= await content.get_nav(), courses= await content.get_courses())
    return res


async def static(req, res):
    res.body = await content.get_file(config.STATIC_DIR + req.wildcards['filename'])
    return res


async def course(req, res):
    course = await content.get_asset(req.wildcards['aid'])
    res.body = render_template('course.html', nav_list= await content.get_nav(), page_data=course, pages=course['pages'])
    return res


async def page(req,res):
    page = await content.get_asset(req.wildcards['aid'])
    if page:
        hcontent = await content.get_html_asset(page['content'])
        res.body = render_template('page.html', nav_list= await content.get_nav(), page_data=page, content=hcontent)
        return res
    else:
        res.body = 'no page'
        return res


async def profile(req,res):
    if req.wildcards.keys():
        uid = req.wildcards['uid']
    else:
        uid = 'none'

    res.body = render_template('profile.html', nav_list= await content.get_nav(), uid=uid)
    return res


async def clear_cache():
    content.CACHE = {}
    print('cache cleared...')


def main():
    app = InjestServer()

    app.add_route('/', root)
    app.add_route('/index', index)
    app.add_route('/static/{filename}', static)
    app.add_route('/course/{aid}', course)
    app.add_route('/page/{aid}', page)
    app.add_route('/profile', profile)
    app.add_route('/profile/{uid}', profile)

    #app.add_task(clear_cache)

    app.run()


if __name__ == '__main__':
    main()
