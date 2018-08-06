# coding=utf-8
from tvboxcore.xbmcutils import XBMCUtils
import urllib
from tvboxcore.downloader import Downloader
from tvboxcore import logger
from tvboxcore.decoder import Decoder
import base64

try:
    import json
except:
    import simplejson as json


class Pepecine(Downloader):

    MAIN_URL = 'https://pepecine.tv'
    SEARCH = "https://pepecine.tv/ver-online?q=%s"

    @staticmethod
    def search(text):
        #searchUrl = Pepecine.SEARCH % urllib.quote_plus(text)
        #html = Pepecine.getContentFromUrl(url=searchUrl,referer=Pepecine.MAIN_URL,cookie=Pepecine.cookie,launchLocation=True)
        #return Pepecine.extractItems(html)
        return Pepecine.searchItemByTitle(text)

    @staticmethod
    def extractItems(html):
        x = []
        htmlList = Decoder.extract('<h2 class="heading s1" style="border-radius: 10px 10px 0px 0px !important;margin-bottom: 1px !important;">','</h2>',html)
        i=0
        for htmlElement in htmlList.split("<a "):
            if i>0:
                element = {}
                title = Decoder.extract(" title=\"","\"",htmlElement)
                link = Pepecine.MAIN_URL+Decoder.extract(" href=\"", "\"", htmlElement)
                #img = Pepecine.MAIN_URL+"/"+Decoder.extract("<img src=\"","\"",htmlElement)
                element["title"] = title
                element["link"] = link
                #element["thumbnail"] = img
                x.append(element)
            i+=1
        return x

    @staticmethod
    def extractProvidersFromLink(page,providers=False):
        x = []
        token = Pepecine.getValidToken()
        logger.debug("TOKEN is: "+token)
        page2 = page % token
        oldTimeout = Downloader.TIMEOUT
        Downloader.TIMEOUT = 40 #needs more because response has too weight
        bruteJson = Pepecine.getContentFromUrl(url=page2,cookie=Pepecine.cookie,referer=Pepecine.MAIN_URL)
        Downloader.TIMEOUT = oldTimeout
        #logger.debug("BruteJSON is: "+bruteJson)
        totalJson = json.loads(bruteJson)
        if not providers:
            logger.debug("total items: " + str(len(totalJson["items"])))
            for elementJson in totalJson["items"]:
                element = {}
                element["thumbnail"] = elementJson["poster"]
                element["title"] = elementJson["title"].encode("utf-8")
                try:
                    #element["link"] = base64.encodestring(element["title"].encode("utf-8"))
                    connector = "/ver-serie/"
                    if elementJson["type"]=='movie':
                        connector = "/ver-online/"
                    element["link"] = Pepecine.MAIN_URL+connector+str(elementJson["id"])
                    x.append(element)
                except:
                    logger.debug("Could not encode: "+element["title"])
                    pass
        else:
            logger.debug("using title (items should be 1 and now is: "+str(len(totalJson["items"]))+" )")
            for elementJsonBefore in totalJson["items"]:
                title = elementJsonBefore["title"].encode("utf-8")
                for elementJson in elementJsonBefore["link"]:
                    element = {}
                    element["title"] = title+" - "+elementJson["url"]
                    element["link"] = elementJson["url"]
                    element["finalLink"] = True
                    x.append(element)
        return x

    @staticmethod
    def getValidToken():
        html = Downloader.getContentFromUrl(url=Pepecine.MAIN_URL)
        token = Decoder.extract("token: '","'",html)
        return token

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("page for pepecine: "+page)
        movie = 'movie'
        serie = 'series'
        if(str(page)=="0"):
            element = {}
            element["title"] = "Películas"
            element["link"] = 'https://pepecine.tv/titles/paginate?_token=%s&perPage=50&page=1&order=mc_num_of_votesDesc&type='+movie+'&minRating=&maxRating=&availToStream=1'
            x.append(element)
            element = {}
            element["title"] = "Series"
            element["link"] = 'https://pepecine.tv/titles/paginate?_token=%s&perPage=50&page=1&order=mc_num_of_votesDesc&type=' + serie + '&minRating=&maxRating=&availToStream=1'
            x.append(element)
            last = {}
            last["title"] = "Últimas películas publicadas"
            last["link"] = "https://pepecine.tv/plugins/estrenos-peliculas-online.php"
            x.append(last)
            last = {}
            last["title"] = "Últimas series actualizadas"
            last["link"] = "https://pepecine.tv/plugins/estrenos-episodios-online.php"
            x.append(last)
            search = {}
            search["title"] = XBMCUtils.getString(11018)
            search["link"] = ".search"
            x.append(search)

        elif page=='.search':
            logger.debug("search page detected...")
            #display keyboard, it will wait for result
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                x = Pepecine.search(text)
        elif '%s' in page: #token issue
            logger.debug("list page detected...")
            x = Pepecine.extractProvidersFromLink(page)
        elif page.endswith("=") or "://" not in page: #title in base64 format
            if "://" not in page:
                page+="=" #base64 could be missed
            title = base64.decodestring(page)
            logger.debug("trying to query by title: "+title)
            searchByTitle = "https://pepecine.tv/titles/paginate?_token=%s&perPage=24&page=1&order=mc_num_of_votesDesc&type=series&minRating=&maxRating=&query="+urllib.quote_plus(title)+"&availToStream=true"
            #x = Pepecine.extractProvidersFromLink(searchByTitle,True)
            x = Pepecine.searchItemByTitle(title)
        elif '/ver-online/' in page:
            #extract links from html
            x = Pepecine.extractLinksFromPage(page)
        elif '/ver-serie/' in page: #serie
            if '/seasons/' in page:
                if '/episodes/' in page: #draw links
                    x = Pepecine.extractLinksFromPage(page)
                else: #draw chapters
                    html = Pepecine.getContentFromUrl(url=page, referer=Pepecine.MAIN_URL)
                    episodesHtml = Decoder.extract('<ul class="list-unstyled" id="episode-list" data-bind="moreLess, playVideos">','</ul>',html)
                    i=0
                    for episodeHtml in episodesHtml.split('<li class="media bord">'):
                        if i>0:
                            link = Decoder.extract('<a class="col-sm-3" href="','"',episodeHtml)
                            img = Decoder.extract('<img class="media-object img-responsive" src="','"',episodeHtml)
                            title = Decoder.extract('"><b>','</a></h4>',episodeHtml)
                            element = {}
                            element["link"] = link
                            element["thumbnail"] = img
                            element["title"] = title.replace("</b>"," - ")
                            x.append(element)
                        i+=1
            else: #draw seasons
                html = Pepecine.getContentFromUrl(url=page, referer=Pepecine.MAIN_URL)
                seasonsHtml = Decoder.extract('<div class="heading bord" style="margin:0 -15px;">','<br>',html)
                i=0
                for seasonHtml in seasonsHtml.split('<a '):
                    if i>0:
                        link = Decoder.extract('href="','"',seasonHtml)
                        title = Decoder.extract('class="sezon">',"<",seasonHtml)
                        element = {}
                        element["title"] = title
                        element["link"] = link
                        x.append(element)
                    i+=1
        elif '/plugins/' in page: #last films and series
            html = Pepecine.getContentFromUrl(url=page, referer=Pepecine.MAIN_URL)
            i=0
            for line in html.split('<td><a'):
                if i>0:
                    link = Pepecine.MAIN_URL+Decoder.extract('href='," ",line)
                    title = Decoder.extract(' alt="','"',line)
                    img = Decoder.extract('<img src=', ' ', line)
                    element = {}
                    element["title"] = title
                    element["link"] = link
                    element["thumbnail"] = img
                    x.append(element)
                i+=1
        else:
            logger.debug("nothing done for page: "+page)
        return x

    @staticmethod
    def extractLinksFromPage(page):
        x = []
        html = Pepecine.getContentFromUrl(url=page, referer=Pepecine.MAIN_URL)
        linksContent = Decoder.extract('<div id="test">','<video id="trailer" class="video-js vjs-default-skin vjs-big-play-centered" controls preload="auto" width="100%" height="500px"> </video>',html)
        i = 0
        for linkContent in linksContent.split('<ul style="display : none;padding:0px;"><li style="list-style-type: none;">'):
            if i > 0 and '<img data-bind="attr: {src: app.utils.getFavicon(\'' in linkContent:
                link = Decoder.extract('<img data-bind="attr: {src: app.utils.getFavicon(\'', "')}", linkContent)
                time = Decoder.extract('<td style="width:130px;">', '</td>', linkContent)
                quality = Decoder.extract('<td style="width:110px;background-color:#B1FFC5;">', '</td>', linkContent)
                element = {}
                element["link"] = link
                element["title"] = quality + " - " + time + " - " + link
                element["finalLink"] = True
                x.append(element)
            i += 1
        return x

    @staticmethod
    def searchItemByTitle(title):
        x = []
        searchByTitle = 'https://pepecine.tv/typeahead/' + urllib.quote_plus(title)
        jsonContent = Pepecine.getContentFromUrl(url=searchByTitle, cookie=Pepecine.cookie, referer=Pepecine.MAIN_URL,ajax=True)
        logger.debug("jsonContent is: "+jsonContent)
        jsonContentParsed = json.loads(jsonContent)
        for jsonLine in jsonContentParsed:
            element = {}
            element["title"] = jsonLine["title"] + " - " + jsonLine["type"]
            element["thumbnail"] = jsonLine["background"]
            element["link"] = jsonLine["link"]
            x.append(element)
        return x