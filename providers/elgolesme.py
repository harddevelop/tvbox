from tvboxcore import logger
from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder

class Elgolesme(Downloader):

    URL = "http://elgoles.me/index.php"

    def getChannels(page):
        x = []
        if str(page) == '0':
            html = Elgolesme.getContentFromUrl(Elgolesme.URL)
            table = Decoder.extract("<table id='my-table' width='100%'>","</tr></table>",html)
            i=0
            for line in table.split('<tr>'):
                if i>0:
                    href = Decoder.extract('td> <a href=','>',line)
                    title = Decoder.rExtract('> ','</a>',html)
                    platform = "Acestream"
                    if 'Html5  </a> </td>' in line:
                        platform = "HTML5"
                    element = {}
                    element["title"] = title+" - "+platform
                    element["link"] = link
                    x.append(element)
                i+=1
        else:
            #Acestream
            html = Elgolesme.getContentFromUrl(url=page,referer=Elgolesme.URL)
            if '.m3u8?id=' in html:
                link = "acestream://"+Decoder.extract( '.m3u8?id=','"',html)
            else:
                link = Elgolesme.decodeLink(html,page)
            element = {}
            element["link"] = link
            element["title"] = page
            x.append(element)
        return x

    @staticmethod
    def decodeLink(html,page):
        if '</script><script type="text/javascript" src="' in html:
            if 'http://www.ezcast.tv/static/scripts/hezcast.js' in html:
                id = Decoder.extract("channel='","'",html)
                url = "http://www.embedezcast.com/hembedplayer/%s/1/640/360"%str(id)
                html = Elgolesme.getContentFromUrl(url=url,referer=page)
                link = Decoder.extract('var hlsUrl = "http://" + ea + "','";')
                key = Decoder.extract('enableVideo("','");')
                id = Decoder.extract("?id=","&",link)
                requestedUrl = 'http://cdn.pubezcast.com:1935/loadbalancer?'+id
                url = Elgolesme.getContentFromUrl(url=requestedUrl).replace('redirect=','http://')
                link = url+link+key
                logger.debug("found link %s"%link)
                return link
