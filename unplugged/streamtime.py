# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Canal para streamtime
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
import re
import sys
import urlparse
import urllib2
import urllib

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "streamtime"
__category__ = "F"
__type__ = "generic"
__title__ = "streamtime"
__language__ = "IT"

host = "http://streamtime.altervista.org"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept', 'application/json, text/javascript, */*; q=0.01'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Host', 'streamtime.altervista.org'],
    ['Referer', host],
    ['Connection', 'keep-alive']
]


DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.streamtime mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist

def search(item, texto):
    logger.info("[streamtime.py] " + item.url + " search " + texto)
    item.url = host + "/search.php?name=" + texto + "&type=film"
    from lib import mechanize
    br = mechanize.Browser()
    br.set_handle_referer(False)
    br.set_handle_robots(False)
    br.set_handle_refresh(True)
    br.set_handle_redirect(True)
    try:
        if item.extra == "serie":
            return peliculas(item)
        else:
            return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item):
    logger.info("streamondemand.streamtime peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<a id="single-item" type="film" value="(.*?)" href="(.*?)"><img src="(.*?)" title="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedid, scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""
        scrapedurl = scrapedurl.replace(scrapedurl, "http://streamtime.altervista.org/get_links.php?type=film&id="+scrapedid)
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

