# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para flashx
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand/
#------------------------------------------------------------

import re

from core import scrapertools
from core import logger
from core import jsunpack

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("streamondemand.servers.flashx url="+page_url)

    # Lo pide una vez
    headers = [['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14']]
    data = scrapertools.cache_page( page_url , headers=headers )

    match = scrapertools.find_single_match(data,"<script type='text/javascript'>(.*?)</script>")

    if match.startswith("eval"):	
        match = jsunpack.unpack(match)

    # Extrae la URL
    #{file:"http://f11-play.flashx.tv/luq4gfc7gxixexzw6v4lhz4xqslgqmqku7gxjf4bk43u4qvwzsadrjsozxoa/video1.mp4"}
    video_urls = []
    media_urls = scrapertools.find_multiple_matches(match,'\{file\:"([^"]+)"')
    for media_url in media_urls:
        if not media_url.endswith("png"):
            video_urls.append( [ media_url[-4:]+" [flashx]",media_url])

    for video_url in video_urls:
        logger.info("streamondemand.servers.flashx %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):

    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    #http://flashx.tv/z3nnqbspjyne
    #http://www.flashx.tv/embed-li5ydvxhg514.html
    patronvideos  = 'flashx.(?:tv|pw)/(?:embed-|)([a-z0-9A-Z]+)'
    logger.info("streamondemand.servers.flashx find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[flashx]"
        url = "http://www.flashx.pw/fxplay-%s.html" % match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'flashx' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve

def test():

    video_urls = get_video_url("http://www.flashx.tv/vpkvjdpkh972.html")

    return len(video_urls)>0
