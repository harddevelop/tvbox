# -*- coding: utf-8 -*-
from tvboxcore.decoder import Decoder
from tvboxcore import jsunpack
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Acetvru(Downloader):

    MAIN_URL = "http://torrent-tv-online.pp.ua/_tv/counter.js"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            page=Acetvru.MAIN_URL
            html = Acetvru.getContentFromUrl(page,"",Acetvru.cookie,"")
            html = Decoder.extract('var playlist = [',']',html)
            x = Acetvru.extractElements(html)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        for value in table.split('\n'):
            if value.find("acestream://")>-1:
                element = {}
                element["title"] = unicode(Decoder.extract("// ",'(',value), errors='replace')
                element["link"] = Decoder.extractWithRegex("acestream:",'\"',value).replace('"',"")
                logger.debug("append: "+element["title"]+", link: "+element["link"])
                x.append(element)
        return x