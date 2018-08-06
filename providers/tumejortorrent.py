# coding=utf-8
from tvboxcore.xbmcutils import XBMCUtils
import urllib
from tvboxcore.downloader import Downloader
from tvboxcore import logger
from tvboxcore.decoder import Decoder

try:
    import json
except:
    import simplejson as json


class TuMejorTorrent(Downloader):

    MAIN_URL = 'http://tumejortorrent.com/'
    SEARCH = "http://tumejortorrent.com/buscar"

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("page: " + page)
        if (str(page) == "0"):
            html = TuMejorTorrent.getContentFromUrl(url=TuMejorTorrent.MAIN_URL)
            menuHtml = Decoder.extract('<nav class="nav nav3" ', '</nav>', html)
            i=0
            for itemHtml in menuHtml.split("<li>"):
                logger.debug("li --> HTML is: " + itemHtml)
                if i>1 and "href=" in itemHtml and 'title="' in itemHtml:
                    item = {}
                    title = Decoder.extract('title="', '"', itemHtml)
                    if "Juegos " not in title:
                        #title = Decoder.removeHTML(title)
                        item["title"] = title
                        link = Decoder.extract('href="', '"', itemHtml)
                        if 'page=categorias' not in link:
                            item["link"] = link
                            x.append(item)
                i+=1
            search = {}
            search["title"] = XBMCUtils.getString(11018)
            search["link"] = ".search"
            x.append(search)

        elif page == '.search':
            # display keyboard, it will wait for result
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                x = TuMejorTorrent.search(text)
        elif '/descargar' in page or '/pelicula/' in page or '/varios/' in page or ('/miniseries/' in page and page != TuMejorTorrent.MAIN_URL+"miniseries/"): #decode
            logger.debug("torrent page detected...")
            link = TuMejorTorrent.extractProviderFromLink(page)
            element = {}
            element["link"] = link
            element["title"] = page
            element["finalLink"] = True
            x.append(element)
            logger.debug("DONE!")
        elif ("/miniseries/" in page or "/series/" in page or '/series-hd/' in page or '/series-vo/' in page) and page != TuMejorTorrent.MAIN_URL+'series/' and page != TuMejorTorrent.MAIN_URL+'series-hd/' and page != TuMejorTorrent.MAIN_URL+"series-vo/" and page != TuMejorTorrent.MAIN_URL+"miniseries/":
            html = TuMejorTorrent.getContentFromUrl(url=page,referer=TuMejorTorrent.MAIN_URL)
            logger.debug("series html is: " + html)
            if '<ul class="buscar-list">' in html:
                x = TuMejorTorrent.extractItems(html)
            elif 'http://tumejorjuego.com/redirect/index.php?link=descargar-torrent/' in html:
                link = "tumejortorrent.com/download/" + Decoder.extract('http://tumejorjuego.com/redirect/index.php?link=descargar-torrent/', '/";', html) + ".torrent"
                logger.debug("torrent obtained is: " + link)
                element = {}
                element["link"] = link
                element["finalLink"] = True
                element["title"] = "[T] "+Decoder.extract('<meta itemprop="description" content="',' - ',html)
                x.append(element)
        else:
            x = TuMejorTorrent.extractContentFromLink(page)
            logger.debug("finished else part for TuMejorTorrent")
        return x


    @staticmethod
    def search(text):
        searchUrl = "q="+urllib.quote_plus(text)
        html = TuMejorTorrent.getContentFromUrl(url=TuMejorTorrent.SEARCH,data=searchUrl,referer=TuMejorTorrent.MAIN_URL,launchLocation=True)
        logger.debug("search html is: "+html)
        return TuMejorTorrent.extractItems(html)

    @staticmethod
    def extractItems(html):
        x = []
        htmlList = Decoder.extract('<ul class="buscar-list">','<!-- end .buscar-list -->',html)
        logger.debug("search part is: "+htmlList)
        i=0
        for htmlElement in htmlList.split('<li>'):
            logger.debug("target html is: "+htmlElement)
            if i>0:
                element = TuMejorTorrent.extractElement(htmlElement)
                if '/juego/' not in element["link"]:
                    x.append(element)
            i+=1
        return x

    @staticmethod
    def extractElement(htmlElement):
        element = {}
        title = Decoder.extract(" title=\"", "\"", htmlElement).replace("Descargar ", "")
        link = Decoder.extract("href=\"", "\"", htmlElement)
        img = Decoder.extract("<img src=\"", "\"", htmlElement)
        element["title"] = title
        element["link"] = link
        element["thumbnail"] = img
        if '/series-hd/' not in link and '/series/' not in link:  # have to search again, sorry
            element["finalLink"] = True
        return element

    @staticmethod
    def extractProviderFromLink(page):
        html = TuMejorTorrent.getContentFromUrl(url=page,referer=TuMejorTorrent.MAIN_URL)
        logger.debug("html is: "+html)
        link = TuMejorTorrent.MAIN_URL+"download/"+Decoder.extract('http://tumejorjuego.com/redirect/index.php?link=descargar-torrent/','/";',html)+".torrent"
        logger.debug("link obtained is: "+link)
        return link

    @staticmethod
    def extractContentFromLink(page):
        x = []
        html = TuMejorTorrent.getContentFromUrl(url=page,referer=TuMejorTorrent.MAIN_URL)
        splitter = ""
        if '<ul class="pelilist">' in html:
            splitter = '<ul class="pelilist">'
        content = Decoder.extract(splitter,'</ul>',html)
        i = 0
        for line in content.split("<li>"):
            if i>0:
                element = TuMejorTorrent.extractElement(line)
                x.append(element)
            i+=1
        return x