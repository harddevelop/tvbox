import urllib

from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
from tvboxcore.xbmcutils import XBMCUtils
from tvboxcore import logger

try:
    import json
except:
    import simplejson as json

class TuneIn(Downloader):

    SEARCH_PAGE = "https://api.tunein.com/profiles?fullTextSearch=true&formats=mp3,aac,ogg,flash,html&partnerId=RadioTime&version=2&itemUrlScheme=secure&build=2.0.1&reqAttempt=1&query="
    MAIN_URL = "https://tunein.com"
    GUIDE_URL = 'https://opml.radiotime.com/Tune.ashx?id=%s&listenId=999&itemToken=%s&formats=mp3,aac,ogg,flash,html&type=station&serial=%s&partnerId=RadioTime&version=2&itemUrlScheme=secure&build=2.0.1&reqAttempt=1'

    @staticmethod
    def getChannels(page):
        x = []
        if page == '0':
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                if len(text)>0:
                    page = TuneIn.SEARCH_PAGE+urllib.quote_plus(text)
                    results = TuneIn.getContentFromUrl(page,ajax=True,referer=TuneIn.MAIN_URL)
                    logger.debug("resultHtml is: "+results)
                    jsonResults = json.loads(results)

                    for resultKind in jsonResults["Items"]:
                        logger.debug("items...")
                        for result in resultKind["Children"]:
                            logger.debug("children...")
                            element = {}
                            img = result["Image"]
                            logger.debug("image is: "+img)
                            guideId = result["GuideId"]
                            url = result["Actions"]["Echo"]["Url"]
                            logger.debug("url is: " + url)
                            id = result["Actions"]["Echo"]["TargetItemId"]#[1:]
                            logger.debug("id is: " + id)
                            #https://api.radiotime.com/profiles/me/activities?serial=11f2610a-b534-41c5-96b4-ccbfd5a6d4c8&partnerId=RadioTime&version=2&formats=mp3%2caac%2cogg%2cflash%2chtml&itemToken=BgQEAAEAAQABAAEACwsAAwQFDAAA
                            serial = url[url.rfind("serial=") + len("serial="):]
                            if "&" in serial:
                                serial = serial[:serial.find("&")]
                            itemToken = url[url.rfind("itemToken=")+len("itemToken="):]
                            if "&" in itemToken:
                                itemToken = itemToken[:itemToken.find("&")]
                            title = result["Title"]
                            link = TuneIn.GUIDE_URL % (id,itemToken,serial)
                            logger.debug("appending result: "+title+", url: "+link)
                            element["title"] = title
                            element["link"] = link
                            element["thumbnail"] = img
                            element["finalLink"] = True
                            x.append(element)

        else:
            logger.debug("extracting stream for: "+page)
            html = TuneIn.getContentFromUrl(url=page)
            logger.debug("decoded html is: "+html)
            #content = json.loads(html)
            element = {}
            while 'https://stream.radiotime.com/listen.stream' in html:
                logger.debug("old html is: " + html)
                html = TuneIn.getContentFromUrl(url=html)
                logger.debug("new html is: " + html)

            if "http://" in html and '"' in html:
                html = html[:html.find('"')]
            elif "http://" in html and "'" in html:
                html = html[:html.find("'")]
            else:
                logger.debug("nothing done")
            logger.debug("new URL is: "+html)
            link = html

            element["link"] = link
            #element["link"] = content["body"][0]["url"]
            #element["title"] = content["body"][0]["element"]
            element["title"] = link
            element["thumbnail"] = ""
            x.append(element)
        return x

