import urllib2
import re
from tvboxcore.decoder import Decoder
from tvboxcore import logger

from tvboxcore.downloader import Downloader

try:
    import json
except:
    import simplejson as json


class ZonaAppCom(Downloader):
    API_URL = "http://zona-app.com/zona-app/api.php?api_key"
    LIST_URL = "http://zona-app.com/zona-app/api.php?cat_id=14&key="
    IMAGES_URL = "http://zona-app.com/zona-app/images/"

    @staticmethod
    def getChannelsJSON():
        content = ZonaAppCom.getContentFromUrl(ZonaAppCom.API_URL)
        apiKey = Decoder.extract('"key":"','"',content)
        logger.debug("extracted key: "+apiKey)
        jsonContent = ZonaAppCom.getContentFromUrl(ZonaAppCom.LIST_URL+apiKey)
        logger.debug("json content is: "+jsonContent)
        jsonList = json.loads(jsonContent)
        x = []
        for jsonEntry in jsonList["LIVETV"]:
            element = {}
            if jsonEntry.has_key("channel_title"):
                element["title"] = jsonEntry["channel_title"]
            if jsonEntry.has_key("channel_url"):
                element["link"] = jsonEntry["channel_url"]
            if jsonEntry.has_key("channel_thumbnail"):
                element["thumbnail"] = ZonaAppCom.IMAGES_URL+jsonEntry["channel_thumbnail"]
            if ".m3u8" in element["link"]:
                x.append(element)
                logger.debug("appended channel: " + element["title"] + ", link: " + element["link"])
        return x

    @staticmethod
    def getFinalLink(link):
        # trying to decode link downloading it again
        if ".m3u8" in link:
            logger.debug("old link: " + link)
            oldLink = link
            m3u8Text = ZonaAppCom.getContentFromUrl(link)
            logger.debug("m3u8 content is: "+m3u8Text)
            if "http" in m3u8Text:
                m3u8Text = m3u8Text[m3u8Text.find("http"):]
                if "\n" not  in m3u8Text:
                    link = m3u8Text
                    logger.debug("1) updated link to: " + link)
                    if ".php" in link:
                        # trying second time
                        m3u8Text = ZonaAppCom.getContentFromUrl(link)
                        if "http" in m3u8Text:
                            oldLink = link
                            link = m3u8Text[m3u8Text.find("http"):]
                            logger.debug("2) updated link to: " + link)
                            link += "|" + Downloader.getHeaders(oldLink)
                    else:
                        link += "|" + Downloader.getHeaders(oldLink)

                else:
                    logger.debug("0) Complex link, not changed!" + link)
            else:
                logger.debug("nothing done! "+link)
        return link

