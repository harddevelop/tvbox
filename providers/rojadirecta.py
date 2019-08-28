from tvboxcore import logger
from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
import urllib
import json #todo

class Rojadirecta(Downloader):

    URL = 'http://rojadirecta.unblocker.cc/'

    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'en-US,en;q=0.5'
    }

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
                            element["link"] = "http://"+link
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
            else:
                url = Rojadirecta.decodeIframes(page)
            element = {}
            element["title"] = page
            element["link"] = url
            x.append(element)
        return x

    @staticmethod
    def decodeIframes(page):
        url = ''
        logger.debug("decoding iframe... %s"%page)
        html = Rojadirecta.getContentFromUrl(url=page,headers=Rojadirecta.headers)
        logger.debug("HTML: %s"%html)
        if "source: '" in html:
            url = Decoder.extract("source: '","'",html)
        elif '<iframe' in html and 'src="':
            iframe = ''
            for line in html.split('<iframe'):
                line = line[0:line.find("</iframe>")]
                logger.debug("line is: %s"%line)
                if ' src="' in line and not ("ads" in line or ".gif" in line):
                    iframe = Decoder.extract(' src="','"',line)
                    logger.debug("selected line is %s"%line)
                    break
                elif " src='" in line and not ("ads" in line or ".gif" in line):
                    iframe = Decoder.extract(" src='","'",line)
                    logger.debug("selecteD line is %s"%line)
                    break
                else:
                    logger.debug("discarting: %s"%line)
            logger.debug("selected iframe is: %s"%iframe)
            if "http" not in iframe and "//" in iframe:
                iframe = "http:"+iframe
            elif "http" not in iframe and not ("../" in iframe or "./" in iframe):
                iframe = "http://"+iframe
            elif "../" in iframe:
                domain = Decoder.extract("//","/",page)
                logger.debug("domain is: %s, page: %s"%(domain,page))
                newUrl = iframe[2:]
                logger.debug("new URL %s"%newUrl)
                iframe = "http://"+domain+newUrl
            elif "./" in iframe:
                domain = Decoder.extract("//","/",page)
                logger.debug("domain is: %s, page: %s"%(domain,page))
                newUrl = iframe[1:]
                logger.debug("new URL %s"%newUrl)
                iframe = "http://"+domain+newUrl
            else:
                logger.debug("nothing with iframe %s" % iframe)
            iframe = iframe.replace(" ","%2D")
            html2 = Rojadirecta.getContentFromUrl(url=iframe,headers=Rojadirecta.headers,referer=page)
            if '<iframe ' in html2 and ' src="':
                logger.debug("detected iframe...")
                url = Rojadirecta.decodeIframes(iframe)
            else:
                logger.debug("HTML2: %s"%html2)
                if "source: '" in html2:
                    url = Decoder.extract("source: '","'",html2)
                elif 'eval(function(p,a,c,k,e,d)' in html2:
                    #packer = Decoder.extractWithRegex('eval(function(p,a,c,k,e,d)',',{}))',html2)
                    packer = "eval("+Decoder.extract("eval(",",{}))",html2)+',{}))'
                    logger.debug("packer: %s"%packer)
                    from tvboxcore import jsunpack
                    unpacked = jsunpack.unpack(packer)
                    logger.debug("unpacked: %s"%unpacked)
                    if '.m3u8' not in unpacked:
                        logger.debug("launching manual method...")
                    else:
                        url = Decoder.rExtract('http','.m3u8',unpacked)
                else:
                    #js player embed
                    if 'https://janjuaplayer.com/resources/scripts/hjanjua.js' in html2:
                        channel = Decoder.extract("channel='","'",html2)
                        url = "https://www.janjua.tv/iembedplayer/"+channel+"/1/700/480"
                        logger.debug("using page: %s, referer: %s"%(url,iframe))
                        html3 = Rojadirecta.getContentFromUrl(url=url,referer=iframe)
                        logger.debug("HTML3: %s"%html3)
                        #using algorithm of vercanalestv1.com
                        lastUrl = Decoder.extract('var hlsUrl = "','="',html3)+"="
                        hmac = Decoder.extract('hlsUrl = hlsUrl + enableVideo("','"',html3)
                        hmac = hmac[:8]+hmac[9:]
                        lastUrl = lastUrl + hmac
                        #loadbalancer domain
                        loadBalancer = Decoder.extract('$.ajax({url: "','",',html3)
                        domain = Rojadirecta.getContentFromUrl(url=loadBalancer,referer=url)
                        domain = domain[domain.find('=')+1:]
                        lastUrl = lastUrl.replace('" + ea + "',domain)
                        logger.debug("link is: %s. Sum headers to kodi..."%lastUrl)
                        lastUrl = lastUrl+"|User-Agent=Mozilla%2F5.0"
                        #lastUrl = lastUrl+"|User-Agent=Mozilla%2F5.0+%28X11%3B+Linux+x86_64%3B+rv%3A68.0%29+Gecko%2F20100101+Firefox%2F68.0&amp;Referer="+urllib.quote_plus(url)
                        #lastUrl = "plugin://plugin.video.f4mTester/?streamtype=TSDOWNLOADER&amp;url="+lastUrl
                        url = lastUrl

        return url
