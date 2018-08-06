import time
import re

import CommonFunctions as common

from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
from tvboxcore import logger

class CNN(Downloader):

    MAIN_URL = "http://www.CNN.com"
    LAST_NEWS_RSS = "http://rss.cnn.com/rss/edition_world.rss"

    @staticmethod
    def getChannels(page):
        x = []
        if page == '0':
            url = CNN.LAST_NEWS_RSS
            logger.debug("news rss url is: "+url)
            bruteResult = CNN.getContentFromUrl(url=url,launchLocation=True,ajax=False)
            logger.debug("brute response: "+bruteResult)
            lists = common.parseDOM(bruteResult, "item")
            if len(lists) > 0:
                logger.info("counted: " + str(len(lists)))
                for item in lists:
                    name = common.parseDOM(item, "title")[0].encode("utf-8")
                    value = common.parseDOM(item, "guid")[0].encode("utf-8")
                    logger.info("Added: " + name + ", url: " + value)
                    element = {}
                    element["title"] = name.replace('<![CDATA[','').replace("]]>","")
                    element["link"] = value.replace("//www.cnn.com/","//edition.cnn.com/")
                    try:
                        img = common.parseDOM(item, "media:content", ret="url")[0].encode("utf-8")
                        element["thumbnail"] = img
                    except:
                        logger.debug("Could not be extracted any img. :'(")
                    x.append(element)
        else:
            html = CNN.getContentFromUrl(url=page,launchLocation=True,referer=CNN.MAIN_URL)
            startRegex = '<div class="el__leafmedia el__leafmedia--sourced-paragraph">'
            body = Decoder.extract(startRegex,'</div><p class="zn-body__paragraph zn-body__footer">',html)
            logger.debug("removing html: "+body)
            body = Decoder.removeHTML(body)
            logger.debug("html has removed from body!")
            if '|' in body:
                body = body[body.find('|')+1:]
            try:
                lowerCaseIndex = int(re.search("[a-z]", body).start())
                body = body[:lowerCaseIndex-1]+"\n"+body[lowerCaseIndex-1:]
            except:
                logger.error("No break for city was done. Something goes wrong")
                pass
            element = {}
            element["link"] = page
            element["title"] = body
            element["thumbnail"] = ''
            x.append(element)
        return x

