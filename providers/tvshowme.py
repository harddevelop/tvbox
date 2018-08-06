# -*- coding: utf-8 -*-
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader
from tvboxcore.xbmcutils import XBMCUtils

import urllib

class Tvshowme(Downloader):

    MAIN_URL = "http://tvshow.me/"

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("using tvshowme...")
        if str(page) == '0':
            page=Tvshowme.MAIN_URL
            html = Tvshowme.getContentFromUrl(page,"",Tvshowme.cookie,"")
            table = Decoder.extract('<ul>','</ul>',html)
            x = Tvshowme.extractElements(table)
        elif page=="search":
            #display keyboard, it will wait for result
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                page = "http://www.tvshow.me/?s="+urllib.quote(text)
            html = Tvshowme.getContentFromUrl(url=page)
            logger.debug(html)
            table = Decoder.extract('<div id="content"', '<h3 class="assistive-text">', html)
            logger.debug("table is: "+table)
            x = Tvshowme.extractLinks2(table)
        else:
            html = Tvshowme.getContentFromUrl(page, "", Tvshowme.cookie, Tvshowme.MAIN_URL)
            logger.debug(html)
            table = Decoder.extract('<div id="content"', '</article>', html)
            x = Tvshowme.extractLinks(table)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        element = {}
        element["title"] = "Search"
        element["link"] = "search"
        x.append(element)
        i=0
        for value in table.split('<li>'):
            if i>0:
                element = {}
                if 'title">' in value:
                    title = Decoder.extract('title">','</span>',value).replace("&#8211;","-")
                link = Decoder.extract('<a href="','"',value)
                element["title"] = title
                element["link"] = link
                logger.debug("append: "+title+", link: "+element["link"])
                x.append(element)
            i+=1
        return x

    @staticmethod
    def extractLinks(html):
        x = []
        i=0
        for value in html.split(' href='):
            if i>1:
                element = {}
                title = Decoder.extract('>','</a>', value).replace("&#8211;","-")
                link = Decoder.extract('"','"', value)
                element["title"] = title
                element["link"] = link
                element["finalLink"] = True
                if "<img" not in title and "tvshow.me" not in link:
                    logger.debug("append: " + title + ", link: " + element["link"])
                    x.append(element)
            i+=1
        return x

    @staticmethod
    def extractLinks2(html):
        x = []
        i=0
        for value in html.split('<h2 class="entry-title ">'):
            if i>1:
                logger.debug("partial html is: "+value)
                element = {}
                title = Decoder.extract(' title="','"', value)
                link = Decoder.extract('href="','"', value)
                element["title"] = title.replace("Permalink to ","").replace("&#8211;","-")
                element["link"] = link
                x.append(element)
            i+=1
        return x