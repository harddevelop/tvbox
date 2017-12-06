# coding=utf-8
from core.xbmcutils import XBMCUtils
import urllib2
import httplib
import urllib
import re
import time
from core import logger
from core.decoder import Decoder
from core.downloader import Downloader
import base64

try:
    import json
except:
    import simplejson as json


class HdfullTv():

    magicKey = ""
    cookie = ""

    @staticmethod
    def search(text):
        cookie = HdfullTv.getNewCookie()
        postForm = {}

        postForm["menu"] = "search"
        postForm["query"] = text
        postForm["search-button"] = ""
        postForm["__csrf_magic"] = HdfullTv.magicKey
        response = HdfullTv.getJSONAJAXResponse("http://hdfull.tv/buscar",postForm,cookie,"http://hdfull.tv")
        if len(HdfullTv.magicKey)==0:

            HdfullTv.magicKey = Decoder.extract("__csrf_magic' value=\"",'"',response.read())
            postForm["__csrf_magic"] = HdfullTv.magicKey
            logger.debug("updated magic with: "+HdfullTv.magicKey)
            oldCookie = cookie
            cookie = HdfullTv.getNewCookie(response)
            if cookie.find("__cfduid")==-1:
                logger.debug("not found cfduid, using last value: "+oldCookie)
                newCookie = oldCookie[oldCookie.find("__cfduid"):]
                if newCookie.find(";")>-1:
                    newCookie = newCookie[0:newCookie.find(";")]
                cookie = cookie+"; "+newCookie
            logger.debug("updated cookie with: "+cookie)
            #and retry
            html = HdfullTv.getJSONAJAXResponse("http://hdfull.tv/buscar",postForm,cookie,"http://hdfull.tv").read()

        '''
        postForm["limit"] = "5"
        postForm["q"] = text
        postForm["timestamp"] = str(int(time.time()))
        postForm["verifiedCheck"] = ""
        jsonText = HdfullTv.getJSONAJAXResponse("http://hdfull.tv/ajax/search.php",{"limit":"5","query":text,"timestamp":str(int(time.time())),"verifiedCheck":""},cookie,"http://hdfull.tv/buscar").read()
        print "json is: "+jsonText
        return json.loads(jsonText)
        '''
        return HdfullTv.extractItems(html)

    @staticmethod
    def extractProvidersFromLink(url,cookie=""):
        x = []
        if cookie == "":
            cookie = HdfullTv.getNewCookie()
        javascript = HdfullTv.getContentFromUrl(url='http://hdfull.tv/js/providers.js?v=3.0.50',referer=url,cookie=cookie)
        '''
        from pyjsparser import PyJsParser
        p = PyJsParser()
        processed = p.parse(javascript)
        logger.debug("str: "+str(processed))
        for value in processed["body"]:
            logger.debug("level: "+str(value))
            if value.has_key('body'):
                pass
        '''
        content = HdfullTv.jhexdecode(javascript)
        logger.debug("content is: "+content)

        html = HdfullTv.getContentFromUrl(url=url,cookie=cookie)
        contentOfuscated = Decoder.extract("var ad = '","';",html)
        logger.debug("ofuscated content is: "+contentOfuscated)

        javascriptKey = Downloader.getContentFromUrl(url="http://hdfull.tv/templates/hdfull/js/jquery.hdfull.view.min.js",cookie=cookie,referer=url)
        logger.debug("hdfull javascript for key is: "+javascriptKey)
        #key = re.match('JSON.parse\(atob.*?substrings\((.*?)\)',javascriptKey)[0]
        key = Decoder.extract('.substrings(',')',javascriptKey)
        logger.debug("key is: "+key)
        logger.debug("decrypting...")
        jsonLinks = HdfullTv.obfs(base64.b64decode(contentOfuscated), 126 - int(key))
        logger.debug("json links are: "+str(jsonLinks))

        jsonList = json.loads(jsonLinks)
        for jsonElement in jsonList:
            id = jsonElement["id"]
            provider = str(jsonElement["provider"])
            code = str(jsonElement["code"])
            lang = jsonElement["lang"]
            quality = jsonElement["quality"]
            logger.debug("splitter is: "+";p["+provider+"]=")
            line = Decoder.extract(";p["+provider+"]=","};",content)
            logger.debug("line is: "+line)
            link = Decoder.extract('return "','"',line)
            logger.debug("hdfull link is: "+link+" - "+code)
            if len(link)>0:
                element = {}
                element["link"] = link+code
                element["title"] = Decoder.extract("://",'"',line)+" - "+lang+" - "+quality
                element["finalLink"] = True
                x.append(element)
            else:
                logger.debug("Discarted: "+line+" - "+code)

        logger.debug("links procesed: "+str(len(x)))
        return x

    @staticmethod
    def getNewCookie(r=None):
        cookie = ""
        if r == None:
            r = HdfullTv.getJSONAJAXResponse("http://hdfull.tv",{},"")
        returnedHeaders = r.getheaders()
        cfduid = ""
        phpsession = ""
        for returnedHeader,rValue in returnedHeaders:
            if returnedHeader == 'set-cookie':
                #print "header1: "+returnedHeader+", value1: "+rValue
                if rValue.find("__cfduid=")>-1:
                    cfduid = rValue[rValue.find("__cfduid="):]
                    if cfduid.find(";")>-1:
                        cfduid = cfduid[0:cfduid.find(";")]
                if rValue.find("PHPSESSID=")>-1:
                    phpsession = rValue[rValue.find("PHPSESSID="):]
                    if phpsession.find(';')>-1:
                        phpsession = phpsession[0:phpsession.find(";")]
        if cfduid!='':
            cookie = cfduid+"; "+phpsession
        elif phpsession !='':
            cookie = phpsession
        return cookie

    @staticmethod
    def getChannels(page="",cookie=""):
        x = []
        ##main has sections: nuevos lanzamientos, episodios estrenos, peliculas mas vistas, series mas listas, peliculas actualizadas, episodios actualizados and "Search"
        if cookie=="":
            cookie = HdfullTv.getNewCookie()

        logger.debug("page: "+page)
        if(page=="0"):
            itemFirst = {}
            itemFirst["title"] = 'Últimos Emitidos'
            itemFirst["permalink"] = 'episodios#latest'
            x.append(itemFirst)
            itemFirst2 = {}
            itemFirst2["title"] = 'Episodios Estreno'
            itemFirst2["permalink"] = 'episodios#premiere'
            x.append(itemFirst2)
            itemFirst3 = {}
            itemFirst3["title"] = 'Episodios Actualizados'
            itemFirst3["permalink"] = 'episodios#updated'
            x.append(itemFirst3)
            itemFirst4 = {}
            itemFirst4["title"] = 'Películas Estreno'
            itemFirst4["permalink"] = 'peliculas-estreno'
            x.append(itemFirst4)
            itemFirst5 = {}
            itemFirst5["title"] = 'Películas Actualizadas'
            itemFirst5["permalink"] = 'peliculas-actualizadas'
            x.append(itemFirst5)
            itemFirst6 = {}
            itemFirst6["title"] = XBMCUtils.getString(11018)
            itemFirst6["permalink"] = "search"
            x.append(itemFirst6)
        elif page=='http://hdfull.tv/episodios#latest':
            html = HdfullTv.getJSONAJAXResponse("http://hdfull.tv/a/episodes",{"action":"latest","start":"0","limit":"24","elang":"ALL"},cookie).read()
            #print html
            x = json.loads(html)
        elif page=='http://hdfull.tv/episodios#premiere':
            html = HdfullTv.getJSONAJAXResponse("http://hdfull.tv/a/episodes",{"action":"premiere","start":"0","limit":"24","elang":"ALL"},cookie).read()
            x = json.loads(html)
        elif page=='http://hdfull.tv/episodios#updated':
            html = HdfullTv.getJSONAJAXResponse("http://hdfull.tv/a/episodes",{"action":"updated","start":"0","limit":"24","elang":"ALL"},cookie).read()
            x = json.loads(html)
        elif page=='http://hdfull.tv/peliculas-estreno':
            html = HdfullTv.getContentFromUrl("http://hdfull.tv/peliculas-estreno")
            #print html
            x = HdfullTv.extractItems(html)
        elif page=='http://hdfull.tv/peliculas-actualizadas':
            html = HdfullTv.getContentFromUrl("http://hdfull.tv/peliculas-actualizadas")
            x = HdfullTv.extractItems(html)
        elif page=='http://hdfull.tv/search':
            #display keyboard, it will wait for result
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                x = HdfullTv.search(text)
        elif page.find("http://hdfull.tv/serie/")>-1 and page.find("episodio-")==-1:
            #proccess serie article, could be: 1) obtain seasons 2) obtains chapters from a season #temporada-2/episodio-2
            if page.find("/temporada-")==-1:
                html = HdfullTv.getContentFromUrl(page)
                x = HdfullTv.extractSeasons(html,page)
            else:
                season = page[page.find("temporada-")+len("temporada-"):]
                html = HdfullTv.getContentFromUrl(page)
                sid = Decoder.extract("var sid = '","'",html) #fix for hardcoded value '126', it was the internal series id, now works fine
                bruteJson = HdfullTv.getJSONAJAXResponse("http://hdfull.tv/a/episodes",{"action":"season","limit":"0","season":season,"show":sid,"start":"0"},cookie).read()
                x = json.loads(bruteJson)
        else:
            x = HdfullTv.extractProvidersFromLink(page,cookie)
        return x

    @staticmethod
    def extractSeasons(html,url):
        items = []
        #extract <a href='http://hdfull.tv/serie/homeland/temporada-1'>1</a>
        while html.find("<a href='"+url+"/temporada-")>-1:
            item = {}
            aHtml = Decoder.extractWithRegex("<a href='"+url+"/temporada-","</a>",html)
            html = html[html.find(aHtml)+len(aHtml):]
            item["permalink"] = Decoder.extractWithRegex(url+"/temporada-","'",aHtml)
            item["permalink"] = item["permalink"][0:item["permalink"].find("'")]
            item["title"] = Decoder.extract('>','</a>',aHtml)
            logger.debug("found title: "+item["title"]+", link: "+item["permalink"])
            if item["title"].find('<img class="tooltip" original-title="Temporada ')>-1:
                title = item["title"]
                item["title"] = Decoder.extract('original-title="','"',title)
                item["thumbnail"] = Decoder.extract('" src="','" />',title)
                logger.debug("procesed title: "+item["title"]+", thumbnail: "+item["permalink"])
                items.append(item)

        return items

    @staticmethod
    def getJSONAJAXResponse(url,form,cookie,referer="http://hdfull.tv/episodios"):
        data = urllib.urlencode(form)
        logger.debug("using ajax data: "+data)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Referer" : referer,
            #"Origin" : "http://hdfull.tv",
            "Host" : "hdfull.tv",
            "Accept-Language" : "en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3",
            #"Accept-Encoding" : "gzip, deflate",
            #"Conection" : "keep-alive",
            "Content-Length" : len(data),
            "X-Requested-With" : "XMLHttpRequest",
            "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Cookie" : cookie+" __test; __atuvc=3%7C44; _ga=GA1.2.1896372675.1446337452; ppu_main_bf08d52cc9e9227d3ea840f5f2a1ef7f=1; ppu_sub_bf08d52cc9e9807d3ea8f045f2a1ef7f=1; language=es"
        }
        #request.add_header("Content-Length", len(form))
        host = url[url.find("://")+len("://"):]
        subUrl = ""
        logger.debug("url is: "+host)
        if host.find("/")>-1:
            host = host[0:host.find("/")]
            subUrl = url[url.find(host)+len(host):]
        logger.debug("host: "+host+":80 , subUrl: "+subUrl)
        h = httplib.HTTPConnection(host+":80")
        h.request('POST', subUrl, data, headers)
        r = h.getresponse()
        return r
        #request = urllib2.Request(url,data,headers)
        #response = urllib2.urlopen(request)
        #html=response.read()
        #response.close()

    @staticmethod
    def extractItems(currentHtml):
        x = []
        i=0
        #print currentHtml
        while currentHtml.find('<div class="span-6 inner-6 tt  view">')>-1 or currentHtml.find('<div class="span-6 inner-6 tt view">')>-1 :
            if currentHtml.find('<div class="span-6 inner-6 tt  view">')>-1:
               currentHtml = currentHtml[currentHtml.find('<div class="span-6 inner-6 tt  view">')+len('<div class="span-6 inner-6 tt  view">'):]
            else: ##TODO, review this part, doesn't work, the down logic is for the previews condition, needs new one
                currentHtml = currentHtml[currentHtml.find('<div class="span-6 inner-6 tt view">')+len('<div class="span-6 inner-6 tt view">'):]
            #print currentHtml
            item = {}
            title = currentHtml[currentHtml.find('" alt="')+len('" alt="'):]
            title = title[:title.find('"')]

            logo = currentHtml[currentHtml.find(' src="')+len(' src="'):]
            logo = logo[:logo.find('"')]
            item["thumbnail"] = logo

            href = currentHtml[currentHtml.find('href="')+len('href="'):]
            href = href[:href.find('"')]
            item["permalink"] = href

            if title.strip()=='': #title could be some ' ' character in the search results, so...
                splitter = ' href="'+href+'" title="'
                title = currentHtml[currentHtml.find(splitter)+len(splitter):]
                title = title[0:title.find('"')]
            item["title"] = title

            logger.debug("title: "+title+", url: "+href)
            x.append(item)
            i+=1
        logger.debug("total: "+str(i))
        #print "REST: "+currentHtml
        return x

    @staticmethod
    def getContentFromUrl(url,cookie="",referer=""):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Referer" : "http://hdfull.tv",
            #"Origin" : "http://hdfull.tv",
            "Host" : "hdfull.tv",
            "Accept-Language" : "es-ES,es;q=0.8",
            #"Accept-Encoding" : "gzip, deflate",
            "Conection" : "keep-alive",
            #"Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Cookie" : cookie+" __test; __atuvc=3%7C44; _ga=GA1.2.1091232675.1446337892; ppu_main_bf08d52cc9e98012345840f5f2a1ef7f=1; ppu_sub_bf08d52cc9e4321d3ea840f5f2a1ef7f=1; language=es"
        }
        if referer != '':
            headers["Referer"] = referer
        #request.add_header("Content-Length", len(form))
        h = httplib.HTTPConnection('hdfull.tv:80')
        subUrl = url[len("http://hdfull.tv"):]
        #print subUrl
        h.request('GET', subUrl, "", headers)
        r = h.getresponse()
        #fill global __csrf_magic if found
        html = r.read()
        HdfullTv.magicKey = Decoder.extract("__csrf_magic' value=\"",'"',html)
        return html


    @staticmethod
    def jhexdecode(t):

        r = re.sub(r'_\d+x\w+x(\d+)', 'var_' + r'\1', t)
        r = re.sub(r'_\d+x\w+', 'var_0', r)

        def to_hx(c):
            h = int("%s" % c.groups(0), 16)
            if 19 < h < 160:
                return chr(h)
            else:
                return ""

        r = re.sub(r'(?:\\|)x(\w{2})', to_hx, r).replace('var ', '')

        f = eval(re.findall('\s*var_0\s*=\s*([^;]+);',r)[0])
        for i, v in enumerate(f):
            r = r.replace('[[var_0[%s]]' % i, "." + f[i])
            r = r.replace(':var_0[%s]' % i, ":\"" + f[i] + "\"")
            r = r.replace(' var_0[%s]' % i, " \"" + f[i] + "\"")
            r = r.replace('(var_0[%s]' % i, "(\"" + f[i] + "\"")
            r = r.replace('[var_0[%s]]' % i, "." + f[i])
            if v == "": r = r.replace('var_0[%s]' % i, '""')

        r = re.sub(r':(function.*?\})', r":'\g<1>'", r)
        r = re.sub(r':(var[^,]+),', r":'\g<1>',", r)

        return r

    @staticmethod
    def obfs(data, key, n=126):
        chars = list(data)
        for i in range(0, len(chars)):
            c = ord(chars[i])
            if c <= n:
                number = (ord(chars[i]) + key) % n
                chars[i] = chr(number)

        return "".join(chars)