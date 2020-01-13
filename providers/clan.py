import time
import re

from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
from tvboxcore import logger

import urllib

try:
    import json
except:
    import simplejson as json

class Clan(Downloader):

    MAIN_URL = "http://www.rtve.es/infantil/series/"
    CATALOG = "http://www.rtve.es/drmn/iso/catalog-category/?&colT=4&colM=2&size=18&sizeT=18&sizeM=11&exT=N&exM=N&tipopag=0&tpT=0&tpM=0&progtitle=S&ctx=INF&n1=Todos&c1=NN&i1=0&t1=PRO&f1=N&o1=FP&e1&q1=inPubTarget%253DINFANTIL%2526lang%253Des%2526order%253Dprogram_orden%252Casc&csel=1&de=S&ll=N&stt=S&fakeImg=S&col=4&r=/infantil/series/"
    JSON_CATALOG = 'http://www.rtve.es/api/agr-programas/490/programas.json?size=60&page=1'

    @staticmethod
    def getChannels(page):
        x = []
        if page == '0':
            jsonCatalog = Clan.getContentFromUrl(url=Clan.JSON_CATALOG,referer=Clan.MAIN_URL)
            jCatalog = json.loads(jsonCatalog)
            for item in jCatalog["page"]["items"]:
                title = item["name"]
                url = item["uri"]
                thumbnail = item["logo"]
                description = ''
                if item.has_key("description"):
                    description = item["description"]
                element = {}
                element["link"] = url
                element["title"] = title
                element["thumbnail"] = thumbnail
                x.append(element)
            logger.debug("returning "+str(len(x))+" elements")
        elif '/api/' in page and '/videos/' not in page:
            logger.debug("decoding videos from "+page)
            jsonCatalog = Clan.getContentFromUrl(url=page+'/videos.json', referer=Clan.MAIN_URL)
            jCatalog = json.loads(jsonCatalog)
            for item in jCatalog["page"]["items"]:
                title = item["title"]+" "+item["longTitle"]
                extractedUrl = item["htmlUrl"]
                thumbnail = item["imageSEO"]
                element = {}
                element["link"] = extractedUrl
                element["title"] = title
                element["thumbnail"] = thumbnail
                element["finalLink"] = True
                x.append(element)
            logger.debug("returning " + str(len(x)) + " elements")
        else:
            logger.debug("decoding final page: "+page)
            decoder = 'http://www.descargavideos.tv/?ajax=1'
            data = "web="+urllib.quote_plus(page)
            html = Clan.getContentFromUrl(url=decoder,data=data,referer='http://www.descargavideos.tv/');
            logger.debug("HTML IS: "+html)
            videoUrl = Decoder.extract(' name="video" value="','"',html)
            videoUrl = videoUrl.replace('&amp;','&')
            element = {}
            element["link"] = videoUrl+"|"+Downloader.getHeaders()
            element["title"] = page
            element["thumbnail"] = ''
            logger.debug("FINAL video is: " + videoUrl)
            x.append(element)
        return x

