import urllib

from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
from tvboxcore import logger


class Yomvies(Downloader):

    MAIN_URL = "http://ver.movistarplus.es"
    CHANNELS_PAGE = "http://akamaicache.dof6.com/vod/yomvi.svc/webplayer.hls/OTT/contents/epg/channels"
    INIT_TOKEN = "http://v36.voddeliveryservices.dof6.com/qsp/gateway/http/js/NmpExtendedService/initializeDevice"
    SIGN_IN = "http://ver.movistarplus.es/qsp/gateway/http/js/signonService/signonByMpDeviceId"
    INICIATE_DEVICE = "http://ver.movistarplus.es/qsp/gateway/http/js/NmpExtendedService/initializeDevice"

    NETWORK = "movistarplus"
    CHANNELS_SUBFIX = '&id_perfil=OTT&suscripcion=PS-APERTURALI%2CPS-APERTURAPC%2CPS-MINTDTLI%2CPS-SELEPLI%2CPS-SELEPPC%2CPS-YOPLAYPC&nv=2&network=movistarplus'

    @staticmethod
    def getChannels(page='0'):
        x = []
        if str(page) == '0':
            page = Yomvies.CHANNELS_PAGE
            logger.debug("loading json data from: "+page)
            bruteJSON = Yomvies.getContentFromUrl(page,"",Yomvies.cookie,Yomvies.MAIN_URL)
            logger.debug("parsing string to json...")
            i = 0
            for jsonChannel in bruteJSON.split('{"CodCadenaTv":'):
                if i>0:
                    element = {}
                    codTv = Decoder.extract('"','"',jsonChannel)
                    element["title"] = Decoder.extract('"Nombre":"','"',jsonChannel)
                    element["thumbnail"] = Decoder.extract('"Logo":"','"',jsonChannel).replace("\\","")
                    m3u8Url = Decoder.extract('"PuntoReproduccion":"','"',jsonChannel).replace("{network}",Yomvies.NETWORK).replace("\\","")
                    logger.debug("Appending channel: "+element["title"]+", with url: "+m3u8Url+", img: "+element["thumbnail"])
                    headers = 'Referer='+codTv
                    element["link"] = m3u8Url+"|"+headers
                    x.append(element)
                i+=1
        else:
            link = Yomvies.extractTargetVideo(page)
            element = {}
            element["title"] = page
            element["link"] = link
            element["finalLink"] = True
            x.append(element)
        return x

    @staticmethod
    def extractTargetVideo(page):
        url = page.split('|')[0]
        referer = page[page.rfind("=")+1:]
        referer = 'http://ver.movistarplus.es/player/?canal='+referer+Yomvies.CHANNELS_SUBFIX
        logger.debug("yomvi url is: "+url+", with referer: "+referer)
        html = Yomvies.getContentFromUrl(url=url,referer=referer,launchLocation=True)
        logger.debug("obtained response for yomvi page: "+html)
        newUrl = url[:url.rfind("/")+1]+Decoder.extractWithRegex("#EXT-",".m3u8",html).split("\n")[1]
        html2 = Yomvies.getContentFromUrl(url=newUrl, referer=url, launchLocation=True)
        logger.debug("obtained second response for yomvi page: " + html2)
        return "http://127.0.0.1:46720?original-request=" + newUrl#+"&referer="+referer

