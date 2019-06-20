# -*- coding: utf-8 -*-
import urllib
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Vercanalestv1com(Downloader):

    MAIN_URL = "https://vercanalestv1.com/ver-tve-1-la-1-online-en-directo-gratis-24h-por-internet/"

    @staticmethod
    def getChannels(page):
        if str(page) == '0':
            page=Vercanalestv1com.MAIN_URL

        page = urllib.unquote_plus(page)
        html = Vercanalestv1com.getContentFromUrl(page,"",Vercanalestv1com.cookie,"")
        x = []
        if page == Vercanalestv1com.MAIN_URL:
            table = Decoder.extract('<center><table><tbody><tr>',"</center>",html)
            for fieldHtml in table.split('<a'):
                element = {}
                element["link"] = Decoder.extract('href="','"',fieldHtml)
                element["title"] = Decoder.extract('alt="','nline',fieldHtml)
                if '"' in element["title"]:
                    element["title"]=element["title"][:element["title"].find('"')]
                element["title"]=element["title"][:element["title"].rfind(' ')]
                element["thumbnail"] = Decoder.extract('<img src="','"',fieldHtml)
                if "http" not in element["thumbnail"]:
                    element["thumbnail"]="https:"+element["thumbnail"]
                element["permaLink"] = True
                logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                if "http" in element["link"]:
                    x.append(element)
        else:
            x.append(Vercanalestv1com.extractChannel(html,page))
        return x

    @staticmethod
    def extractChannel(html,page="https://vercanalestv1.com"):
        element = {}
        if '<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="500" allowfullscreen src="' in html: 
            script = Decoder.extract('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="500" allowfullscreen src="','"',html)
            scriptUrl = "https://vercanalestv1.com"+script
            html2 = Vercanalestv1com.getContentFromUrl(url=scriptUrl,referer=page)
            newScriptUrl = "https:"+Decoder.extract(' src="','"',html2)
            html3 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,referer=scriptUrl)
            key = Decoder.extract('" name="','"',html3) #manzana66 key
            formData = key+"=12345"
            html4 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,data=formData,referer=scriptUrl)
            logger.debug("final HTML: "+html4)
            lastUrl = "https:"+Decoder.extract("source: '","'",html4)+"|User-Agent=Mozilla/5.0"
            logger.debug("decoded link is: "+lastUrl)
            element["title"] = page
            element["link"] = lastUrl
        return element
