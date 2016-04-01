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
__category__ = "F,T"
__type__ = "generic"
__title__ = "Scambio Etico(IT)"
__language__ = "IT"

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Host', 'forum.tntvillage.scambioetico.org'],
    ['Connection', 'keep-alive']
]

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
    data = scrapertools.cache_page(item.url,headers=headers,timeout=95)

    # Extrae las entradas (carpetas)
    #patron = '<td class=\'row4\'>\s*<a href="(.*?)"[^>]+>(.*?)</a>'
    patron = '<a href="(.*?)" title="discussione inviata[^>]+>(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        title=scrapedtitle.split("(")[0]
        tmdbtitle = scrapertools.decodeHtmlentities(title)
        url = scrapedurl
        url = url.replace("&amp;", "&")
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
        try:
           plot, fanart, poster, extrameta = info(tmdbtitle, scrapedthumbnail)

           itemlist.append( Item(channel=__channel__, action="play", fulltitle=scrapedtitle, show=scrapedtitle, title="[COLOR darkkhaki].torrent [/COLOR]""[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=url , thumbnail=poster , plot=str(plot) , fanart=fanart if fanart != "" else poster , extrameta=extrameta , folder=True) )
        except:
           itemlist.append( Item(channel=__channel__, action="play", fulltitle=scrapedtitle, show=scrapedtitle, title="[COLOR darkkhaki].torrent [/COLOR]""[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=url , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

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

    data = scrapertools.cache_page(item.url,timeout=95)
    logger.info("data="+data)
    link = scrapertools.get_match(data,'<a href=\'(magnet[^&]+)[^ ]+ title =\'Magnet link\'>')
    link = urlparse.urljoin(item.url,link)
    logger.info("link="+link)


    itemlist.append( Item(channel=__channel__, action=play, server="torrent", title=item.title , url=link , thumbnail=item.thumbnail , plot=item.plot , folder=False) )

    return itemlist

def info(title, thumbnail):
    logger.info("streamondemand.scambioetico info")
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(texto_buscado=title, tipo= "movie", include_adult="true", idioma_busqueda="it")
        count = 0
        if oTmdb.total_results > 0:
            #Mientras el thumbnail no coincida con el del resultado de la búsqueda, pasa al siguiente resultado
            while oTmdb.get_poster(size="w185") != thumbnail:
                count += 1
                oTmdb.load_resultado(index_resultado=count)
                if count == oTmdb.total_results : break
            extrameta = {}
            extrameta["Year"] = oTmdb.result["release_date"][:4]
            extrameta["Genre"] = ", ".join(oTmdb.result["genres"])
            extrameta["Rating"] = float(oTmdb.result["vote_average"])
            fanart=oTmdb.get_backdrop()
            poster=oTmdb.get_poster()
            plot=oTmdb.get_sinopsis()
            return plot, fanart, poster, extrameta
    except:
        pass	

