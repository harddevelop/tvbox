from core import logger
from core.decoder import Decoder
from core.downloader import Downloader
from core.xbmcutils import XBMCUtils
import urllib

try:
    import json
except:
    import simplejson as json

class Youtube(Downloader):

    MAIN_URL = "https://www.youtube.com"
    SEARCH_URL = "https://www.youtube.com/results?search_query="

    @staticmethod
    def getChannels(page='0'):
        x = []
        if str(page) == '0':
            page=Youtube.MAIN_URL+"/"
            html = Youtube.getContentFromUrl(page,"",Youtube.cookie,"")
            logger.debug("html: "+html)
            x = Youtube.extractMainChannels(html)
            if len(x)==0:
                jsonScript = Decoder.extract('ytInitialGuideData = ',';',html)
                x = Youtube.extractMainChannelsJSON(jsonScript)
            element = {}
            element["title"] = XBMCUtils.getString(11018)
            element["page"] = 'search'
            x.append(element)
        elif str(page) == 'search':
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                text = urllib.quote_plus(text)
                html = Youtube.getContentFromUrl(Youtube.SEARCH_URL+text, "", Youtube.cookie, "https://www.youtube.com/?app=desktop")
                html = html.replace('\u003e','>').replace("\u003c","<").replace("\\","")
                logger.debug("brute html is: "+html)
                x = Youtube.extractAllVideosFromHtml(html)
                logger.debug("done search logic!")
        elif '/results?' in page:
            logger.debug("pagination detected: "+page)
            html = Youtube.getContentFromUrl(page, "", Youtube.cookie,Youtube.MAIN_URL)
            x = Youtube.extractAllVideosFromHtml(html)
            logger.debug("done search logic pagination!")
        elif page.find('/channel/')>-1:
            h= {}
            h['Host'] = 'www.youtube.com'
            h['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'
            h['Accept'] = "text/html,application/xhtml+xml,application/xml;q='0.9,*/*;q='0.8"
            h['Accept-Language'] = "es-MX,es-ES;q='0.9,es;q='0.7,es-AR;q='0.6,es-CL;q='0.4,en-US;q='0.3,en;q='0.1"
            h['Accept-Encoding'] = 'gzip, deflate, br'
            h['DNT'] = '1'
            h['Upgrade-Insecure-Requests'] = '1'
            h['Connection'] = 'keep-alive'
            h['Pragma'] = 'no-cache'
            h['Cache-Control'] = 'no-cache'
            html = Youtube.getContentFromUrl(url=page,referer=page,ajax=True,headers=h)
            x = Youtube.extractAllVideos(html)
            #if len(x) == 0:
            #jsonScript = Decoder.extract('window["ytInitialData"] = ',';',html)
            #try:
            #    x = Youtube.extractVideosFromChannelJSON(jsonScript)
            #except:
            #    x = Youtube.extractVideosFromSpecialChannelJSON(jsonScript)
        elif "/trending" in page:
            html = Youtube.getContentFromUrl(page, "", Youtube.cookie, Youtube.MAIN_URL)
            x = Youtube.extractAllVideosFromHtml(html)
        elif '&amp;list=' in page and '&amp;index=' not in page:
            logger.debug("detected a list, PARSING...")
            html = Youtube.getContentFromUrl(page, "", Youtube.cookie, Youtube.MAIN_URL)
            x = Youtube.extractListVideos(html)
        else:
            link = Youtube.extractTargetVideo(page)
            element = {}
            element["title"] = page.replace("&amp;","&")
            element["link"] = link
            element["finalLink"] = True
            x.append(element)
        return x

    @staticmethod
    def decodeKeepVid(link):
        html = Downloader.getContentFromUrl("http://keepvid.com/?url="+urllib.quote_plus(link))
        tableHtml = Decoder.extract('<table class="result-table" cellspacing="0" cellpadding="0" border="0">',"</table>",html)
        logger.debug("extracting from html: "+tableHtml)
        links = []
        selectedLink = ""
        for liHtml in tableHtml.split('<tr>'):
            link = Decoder.extract('a href="','"',liHtml)
            title = Decoder.extract('<td class="al" width="25%">', '</', liHtml)
            if ("1080P" in title and '(Pro Version)' not in title) or "1080p" not in title:
                selectedLink = link
            else:
                logger.debug("No link selected with title: "+title)
            logger.debug("url at this moment is (youtube external): " + link)
            links.append(link)
        if len(selectedLink)==0:
            selectedLink = links[0]
        return selectedLink

    @staticmethod
    def extractTargetVideo(link):
        logger.debug("trying to decode with youtube link decrypter: " + link)
        code = link[link.find("v=") + 2:]
        logger.debug("trying with code: " + code)
        try:
            link = Decoder.downloadY(code)
        except:
            # trying second way, external page

            html = Downloader.getContentFromUrl(link, referer=Youtube.MAIN_URL)
            oldLink = link
            if 'ytplayer.config = {' in html:
                logger.debug("trying new way for .m3u8 links...")
                link = Decoder.extract(',"hlsvp":"', '"', html).replace('\\', '')
                link = urllib.unquote(link)
                logger.debug("new youtube extracted link from json is: " + link)
                # link += "|" + Downloader.getHeaders(oldLink)
            if "http" not in link:
                logger.debug("trying old second way: external resource...")
                link = Youtube.decodeKeepVid(oldLink)
            pass
        if ".m3u8" in link:
            bruteM3u8 = Youtube.getContentFromUrl(link);
            if 'https://' in bruteM3u8:
                m3u8 = bruteM3u8[bruteM3u8.rfind('https://'):]
                link = urllib.unquote_plus(m3u8).strip()
                logger.debug("using the last one inside: "+m3u8)
            else:
                logger.debug("no last one link selected :'(")
        else:
            logger.debug("nothing is transformed for youtube links.")

        logger.debug("final youtube decoded url is: " + link)
        if ";" in link:
            logger.debug("; part, replacing = and ; characters")
            link = link.replace("=", "%3D").replace(";", "%3B")
        else:
            logger.debug("else part, replacing %3D by =")
            #link = link.replace("%3D","=")
        return link

    @staticmethod
    def extractListVideos(html):
        x = []
        tableHtml = Decoder.extract('<div class="playlist-videos-container yt-scrollbar-dark yt-scrollbar">','</div><div id="content" class="  content-alignment" role="main">',html)
        i=0
        for rowHtml in tableHtml.split('<span class="index">'):
            if i>0:
                element = {}
                link = "/watch?"+Decoder.extract('href="/watch?', '"', rowHtml)
                title = Decoder.extract('<h4 class="yt-ui-ellipsis yt-ui-ellipsis-2">','</h4>', rowHtml)
                if 'youtube.com' not in link:
                    link = Youtube.MAIN_URL+link
                logger.debug("link: " + link + ", title is: " + title)
                image = Decoder.extractWithRegex('https://i.ytimg.com/','"',rowHtml).replace('"','')
                element["title"] = title.strip()
                element["page"] = link
                element["finalLink"] = True
                element["thumbnail"] = image
                x.append(element)
            i+=1
        return x


    @staticmethod
    def extractAllVideosFromHtml(html):
        x = []
        tableHtml = Decoder.extract('class="item-section">','<div class="branded-page-box search-pager',html)
        i=0
        for rowHtml in tableHtml.split('<div class="yt-lockup-dismissable yt-uix-tile">'):
            if i>0:
                logger.debug("row html is: "+rowHtml)
                element = {}
                link = "/watch?"+Decoder.extract('href="/watch?', '"', rowHtml)
                title = Decoder.extract('  title="','"', rowHtml)
                if 'youtube.com' not in link:
                    link = Youtube.MAIN_URL+link
                logger.debug("link: " + link + ", title is: " + title)
                image = Decoder.extractWithRegex('https://i.ytimg.com/','"',rowHtml).replace('"','').replace("&amp;","&")
                element["title"] = title
                element["page"] = link
                if '&amp;list=' not in link:
                    element["finalLink"] = True
                element["thumbnail"] = image
                x.append(element)
            i+=1
        #add next if pagination exists
        if '<div class="branded-page-box search-pager  spf-link ">' in html:
            bruteHtmlPaginate = Decoder.rExtract('<div class="branded-page-box search-pager  spf-link ">','<div class="branded-page-v2-secondary-col">',html)
            title = Decoder.rExtract(">","</span></a>",bruteHtmlPaginate)
            title = title[:len(title)-2]
            link = Decoder.rExtract('href="','" class="yt-uix-button', bruteHtmlPaginate)
            if 'youtube.com' not in link:
                link = Youtube.MAIN_URL + link
            element = {}
            element["title"] = title
            element["page"] = link
            logger.debug("link: " + link + ", title is: " + title)
            x.append(element)
        return x

    @staticmethod
    def extractAllVideos(html):
        x = []
        jsonScript = Decoder.extract('<script type="application/ld+json">','</script>',html).strip()
        #logger.debug("json: "+jsonScript)
        jsonList = json.loads(jsonScript)
        for element in jsonList['itemListElement']:
            #logger.debug("element: "+str(element))
            if element.has_key('item'):
                for element2 in element["item"]["itemListElement"]:
                    #logger.debug("element2: "+str(element2))
                    target = {}
                    target["page"] = str(element2["url"])
                    code = target["page"][target["page"].rfind("=")+1:]
                    target["thumbnail"] = "https://i.ytimg.com/vi/"+code+"/mqdefault.jpg"
                    target["title"] = Decoder.extract('href="/watch?v='+code+'">',"</",html)
                    logger.debug("appended: "+target["title"]+", url: "+target["page"])
                    target["finalLink"] = True
                    x.append(target)
        return x

    @staticmethod
    def extractMainChannels(html):
        x = []
        i = 0
        for value in html.split('guide-item yt-uix-sessionlink yt-valign spf-link'):
            if i>0 and value.find("href=\"")>-1 and value.find('title="')>-1:
                element = {}
                title = Decoder.extract('title="','"',value)
                link = Youtube.MAIN_URL+Decoder.extract('href="','"',value)
                element["title"] = title
                element["page"] = link
                if value.find('<img ')>-1:
                    element["thumbnail"] = 'https://'+Decoder.extractWithRegex('i.ytimg.com','"',value).replace('"','')
                    logger.debug("thumbnail: "+element["thumbnail"])
                logger.debug("append: "+title+", link: "+element["page"])
                if "Home" not in title and "Movies" not in title:
                    x.append(element)
            i+=1
        return x

    @staticmethod
    def extractMainChannelsJSON(jsonScript):
        x = []
        jsonList = json.loads(jsonScript)
        for jsonElement in jsonList['items'][1]["guideSectionRenderer"]["items"]:
            title = ''
            url = ''
            thumbnail = ''
            element = {}
            element2 = jsonElement["guideEntryRenderer"]
            if element2.has_key('title'):
                title = element2['title']
            if element2.has_key('thumbnail'):
                thumbnail = element2['thumbnail']['thumbnails'][0]['url']
                if 'https' not in thumbnail:
                    thumbnail = 'https:'+thumbnail
            if element2.has_key('navigationEndpoint'):
                url = element2['navigationEndpoint']['webNavigationEndpointData']['url']
                if 'youtube.com' not in url:
                    url = 'https://youtube.com'+url
            element = {}
            element["title"] = title
            element["page"] = url
            element["thumbnail"] = thumbnail
            x.append(element)

        return x

    @staticmethod
    def extractVideosFromChannelJSON(jsonScript):
        x = []
        jsonList = json.loads(jsonScript)
        #contents -> twoColumnBrowseResultsRenderer -> tabs[0-4][0] -> tabRenderer -> content -> sectionListRenderer -> contents[0-9]
        for jsonElements in jsonList['contents']['twoColumnBrowseResultsRenderer']["tabs"][0]['tabRenderer']['content']['sectionListRenderer']['contents']:
            #-> itemSectionRenderer -> contents [0] -> shelfRenderer -> content -> horizontalListRenderer -> items [0-11] (4) -> gridVideoRenderer
            for jsonElement in jsonElements['itemSectionRenderer']['contents'][0]['shelfRenderer']['content']['horizontalListRenderer']['items']:
                title = ''
                url = ''
                thumbnail = ''
                element = {}
                element2 = jsonElement["gridVideoRenderer"]
                if element2.has_key('title'):
                    title = element2['title']['simpleText']
                if element2.has_key('thumbnails'):
                    thumbnail = element2['thumbnail']['thumbnails'][0]['url']
                    if 'https' not in thumbnail:
                        thumbnail = 'https:' + thumbnail
                if element2.has_key('videoId'):
                    url = element2['videoId']
                    url = 'https://youtube.com/watch?v='+url
                element = {}
                element["title"] = title
                element["page"] = url
                element["thumbnail"] = thumbnail
                x.append(element)

        return x

    @staticmethod
    def extractVideosFromSpecialChannelJSON(jsonScript):
        x = []
        jsonList = json.loads(jsonScript)
        # contents -> twoColumnBrowseResultsRenderer -> tabs[0-4][0] -> tabRenderer -> content -> sectionListRenderer -> contents[0-9]
        for jsonElements in jsonList['contents']['twoColumnBrowseResultsRenderer']["tabs"][0]['tabRenderer']['content'][
            'sectionListRenderer']['contents']:
            # -> itemSectionRenderer -> contents [0] -> shelfRenderer -> content -> horizontalListRenderer -> items [0-11] (4) -> gridVideoRenderer
            for jsonElement in \
            jsonElements['itemSectionRenderer']['contents'][0]['shelfRenderer']['content']['horizontalListRenderer'][
                'items']:
                title = ''
                url = ''
                thumbnail = ''
                element = {}
                element2 = jsonElement["gridVideoRenderer"]
                if element2.has_key('title'):
                    title = element2['title']['simpleText']
                if element2.has_key('thumbnails'):
                    thumbnail = element2['thumbnail']['thumbnails'][0]['url']
                    if 'https' not in thumbnail:
                        thumbnail = 'https:' + thumbnail
                if element2.has_key('videoId'):
                    url = element2['videoId']
                    url = 'https://youtube.com/watch?v=' + url
                element = {}
                element["title"] = title
                element["page"] = url
                element["thumbnail"] = thumbnail
                x.append(element)

        return x