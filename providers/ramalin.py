# -*- coding: utf-8 -*-
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Ramalin(Downloader):

    MAIN_URL = "http://www.ramalin.com/"

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("using Ramalin...")
        if str(page) == '0' or "/page/" in page:
            figure = "2"
            if str(page) == '0':
                page=Ramalin.MAIN_URL
            else:
                figure = str(int(page[page.find("/page/")+len("/page/"):])+1)
            html = Ramalin.getContentFromUrl(page,"",Ramalin.cookie,"")
            table = Decoder.extract('<ul class="article-list">','</ul>',html)
            x = Ramalin.extractElements(table)
            element = {}
            element["title"] = "Next"
            element["link"] = "http://www.ramalin.com/page/"+figure
            x.append(element)
        else:
            html = Ramalin.getContentFromUrl(page, "", Ramalin.cookie, Ramalin.MAIN_URL)
            logger.debug(html)
            table = Decoder.rExtract('#EXTM3U<br />"', '<!--Ad Injection:bottom-->', html[html.find("<body"):])
            logger.debug("using: "+table)
            x = Ramalin.extractLinks(table)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        i=0
        for value in table.split('<li id='):
            if i>0:
                element = {}
                title = Decoder.extract(' alt="','"',value)
                link = Decoder.extract('<a href="','"',value)
                img = Decoder.extract('<img src="','"',value)
                element["title"] = title
                element["link"] = link
                element["thumbnail"] = img
                if "<" not in title and "/" not in title:
                    logger.debug("append: "+title+", link: "+element["link"])
                    x.append(element)
            i+=1
        return x

    @staticmethod
    def extractLinks(html):
        x = []
        i=0
        for value in html.split('#EXTINF:'):
            if i>1:
                element = {}
                title = Decoder.extract(',','<br />', value)
                link = Decoder.rExtract('\n','<br />', value)
                element["title"] = title
                element["link"] = link
                element["finalLink"] = True
                logger.debug("append final link: " + title + ", link: " + element["link"])
                x.append(element)
            i+=1
        return x