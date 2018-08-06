# coding=utf-8
from tvboxcore.xbmcutils import XBMCUtils
import urllib2
import httplib
import urllib
import re
import time
from tvboxcore import logger
from tvboxcore.decoder import Decoder
from tvboxcore.downloader import Downloader
import base64

try:
    import json
except:
    import simplejson as json


class HdfullTv(Downloader):

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
        response = HdfullTv.getJSONAJAXResponse("https://hdfull.me/buscar",postForm,cookie,"https://hdfull.me")
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
            html = HdfullTv.getJSONAJAXResponse("https://hdfull.me/buscar",postForm,cookie,"https://hdfull.me").read()

        return HdfullTv.extractItems(html)

    @staticmethod
    def extractProvidersFromLink(url,cookie=""):
        x = []
        if cookie == "":
            cookie = HdfullTv.getNewCookie()
        javascript = HdfullTv.getContentFromUrl(url='https://hdfull.me/js/providers.js?v=3.0.50',referer=url,cookie=cookie)
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

        javascriptKey = Downloader.getContentFromUrl(url="https://hdfull.me/templates/hdfull/js/jquery.hdfull.view.min.js",cookie=cookie,referer=url)
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
            r = HdfullTv.getJSONAJAXResponse("https://hdfull.me",{},"")
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
        elif page=='https://hdfull.me/episodios#latest':
            html = HdfullTv.getContentFromUrl(url="https://hdfull.me/a/episodes",data="action=latest&start=0&limit=24&elang=ALL",cookie=cookie)
            logger.debug(html)
            x = json.loads(html)
        elif page=='https://hdfull.me/episodios#premiere':
            html = HdfullTv.getContentFromUrl(url="https://hdfull.me/a/episodes",data="action=premiere&start=0&limit=24&elang=ALL",cookie=cookie)
            logger.debug(html)
            x = json.loads(html)
        elif page=='https://hdfull.me/episodios#updated':
            html = HdfullTv.getContentFromUrl(url="https://hdfull.me/a/episodes",data="action=updated&start=0&limit=24&elang=ALL",cookie=cookie)
            logger.debug(html)
            x = json.loads(html)
        elif page=='https://hdfull.me/peliculas-estreno':
            html = HdfullTv.getContentFromUrl("https://hdfull.me/peliculas-estreno")
            logger.debug(html)
            x = HdfullTv.extractItems(html)
        elif page=='https://hdfull.me/peliculas-actualizadas':
            html = HdfullTv.getContentFromUrl("https://hdfull.me/peliculas-actualizadas")
            logger.debug(html)
            x = HdfullTv.extractItems(html)
        elif page=='https://hdfull.me/search':
            #display keyboard, it will wait for result
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                x = HdfullTv.search(text)
        elif page.find("https://hdfull.me/serie/")>-1 and page.find("episodio-")==-1:
            #proccess serie article, could be: 1) obtain seasons 2) obtains chapters from a season #temporada-2/episodio-2
            if page.find("/temporada-")==-1:
                html = HdfullTv.getContentFromUrl(page)
                x = HdfullTv.extractSeasons(html,page)
            else:
                season = page[page.find("temporada-")+len("temporada-"):]
                html = HdfullTv.getContentFromUrl(page)
                sid = Decoder.extract("var sid = '","'",html) #fix for hardcoded value '126', it was the internal series id, now works fine
                bruteJson = HdfullTv.getContentFromUrl(url="https://hdfull.me/a/episodes",data={"action":"season","limit":"0","season":season,"show":sid,"start":"0"},cookie=cookie).read()
                x = json.loads(bruteJson)
        else:
            x = HdfullTv.extractProvidersFromLink(page,cookie)
        return x

    @staticmethod
    def extractSeasons(html,url):
        items = []
        #extract <a href='https://hdfull.me/serie/homeland/temporada-1'>1</a>
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
    def getJSONAJAXResponse(url,form,cookie,referer="https://hdfull.me/episodios"):
        data = urllib.urlencode(form)
        logger.debug("using ajax data: "+data)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Referer" : referer,
            #"Origin" : "https://hdfull.me",
            "Host" : "hdfull.me",
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
    def jhexdecode(t):
        k = re.sub(r'(_0x.{4})(?=\(|=)', 'var_0', t).replace('\'', '\"')

        def to_hex(c, type):
            h = int("%s" % c, 16)
            if type == '1':
                return 'p[%s]' % h
            if type == '2':
                return '[%s]' % h

        x = re.sub(r'(?:p\[)(0x.{,2})(?:\])', lambda z: to_hex(z.group(1), '1'), k)
        y = re.sub(r'(?:\(")(0x.{,2})(?:"\))', lambda z: to_hex(z.group(1), '2'), x)

        def to_hx(c):
            h = int("%s" % c.groups(0), 16)
            if 19 < h < 160:
                return chr(h)
            else:
                return ""

        r = re.sub(r'(?:\\|)x(\w{2})(?=[^\w\d])', to_hx, y).replace('var ', '')
        response = re.findall('=(\[.*?\])', r, flags=re.DOTALL)[0]
        logger.debug("response is: "+str(response))
        server_list = eval(response)
        logger.debug("continue...")
        for val in range(475, 0, -1):
            server_list.append(server_list[0])
            server_list.pop(0)

        r = re.sub(r'=\[(.*?)\]', '=%s' % str(server_list), r)
        logger.debug("second eval...")
        f = eval(re.findall('\s*var_0\s*=\s*([^;]+);', r, flags=re.DOTALL)[0])
        logger.debug("done second eval...")
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