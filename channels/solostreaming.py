# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale per solo-streaming.com
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import urlparse,urllib2,urllib, json
import re
import sys


from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools


import codecs
from datetime import datetime

__channel__ = "solostreaming"
__category__ = "S"
__type__ = "generic"
__title__ = "solostreaming"
__language__ = "IT"

DEBUG = True

host = "http://solo-streaming.com"
serietvhost = "http://serietv.solo-streaming.com/"
''''
if sys.version[0] == '2':
    print "Python 2"
    print "Encoding: " + sys.getdefaultencoding()
    reload(sys)
    sys.setdefaultencoding("utf-8")
    print "Encoding: " + sys.getdefaultencoding()
'''

def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.solostreaming mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[B][COLOR royalblue][SERIE TV][/COLOR][/B] [B][COLOR deepskyblue]ULTIMI EPISODI AGGIORNATI[/COLOR][/B]",
                     action="updateserietv",
                     url="%s/sod/api.php?get=serietv&type=elenco&order=multi&days=7" % host,
                     thumbnail="http://solo-streaming.com/images/sod/serietv1_225x330.jpg"),
                Item(channel=__channel__,
                     title="[B][COLOR royalblue][SERIE TV][/COLOR][/B] [B][COLOR deepskyblue]AGGIORNAMENTI MENSILI[/COLOR][/B]",
                     action="dailyupdateserietv",
                     url="%s/sod/api.php?get=serietv&type=elenco&order=multi&days=30" % host,
                     thumbnail="http://solo-streaming.com/images/sod/serietv2_225x330.jpg"),
                Item(channel=__channel__,
                     title="[B][COLOR royalblue][SERIE TV][/COLOR][/B] [B][COLOR deepskyblue]ELENCO COMPLETO SERIE TV[/COLOR][/B]",
                     action="elencoserie",
                     #url="%s/sod/api.php?get=serietv&type=elenco&order=alphabetic" % host,
                     thumbnail="http://solo-streaming.com/images/sod/serietv3_225x330.jpg"),
                Item(channel=__channel__,
                     title="[B][COLOR royalblue][SERIE TV][/COLOR][/B] [B][COLOR deepskyblue]CERCA...[/COLOR][/B]",
                     action="elencoserie",
                     #url="%s/sod/api.php?get=serietv&type=elenco&order=alphabetic" % host,
                     thumbnail="http://solo-streaming.com/images/sod/serietv4_225x330.jpg"),
                 Item(channel=__channel__,
                     title="[B][COLOR springgreen][ANIME][/COLOR][/B] [B][COLOR deepskyblue]ULTIMI EPISODI AGGIORNATI[/COLOR][/B]",
                     action="elencoserie",
                     #url="%s/sod/api.php?get=serietv&type=elenco&order=alphabetic" % host,
                     thumbnail="http://solo-streaming.com/images/sod/anime1_225x330.jpg")]
                     

    return itemlist

    
def elencoserie(item):
    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
    apielenco = "http://solo-streaming.com/sod/api.php?get=serietv&type=elenco&order=alphabetic&letter="
    itemlist = []
    for letter in alphabet:
        itemlist.append(
            Item(channel=__channel__,
                 action="elencoserieletter",
                 title="[B][COLOR deepskyblue]" +letter.upper() + "[/COLOR][/B]",
                 url=apielenco + letter,
                 thumbnail=item.thumbnail,
                 fulltitle="[B][COLOR deepskyblue]" + letter.upper() + "[/COLOR][/B]",
                 show="[B][COLOR deepskyblue]" + letter.upper() + "[/COLOR][/B]"))
    
    return itemlist

    
