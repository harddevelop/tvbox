# -*- coding: utf-8 -*-
import urllib
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Tvporinternetnet(Downloader):

    MAIN_URL = "http://tvpor-internet.net/channels"

    @staticmethod
    def getChannels(page):
        if str(page) == '0':
            page=Tvporinternetnet.MAIN_URL

        page = urllib.unquote_plus(page)
        html = Tvporinternetnet.getContentFromUrl(page,"",Tvporinternetnet.cookie,"")
        x = []
        if page == Tvporinternetnet.MAIN_URL:
            table = Decoder.extract('<div id="canalesdown" class="canales">',"<br>",html)
            for fieldHtml in table.split('<li'):
                element = {}
                element["link"] = Decoder.extract('<a href="','"',fieldHtml)
                element["title"] = Decoder.extract('<div style="color: #ffffff;">','<',fieldHtml)
                element["permalink"] = True
                element["thumbnail"] = Decoder.extract('<img src="','"',fieldHtml)
                logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                if "http" in element["link"]:
                    x.append(element)
        else:
            x.append(Tvporinternetnet.extractChannel(html,page))
        return x

    @staticmethod
    def extractChannel(html,page="http://tvpor-internet.net"):
        element = {}
        if "<script type='text/javascript'>" in html: #old part
            script = Decoder.extract("<script type='text/javascript'>","</",html)
            cosa = Decoder.extract("cosa = '","'",script)
            id = Decoder.extract("id='", "'", script)
            scriptUrl = "http://tvpor-internet.net/player/"+cosa+"/"+id
            html2 = Tvporinternetnet.getContentFromUrl(scriptUrl)
            lastUrl = Decoder.extract('<source src="','"',html2)
            logger.debug("decoded link is: "+lastUrl)
            element["title"] = page
            element["permalink"] = True
            element["link"] = lastUrl
        return element