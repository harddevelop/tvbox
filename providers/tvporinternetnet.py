# -*- coding: utf-8 -*-
import urllib
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Tvporinternetnet(Downloader):

    MAIN_URL = "http://tvporinternet.eshost.com.ar"

    @staticmethod
    def getChannels(page):
        if str(page) == '0':
            page=Tvporinternetnet.MAIN_URL

        page = urllib.unquote_plus(page)
        html = Tvporinternetnet.getContentFromUrl(page,"",Tvporinternetnet.cookie,"")
        x = []
        if page == Tvporinternetnet.MAIN_URL:
            table = Decoder.extract('<div data-p="43.75">',"<!-- Bullet Navigator -->",html)
            for fieldHtml in table.split('<div data-p="43.75">'):
                if ' href=' in fieldHtml:
                    element = {}
                    element["link"] = Decoder.extract('<a href="','"',fieldHtml)
                    element["title"] = Decoder.extract('/p/','-en-',element["link"])
                    element["thumbnail"] = Decoder.extract('<img data-u="image" src="','"',fieldHtml)
                    element["permaLink"] = True
                    logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                    if "http" in element["link"]:
                        x.append(element)
        else:
            x.append(Tvporinternetnet.extractChannel(html,page))
        return x

    @staticmethod
    def extractChannel(html,page=MAIN_URL):
        element = {}
        if '<iframe src="' in html:
            iframe = Decoder.extract('<iframe src="','"',html)
            logger.debug("iframe url is %s"%iframe)
            html2 = Tvporinternetnet.getContentFromUrl(url=iframe,referer=page)
            logger.debug("html: %s"%html2)
            if 'source: "' in html2:
                source = Decoder.extract('source: "','"',html2)
                logger.debug("found link: %s"%source)
                element["link"] = source+"|User-Agent=Mozilla%2F5.0+%28X11%3B+Linux+x86_64%3B+rv%3A68.0%29+Gecko%2F20100101+Firefox%2F68.0&amp;Referer="+urllib.quote_plus(iframe)
                element["title"] = page
        return element
