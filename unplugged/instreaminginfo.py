# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para instreaminginfo
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re
import sys
import time
import urllib2
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "instreaminginfo"
__category__ = "F"
__type__ = "generic"
__title__ = "instreaminginfo (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

headers = [
    ['Host', 'instreaminginfo.com'],
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', 'http://instreaming.info/'],
    ['Cache-Control', 'max-age=0']
]

host = "http://instreaming.info/news/"


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.instreaminginfo mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi Film Inseriti[/COLOR]",
                     action="peliculas",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png")]

    return itemlist


def peliculas(item):
    logger.info("streamondemand.instreaminginfo peliculas")
    itemlist = []

    # Descarga la pagina
    data = anti_cloudflare(item.url)

    ## ------------------------------------------------
    cookies = ""
    matches = re.compile('(.instreaming.info)\n', re.DOTALL).findall(config.get_cookie_data())
    for cookie in matches:
        name = cookie.split('\t')[5]
        value = cookie.split('\t')[6]
        cookies += name + "=" + value + ";"
    headers.append(['Cookie', cookies[:-1]])
    import urllib
    _headers = urllib.urlencode(dict(headers))
    ## ------------------------------------------------


    # Extrae las entradas (carpetas)
    patron = '<div class="item">\s*<a href="(.*?)">\s*[^>]+>\s*<img src="(.*?)" alt="(.*?)"[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patron = '<link rel="next" href="(.*?)" />'
    match = scrapertools.find_single_match(data, patron)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")

def play(item):
    logger.info("[instreaminginfo.py] play")

    data = scrapertools.cache_page(item.url, headers=headers)

    path = scrapertools.find_single_match(data, 'href="https://href.li/.([^"]+)"')
    url = path

    itemlist = servertools.find_video_items(data=url)

    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist

def anti_cloudflare(url):
    # global headers

    try:
        resp_headers = scrapertools.get_headers_from_response(url, headers=headers)
        resp_headers = dict(resp_headers)
    except urllib2.HTTPError, e:
        resp_headers = e.headers

    if 'refresh' in resp_headers:
        time.sleep(int(resp_headers['refresh'][:1]))

        scrapertools.get_headers_from_response(host + '/' + resp_headers['refresh'][7:], headers=headers)

    return scrapertools.cache_page(url, headers=headers)

