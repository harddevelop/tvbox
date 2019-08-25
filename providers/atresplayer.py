from tvboxcore import logger
from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
import json

class Atresplayer(Downloader):

    URL = "https://api.atresplayer.com/client/v1/info/channels"
    DIRECTOS = "https://api.atresplayer.com/client/v1/row/live"
    SCHEDULE = "https://www.atresplayer.com/programacion/"

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Origin':'https://www.atresplayer.com'
    }

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            jsonContent = Atresplayer.getContentFromUrl(url=Atresplayer.DIRECTOS,headers=Atresplayer.HEADERS,referer=Atresplayer.SCHEDULE)
            parsed = json.loads(jsonContent)
            for line in parsed["itemRows"]:
                element = {}
                element["title"] = line["link"]["url"]+" - "+line["title"]
                element["link"] = line["link"]["href"]
                element["finalLink"] = True
                x.append(element)
        else:
            logger.debug("decoding link %s"%page)
            jsonContent = Atresplayer.getContentFromUrl(url=page,headers=Atresplayer.HEADERS,referer=Atresplayer.SCHEDULE)
            parsed = json.loads(jsonContent)
            url = parsed["urlVideo"]
            jsonContent = Atresplayer.getContentFromUrl(url=url,headers=Atresplayer.HEADERS,referer=Atresplayer.SCHEDULE)
            parsed = json.loads(jsonContent)
            link = parsed["sources"][0]["src"]
            title = parsed["omniture"]["channel"]
            logger.debug("found link %s"%link)
            element = {}
            element["title"] = title
            element["link"] = link
            x.append(element)
        return x
