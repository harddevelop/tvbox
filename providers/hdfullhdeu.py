# -*- coding: utf-8 -*-
from tvboxcore.decoder import Decoder
from tvboxcore import jsunpack
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Hdfullhdeu(Downloader):

    MAIN_URL = "http://hdfullhd.eu/iptv_groups.txt"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            page=Hdfullhdeu.MAIN_URL
        html = Hdfullhdeu.getContentFromUrl(page,"",Hdfullhdeu.cookie,"")
        x = Hdfullhdeu.extractElements(html)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        i = 0
        for value in table.split('\n'):
            element = {}
            title = value[0:value.find(",")]
            link = value[value.find(",")+1:]
            element["title"] = title
            element["link"] = link
            if link.find(".m3u8")>-1 or link.find(".ts")>-1:
                element["permaLink"] = True
            logger.debug("append: "+title+", link: "+element["link"])
            x.append(element)
            i+=1
        return x