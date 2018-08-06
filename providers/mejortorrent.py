# coding=utf-8
from tvboxcore.xbmcutils import XBMCUtils
import urllib
from tvboxcore.downloader import Downloader
from tvboxcore import logger
from tvboxcore.decoder import Decoder

try:
    import json
except:
    import simplejson as json


class MejorTorrent(Downloader):

    MAIN_URL = 'http://www.mejortorrent.com/'
    SEARCH = "http://www.mejortorrent.com/secciones.php?sec=buscador&valor=%s"

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
        elif '-descargar-' in page:
            logger.debug("-descargar- page detected...")
            x = MejorTorrent.extractProvidersFromLink(page)
        elif 'sec=descargas' in page and '&p=' not in page:
            logger.debug("decoding torrent..."+page)
            html = MejorTorrent.getContentFromUrl(url=page)
            link = MejorTorrent.MAIN_URL+Decoder.extract("Pincha <a href='/","'",html)
            logger.debug("extracted torrent link: "+link)
            element = {}
            element["link"] = link
            element["title"] = page
            element["finalLink"] = True
            x.append(element)
        else:
            x = MejorTorrent.extractContentFromLink(page)

        return x

    @staticmethod
    def search(text):
        x = []
        searchUrl = MejorTorrent.SEARCH % urllib.quote_plus(text)
        html = MejorTorrent.getContentFromUrl(url=searchUrl,referer=MejorTorrent.MAIN_URL)
        logger.debug("search html is: "+html)
        if "<table width='96%' border='0' cellspacing='0' cellpadding='4' align='center'>" in html:
            table = Decoder.extract("<table width='96%' border='0' cellspacing='0' cellpadding='4' align='center'>","</table>",html)
            i=0
            for line in table.split("<tr height='22'>"):
                if i>0:
                    link = Decoder.extract("<a href='","'",line)
                    title = Decoder.extract('onmouseout="style.textDecoration=\'none\';">', "</td>", line)
                    title = Decoder.removeHTML(title)
                    element = {}
                    element["title"] = title
                    element["link"] = "http://www.mejortorrent.com"+link
                    x.append(element)
                i+=1
        else:
            logger.debug("nothing done in search!")
        return x

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
    def extractProvidersFromLink(page):
        x = []
        html = MejorTorrent.getContentFromUrl(url=page,referer=MejorTorrent.MAIN_URL)
        logger.debug("html is: "+html)
        if '<b>Selecciona los que quieres descargar</b>' in html:
            tableHtml = Decoder.extract('<b>Selecciona los que quieres descargar</b>','<b>Marcar/Desmarcar Todos</b>',html)
            logger.debug("TABLE HTML IS: "+tableHtml)
            if "<input type='hidden' name='tabla' value='" in html:
                table = Decoder.extract("<input type='hidden' name='tabla' value='", "'", html)
            elif "name='tabla' value='" in html:
                table = Decoder.extract("name='tabla' value='", "'", html)
            logger.debug("table is: "+table)
            i=0
            for htmlLine in tableHtml.split("<td bgcolor='#C8DAC8' style='border-bottom:1px solid black;'>"):
                if i>0:
                    if '<a ' in htmlLine:
                        text = Decoder.extract("'>","<",htmlLine)
                    else:
                        text = htmlLine[:htmlLine.find("<")]
                    logger.debug("target line html is: "+text)
                    #text = Decoder.removeHTML(text)
                    id = Decoder.extract(" value='","'",htmlLine)
                    link = "http://www.mejortorrent.com/secciones.php?sec=descargas&ap=contar&tabla=%s&id=%s&link_bajar=1" % (table,id)
                    element = {}
                    element["title"] = text
                    element["link"] = link
                    element["finalLink"] = True
                    logger.debug("appending: "+text+", link: "+link)
                    x.append(element)
                i+=1
        else: #download
            x = MejorTorrent.extractDownloadItem(html)
        return x

    @staticmethod
    def extractDownloadItem(html):
        x = []
        refinedHtml = Decoder.extract('<b>Torrent:</b>', "</a>", html)
        link = "http://www.mejortorrent.com/secciones.php" + Decoder.extract("<a href='secciones.php", "'", refinedHtml)
        text = Decoder.extract("<title>", "</title>", html).replace("Torrent Descargar Bajar Gratis", "")
        element = {}
        element["title"] = text
        element["link"] = link
        element["finalLink"] = True
        logger.debug("appending: "+text+", link: "+link)
        x.append(element)
        return x

    @staticmethod
    def extractContentFromLink(page):
        x = []
        html = MejorTorrent.getContentFromUrl(url=page,referer=MejorTorrent.MAIN_URL)
        if "<td height='20' width='440' colspan='2'>" in html:
            if "' class='paginar'> << Anterior </a>" in html:
                prevLink = MejorTorrent.MAIN_URL+Decoder.rExtract("<a href='/","' class='paginar'> << Anterior </a>",html)
                element = {}
                element["link"] = prevLink
                element["title"] = "Anterior"
                x.append(element)
            content = Decoder.extract("<td height='20' width='440' colspan='2'>","<center><span style='font-size:15px; font-family:arial;'><b>Páginas:</b>",html)
            i = 0
            for line in content.split("<td><div align='justify'><center>"):
                if i>0:
                    img = (MejorTorrent.MAIN_URL+Decoder.extract('<img src="', '"', line)).replace(".com//",".com/")
                    link = (MejorTorrent.MAIN_URL + Decoder.extract('<a href="', '"', line)).replace(".com//",".com/")
                    logger.debug("link is: "+link)
                    element = {}
                    element["link"] = link
                    element["thumbnail"] = img.replace(" ","%20")
                    element["title"] = img[img.rfind("/")+1:img.find(".jpg")]
                    #if len(title)>0:
                    x.append(element)
                i+=1
            if "' class='paginar'> Siguiente >> </a>" in html:
                nextLink = MejorTorrent.MAIN_URL+Decoder.rExtract("<a href='/","' class='paginar'> Siguiente >> </a>",html)
                element = {}
                element["link"] = nextLink
                element["title"] = "Siguiente"
                x.append(element)
        else: #download link
            x = MejorTorrent.extractDownloadItem(html)
        return x