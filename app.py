#!/usr/local/bin/python3

import asyncio
import pahttp
from pahs import InjestServer, render_template
import config
import json
import content

OOPSIE = "<h3>Oopsie...</h3>"




async def root(request, response):
    response.body = render_template('root.html', {'nav_list' : await content.get_nav()})
    return response

async def index(req,res):
    res.body = render_template('index.html', {'nav_list': await content.get_nav(), 'courses': await content.get_courses()})
    return res

async def static(req, res):
    res.body = await content.get_file(config.STATIC_DIR + req.wildcards['filename'])
    return res

async def course(req, res):
    course = await content.get_asset(req.wildcards['aid'])
    res.body = render_template('course.html',{'nav_list' : await content.get_nav(), 'page_data':course, 'pages':course['pages']})
    return res

async def page(req,res):
    page = await content.get_asset(req.wildcards['aid'])
    if page:
        hcontent = await content.get_html_asset(page['content'])
        res.body = render_template('page.html', {'nav_list' : await content.get_nav(), 'page_data':page, 'content':hcontent})
        return res
    else:
        res.body = 'no page'
        return res

async def profile(req,res):
    res.body = render_template('profile.html', {'nav_list' : await content.get_nav(), 'uid':req.wildcards['uid']})
    return res

def main():
    app = InjestServer()

    app.add_route('/', root)
    app.add_route('/index', index)
    app.add_route('/static/{filename}', static)
    app.add_route('/course/{aid}', course)
    app.add_route('/page/{aid}', page)
    app.add_route('/profile/{uid}', profile)

    app.run()


if __name__ == '__main__':
    main()
