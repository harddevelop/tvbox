from tvboxcore import logger
from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
import urllib

class Dailysport(Downloader):

    URL = "https://dailysport.pw/"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            html = Dailysport.getContentFromUrl(Dailysport.URL)
            table = Decoder.extract("</thead>","</tbody>",html)
            i=0
            for line in table.split('<tr>'):
                if i>0:
                    href = Dailysport.URL+Decoder.extract('<a href=','>',line)
                    title = Decoder.extract('</td>','</td>',line).replace("<td>","").replace("\n","")
                    time = line[:line.find('</td>')].replace("<td>","").replace("\n","")
                    element = {}
                    element["title"] = str(time+" : "+title).strip()
                    element["link"] = href
                    x.append(element)
                    logger.debug("appended %s -#- %s"%(title,href))
                i+=1
        else:
            link = Dailysport.decodeLink(page)
            element = {}
            element["link"] = link
            element["title"] = page
            x.append(element)
        return x

    @staticmethod
    def decodeLink(page):
        html = Dailysport.getContentFromUrl(url=page,referer=Dailysport.URL)
        link = Decoder.rExtract("source:'",".m3u8'",html)+".m3u8"
        return link+"|User-Agent=Mozilla%2F5.0+%28X11%3B+Linux+x86_64%3B+rv%3A68.0%29+Gecko%2F20100101+Firefox%2F68.0&amp;Referer="+urllib.quote_plus(page)
