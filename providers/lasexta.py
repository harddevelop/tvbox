# -*- coding: utf-8 -*-
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader
from tvboxcore.xbmcutils import XBMCUtils

class LaSexta(Downloader):

    MAIN_URL = "http://www.lasexta.com/teletexto/datos/"
    SUB_PAGE = "%s/%s_0001.htm"

    @staticmethod
    def getChannels(page):
        x = []
        subpage = LaSexta.SUB_PAGE
        currentPage = page
        if str(page) == '0':
            page = "100"
            currentPage = page
            arr = [str(page),str(page)] #page - subpage
            subpage = subpage % tuple(arr)
            page = LaSexta.MAIN_URL + subpage  # final parse
        elif '.search' in str(page):
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                page = text
                pageInt = page[0:1]+"00"
                arr = [str(pageInt), str(page)]  # page - subpage
                subpage = subpage % tuple(arr)
                currentPage = text
                page = LaSexta.MAIN_URL + subpage  # final parse
        else:
            logger.debug("Nothing done for page: "+str(page))
            subpage = page[page.rfind("/")+1:]
            subpage = subpage[:subpage.rfind("_")]
            logger.debug("Subpage is: " + str(subpage))
            currentPage = subpage
            page = page.replace("/"+subpage+"/","/"+currentPage+"/")
        element = {}
        element["link"] = LaSexta.MAIN_URL+".search"
        element["title"] = XBMCUtils.getString(10013)
        x.append(element)
        html = LaSexta.getContentFromUrl(url=page,referer=LaSexta.MAIN_URL)
        element = {}
        element["thumbnail"] = Decoder.extract('<img id="FABTTXImage" src="','"',html)
        if "://" not in element["thumbnail"]:
            thumbnailPage = element["thumbnail"][:element["thumbnail"].find("_")]
            element["thumbnail"] = LaSexta.MAIN_URL+(thumbnailPage[0:1]+"00")+"/"+element["thumbnail"]
        x.append(element)
        teletextHtml = Decoder.extract('<span class="LB" align="left">','</span>',html)
        x2 = LaSexta.extractElements(currentPage,teletextHtml)
        x.extend(x2)
        return x

    @staticmethod
    def extractElements(page,tableHtml):
        x = []
        i = 0
        for value in tableHtml.split('<a '):
            if i>0:
                element = {}
                title = Decoder.extract(">","</a>",value)
                link = Decoder.extract("href=\"","\"",value)
                element["title"] = page+" ver. "+title
                element["link"] = page[0:1]+"00/"+link
                if "://" not in element["link"]:
                    element["link"] = LaSexta.MAIN_URL+element["link"]
                logger.debug("append: "+element["title"]+", link: "+element["link"])
                x.append(element)
            i+=1
        return x