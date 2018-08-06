# -*- coding: utf-8 -*-
from tvboxcore.decoder import Decoder
from tvboxcore import jsunpack
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Skylinewebcamscom(Downloader):

    MAIN_URL = "http://www.skylinewebcams.com/"

    @staticmethod
    def getChannels(page,decode=False):
        x = []
        if str(page) == '0':
            page=Skylinewebcamscom.MAIN_URL
        html = Skylinewebcamscom.getContentFromUrl(page,"",Skylinewebcamscom.cookie,"")
        if page.find(".html")==-1 and not decode:
            logger.debug("browsing main menu...")
            menu = Decoder.extract('<ul class="nav" id="main-menu">',"</li></ul></li></ul>",html)
            x = Skylinewebcamscom.extractElements(menu)
        else:
            logger.debug("browsing page...")
            if html.find('<ul class="hidden-xs nav nav-tabs')>-1 and not decode:
                logger.debug("browsing submenu")
                menu = Decoder.extract('<ul class="hidden-xs nav nav-tabs','</li></ul>',html) #first tries to extract submenu
                x = Skylinewebcamscom.extractElements(menu)
                if len(x)==0: #no submenu, so final channels have to been extracted
                    logger.debug("browsing webcams")
                    content = Decoder.extract('<ul class="row list-unstyled block webcams">','</li></ul>',html)
                    x = Skylinewebcamscom.extractElements(content)
            else:
                logger.debug("building url for webcam...")
                if html.find(",url:'")==-1 and not decode: #needs subchannels
                    logger.debug("browsing webcams")
                    content = Decoder.extract('<ul class="row list-unstyled block webcams">','</li></ul>',html)
                    x = Skylinewebcamscom.extractElements(content)
                else: #final channel
                    logger.debug("html is: "+html)
                    if html.find("\" type='application/x-mpegURL'")>-1:
                        url = Decoder.rExtract('"',"\" type='application/x-mpegURL'",html)
                    else:
                        url = Decoder.extract(",url:'","'",html)
                    logger.debug("url is: "+url)
                    logger.debug("building final link: "+url)
                    element = {}
                    element["title"] = "Webcam"
                    element["link"] = url
                    element["permaLink"] = True
                    x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        i = 0
        for value in table.split('<a '):
            logger.debug("loop: "+str(i))
            if i>0:
                element = {}
                logger.debug("processing html: "+value)
                if value.find('<img ')==-1:
                    title = Decoder.rExtract(">",'</a></li>',value)
                    link = Decoder.extract("href=\"/",'"',value)
                    if title == '</a':
                        title = Decoder.extract('class="menu-item">','<',value).replace("&nbsp;","")
                    element["title"] = title
                    element["link"] = Skylinewebcamscom.MAIN_URL+link
                    if len(title)>0 and link.find("#")==-1 and len(element["link"])>len(Skylinewebcamscom.MAIN_URL) and (title.find("<")==-1 and title.find(">")==-1):
                        logger.debug("append: "+title+", link: "+element["link"])
                        x.append(element)
                    else:
                        logger.debug("discarted: "+title+", link: "+element["link"])
                else:
                    img = "http://"+Decoder.extract("data-original=\"//",'" ',value)
                    title = Decoder.extract("class=\"title\">",'</span>',value)
                    link = Decoder.extract("href=\"/",'"',value)
                    element["title"] = title
                    element["link"] = Skylinewebcamscom.MAIN_URL+link
                    element["thumbnail"] = img
                    element["permaLink"] = True
                    if link.find(".html")>-1 and (title.find("<")==-1 and title.find(">")==-1):
                        logger.debug("append: "+title+", link: "+element["link"]+", img: "+element["thumbnail"])
                        x.append(element)
                    else:
                        logger.debug("discarted: "+title+", link: "+element["link"]+", img: "+element["thumbnail"])
            i+=1
        return x