def elencoserieletter(item):
    
    itemlist = []

    # Descarga la pagina
    data = cache_jsonpage(item.url)
    logger.info("[solostreaming.py  dailyupdateserietv url=] " + item.url)
    logger.info("[solostreaming.py  dailyupdateserietv data=] " + str(data))
    
    for singledata in data['results']:
        serie = replaceshitchar(singledata['serieNome']).strip()
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle="[B][COLOR deepskyblue]" + serie + "[/COLOR][/B]",
                 show="[B][COLOR deepskyblue]" + serie + "[/COLOR][/B]",
                 title="[B][COLOR deepskyblue]" + serie + "[/COLOR][/B]",
                 url=singledata['uri'],
                 thumbnail=singledata['fileName'],
                 plot=scrapedplot,
                 folder=True))
    
    
    itemlist.append(
        Item(channel=__channel__,
             action="HomePage",
             title="[COLOR yellow]Torna Home[/COLOR]",
             folder=True))
    
    return itemlist

    
def cache_jsonpage(url):
    print "streamondemand.solostreaming cache_jsonpage url="+url
    response = urllib.urlopen(url)
    #print "streamondemand.core.scrapertools cache_jsonpage response="+ str(response)
    data = json.loads(response.read())
    #print data["total_results"]
    return data

    
def dailyupdateserietv(item):
    logger.info("streamondemand.solostreaming dailyupdateserietv")
    logger.info("[solostreaming.py dailyupdateserietv url=] " + item.url)
    #print "[solostreaming.py] " + item.url
    itemlist = []

    # Descarga la pagina
    data = cache_jsonpage(item.url)
    #logger.info("[solostreaming.py  dailyupdateserietv data=] " + item.url)
    #print "[solostreaming.py  dailyupdateserietv data=] " + str(data)
    
    dailyupdate = {}
    
    for singledata in data['results']:
        if len(dailyupdate) == 0:
            dailyupdate[singledata['created']] = {}
            dailyupdate[singledata['created']][0] = [singledata] 
        else:
            for index, (key, value) in enumerate(dailyupdate.items()):
                
                if key == singledata['created']:
                    dailyupdate[key][len(dailyupdate[key])] = [singledata]
                    break
                if index == len(dailyupdate) - 1:
                    dailyupdate[singledata['created']] = {}
                    dailyupdate[singledata['created']][0] = [singledata]
                    
   
    
    #http://forum.kodi.tv/showthread.php?tid=112916 
    for index, (key, value) in enumerate(dailyupdate.items()):
        
        try:
            #datekey = datetime.strptime(key, '%Y-%m-%d')
            dailyupdate[datetime.strptime(key, '%Y-%m-%d')] = value
        except TypeError:
            import time
            dailyupdate[datetime(*(time.strptime(key, '%Y-%m-%d')[0:6]))] = value
           
        del(dailyupdate[key])
        
    
    from collections import OrderedDict
    
    ordered = OrderedDict(sorted(dailyupdate.items(), key=lambda t: t[0], reverse=True))
    
    for index, (key, value) in enumerate(ordered.items()):
       
        datekey = datetime.strftime(key, '%d-%m-%Y')
        ordered[str(datekey)] = value
        del(ordered[key])
    
    

    for index, (key, value) in enumerate(ordered.items()):
        color = "deepskyblue"
        #if index%2 == 0:
        #    color =  "cyan"
        scrapedplot = ""
        
        extra = json.dumps(value)
       
       
        itemlist.append(
            Item(channel=__channel__,
                 action="showupdateserietv",
                 fulltitle="[B][COLOR " + color +"]" + key + "[/COLOR][/B] [COLOR white](" + str(len(value)) + " serie aggiornate)[/COLOR]",
                 show=key + " (" + str(len(value)) + " episodi aggiornati)",
                 title="[B][COLOR " + color +"]" + key + "[/COLOR][/B] [COLOR white](" + str(len(value)) + " serie aggiornate)[/COLOR]",
                 url="",
                 thumbnail="",
                 extra=extra,
                 plot=scrapedplot,
                 folder=True))
        
    totalresults = data["total_results"]
   
    return itemlist

 
