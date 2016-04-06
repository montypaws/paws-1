import asyncio
import aiohttp
from multiprocessing import Process
import time

NUM = 10000
URL = 'http://127.0.0.1:8080'

async def fetch_page(session, url):
    with aiohttp.Timeout(10):
        async with session.get(url) as response:
            assert response.status == 200
            return await response.read()

def do_eet(arg):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for i in range(int(NUM/4)):
        with aiohttp.ClientSession(loop=loop) as session:
            content = loop.run_until_complete(
                fetch_page(session, URL))
            print('{}: {} done...'.format(arg, i))

def main():

    procs = []

    start = time.time()

    for i in range(4):
        p = Process(target=lambda: do_eet(i))
        procs.append(p)
        p.start()

    for proc in procs:
        proc.join()

    finish = time.time()
    total = finish - start
    print("{} in {}: {} ms/req".format(NUM,total, (total/float(NUM))*1000))

if __name__ == '__main__':
    main()
