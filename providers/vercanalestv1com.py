# -*- coding: utf-8 -*-
import urllib
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Vercanalestv1com(Downloader):

    MAIN_URL = "https://vercanalestv1.com/ver-tve-1-la-1-online-en-directo-gratis-24h-por-internet"

    @staticmethod
    def getChannels(page):
        if str(page) == '0':
            page=Vercanalestv1com.MAIN_URL
        page = urllib.unquote_plus(page)
        html = Vercanalestv1com.getContentFromUrl(page,"",Vercanalestv1com.cookie,referer="https://vercanalestv1.com")
        logger.debug("end FIRST")
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
        if ' allowfullscreen src="' in html:
            try:
                script = Decoder.extract(' allowfullscreen src="','"',html)
                scriptUrl = "https://vercanalestv1.com"+script
                logger.debug("triying first fix... "+script)
                html2 = Vercanalestv1com.getContentFromUrl(url=scriptUrl,referer=page)
                logger.debug("DONE fix")
                if "source: '" not in html2 and '/embed.js' not in html2:
                    newScriptUrl = "https:"+Decoder.rExtractWithRegex('//','.php',html2)
                    html3 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,referer=scriptUrl)
                    key = Decoder.extract('" name="','"',html3) #manzana66 key
                    formData = key+"=12345"
                    html4 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,data=formData,referer=scriptUrl)
                    if "source: '" in html4:
                        lastUrl = "https:"+Decoder.extract("source: '","'",html4)+"|User-Agent=Mozilla/5.0"
                    elif ".php" in html4:
                        scriptUrl = newScriptUrl
                        newScriptUrl = "https:"+Decoder.rExtractWithRegex('//','.php',html4)
                        html5 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,referer=scriptUrl)
                        key = Decoder.extract('" name="','"',html5) #manzana66 key
                        formData = key+"=12345"
                        html6 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,data=formData,referer=scriptUrl)
                        logger.debug("html is: "+html6)
                        if "source: '" in html6:
                            lastUrl = "https:"+Decoder.extract("source: '","'",html6)+"|User-Agent=Mozilla/5.0"
                elif "source: '" in html2:
                    lastUrl = "https:"+Decoder.extract("source: '","'",html2)+"|User-Agent=Mozilla/5.0"
                elif 'embed.js' in html2:
                    domain = Decoder.rExtract("//","/embed.js",html2)
                    id = Decoder.extract(", id='","'",html2)
                    newScriptUrl = "http://"+domain+"/embed/"+id
                    html3 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,referer=scriptUrl)
                    lastUrl = Decoder.extract('file: "','"',html3)+"|User-Agent=Mozilla/5.0"
                logger.debug("decoded link is: "+lastUrl)
                element["title"] = page
                element["link"] = lastUrl
            except Exception as ex:
                logger.debug("Ex: "+str(ex))
        return element
