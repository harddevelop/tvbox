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


class Elitetorrent(Downloader):

    MAIN_URL = 'http://www.elitetorrent.net'
    SEARCH = "http://www.elitetorrent.net/resultados/%s"

    @staticmethod
    def search(text,cookie=''):
        searchUrl = Elitetorrent.SEARCH % urllib.quote_plus(text)
        html = Elitetorrent.getContentFromUrl(url=searchUrl,referer=Elitetorrent.MAIN_URL,cookie=cookie,launchLocation=True)
        logger.debug("search html is: "+html)
        if '<meta http-equiv="Refresh" content="0;url=' in html:
            url2 = Decoder.extract('<meta http-equiv="Refresh" content="0;url=','"',html)
            url2 = url2[:url2.find("=")+1]+urllib.quote_plus(url2[url2.find("=")+1:])
            html = Elitetorrent.getContentFromUrl(url=url2, referer=searchUrl,launchLocation=True,cookie=Elitetorrent.cookie)
            logger.debug("search2 html2 is: " + html)
        else:
            logger.debug("ok, done!")
        return Elitetorrent.extractItems(html)

    @staticmethod
    def extractItems(html):
        x = []
        htmlList = Decoder.extract('<ul class="miniboxs miniboxs-ficha">','</ul>',html)
        i=0
        for htmlElement in htmlList.split("<li>"):
            if i>0:
                element = {}
                title = Decoder.extract(" title=\"","\"",htmlElement)
                link = Elitetorrent.MAIN_URL+Decoder.extract(" href=\"", "\"", htmlElement)
                img = Elitetorrent.MAIN_URL+"/"+Decoder.extract("<img src=\"","\"",htmlElement)
                element["title"] = title
                element["link"] = link
                element["thumbnail"] = img
                x.append(element)
            i+=1
        return x

    @staticmethod
    def extractProviderFromLink(page,cookie=''):
        html = Elitetorrent.getContentFromUrl(url=page,cookie=cookie,referer=Elitetorrent.MAIN_URL)
        logger.debug("html is: "+html)
        link = "magnet:"+Decoder.extract('<a href="magnet:','"',html)
        logger.debug("link obtained is: "+link)
        return link

    @staticmethod
    def extractContentFromLink(page,cookie=''):
        x = []
        html = Elitetorrent.getContentFromUrl(url=page,cookie=cookie,referer=Elitetorrent.MAIN_URL)
        if '<ul class="miniboxs miniboxs-ficha">' in html:
            logger.debug("thumbnails parts...")
            content = Decoder.extract('<ul class="miniboxs miniboxs-ficha">','</ul>',html)
            i = 0
            for line in content.split("<li>"):
                if i>0:
                    link = Elitetorrent.MAIN_URL+Decoder.extract('<a href="','"',line)
                    img = Elitetorrent.MAIN_URL+"/"+Decoder.extract('<img src="', '"', line)
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
    def getValidCookie():
        Downloader.getContentFromUrl(url=Elitetorrent.MAIN_URL)
        return "NOBOT="+Decoder.extract('NOBOT=',';',Downloader.cookie)+";"

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("page: "+page)
        cookie = Elitetorrent.getValidCookie()
        logger.debug("Using new cookie: "+cookie)
        if(str(page)=="0"):
            html = Elitetorrent.getContentFromUrl(url=Elitetorrent.MAIN_URL,cookie=cookie)
            menuHtml = Decoder.extract('<div class="wrap">','</div>',html)
            for itemHtml in menuHtml.split("<a"):
                logger.debug("li --> HTML is: "+itemHtml)
                if "href=" in itemHtml:
                    item = {}
                    item["title"] = Decoder.extract('">','<',itemHtml)
                    link = Decoder.extract('href="', '"', itemHtml)
                    if "://" not in link:
                        item["link"] = Elitetorrent.MAIN_URL+link
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
                x = Elitetorrent.search(text,cookie)
        elif '/torrent/' in page:
            logger.debug("torrent page detected...")
            link = Elitetorrent.extractProviderFromLink(page,cookie)
            element = {}
            element["link"] = link
            x.append(element)
        else:
            x = Elitetorrent.extractContentFromLink(page,cookie)

        return x