# -*- coding: utf-8 -*-
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader
from tvboxcore.xbmcutils import XBMCUtils

try:
    import json
except:
    import simplejson as json

import urllib,urllib2,sys,time,md5,base64

class Mobdro(Downloader):

    MAIN_URL = "mobdro.me"
    CHANNELS = "channels"
    API_URL = "https://api.mobdro.sx/streambot/v4/show"
    API_URL_SEARCH = "https://api.mobdro.sx/streambot/v4/search"

    TOKEN = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "mobdro_api")  #stored for premium support, implementation will change
    REMOTE_TOKEN = XBMCUtils.getSettingFromContext(int(sys.argv[1]),"remote_api_url")

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("using Mobdro...")
        if str(page) == '0':
            element = {}
            element["title"]="Channels"
            element["link"] = "channels"
            x.append(element)
            element = {}
            element["title"] ="News"
            element["link"] = "news"
            x.append(element)
            element = {}
            element["title"] = "Shows"
            element["link"] = "shows"
            x.append(element)
            element = {}
            element["title"] = "Movies"
            element["link"] = "movies"
            x.append(element)
            element = {}
            element["title"] = "Sports"
            element["link"] = "sports"
            x.append(element)
            element = {}
            element["title"] = "Music"
            element["link"] = "music"
            x.append(element)
            element = {}
            element["title"] = "Gaming"
            element["link"] = "gaming"
            x.append(element)
            element = {}
            element["title"] = "Animals"
            element["link"] = "animals"
            x.append(element)
            element = {}
            element["title"] = "Tech"
            element["link"] = "tech"
            x.append(element)
            element = {}
            element["title"] = "Podcasts"
            element["link"] = "podcasts"
            #x.append(element)
            element = {}
            element["title"] = "Spiritual"
            element["link"] = "spiritual"
            #x.append(element)
            element = {}
            element["title"] = "Others"
            element["link"] = "others"
            x.append(element)
            element = {}
            element["title"] = "Search"
            element["link"] = "search"
            #x.append(element) #TODO
        elif str(page) is not 'search': #action
            logger.debug("launching action: "+page)
            response = Mobdro.channel_list(page)
            x = Mobdro.parse_results(response)
        elif str(page) == "search": #search
            logger.debug("launching action: SEARCH")
            # display keyboard, it will wait for result
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                response = Mobdro.search_list(text)
                x = Mobdro.parse_results(response)
        return x

    @staticmethod
    def parse_results(response):
        x = []
        # parse results
        results = json.loads(response)
        for result in results:
            url = Mobdro.parse_relayer(result)
            if url is not "exception":
                element = {}
                element["link"] = url
                try:
                    element["thumbnail"] = result["img"]
                except:
                    pass
                element["title"] = result["name"] + " - " + result["language"]
                element["finalLink"] = True
                logger.debug("appending: " + element["title"] + ", url: " + url)
                x.append(element)
        return x

    @staticmethod
    def pretoken():
        if (Mobdro.TOKEN is None or len(Mobdro.TOKEN)==0) and (Mobdro.REMOTE_TOKEN is not None and len(Mobdro.REMOTE_TOKEN)>0):
            remoteToken = Downloader.getContentFromUrl(Mobdro.REMOTE_TOKEN).encode("utf-8").strip()
            logger.debug("mobdro token is: "+remoteToken)
            Mobdro.TOKEN = remoteToken
            logger.debug("constant is: "+Mobdro.TOKEN)

    @staticmethod
    def search_list(term):
        response = "ERROR"
        c_headers = {"User-Agent": "Mobdro/5.0", "Referer": "api.mobdro.sx"}
        logger.debug("TOKEN is: " + Mobdro.TOKEN)
        c_data = {'query':term,'parental':0,'languages':'[]','alphabetical':0,'token': Mobdro.TOKEN}
        c_data = urllib.urlencode(c_data)
        # Fetch channel list
        req = urllib2.Request(Mobdro.API_URL_SEARCH, c_data, c_headers)
        response = urllib2.urlopen(req)
        response = response.read()
        return response

    @staticmethod
    def channel_list(action):
        Mobdro.pretoken()
        response = "ERROR"
        # On first page, pagination parameters are fixed
        if action is not None:
            c_headers = {"User-Agent": "Mobdro/5.0", "Referer": "api.mobdro.sx"}
            logger.debug("TOKEN is: " + Mobdro.TOKEN)
            c_data = {'data': action, 'parental': 0, 'languages': '[]', 'alphabetical': 0, 'token': Mobdro.TOKEN}
            c_data = urllib.urlencode(c_data)
            # Fetch channel list
            req = urllib2.Request(Mobdro.API_URL, c_data, c_headers)
            response = urllib2.urlopen(req)
            response = response.read()
        return response

    @staticmethod
    def parse_relayer(params):
        url = "NonE"
        try:
            if params.has_key("url"):
                url = params["url"]
                logger.debug("mobdro.directURL: " + url)
            elif params.has_key("relayer"):
                params2 = json.loads(params["relayer"])
                logger.debug("RELAYED: "+repr(params2))
                protocol = "http"#params2["protocol"]
                app = params2["app"]
                server = params2["server"]
                playpath = params2["playpath"]
                password = params2["password"]
                dire = params2["dir"]
                expiration_time = params2["expiration_time"]
                millis = int(round(time.time() * 1000))
                l = millis / 1000L + expiration_time
                arr = [password, l, dire, playpath]
                url = "%s%d/%s/%s"
                url = url % tuple(arr)
                url_md5 = md5.new(url).digest()
                url_base64 = base64.b64encode(url_md5)
                url_base64 = url_base64.replace("+", "-").replace("/", "_").replace("=", "")
                #arr = [server, url_base64, l, playpath]
                arr = [protocol,server,app,playpath,url_base64,l]
                url = "%s://%s/%s/%s?st=%s&e=%d" #"http://%s/live/%s/%d/%s"
                url = url % tuple(arr)
                url += "|"+Downloader.getHeaders(Mobdro.MAIN_URL)
            else:
                logger.debug("REJECTED: " + repr(params))
        except KeyError:
            url = "exception"
            pass
        return url