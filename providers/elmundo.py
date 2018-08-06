import time
import re

import CommonFunctions as common

from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
from tvboxcore import logger

class ElMundo(Downloader):

    MAIN_URL = "http://www.elmundo.es"
    LAST_NEWS_RSS = "http://estaticos.elmundo.es/elmundo/rss/portada.xml"

    @staticmethod
    def getChannels(page):
        x = []
        if page == '0':
            url = ElMundo.LAST_NEWS_RSS
            logger.debug("news rss url is: "+url)
            bruteResult = ElMundo.getContentFromUrl(url=url,launchLocation=True,ajax=False,referer=ElMundo.MAIN_URL)
            logger.debug("brute response: "+bruteResult)
            lists = common.parseDOM(bruteResult, "item")
            if len(lists) > 0:
                logger.info("counted: " + str(len(lists)))
                for item in lists:
                    name = common.parseDOM(item, "title")[0].encode("utf-8")
                    link = common.parseDOM(item, "link")[0].encode("utf-8")
                    logger.info("Added: " + name + ", url: " + link)
                    element = {}
                    element["title"] = name.replace('<![CDATA[','').replace("]]>","")
                    element["link"] = link
                    try:
                        img = common.parseDOM(item, "media:content", ret="url")[0].encode("utf-8")
                        logger.debug("thumbnail is: "+img)
                        element["thumbnail"] = img
                    except:
                        logger.debug("Could not be extracted any img. :'(")
                    x.append(element)
        else:
            html = ElMundo.getContentFromUrl(url=page,launchLocation=True,referer=ElMundo.MAIN_URL).decode('iso-8859-15').encode('utf8')
            startRegex = '<article class="news-item" itemscope itemtype="http://schema.org/NewsArticle">'
            body = Decoder.extract(startRegex,'<h3 class="list-header">',html)
            if 'class="comentarios ' in body:
                body = body[:body.find('class="comentarios ')]
            if '<a href="#ancla_comentarios">' in body:
                replacedBy = Decoder.extract('<a href="#ancla_comentarios">',"</a>",body)
                logger.debug("removing: "+replacedBy)
                body = body.replace(replacedBy,"")
            logger.debug("removing html: "+body)
            body = Decoder.removeHTML(body)
            if ' Twitter Facebook Enviar ' in body:
                body = body.replace(" Twitter Facebook Enviar ","\n")
            if ":" in body: #search by time
                index = body.find(":")
                try:
                    figure = int(body[index+1]) #it's a number
                except: #it's not a number, so needs next one
                    body2 = body[index+1:]
                    index += body2.find(":")+1
                    pass
                body = body[:index+3]+"\n\n"+body[index+3:]
            logger.debug("html has removed from body!")
            element = {}
            element["link"] = page
            element["title"] = body
            element["thumbnail"] = ''
            x.append(element)
        return x

