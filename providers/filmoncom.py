import urllib2
import re
from tvboxcore.decoder import Decoder
from tvboxcore import logger

try:
    import json
except:
    import simplejson as json


class Filmoncom():
    MAIN_URL = "http://www.filmon.com/tv/"

    @staticmethod
    def getChannelsJSON():
        request = urllib2.Request(Filmoncom.MAIN_URL)
        request.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0")
        response = urllib2.urlopen(request)
        html=response.read()
        response.close()
        #THIS CODE IS NOT USED BECAUSE IT'S FOR TESTS CHANNELS
        #script = re.search('(?si)<script type="text/javascript">(.*?)"is_free_sd_mode"(.*?)</script>', html) #short list, only 42 channels
        #bruteScript = script.group(0);
        #jsonContent = bruteScript[(bruteScript.find("var featured = ")+len("var featured = ")):]
        #jsonContent = jsonContent[:(jsonContent.find("}];")+len("}]"))]
        #jsonList = json.loads(jsonContent)

        script2 = re.search('(?si)<script type="text/javascript" defer="defer">(.*?)"is_free_sd_mode"(.*?)</script>', html) #all channels with groups
        bruteScript = script2.group(0);
        jsonContent = bruteScript[(bruteScript.find("var groups = ")+len("var groups = ")):]
        jsonContent = jsonContent[:(jsonContent.find("}];")+len("}]"))]
        jsonList2 = json.loads(jsonContent)
        return jsonList2


    @staticmethod
    def launchScriptLogic(url,referer):

        id = url[url.find('channel_id=')+len('channel_id='):] #could be used last index of '=' but... I'm boried about this provider

        ajaxUrl = "http://www.filmon.com/api-v2/channel/"
        ajaxUrl = ajaxUrl+id #update with the channel id

        request = urllib2.Request(ajaxUrl, "", {"X-Requested-With":"XMLHttpRequest"})
        request.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0")

        logger.debug("launching ajax request: "+ajaxUrl)

        #response = urllib2.urlopen(request)
        response = Decoder.getContent(ajaxUrl,"",referer,"",True)
        html=response.read()
        response.close()

        jsonList = json.loads(html)
        return jsonList["data"]["streams"]

    @staticmethod
    def getChannelUrl(url):
        print url
        request = urllib2.Request(url)
        request.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0")
        request.add_header("Referer", Filmoncom.MAIN_URL)
        response = urllib2.urlopen(request)
        html=response.read()
        response.close()

        pattern = '(?si)<script(.*?)default_channel = (.*?)</script>'
        #print html
        script = re.search(pattern, html)
        bruteScript = script.group(0);
        id = bruteScript[(bruteScript.find("default_channel = ")+len("default_channel = ")+4):]
        id = id[:id.find("'")]

        ajaxUrl = "http://www.filmon.com/ajax/getChannelInfo"
        #data = json.dumps([{"channel_id":id},{"quality":"high"}])
        data = "channel_id="+id+"&quality=high"
        request = urllib2.Request(ajaxUrl, data, {"X-Requested-With":"XMLHttpRequest"})
        request.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0")

        finalCookie = ""
        cookies = response.info()['Set-Cookie']
        for cookie in cookies.split(";"):
            if cookie.find("path=") == -1 and cookie.find("expires=") == -1 and cookie.find("Max-Age=") and cookie.find("domain="):
                if len(finalCookie)>0:
                    finalCookie += "; "
                finalCookie+= cookie

        completeCookie = "ftv_defq=hd; flash-player-type=hls; return_url=%2Ftv%2F"+url[:url.rfind("/")]+"; "+finalCookie
        request.add_header("Cookie", completeCookie)

        response = urllib2.urlopen(request)
        html=response.read()
        response.close()

        jsonList = json.loads(html)
        return jsonList["streams"]
