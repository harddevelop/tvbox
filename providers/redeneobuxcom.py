import time
import random
import re
import urllib

from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
from tvboxcore import logger

class RedeneobuxCom(Downloader):

    LIST_PAGE = "http://redeneobux.com/en/updated-kodi-iptv-m3u-playlist/"

    @staticmethod
    def getChannels(page):
        x = []
        if page == '0':
            page = RedeneobuxCom.LIST_PAGE
            results = RedeneobuxCom.getContentFromUrl(page)
            i=0
            for result in results.split('<div class="media">'):
                if i>0:
                    element = {}
                    img = Decoder.extract('<img src=\'',"'",result)
                    link = Decoder.extract('location.href=\'', "'", result)
                    title = Decoder.extract('\' alt=\'', "'", result)
                    if "http" in link:
                        logger.debug("appending result: "+title+", url: "+link)
                        element["title"] = title
                        element["link"] = link
                        element["thumbnail"] = img
                        x.append(element)
                i+=1
        else:
            content = RedeneobuxCom.getContentFromUrl(url=page,referer=RedeneobuxCom.LIST_PAGE)
            logger.debug("list content is: " + content)
            url = Decoder.extractWithRegex('http'," ",content).replace(" ","")
            logger.debug("url is: " + url)
            if 'adf' in url:
                listUrl = Decoder.decodeAdfly(url)
                logger.debug("list obtained is: "+listUrl)
                m3uContent = Downloader.getSimpleDownload(listUrl) #simple urllib2 download
                logger.debug("content: "+m3uContent)
                i=0
                for lineContent in m3uContent.split('#EXTINF:'):
                    if i>0:
                        title = Decoder.extract(',','\n',lineContent)
                        lineContent = lineContent[lineContent.find("\n"):]
                        urlContent = Decoder.extractWithRegex('http://',"\n",lineContent).replace('\n','')
                        element = {}
                        element["title"] = title
                        element["link"] = urlContent#+"|"+Downloader.getHeaders(listUrl)
                        element["thumbnail"] = ''
                        element["finalLink"] = True
                        if "://" in urlContent:
                            logger.debug("added: " + title + ", content: " + urlContent)
                            x.append(element)
                    i+=1
        return x

