# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para corsaronero
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "corsaronero"
__category__ = "F"
__type__ = "generic"
__title__ = "Corsaro Nero (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://torcache.net/torrent/"
site = "http://corsaronero.info"

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.corsaronero mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Novità-Film .torrent stream[/COLOR]", action="peliculas", url="http://ilcorsaronero.info/cat/1", thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]", action="search", thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"))
    
    return itemlist

def search(item,texto):
    logger.info("[corsaronero.py] "+item.url+" search "+texto)
    item.url = "http://ilcorsaronero.info/argh.php?search="+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("streamondemand.corsaronero peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, timeout=10)

    # Extrae las entradas (carpetas)
    patron = '<A class="tab" HREF="(.*?)"[^>]+>(.*?)</A>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.replace("."," "))
        title = scrapedtitle.split("(")[0]
        tmdbtitle = scrapertools.decodeHtmlentities(title)
        url = scrapedurl
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
        try:
           plot, fanart, poster, extrameta = info(tmdbtitle, scrapedthumbnail)

           itemlist.append( Item(channel=__channel__, action="play", fulltitle=tmdbtitle, show=tmdbtitle, title="[COLOR darkkhaki].torrent [/COLOR]""[COLOR azure]"+tmdbtitle+"[/COLOR]" , url=url , thumbnail=poster , plot=str(plot) , extrameta=extrameta , fanart=fanart if fanart != "" else poster, folder=True) )
        except:
           itemlist.append( Item(channel=__channel__, action="play", fulltitle=scrapedtitle, show=scrapedtitle, title="[COLOR darkkhaki].torrent [/COLOR]""[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=url , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '<a href="([^>"]+)">pagine successive'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Successivo>>[/COLOR]" , url=scrapedurl , thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png", folder=True) )

    return itemlist

def play(item):
    logger.info("[corsaronero.py] play")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    logger.info("data="+data)
    link = scrapertools.get_match(data,'<a class="forbtn magnet" target="_blank" href="(magnet[^"]+)" title="Magnet" ></a>')
    link = urlparse.urljoin(item.url,link)
    logger.info("link="+link)


    itemlist.append( Item(channel=__channel__, action=play, server="torrent", title=item.title , url=link , thumbnail=item.thumbnail , plot=item.plot , folder=False) )

    return itemlist

def info(title, thumbnail):
    logger.info("streamondemand.corsaronero info")
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(texto_buscado=title, tipo="movie", include_adult="true", idioma_busqueda="it")
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

