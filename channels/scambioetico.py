# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para scambioetico
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "scambioetico"
__category__ = "F"
__type__ = "generic"
__title__ = "Scambio Etico(IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.scambioetico mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Novità-Film .torrent stream[/COLOR]", action="peliculas", url="http://forum.tntvillage.scambioetico.org/index.php?showforum=401", thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"))
    #itemlist.append( Item(channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]", action="search", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"))
    
    return itemlist


def peliculas(item):
    logger.info("streamondemand.scambioetico peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<td class=\'row4\'>\s*<a href="(.*?)"[^>]+>(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        url = scrapedurl
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="play", fulltitle=scrapedtitle, show=scrapedtitle, title="[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=url , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = ']</b>&nbsp;<a href=\'(.*?)\'>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        url = urlparse.urljoin(item.url,matches[0])
        url = url.replace("&amp;", "&")
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Successivo>>[/COLOR]" , url=url , thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", folder=True) )

    return itemlist

def play(item):
    logger.info("[scambioetico.py] play")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    logger.info("data="+data)
    link = scrapertools.get_match(data,'<a href=\'(magnet[^&]+)[^ ]+ title =\'Magnet link\'>')
    link = urlparse.urljoin(item.url,link)
    logger.info("link="+link)


    itemlist.append( Item(channel=__channel__, action=play, server="torrent", title=item.title , url=link , thumbnail=item.thumbnail , plot=item.plot , folder=False) )

    return itemlist

