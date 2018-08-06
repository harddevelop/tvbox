from tvboxcore.decoder import Decoder
from tvboxcore import jsunpack
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Mamahdcom(Downloader):

    MAIN_URL = "http://mamahd.com/live/"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            html = Mamahdcom.getContentFromUrl(Mamahdcom.MAIN_URL,"",Mamahdcom.cookie,"")
        else:
            html = Mamahdcom.getContentFromUrl(page,"",Mamahdcom.cookie,"")
        #print html
        if page=='0': #menu
            table = Decoder.extract('<div class="standard row channels">','</div>',html)
            logger.debug("table is: "+table)
            x = Mamahdcom.extractElements(table)
            logger.debug("mamahd channels logic done!")
        else:
            iframeHtml = Decoder.extract("<iframe ","</iframe>",html)
            iframeUrl = Decoder.extract('src="','"',iframeHtml)
            html2 = Mamahdcom.getContentFromUrl(url=iframeUrl,referer=page)
            logger.debug("obtained html from iframe: "+iframeUrl+"; html: "+html2)
            if 'src="http://hdcast.org' in html2:
                logger.debug("found script, launching logic...")
                scriptUrl = Decoder.extract('<script type="text/javascript" src="','"></script>',html2)
                logger.debug("extracting script url... from: "+scriptUrl)
                iframeUrl2 = Mamahdcom.extractScriptIframeUrl(html2,scriptUrl,iframeUrl)
                logger.debug("script url extracted: "+iframeUrl2)
                finalRtmpUrl = Mamahdcom.extractFinalRtmpUrl(iframeUrl2,iframeUrl)
                logger.debug("rtmp extracted is: "+finalRtmpUrl)
                element = {}
                element["link"] = finalRtmpUrl
                element["title"] = "Watch channel"
                element["permaLink"] = True
                logger.debug("finished append element!")
                x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        for fieldHtml in table.split('</a>'):
            logger.debug("using html: "+fieldHtml)
            element = {}
            element["link"] = Decoder.extract('href="','"',fieldHtml)
            element["title"] = Decoder.extract("<span>","</span>",fieldHtml)
            element["thumbnail"] = Decoder.extract('<img src="','"',fieldHtml)
            element["permaLink"] = True
            logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
            if "http" in element["link"]:
                x.append(element)
        return x


    @staticmethod
    def extractScriptIframeUrl(html,scriptUrl,referer):
        iframeUrl = ""
        logger.debug("extracting script iframe... url: "+scriptUrl)
        scriptContent = Mamahdcom.getContentFromUrl(scriptUrl,"",Mamahdcom.cookie,referer)
        #print scriptContent
        iframeUrl = Decoder.extract('src="',"'",scriptContent)
        logger.debug("brute iframeUrl is: "+iframeUrl)
        if iframeUrl.find("?u=")>-1:
            if '<script type="text/javascript"> fid="' in html:
                id = Decoder.extract('<script type="text/javascript"> fid="','"; ',html)
            iframeUrl = iframeUrl+id+Mamahdcom.getWidthAndHeightParams(html)
        return iframeUrl

    @staticmethod
    def getWidthAndHeightParams(html):
        subUrl = ""
        if html.find("; v_width=")>-1:
            width = Decoder.extract("; v_width=",";",html)
            height = Decoder.extract("; v_height=",";",html)
            subUrl = "&vw="+width+"&vh="+height
            logger.debug("width-height subUrl now is: "+subUrl)
        return subUrl

    @staticmethod
    def extractFinalRtmpUrl(url,referer):
        rtmpUrl = ""
        html = Mamahdcom.getContentFromUrl(url,"",Mamahdcom.cookie,referer)
        if 'file:\'' in html:
            file = Decoder.extract("file:'",'\',',html)
            rtmp = file[0:file.rfind("/") + 1]
            playpath = file[file.rfind("/") + 1:]
            swfUrl = ""
            secureToken = "SECURET0KEN#yw%.?()@W!"
            if url.find("hdcast.org") > -1:
                swfUrl = "http://player.hdcast.org/jws/jwplayer.flash.swf"
            rtmpUrl = rtmp + " playPath=" + playpath + " swfUrl=" + swfUrl + " pageUrl=" + url + " flashver=WIN/2019,0,0,226 live=true timeout=14 token=" + secureToken
            logger.debug("built final rtmp link: " + rtmpUrl)
        elif 'allowtransparency="true" src=' in html:
                logger.debug("using second way...")
                secondIframe = Decoder.extract('allowtransparency="true" src=', ' ', html).replace("&amp;","&")
                logger.debug("found second way url: " + secondIframe+", referer: "+url)
                headers = {
                    "User-Agent": Downloader.USER_AGENT,
                    "Accept-Language": "en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3",
                    "Upgrade-Insecure-Requests" : "1",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Referer": url
                }
                html2 = Mamahdcom.getContentFromUrl(url=secondIframe,headers=headers)
                logger.debug("html2 is: "+html2)
                if 'file:"' in html2:
                    rtmpUrl = Decoder.extract('file:"', '",', html2)
                    logger.debug("using m3u8 for: "+rtmpUrl)
        return rtmpUrl