def replaceshitchar(string):
    
    html_escape_table = {
            "&": "&amp;",
            "&": "&#038;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
            "'": "&rsquo;",
            "e": "&egrave;",
            "'": "&#8217;",
            "-": "&#8211;"
            }
    
    
    import re
    import htmllib
    p = re.compile(ur'&(#?)(\d{1,5}|\w{1,8});')
   
    def unescape(s):
        p = htmllib.HTMLParser(None)
        p.save_bgn()
        p.feed(s)
        return p.save_end()
    
     
    def process_match(m):
        
        print "Match: " + m.group()
        print "UTF" + unescape(m.group())
        print "Check" + unicode(unescape(m.group()), errors='ignore')
        unescaped = unicode(unescape(m.group()), errors='ignore')#unescape(m.group())
        shit = unescaped
        
        if shit == None or shit == "":
            shit = m.group()
            
        for key, value in html_escape_table.items():
            if value == shit:
               shit = key
               break
        return shit
            
        
 
        
        
    #string = entitiesfix(string)
    s = p.sub(process_match,  string)
    print "Mod " + s
    #print "Original" + string
    return s
    
    
def showupdateserietv(item):
    logger.info("streamondemand.solostreaming showupdateserietv")
    #logger.info("streamondemand.solostreaming showupdateserietv item.extra="  + item.extra)
    
    extra = json.loads(item.extra)
    #from pprint import pprint
    #pprint(extra)
                
    itemlist = []
    
    for index, (key, value) in enumerate(extra.items()):
         for singledata in value:
            scrapedplot = ""
           
            apisingle = host + "/sod/api.php?get=serietv&type=episodi&uri=" + singledata['uri'] + "&ep_num=" + singledata['ep_num'] + "&sub=" + singledata['type']
   
            serie =   replaceshitchar(singledata['serieNome']).strip()
            titolo = replaceshitchar(singledata['ep_title']).strip().lower().capitalize()
            
            itemlist.append(
                Item(channel=__channel__,
                     action="singleepisodios",
                     fulltitle="[COLOR white](" +  singledata['type'].upper() + ")[/COLOR] [B][COLOR royalblue]" 
                     + serie +  "[/COLOR][/B] [B][COLOR deepskyblue]- " 
                     + singledata['ep_num'] + " " 
                     + titolo + "[/COLOR][/B]",
                     show="[COLOR white](" +  singledata['type'].upper() + ")[/COLOR] [B][COLOR royalblue]" + serie + "[/COLOR][/B] [B][COLOR deepskyblue]- " + singledata['ep_num'] + " " 
                     +  titolo + "[/COLOR][/B]", 
                     title="[COLOR white](" +  singledata['type'].upper() + ")[/COLOR] [B][COLOR royalblue]" + serie + "[/COLOR][/B] [B][COLOR deepskyblue]- " + singledata['ep_num'] + " " 
                     +  titolo + "[/COLOR][/B]",
                     url=apisingle, 
                     thumbnail=singledata['fileName']))
        
    itemlist.append(
        Item(channel=__channel__,
             action="HomePage",
             title="[COLOR yellow]Torna Home[/COLOR]"))
    
    return itemlist
 
 
