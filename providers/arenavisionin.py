# -*- coding: utf-8 -*-
from tvboxcore.xbmcutils import XBMCUtils
import os
from tvboxcore.decoder import Decoder
from tvboxcore import jsunpack
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Arenavisionin(Downloader):

    MAIN_URL = "https://linkotes.com/arenavision/"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            try:
                page=Arenavisionin.MAIN_URL
                html = str(Arenavisionin.getContentFromUrl(url=Arenavisionin.MAIN_URL))
            except:
                pass
            logger.debug("obtained html")
            html = Decoder.extract('<div id="agenda_av">','</td></tr></table></div>',html)
            i=0
            logger.debug("extracting channels...")
            x2 = Arenavisionin.extractChannelsFromAcestreamId()
            logger.debug("extracted channel")
            for line in html.split('<tr class='):
                if i>0:
                    title = Decoder.extract('<td>','</td></tr>',line).replace('<td>',' ').replace('</td>',' ')
                    number = Decoder.extract('#av','"',title)
                    href = ""
                    for link in x2:
                        if link["title"].lower() == "arenavision "+number:
                            logger.debug("found link!")
                            href = link["link"]
                    if href == '':
                        x3 = Arenavisionin.extractChannelsFromAcestreamId("Arenavision "+number)
                        for link in x3:
                            if link["title"].lower() == "arenavision "+number:
                                logger.debug("found 2 link!")
                                href = link["link"]
                            else:
                                logger.debug("%s - %s",(link["title"].lower(),"arenavision "+number))
                    element = {}
                    element["title"] = title[0:title.find(": ")]
                    element["link"] = "plugin://program.plexus/?mode=2&url=acestream://"+href+"&name=RemoteLink"
                    logger.debug("decoded link... %s"%title)
                    x.append(element)
                i+=1
        return x

    @staticmethod
    def extractChannelsFromAcestreamId(name='arenavision'):
        name = name.replace(" ","%3D")
        logger.debug("SEARCHING '%s'"%name)
        x = []
        url = 'https://acestreamid.com/search/'
        headers = {
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Content-Type':'application/x-www-form-urlencoded',
            'Cookie':'session=1b5f2c1723c2921adc20f5467cd5212d5f450eaa%7E5d6295ad9eb576-51875608;'
        }
        content = 'csrf=LXaVHAtkXnnwahhGLK%%2B0HPyRCZZEnMUC2ijvFpXT6PY%%3D&query=%s'%name
        html = str(Arenavisionin.getContentFromUrl(url=url,headers=headers,referer=url,data=content))
        logger.debug("html obtaned for extracting channels...")
        table = Decoder.extract('<ul id="acestreamids" class="collection with-header">','</ul',html)
        logger.debug("obtained table... %s "%table)
        i=0
        for line in table.split('<li class="collection-item acestreamidID ">'):
            if i>0:
                title = Decoder.extract('<a class="font-small grey-text truncate content" title="','"',line)
                link = Decoder.extract('<a href="acestream://','"',line)
                element = {}
                element["title"] = title
                element["link"] = link
                logger.debug("extracted element %s"%title)
                x.append(element)
            i+=1
        return x
