# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para rapidvideo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import re

from core import jsunpack
from core import logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("[rapidvideo.py] test_video_exists(page_url='%s')" % page_url)

    page_url = page_url.replace('.tv/', '.org/')

    video_id = scrapertools.get_match(page_url, 'org/([A-Za-z0-9]+)')
    url = 'http://www.rapidvideo.org/embed-%s-607x360.html' % video_id

    data = scrapertools.cache_page(url)

    if "The file was removed from RapidVideo" in data:
        return False, "The file not exists or was removed from RapidVideo."

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[rapidvideo.py] url=" + page_url)

    page_url = page_url.replace('.tv/', '.org/')

    video_id = scrapertools.get_match(page_url, 'org/([A-Za-z0-9]+)')
    url = 'http://www.rapidvideo.org/embed-%s-607x360.html' % video_id

    data = scrapertools.cache_page(url)

    packed = scrapertools.get_match(data, "<script type='text/javascript'>eval.function.p,a,c,k,e,.*?</script>")
    unpacked = jsunpack.unpack(packed)
    media_url = scrapertools.get_match(unpacked, 'file:"([^"]+)"')

    video_urls = [[scrapertools.get_filename_from_url(media_url)[-4:] + " [rapidvideo.org]", media_url]]

    for video_url in video_urls:
        logger.info("[rapidvideo.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos de este servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://www.rapidvideo.tv/embed-xr1nb7cfh58a-607x360.html
    # http://www.rapidvideo.org/embed-xr1nb7cfh58a-607x360.html
    # http://www.rapidvideo.tv/xr1nb7cfh58a
    # http://www.rapidvideo.org/xr1nb7cfh58a

    patterns = [
        r'rapidvideo\....?/([A-Z0-9a-z]{12})',
        r'rapidvideo\....?/embed-([^-]{12})-'
    ]

    for pattern in patterns:

        logger.info("[rapidvideo.py] find_videos #" + pattern + "#")
        matches = re.compile(pattern, re.DOTALL).findall(data)

        for match in matches:
            titulo = "[rapidvideo]"
            url = "http://www.rapidvideo.org/" + match
            if url not in encontrados:
                logger.info("  url=" + url)
                devuelve.append([titulo, url, 'rapidvideo'])
                encontrados.add(url)
            else:
                logger.info(" url duplicada=" + url)

    return devuelve


def test():
    video_urls = get_video_url("http://www.rapidvideo.org/xr1nb7cfh58a")

    return len(video_urls) > 0