def updateserietv(item):
    logger.info("streamondemand.solostreaming update serietv")
    logger.info("[solostreaming.py] " + item.url)
    print "[solostreaming.py] " + item.url
    
    
    itemlist = []
        
    # Descarga la pagina
    data = cache_jsonpage(item.url)
    print "[solostreaming.py] " + str(data)
    
    totalresults = data["total_results"]
    
    for singledata in data['results']:
        apisingle = host + "/sod/api.php?get=serietv&type=episodi&uri=" + singledata['uri'] + "&ep_num=" + singledata['ep_num'] + "&sub=" + singledata['type']
        #dataapi = cache_jsonpage(apisingle)
        #logger.info("[solostreaming.py  dailyupdateserietv data=] " + apisingle)
        #link = ""
        #for links in dataapi:
        #    for singlelink in links['links']:
        #        link+=str(singlelink) + " "
        #print link
        
        serie =   replaceshitchar(singledata['serieNome']).strip()
        titolo = replaceshitchar(singledata['ep_title']).strip().lower().capitalize()
       
        itemlist.append(
            Item(channel=__channel__,
                 action="singleepisodios",
                 fulltitle="[COLOR white](" +  singledata['type'].upper() + ")[/COLOR] [B][COLOR royalblue]" + serie + "[/COLOR][/B] [B][COLOR deepskyblue]- " + singledata['ep_num'] + " " +  titolo + "[/COLOR][/B]",
                 show="[COLOR white](" +  singledata['type'].upper() + ")[/COLOR] [B][COLOR royalblue]" + serie + "[/COLOR][/B] [B][COLOR deepskyblue]- " + singledata['ep_num'] + " " +  titolo + "[/COLOR][/B]",
                 title="[COLOR white](" +  singledata['type'].upper() + ")[/COLOR] [B][COLOR royalblue]" + serie + "[/COLOR][/B] - [B][COLOR deepskyblue]" + singledata['ep_num'] + " " +  titolo + "[/COLOR][/B]",
                 url= apisingle,
                 thumbnail=singledata['fileName'],
                 ))
    
    
    itemlist.append(
        Item(channel=__channel__,
             action="HomePage",
             title="[COLOR yellow]Torna Home[/COLOR]"))
    
    return itemlist

    
def singleepisodios(item):
    logger.info("streamondemand.solostreaming singleepisodios")
    logger.info("[solostreaming.py] " + item.url)  
    dataapi = cache_jsonpage(item.url)
  
    link = ""
    for links in dataapi:
        for singlelink in links['links']:
            link+=str(singlelink) + " "
    print link
    itemlist = servertools.find_video_items(data=link)
    for videoitem in itemlist:
        #print videoitem
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__
        
    return itemlist
  
  
def serietv(item):
    logger.info("streamondemand.solostreaming serietv")
    logger.info("[solostreaming.py] " + item.url)
    print "[solostreaming.py] " + item.url
    itemlist = []

    # Descarga la pagina
    data = cache_jsonpage(item.url)
    print "[solostreaming.py] " + str(data)
    
    totalresults = data["total_results"]
    
    for singledata in data['results']:
        serie = replaceshitchar(singledata['serieNome']).strip()
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=serie,
                 show=serie,
                 title=serie,
                 url=serie,
                 thumbnail=singledata['fileName'],
                 plot=scrapedplot,
                 folder=True))
    
    
    itemlist.append(
        Item(channel=__channel__,
             action="HomePage",
             title="[COLOR yellow]Torna Home[/COLOR]",
             folder=True))
    
    return itemlist
 
 
def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")

    
def search(item, texto):
    logger.info("[solostreaming.py] " + item.url + " search " + texto)
    item.url = "%s/?s=%s" % (host, texto)
    try:
        return serietv(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

        
def episodios(item):
   
    logger.info("[solostreaming.py] episodios")
    
    hosturi = "http://solo-streaming.com/sod/api.php?get=serietv&type=episodi&uri="
    
    itemlist = []

    ## Descarga la página
    print hosturi + item.url
    data = cache_jsonpage(hosturi + item.url)
    print str(data)
    print str(item)
    for singledata in data:
        print singledata['ep_num'] + " - " + singledata['ep_title'] +" (" + singledata['type'] + ")"
        print singledata
        #for link in singledata['links']:
            #print link
        link = ""
        for singlelink in singledata['links']:
            link+=str(singlelink) + " "
        print link
        itemlist.append(
            Item(channel=__channel__,
                 action="findvid_serie",
                 title=singledata['ep_num'] + " - " + singledata['ep_title'] +" (" + singledata['type'] + ")",
                 url=item.url,
                 thumbnail=item.thumbnail,
                 extra=link,
                 fulltitle=item.title,
                 show=item.title))

    print "itemlist" + str(itemlist)
    
    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title=item.title,
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))
        itemlist.append(
            Item(channel=item.channel,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodios",
                 show=item.show))
    
    return itemlist
    

def findvid_serie(item):
    logger.info("[solostreaming.py] findvideos")
    
    #print item.title
    #print item.show
    
    ## Descarga la página
    data = item.extra
    
    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        print videoitem
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
