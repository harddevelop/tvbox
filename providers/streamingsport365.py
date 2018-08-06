from tvboxcore.downloader import Downloader
from tvboxcore.decoder import Decoder
from tvboxcore import logger

class StreamingSports365(Downloader):

    MAIN_URL = "http://www.streamingsport365.com"
    HTML_CHANNELS = "http://streamingsport365.com/en/tv-guide-channel-9/"

    @staticmethod
    def getChannels():
        x = []
        url = StreamingSports365.HTML_CHANNELS
        logger.debug("html channels url is: "+url)
        bruteResult = StreamingSports365.getContentFromUrl(url=url,referer=StreamingSports365.MAIN_URL)
        logger.debug("html is: "+bruteResult)
        htmlResults = Decoder.extract('<table class="uk-table uk-table-hover uk-table-striped">',"</table>",bruteResult)
        for item in htmlResults.split("<tr>"):
            if "<td>acestream://" in item:
                name = ""
                if '"><strong>' in item:
                    name = Decoder.extract('"><strong>','</strong>',item)
                else:
                    name = Decoder.extract('html">', '<', item)
                link = "acestream://"+Decoder.extract('<td>acestream://','</td>',item)
                logger.info("Added: " + name + ", url: " + link)
                element = {}
                element["title"] = name
                element["link"] = link
                x.append(element)
        return x