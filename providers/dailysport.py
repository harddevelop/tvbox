from tvboxcore import logger
from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
import urllib
import base64

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
                    links = []
                    for link in line.split("<a "):
                        if 'href=' in link:
                            href = Dailysport.URL+Decoder.extract('href=','>',link).replace('"','')
                            logger.debug("href found %s" % href)
                            links.append(href)
                    title = Decoder.extract('</td>','</td>',line).replace("<td>","").replace("\n","")
                    if "</span>" in title:
                        title = title[title.find("</span>")+len("</span>"):]
                    time = line[:line.find('</td>')].replace("<td>","").replace("\n","")
                    for href in links:
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
        if 'source: window.atob("' in html:
            extractor = 'source: window.atob("'
        elif "source:'" in html:
            extractor = "source: '"
        else:
            extractor = "'"
        link = Decoder.rExtract(extractor,'"',html)
        link = base64.b64decode(link)
        return link+"|User-Agent=Mozilla%2F5.0+%28X11%3B+Linux+x86_64%3B+rv%3A68.0%29+Gecko%2F20100101+Firefox%2F70.0&amp;Referer="+urllib.quote_plus(page)+"&amp;Origin=https://dailysport.pw"
