import time
import re

import CommonFunctions as common

from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
from tvboxcore import logger

class ElPais(Downloader):

    MAIN_URL = "http://www.elpais.es"
    LAST_NEWS_RSS = "http://ep00.epimg.net/rss/tags/ultimas_noticias.xml"

    @staticmethod
    def getChannels(page):
        x = []
        if page == '0':
            url = ElPais.LAST_NEWS_RSS
            logger.debug("news rss url is: "+url)
            bruteResult = ElPais.getContentFromUrl(url=url,launchLocation=True,ajax=False,referer=ElPais.MAIN_URL)
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
                    element["link"] = link.replace('<![CDATA[','').replace("]]>","")
                    element["link"] = element["link"][:element["link"].find(".html")]+".html"
                    try:
                        img = common.parseDOM(item, "enclosure", ret="url")[0].encode("utf-8")
                        logger.debug("thumbnail is: "+img)
                        element["thumbnail"] = img
                    except:
                        logger.debug("Could not be extracted any img. :'(")
                    x.append(element)
        else:
            import urllib2
            page2 = ""
            response = urllib2.urlopen(page)
            for key1, value1 in sorted(response.info().items()):
                logger.debug("key: "+key1+", value: "+value1)
                if key1 == 'Location':
                    page2 = value1

            logger.debug(page2)
            if page2 == "":
                html = response.read()
            else:
                html = ElPais.getContentFromUrl(url=page,launchLocation=True,referer=ElPais.MAIN_URL)
            logger.debug("html is: "+html)
            startRegex = '<div class="articulo-cuerpo" id="cuerpo_noticia" itemprop="articleBody">'
            if startRegex in html:
                endRegex = '<div id="div_redes_sociales" '
                body = Decoder.extract(startRegex,endRegex,html)
                logger.debug("removing html: "+body)
                body = Decoder.removeHTML(body)
                logger.debug("html has removed from body!")
            else:
                body = ""
            element = {}
            element["link"] = page
            element["title"] = body
            element["thumbnail"] = ''
            x.append(element)
        return x

