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

    MAIN_URL = 'https://www.elitetorrent.biz'
    SEARCH = "https://www.elitetorrent.biz/?s=%s&x=1&y=13"

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
                title = Decoder.extract(" title=\"","\"",htmlElement).replace(" torrent","")
                link = Decoder.extract(" href=\"", "\"", htmlElement)
                img = Elitetorrent.MAIN_URL+Decoder.extract(" src=\"","\"",htmlElement)
                logger.debug("link is %s " % link)
                element["title"] = title
                element["link"] = link
                element["thumbnail"] = img
                element["finalLink"] = True
                x.append(element)
            i+=1
        return x

    @staticmethod
    def extractProviderFromLink(page,cookie=''):
        html = Elitetorrent.getContentFromUrl(url=page,cookie=cookie,referer=Elitetorrent.MAIN_URL)
        logger.debug("html is: "+html)
        link = "magnet:"+Decoder.extract(' href="magnet:','"',html)
        if "&amp;" in link:
            link = link[:link.find("&amp;")]
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
                    link = Decoder.extract(' href="','"',line)
                    img = Elitetorrent.MAIN_URL+"/"+Decoder.extract(' src="', '"', line)
                    title = Decoder.extract(' alt="', '"', line).replace(" torrent","")
                    element = {}
                    element["link"] = link
                    element["thumbnail"] = img
                    element["title"] = title
                    element["finalLink"] = True
                    if len(title)>0:
                        x.append(element)
                i+=1
        return x

    @staticmethod
    def getValidCookie():
        Downloader.getContentFromUrl(url=Elitetorrent.MAIN_URL)
        return "NOBOT="+Decoder.extract('NOBOT=',';',Downloader.cookie)+";"

    @staticmethod
    def getChannels(page,decode=False):
        x = []
        logger.debug("page: "+page)
        cookie = Elitetorrent.getValidCookie()
        logger.debug("Using new cookie: "+cookie)
        if(str(page)=="0"):
            html = Elitetorrent.getContentFromUrl(url=Elitetorrent.MAIN_URL,cookie=cookie)
            menuHtml = Decoder.extract('<li id="mas_categorias"><i class="fa fa-plus" aria-hidden="true"></i> categorias</li>','</ul>',html)
            for itemHtml in menuHtml.split("</li>"):
                logger.debug("li --> HTML is: "+itemHtml)
                if "href=" in itemHtml:
                    item = {}
                    item["title"] = Decoder.extract('">','<',itemHtml)
                    logger.debug(item["title"])
                    link = Decoder.extract('href="', '"', itemHtml)
                    logger.debug(link)
                    if "://" not in link:
                        link = Elitetorrent.MAIN_URL+link
                    item["link"] = link
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
        elif '/torrent/' in page or decode:
            logger.debug("torrent page detected...")
            link = Elitetorrent.extractProviderFromLink(page,cookie)
            element = {}
            element["link"] = link
            x.append(element)
        else:
            x = Elitetorrent.extractContentFromLink(page,cookie)

        return x