# coding=utf-8
from core.xbmcutils import XBMCUtils
import urllib
from core.downloader import Downloader
from core import logger
from core.decoder import Decoder

try:
    import json
except:
    import simplejson as json


class MejorTorrent(Downloader):

    MAIN_URL = 'http://www.mejortorrent.com/'
    SEARCH = "http://www.mejortorrent.com/resultados/%s"

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("page: "+page)
        if(str(page)=="0"):
            html = MejorTorrent.getContentFromUrl(url=MejorTorrent.MAIN_URL)
            menuHtml = Decoder.extract("<table width='140' border='0' cellpadding='0' cellspacing='0' style='border-left:1px solid black; border-right:1px solid black; border-bottom:1px solid black;'>",'</table>',html)
            for itemHtml in menuHtml.split("<a"):
                logger.debug("li --> HTML is: "+itemHtml)
                if "href=" in itemHtml:
                    item = {}
                    title = Decoder.extract('">','</a>',itemHtml)
                    title = Decoder.removeHTML(title)
                    if len(title)>0:
                        item["title"] = title
                        link = Decoder.extract("href='", "'", itemHtml)
                        if 'musica' not in link and 'juegos' not in link and 'variados' not in link:
                            if "://" not in link:
                                item["link"] = MejorTorrent.MAIN_URL+link
                            x.append(item)
            search = {}
            search["title"] = XBMCUtils.getString(11018)
            search["link"] = ".search"
            x.append(search)

        elif page=='.search':
            #display keyboard, it will wait for result
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                x = MejorTorrent.search(text)
        elif '/torrent/' in page:
            logger.debug("torrent page detected...")
            link = MejorTorrent.extractProviderFromLink(page)
            element = {}
            element["link"] = link
            x.append(element)
        else:
            x = MejorTorrent.extractContentFromLink(page)

        return x

    @staticmethod
    def search(text):
        searchUrl = MejorTorrent.SEARCH % urllib.quote_plus(text)
        html = MejorTorrent.getContentFromUrl(url=searchUrl,referer=MejorTorrent.MAIN_URL,launchLocation=True)
        logger.debug("search html is: "+html)
        if '<meta http-equiv="Refresh" content="0;url=' in html:
            url2 = Decoder.extract('<meta http-equiv="Refresh" content="0;url=','"',html)
            url2 = url2[:url2.find("=")+1]+urllib.quote_plus(url2[url2.find("=")+1:])
            html = MejorTorrent.getContentFromUrl(url=url2, referer=searchUrl,launchLocation=True,cookie=MejorTorrent.cookie)
            logger.debug("search2 html2 is: " + html)
        else:
            logger.debug("ok, done!")
        return MejorTorrent.extractItems(html)

    @staticmethod
    def extractItems(html):
        x = []
        htmlList = Decoder.extract('<ul class="miniboxs miniboxs-ficha">','</ul>',html)
        i=0
        for htmlElement in htmlList.split("<li>"):
            if i>0:
                element = {}
                title = Decoder.extract(" title=\"","\"",htmlElement)
                link = MejorTorrent.MAIN_URL+Decoder.extract(" href=\"", "\"", htmlElement)
                img = MejorTorrent.MAIN_URL+"/"+Decoder.extract("<img src=\"","\"",htmlElement)
                element["title"] = title
                element["link"] = link
                element["thumbnail"] = img
                x.append(element)
            i+=1
        return x

    @staticmethod
    def extractProviderFromLink(page):
        html = MejorTorrent.getContentFromUrl(url=page,referer=MejorTorrent.MAIN_URL)
        logger.debug("html is: "+html)
        link = "magnet:"+Decoder.extract('<a href="magnet:','"',html)
        logger.debug("link obtained is: "+link)
        return link

    @staticmethod
    def extractContentFromLink(page):
        x = []
        html = MejorTorrent.getContentFromUrl(url=page,referer=MejorTorrent.MAIN_URL)
        if "<td height='20' width='440' colspan='2'>" in html:
            content = Decoder.extract("<td height='20' width='440' colspan='2'>","<center><span style='font-size:15px; font-family:arial;'><b>Páginas:</b>",html)
            i = 0
            for line in content.split("<td><div align='justify'><center>"):
                if i>0:
                    img = (MejorTorrent.MAIN_URL+"/"+Decoder.extract('<img src="', '"', line)).replace("///","/").replace(" ","+")
                    line2 = line[line.find("</a>"):]
                    link = MejorTorrent.MAIN_URL + Decoder.extract('<a href=/"', '"', line)
                    title = Decoder.extract('">', '</a>', line2)
                    element = {}
                    element["link"] = link
                    element["thumbnail"] = img
                    element["title"] = title
                    if len(title)>0:
                        x.append(element)
                i+=1
        return x