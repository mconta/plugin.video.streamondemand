# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for openload.io
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------
import json
import re
import time
import urllib

from core import logger
from core import scrapertools
from platformcode import captcha

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate']
]


def test_video_exists(page_url):
    logger.info("[openload.py] test_video_exists(page_url='%s')" % page_url)

    url = 'http://openload.co/f/%s' % page_url
    data = scrapertools.cache_page(url, headers=headers)

    if 'We are sorry!' in data:
        return False, 'File Not Found or Removed.'

    ticket_url = 'https://api.openload.io/1/file/dlticket?file=%s' % page_url
    result = scrapertools.cache_page(ticket_url, headers=headers)

    js_result = json.loads(result)
    if js_result['status'] != 200:
        return False, js_result['msg']

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[openload.py] url=" + page_url)
    video_urls = []

    ticket_url = 'https://api.openload.io/1/file/dlticket?file=%s' % page_url
    result = scrapertools.cache_page(ticket_url, headers=headers)

    js_result = json.loads(result)
    if js_result['status'] == 200:
        video_url = 'https://api.openload.io/1/file/dl?file=%s&ticket=%s' % (page_url, js_result['result']['ticket'])
        captcha_url = js_result['result'].get('captcha_url', None)
        if captcha_url:
            keyb = captcha.Keyboard(heading='', captcha=captcha_url)
            keyb.doModal()
            if keyb.isConfirmed():
                captcha_response = keyb.getText()
                video_url += '&captcha_response=%s' % urllib.quote(captcha_response)
        time.sleep(js_result['result']['wait_time'])
        result = scrapertools.cache_page(video_url, headers=headers)
        js_result = json.loads(result)
        if js_result['status'] == 200:
            url = js_result['result']['url'] + '?mime=true'
            _headers = urllib.urlencode(dict(headers))
            # URL del vídeo
            url += '|' + _headers
            video_urls.append([".mp4" + " [Openload]", url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = '(?://|\.)openload.../(?:embed|f)/([0-9a-zA-Z-_]+)'
    logger.info("[openload.py] find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for media_id in matches:
        titulo = "[Openload]"
        url = media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'openload'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
