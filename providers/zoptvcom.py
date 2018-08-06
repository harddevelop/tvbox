import os
import binascii
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Zoptvcom(Downloader):

    MAIN_URL = "http://www.zoptv.com"

    @staticmethod
    def getChannels(page):
        #print "original page: "+page
        #print "original page: "+page
        x = []
        oldPage = page
        if str(page) == '0':
            element = {}
            element["link"] = 'country'
            element["title"] = 'Browse by Country'
            x.append(element)
            element = {}
            element["link"] = 'genre'
            element["title"] = 'Browse by Genre'
            x.append(element)
        elif page=='country' or page=='genre':
            page=Zoptvcom.MAIN_URL
        html = ""
        if str(page) != '0':
            html = Zoptvcom.getContentFromUrl(page,"",Zoptvcom.cookie,"")
        if oldPage=='country' or oldPage=='genre':
            if oldPage == 'country':
                table = Decoder.extract('<li class="dropdown-header">Browse by Country</li>',"</ul>",html)
            else: #genre
                table = Decoder.extract('<li class="dropdown-header">Browse by Genre</li>',"</ul>",html)
            x = Zoptvcom.extractElements(table)
        else:
            if html.find('<div class="zp-channel-list">')>-1:
                #it's a list, needs decode
                table = Decoder.extract('<div class="zp-channel-list">','</a>\n</div>',html)
                x = Zoptvcom.extractElements(table)
            else:
                while (html.find("decodeURIComponent") > -1):
                    extracted = Decoder.extract("eval(decodeURIComponent(atob('","')));",html)
                    html = binascii.a2b_base64(extracted)
                    logger.debug("decoded proccess has converted brute code to: "+html)
                if html.find('var streams =[{"src":"')>-1:
                    link = Decoder.extract('var streams =[{"src":"','","',html)
                    logger.debug("has been detected a link: "+link)
                    if link.find("vimeo.com/")==-1 and link.find("youtube.com/")==-1:
                        if link.find(".m3u8")==-1: #iframe
                            logger.debug("extracting iframe link from: "+link)
                            html = Zoptvcom.getContentFromUrl(link,"",Zoptvcom.cookie,page,False,False)
                            #print html
                            host = Decoder.extract("://","embed?",link)
                            m3u8File = Decoder.extract("var src = '","';",html)
                            if m3u8File.find("http://")==-1:
                                if m3u8File[0] == "/":
                                    logger.debug("converting a partial link: "+m3u8File)
                                    host = Decoder.extract("://","/",link)
                                link = "http://"+host+m3u8File
                            else:
                                link = m3u8File
                            logger.debug("new link is: "+link)
                        element = {}
                        element["title"] = ""
                        element["permalink"] = True
                        element["link"] = link+"|User-Agent=Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0,Cookie="+Zoptvcom.cookie+",Referer=http://www.juhe.ml/player/grindplayer/GrindPlayer.swf" #in some cases there are GET HEADERS checks, it fix issues
                        logger.debug("link used will be: "+element["link"])
                        x.append(element)
                    else:
                        if link.find("youtube.com/embed/")>-1:
                            link = link.replace("/embed/","/watch?v=")
                        element = {}
                        element["title"] = ""
                        element["permalink"] = True
                        element["link"] = link #it could be vimeo and youtube links so call to his addon
                        logger.debug("link used will be: "+element["link"])
                        x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        for fieldHtml in table.split(' href="'):
            if fieldHtml.find("<li>")>-1 or fieldHtml.find(' <img src="')>-1:
                element = {}
                element["link"] = Zoptvcom.MAIN_URL+fieldHtml[0:fieldHtml.find('"')]
                if fieldHtml.find(' <img src="')>-1:
                    element["title"] = Decoder.extract("<span>","</span>",fieldHtml)
                    element["thumbnail"] = Zoptvcom.MAIN_URL+Decoder.extract('<img src="','"> <span>',fieldHtml)
                    logger.debug("found thumbnail: "+element["thumbnail"])
                else:
                    element["title"] = fieldHtml[fieldHtml.find('">')+2:].replace("<li>","").replace("</li>","").replace("</a>","").replace("<a","").rstrip(os.linesep)
                logger.debug("found title: "+element["title"]+", link: "+element["link"])
                if len(element["title"])>0:
                    x.append(element)

        return x