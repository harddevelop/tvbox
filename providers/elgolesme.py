from tvboxcore import logger
from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder

class Elgolesme(Downloader):

    URL = "http://elgoles.me/index.php"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            html = Elgolesme.getContentFromUrl(Elgolesme.URL)
            table = Decoder.extract("<table id='my-table' width='100%'>","</tr></table>",html)
            i=0
            for line in table.split('<tr>'):
                if i>1:
                    href = Decoder.extract('td> <a href=','>',line)
                    title = Decoder.extract(href+'> ','</a>',line)
                    time = Decoder.extract('<td> <span class= t >','<',line)
                    platform = "Acestream"
                    if 'Html5  </a> </td>' in line:
                        platform = "HTML5"
                    element = {}
                    element["title"] = time+" : "+title+" - "+platform
                    element["link"] = href
                    x.append(element)
                    logger.debug("appended %s -#- %s"%(title,href))
                i+=1
        else:
            #Acestream
            html = Elgolesme.getContentFromUrl(url=page,referer=Elgolesme.URL)
            if '.m3u8?id=' in html:
                link = "acestream://"+Decoder.extract( '.m3u8?id=','"',html)
                link = "plugin://program.plexus/?mode=1&url="+link+"&name=RemoteLink"
            else:
                logger.debug("time for m3u8 source...")
                link = Elgolesme.decodeLink(html,page)
            element = {}
            element["link"] = link
            element["title"] = page
            x.append(element)
        return x

    @staticmethod
    def decodeLink(html,page):
        if 'http://www.ezcast.tv/static/scripts/hezcast.js' in html:
            id = Decoder.extract("channel='","'",html)
            url = "http://www.embedezcast.com/hembedplayer/%s/1/640/360"%str(id)
            html = Elgolesme.getContentFromUrl(url=url,referer=page)
            logger.debug("html is %s"%html)
            link = Decoder.extract('var hlsUrl = "http://" + ea + "','";',html)
            key = Decoder.extract('enableVideo("','");',html)
            id = Decoder.extract("?id=","&",link)
            requestedUrl = 'http://cdn.pubezcast.com:1935/loadbalancer?'+id
            url = Elgolesme.getContentFromUrl(url=requestedUrl).replace('redirect=','http://')
            link = url+link+key
            logger.debug("found link %s"%link)
            return link
