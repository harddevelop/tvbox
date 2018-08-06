# -*- coding: utf-8 -*-
import urllib
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from providers.cinestrenostv import Cineestrenostv

from tvboxcore.downloader import Downloader

class Vigoal(Downloader):

    MAIN_URL = "http://www.vipgoal.net/"

    @staticmethod
    def getChannels(page):
        start = False
        #logger.debug("Current page is: "+page)
        if str(page) == '0' or str(page)=='1':
            if str(page)=='0':
                start = True
            page=Vigoal.MAIN_URL

        page = urllib.unquote_plus(page)
        html = Vigoal.getContentFromUrl(page,"",Vigoal.cookie,"")
        x = []
        if page.find(".html")==-1:
            if start:
                element = {}
                element["link"] = '1'
                element["title"] = 'Display by event'
                x.append(element)
                table = Decoder.extract("<center><table><tr><td>","</tr></table></center>",html)
                for fieldHtml in table.split('<a href="'):
                    element = {}
                    element["link"] = urllib.quote_plus(str(fieldHtml[0:fieldHtml.find('"')]))
                    element["title"] = fieldHtml[fieldHtml.find('title="')+len('title="'):]
                    element["title"] = element["title"][0:element["title"].find('"')].replace("-"," ").replace("en directo","").replace("Live Stream","").replace("\n","").replace("\t","").replace("  ","").strip() #cleaned
                    while element["title"].find("<")>-1: #clean tags
                        tag = Decoder.extract("<",">",element["title"])
                        element["title"] = element["title"].replace("<"+tag+">","")
                    element["thumbnail"] = fieldHtml[fieldHtml.find('<img src="')+len('<img src="'):]
                    element["thumbnail"] = element["thumbnail"][0:element["thumbnail"].find('"')]
                    logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                    if element["link"].find("http")==0:
                        x.append(element)
            else: #display program content
                table = Decoder.extract("<h2>Events Today:</h2>","</ul>",html) #instead could be used <div class="ppal"> but... fate I suppose
                i = 0
                for fieldHtml in table.split('<li class="">'):
                    if i>0:
                        element = {}
                        element["link"] = Decoder.extract('<a href="','">',fieldHtml)
                        element["title"] = Decoder.extract(' - ','</div>',fieldHtml)
                        if fieldHtml.find('"><h2>')>-1:
                            titleLine = Decoder.extract('"><h2>',"</h2>",fieldHtml)
                        else:
                            titleLine = Decoder.rExtract('html">',"</a></div>",fieldHtml)
                        timeLine = (element["title"].replace("</b>","").replace(" - ","")).replace("-"," ").replace("en directo","").replace("Live Stream","").replace("\n","").replace("\t","").replace("  ","").strip() #cleaned
                        element["title"] = timeLine+" - "+titleLine
                        while element["title"].find("<")>-1: #clean tags
                            tag = Decoder.extract("<",">",element["title"])
                            element["title"] = element["title"].replace("<"+tag+">","")
                        element["thumbnail"] = fieldHtml[fieldHtml.find('<img src="')+len('<img src="'):]
                        element["thumbnail"] = Vigoal.MAIN_URL+element["thumbnail"][0:element["thumbnail"].find('"')]
                        logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                        element["link"] = urllib.quote_plus(str(Vigoal.MAIN_URL+element["link"]))
                        x.append(element)
                    i+=1
        else:
            x.append(Vigoal.extractChannel(html,page))
        return x

    @staticmethod
    def extractChannel(html,page="http://www.vipgoal.net/"):
        element = {}
        if html.find('<script type="text/javascript" src="http://www.playerapp1.pw/channel.php?file=')>-1: #old part
            scriptUrl = Decoder.extractWithRegex('http://www.playerapp1.pw/channel.php?file=','"',html)
            html2 = Vigoal.getContentFromUrl(scriptUrl)
            lastUrl = Decoder.extractWithRegex('http://','" ',html2)
            lastUrl = lastUrl.replace('"',"")
            logger.debug("last url: "+lastUrl+", cookie="+Vigoal.cookie)
            html3 = Vigoal.getContentFromUrl(lastUrl,"",Vigoal.cookie,lastUrl)
            playerUrl = Decoder.decodeBussinessApp(html3,lastUrl)
            logger.debug("player url is: "+playerUrl)
            element["title"] = "Watch streaming"
            element["permalink"] = True
            element["link"] = playerUrl
        else: #unified with cinestrenostv, they are the same people, at least the same code works and the changes are at the same time xD
            logger.debug('Extracting channel from: '+page)
            element = Cineestrenostv.extractIframeChannel(html,page)
        return element