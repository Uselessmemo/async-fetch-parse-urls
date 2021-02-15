# async req and parse

import asyncio
import aiohttp
import aiofiles
import urllib
import time
import re

HREF_re = re.compile(r'href="(.*?)"')

async def fetch_url(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.text()
                    result = result.strip()
                else:
                    result = None
        except (aiohttp.client_exceptions.InvalidURL):
            print('Invalid http...')
            result = None
    return result

async def parse_url(url: str):
    html = await fetch_url(url)
    found_urls = set()
    if html == None:
        return None

    for raw_url in HREF_re.findall(html):
        try:
            abslink = urllib.parse.urljoin(url, raw_url)
        except (urllib.error.URLError, ValueError):
            pass
        else:
            if abslink.strip():
                found_urls.add(abslink.strip())
    
    response = await write_urls(found_urls)
    return (True if response else None)

async def write_urls(urls: set):
    if not urls:
        return None

    async with aiofiles.open('parsed_urls.txt', 'a') as f:
        for url in urls:
            await f.write(url + '\n')
    return True


async def main():
    with open('urls.txt', 'r') as f:
        urls = f.read().split('\n')
    with open('parsed_urls.txt', 'w') as f:
        f.write('')
    try:
        await asyncio.gather(*(parse_url(url) for url in urls))
    except RuntimeError:
        pass

if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print(f'{time.time() - start} sec...')