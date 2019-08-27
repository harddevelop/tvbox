from tvboxcore import logger
from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
import urllib
import json #todo

class Rojadirecta(Downloader):

    URL = 'http://rojadirecta.unblocker.cc/'

    @staticmethod
    def getChannels(page):
        x = []
        if page == '0':
            html = Rojadirecta.getContentFromUrl(Rojadirecta.URL)
            table = Decoder.extract('<table class="taboastreams" id="taboastreams7" border="0" cellpadding="1" cellspacing="1">','<div class="menutitle"><br></div>',html)
            logger.debug("html is: %s"%table)
            i=0
            for line in table.split('<td><span class="es">Nombre</span>'):
                if i>0:
                    title = Decoder.extract('div class="menutitle"','</div>',line)
                    title = title[title.find('">')+len('">')+1:]
                    title = title[title.find('>')+1:]
                    title = title.replace('<span class="t">','').replace('</span>','').replace("</b>","").replace("<b>","").replace('<span class="en">','').replace('<span class="es">','').replace('<span itemprop="name">','')
                    j=0
                    for lines in line.split('td><b><a rel="nofollow" href="'):
                        if j>0 and '/goto/' in lines:
                            link = Decoder.extract('/goto/','"',lines)
                            element = {}
                            element["title"] = title+" - "+link
                            element["link"] = "https://"+link
                            x.append(element)
                        else:
                            logger.debug("discarted: %s"%lines) #todo: probably an arenavision link
                        j+=1
                i+=1
        else:
            #decode -> use if possible current production kodi plugins
            url = ''
            if 'livestream.com' in page:
                logger.debug("livestream provider %s" % page)
                #url = "plugin://plugin.video.vimeo/play/?video_id=" + urllib.quote_plus(page)
                html = Rojadirecta.getContentFromUrl(page)
                url = Decoder.extract('app-argument=','"',html)
                apiUrl = url.replace('https://livestream.com/','https://player-api.new.livestream.com/')+'/stream_info'
                logger.debug("sending api url %s"%apiUrl)
                headers = {
                    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language':'en-US,en;q=0.5'
                }

                html = Rojadirecta.getContentFromUrl(url=apiUrl,headers=headers)
                jsonLoaded = json.loads(html)
                url = jsonLoaded["m3u8_url"]
            elif 'youtube.com' in page:
                logger.debug("youtube provider %s" % page)
                id = ""
                if "v=" in page:
                    id = page[page.find("v=") + len("v="):]
                elif "/embed/" in page:
                    id = page[page.find("/embed/") + len("/embed/"):]
                url = "plugin://plugin.video.youtube/play/?video_id=%s" % id
            elif 'mycujoo.tv' in page:
                logger.debug("mycujoo.tv provider %s"%page)
                html = Rojadirecta.getContentFromUrl(page)
                url = Decoder.extract('property="twitter:player:stream" content="','"',html)
            elif 'twitch.tv' in page:
                channel = page[page.find('channel=')+len('channel='):]
                url = 'plugin://plugin.video.twitch/?mode=play&channel_name=%s' % channel
            element = {}
            element["title"] = page
            element["link"] = url
            x.append(element)
        return x
