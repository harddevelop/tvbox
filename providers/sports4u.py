from tvboxcore.decoder import Decoder
from tvboxcore import jsunpack
from tvboxcore import logger
from providers.cricfreetv import Cricfreetv
from tvboxcore.downloader import Downloader

class Sports4u(Downloader):

    MAIN_URL = "http://sports4u.live/"

    @staticmethod
    def getChannels(page):
        x = []
        start = False
        if str(page) == '0':
            start = True
            page=Sports4u.MAIN_URL
        html = Sports4u.getContentFromUrl(page,"",Sports4u.cookie,"")
        #print html
        if start and 'live-channels-list">' in html: #it's a list, needs decode
            table = Decoder.extract('live-channels-list">','</li><br>',html)
            logger.debug("using menu table: "+table)
            x = Sports4u.extractElements(table)
            logger.debug("channel list logic done!")
        else:
            iframeUrl = Decoder.extract('<iframe frameborder="0" marginheight="0" marginwidth="0" height="490" ','"></iframe>',html)
            iframeUrl = Decoder.extract('src="','"',iframeUrl)
            logger.debug("iframeUrl is: "+iframeUrl)
            html2 = Sports4u.getContentFromUrl(url=iframeUrl,referer=page)
            logger.debug("html is: "+html2)
            file = Cricfreetv.seekIframeScript(html2,page,iframeUrl)
            logger.debug("Finished file logic, obtained file: "+file)
            element = {}
            element["link"] = file
            element["title"] = "Watch streaming"
            x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        for fieldHtml in table.split('<li>'):
            if fieldHtml.find("<a href=")>-1:
                element = {}
                element["link"] = Decoder.extract('<a href="','"',fieldHtml)
                title = Decoder.extract('alt="','">',fieldHtml)
                if len(title)==0 and len(element["link"])>0: #provider probably has removed the alt content to 'destroy' scripts xD
                    link = element["link"]
                    title = Decoder.extract("channel/","/",link)
                    logger.debug("alternative title: "+title)
                element["title"] = Decoder.extract('/channel/','-live',element["link"]).replace("-"," ")
                element["thumbnail"] = Decoder.extract('src="','" ',fieldHtml)
                logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumbnail: "+element["thumbnail"])
                if len(element["title"])>0:
                    x.append(element)

        return x
