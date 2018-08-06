# -*- coding: utf-8 -*-
import urllib2
import urllib
import os,re
import base64
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Zonasportsme(Downloader):

    MAIN_URL = "http://zonasports.me/"

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("page is: "+page)
        if str(page) == '0':
            page=Zonasportsme.MAIN_URL
        else:
            logger.debug("decoding page: "+page)
            page = base64.b64decode(page)
            logger.debug("decoded page: "+page)
        logger.debug("launching web petition to page: "+page)
        html = Zonasportsme.getContentFromUrl(page,"",Zonasportsme.cookie,Zonasportsme.MAIN_URL)
        if page==Zonasportsme.MAIN_URL:
            logger.debug("browsing main menu...")
            menu = Decoder.extract('<ul class="nav" id="main-menu">',"</li></ul></li></ul>",html)
            x = Zonasportsme.extractElements(menu)
        else:
            url = ""
            #decoder part
            if 'http://www.ustream.tv/' in html:
                uStreamUrl = Decoder.extractWithRegex('http://www.ustream.','"',html)
                url = Decoder.getUstreamLink(uStreamUrl,page)
            elif 'castamp.com/embed.js' in html:
                channel = Decoder.extract('channel="','"',html)
                url = Decoder.getCastcampLink(channel,page)
            elif 'adca.st/broadcast/player.js' in html:
                if "<script type='text/javascript'>id='" in html:
                    id2 = Decoder.extract("<script type='text/javascript'>id='", "';", html)
                logger.debug("using id = " + id2)
                url4 = "http://bro.adca.st/stream.php?id=" + id2 + "&width=700&height=450&stretching=uniform"
                html4 = Zonasportsme.getContentFromUrl(url4, "", Zonasportsme.cookie, page)
                logger.debug("html4: " + html4)
                curl = Decoder.rExtract('= "', '=";', html4)+'='
                fn = Decoder.rExtract('"','.php";',html4)
                token = Zonasportsme.getContentFromUrl('http://bro.adca.st/'+fn+'.php', "",Zonasportsme.cookie, url4, True)
                logger.debug("token: " + token)
                token = Decoder.extract('":"', '"', token)
                file = base64.decodestring(curl) + token + "|" + Downloader.getHeaders('http://cdn.allofme.site/jw/jwplayer.flash.swf')
                logger.debug("final url is: " + file)
                url = file
            elif 'zony.tv/static/scripts/zony.js' in html:
                channel = Decoder.extract("channel='","'",html)
                url = 'http://www.zony.tv/embedplayer/'+channel+'/1/700/400/'
                html2 = Zonasportsme.getContentFromUrl(url=url,referer=page)
                logger.debug("html2 is: "+html2)
                #newParam = Decoder.extract("so.addParam('FlashVars', '", "'", html2)  # brute params, needs a sort
                newParam = Decoder.extractParams(html2)
                rtmp = "rtmp://146.185.16.62/stream playPath="+newParam+" swfVfy=1 timeout=10 conn=S:OK live=true swfUrl=http://www.zony.tv/static/scripts/fplayer.swf flashver=WIN/2019,0,0,226 pageUrl="+page
                url = rtmp
            elif 'http://www.embeducaster.com/static/' in html:
                channel = Decoder.extract("channel='", "'", html)
                url = 'http://www.embeducaster.com/embedplayer/' + channel + '/1/700/400/'
                html2 = Zonasportsme.getContentFromUrl(url=url, referer=page)
                logger.debug("html2 is: " + html2)
                url = Decoder.decodeUcaster(html2,url)
            elif '247bay.tv/static/' in html:
                channel = Decoder.extract("channel='", "'", html)
                url = 'http://www.247bay.tv/embedplayer/'+channel+'/2/750/420'
                url = Decoder.decode247bay(url,page)
            element = {}
            element["title"] = "Stream"
            element["link"] = url
            element["permaLink"] = True
            x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        i = 0
        for value in table.split('<li>'):
            logger.debug("loop: "+str(i))
            if i>0:
                element = {}
                title = Decoder.extract(">",'</a></li>',value)
                link = Decoder.extract("href=\"",'"',value)
                element["title"] = title
                element["link"] = base64.b64encode(str(Zonasportsme.MAIN_URL+link))
                logger.debug("append: "+title+", link: "+element["link"])
                x.append(element)
            i+=1
        return x
