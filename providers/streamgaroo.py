import urllib
try:
    import json
except:
    import simplejson as json

from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
from tvboxcore import logger
import base64

class Streamgaroo(Downloader):

    MAIN_URL = "http://www.streamgaroo.com"
    CHANNEL_API = 'http://www.streamgaroo.com/calls/get/source'
    COUNTRIES = 'http://www.streamgaroo.com/live-television'
    EVENTS = 'http://www.streamgaroo.com/live-sport'

    @staticmethod
    def getChannels(page='0'):
        x = []
        if str(page) == '0':
            page = Streamgaroo.MAIN_URL
            #add first element show by country
            element = {}
            element["title"] = 'Browse by Country'
            element["link"] = '1'
            element["navigate"] = True
            x.append(element)
            '''
            element = {}
            element["title"] = 'Browse by Event'
            element["link"] = '2'
            element["navigate"] = True
            x.append(element)
            '''
            #continue with splitted home links
            logger.debug("loading json data from: "+page)
            html = Streamgaroo.getContentFromUrl(page,"",Streamgaroo.cookie,Streamgaroo.MAIN_URL)
            for lineLink in html.split(' data-clk='):
                link = urllib.unquote_plus(Decoder.extract('"','"',lineLink))
                title = Decoder.extract(' title="','"',lineLink)
                img = Decoder.extract('<img class="stream-thumb" src="', '"', lineLink)
                element = {}
                element["title"] = title
                element["link"] = link
                element["thumbnail"] = img
                if "http" in link:
                    x.append(element)
        elif str(page) == '1':
            #show by country
            html = Streamgaroo.getContentFromUrl(Streamgaroo.COUNTRIES,"",Streamgaroo.cookie,Streamgaroo.MAIN_URL)
            splitter = '<div class="left-sidebar nc"><div class="left-sidebar-item"><div class="navigation navigation_0" data-type="normal">'
            menuHtml = Decoder.extract(splitter,'</li></ul></div></div></div>',html)
            for lineMenu in menuHtml.split('<li class="navigation-li"'):
                if '<a title="' in lineMenu:
                    title = Decoder.extract('<a title="','"',lineMenu)
                    link = Decoder.extract(' href="','"',lineMenu)
                    img = Decoder.extract(' src="','"',lineMenu)
                    element = {}
                    element["title"] = title
                    element["link"] = link
                    element["thumbnail"] = img
                    element["navigate"] = True
                    if "http" in link:
                        x.append(element)
        elif str(page) == '2':
            #show by country
            html = Streamgaroo.getContentFromUrl(Streamgaroo.EVENTS,"",Streamgaroo.cookie,Streamgaroo.MAIN_URL)
            splitter = '<table class="table-streams table table-condensed table-responsive">'
            menuHtml = Decoder.extract(splitter,'</table>',html)
            logger.debug(menuHtml)
            for lineMenu in menuHtml.split('<a class="title-'):
                if ' title="' in lineMenu:
                    title = Decoder.extract(' title="','"',lineMenu)
                    link = Decoder.extract(' href="','"',lineMenu)
                    img = Decoder.extract(' src="','"',lineMenu)
                    element = {}
                    element["title"] = title
                    element["link"] = link
                    element["thumbnail"] = img
                    if "http" in link:
                        x.append(element)
        elif '/live-television/' in page and '/' not in str(page[page.find('/live-television/')+len('/live-television/'):]) :
            #show country pages
            html = Streamgaroo.getContentFromUrl(page, "", Streamgaroo.cookie, Streamgaroo.MAIN_URL)
            channelsListsSplitter = '<div class="layouts layouts-streams layouts-streams-blocks">'
            channelsListsSplitterEnd = '</div>\n</div>\n</div> </div>'
            channelsHtml = Decoder.extract(channelsListsSplitter,channelsListsSplitterEnd,html)
            for channelLineHtml in channelsHtml.split('<a class="stream-thumb-a" '):
                link = Decoder.extract('href="','"',channelLineHtml)
                img = Decoder.extract('<img class="stream-thumb" src="','"',channelLineHtml)
                title = Decoder.extract(' title="','"',channelLineHtml)
                element = {}
                element["title"] = title
                element["link"] = link
                element["thumbnail"] = img
                if "http" in link:
                    x.append(element)
        else:
            link = Streamgaroo.extractTargetVideo(page)
            element = {}
            element["title"] = page
            element["link"] = link
            element["finalLink"] = True
            x.append(element)
        return x

    @staticmethod
    def extractTargetVideo(page):
        logger.debug("extracting from page: "+page)
        html = Streamgaroo.getContentFromUrl(url=page,referer=Streamgaroo.MAIN_URL)
        logger.debug("html is: "+html)
        apiKey = Decoder.extract('data-sh="','"',html)
        bruteJSON = Streamgaroo.getContentFromUrl(Streamgaroo.CHANNEL_API, "h="+apiKey, Streamgaroo.cookie, Streamgaroo.MAIN_URL)
        jsonList = json.loads(bruteJSON)
        url2 = jsonList["link"]
        logger.debug("using url: "+url2)
        html2 = Streamgaroo.getContentFromUrl(url2, "", Streamgaroo.cookie, page)
        logger.debug("html2 is: "+html2)
        if 'playJS("' in html2:
            finalUrl = Decoder.extract('playJS("','"',html2)
            logger.debug("found final url: "+finalUrl)
            finalUrl = finalUrl.replace("http://www.streamgaroo.com/fetch/r/","") #clean proxies
            if 'playlist.m3u8' in finalUrl and '==' in finalUrl:
                finalUrl = finalUrl.replace('playlist.m3u8?','chunks.m3u8?')
            finalUrl = finalUrl + "|" + urllib.unquote(Downloader.getHeaders())
        elif "playStream('iframe','" in html2:
            iframeUrl = finalUrl = Decoder.extract("playStream('iframe','","'",html2)
            logger.debug("found iframe link: " + iframeUrl)
            try:
                iframeHtml = Downloader.getContentFromUrl(url=iframeUrl, data=" ", referer=page)
            except:
                logger.debug("trying second way, easy!!")
                import urllib2
                req = urllib2.Request(iframeUrl)
                req.add_header('Referer', page)
                req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0')
                resp = urllib2.urlopen(req)
                iframeHtml = resp.read()
                logger.debug("done!")
                pass
            logger.debug("html iframe is: "+iframeHtml)
            if 'adca.st/broadcast/player' in iframeHtml:
                finalUrl = Decoder.decodeBroadcastst(iframeUrl,page)
            elif 'vaughnlive.tv/embed/video/' in iframeUrl:
                finalUrl = Decoder.decodeVaughnlivetv(iframeUrl,page)
        logger.debug("done!")
        return finalUrl
