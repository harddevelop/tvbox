# coding=utf-8
from core.xbmcutils import XBMCUtils
import urllib
from core.downloader import Downloader
from core import logger
from core.decoder import Decoder

try:
    import json
except:
    import simplejson as json


class Peliculasbiz(Downloader):

    MAIN_URL = 'http://peliculasid.cc/'
    SEARCH = "http://peliculasid.cc/ajax/autocomplete.php?search="
    GOTO = "http://peliculasid.cc/goto/"

    @staticmethod
    def search(text):
        html = Peliculasbiz.getContentFromUrl(url=Peliculasbiz.SEARCH+urllib.quote_plus(text),referer=Peliculasbiz.MAIN_URL)
        return Peliculasbiz.extractItems(html)

    @staticmethod
    def extractItems(html):
        x = []
        jsonList = json.loads(html)
        for jsonElement in jsonList:
            element = {}
            title = Decoder.extract("target='_self'>","<",jsonElement)
            link = Decoder.extract("href='", "'", jsonElement)
            img = Decoder.extract("<img src='","'",jsonElement)
            element["title"] = title
            element["link"] = link
            element["thumbnail"] = img
            x.append(element)
        return x

    @staticmethod
    def extractProviderFromLink(page):
        data = 'id='+page
        html = Peliculasbiz.getContentFromUrl(url=Peliculasbiz.GOTO,data=data, referer=Peliculasbiz.MAIN_URL)
        logger.debug("html is: "+html)
        link = Decoder.extract('document.location = "','";',html).replace("cinefox.bio/u/","")
        logger.debug("link obtained is: "+link)
        return link

    @staticmethod
    def extractProvidersFromLink(page):
        x = []
        html = Peliculasbiz.getContentFromUrl(url=page,referer=Peliculasbiz.MAIN_URL)
        if '<ul class="opcoes">' in html:
            content = Decoder.extract('<ul class="opcoes">','</ul>',html)
            logger.debug("elements parts...")
            i = 0
            for line in content.split("</li>"):
                if i>1:
                    link = Decoder.extract('<li data-target="','"',line)
                    img = Decoder.extract('<img src="', '"', line)
                    title = Decoder.extract(' alt="', '"', line)
                    element = {}
                    element["link"] = link.replace("cinefox.cc/u/","")
                    element["thumbnail"] = img
                    element["title"] = title
                    element["finalLink"] = True
                    if len(title)>0:
                        x.append(element)
                i+=1
        elif '<ul id="category-thumbs">' in html:
            logger.debug("thumbnails parts...")
            content = Decoder.extract('<ul id="category-thumbs">','</ul>',html)
            i = 0
            for line in content.split("</li>"):
                if i>1:
                    link = Peliculasbiz.MAIN_URL+Decoder.extract('<a href="','"',line)
                    img = Decoder.extract('<img src="', '"', line)
                    title = Decoder.extract(' alt="', '"', line)
                    element = {}
                    element["link"] = link
                    element["thumbnail"] = img
                    element["title"] = title
                    if len(title)>0:
                        x.append(element)
                i+=1
        return x

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("page: "+page)
        if(str(page)=="0"):
            html = Peliculasbiz.getContentFromUrl(Peliculasbiz.MAIN_URL)
            menuHtml = Decoder.extract('<ul class="clearfix">','</ul>',html)
            for itemHtml in menuHtml.split("<li>"):
                if "href=" in itemHtml:
                    item = {}
                    item["title"] = Decoder.extract('">','<',itemHtml)
                    item["link"] = Decoder.extract('href="', '"', itemHtml)
                    x.append(item)
            search = {}
            search["title"] = XBMCUtils.getString(11018)
            search["link"] = ".search"
            x.append(search)

        elif page=='.search':
            #display keyboard, it will wait for result
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                x = Peliculasbiz.search(text)
        elif str(page).isdigit():
            logger.debug("numeric detected...")
            link = Peliculasbiz.extractProviderFromLink(page)
            element = {}
            element["link"] = link
            x.append(element)
        else:
            x = Peliculasbiz.extractProvidersFromLink(page)

        return x