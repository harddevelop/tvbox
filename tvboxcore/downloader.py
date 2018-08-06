import urllib, urllib2, httplib
import StringIO
import gzip
from tvboxcore import logger

class Downloader():
    TIMEOUT = 20
    cookie = ""
    USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
    USER_AGENT_CHROME = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

    @staticmethod
    def getContentFromUrl(url,data="",cookie="",referer="",ajax=False,launchLocation=True,headers={},gzip=False):
        host = url[url.find("://")+len("://"):]
        subUrl = ""
        logger.info("url is: "+host)
        if host.find("/")>-1:
            host = host[0:host.find("/")]
            subUrl = url[url.find(host)+len(host):]
        if host.find(":")==-1:
            logger.debug("host: "+host+":80 , subUrl: "+subUrl)
        else:
            logger.debug("host: "+host+" , subUrl: "+subUrl)
        if headers == {}:
            logger.debug("building default headers...")
            headers = {
                "User-Agent": Downloader.USER_AGENT,
                "Accept-Language" : "en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3",
                #"Conection" : "keep-alive",
                "Host":host,
                "DNT":"1",
                #"Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            if referer!="":
                headers["Referer"] = referer

            if cookie !="":
                headers["Cookie"] = cookie
            if ajax:
                headers["X-Requested-With"] = "XMLHttpRequest"
                headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
            if gzip:
                headers["Accept-Encoding"]="gzip, deflate, br"
        if host.find(":")==-1:
            if url.find("https://")>-1:
                h = httplib.HTTPSConnection(host+":443")
                logger.debug("launching https to port 443")
            else:
                h = httplib.HTTPConnection(host+":80")
                logger.debug("launching http to port 80")
        else:
            h = httplib.HTTPConnection(host)
        if data == "":
            logger.debug("launching GET for "+url+"...")
            req = urllib2.Request(url, headers=headers)
            try:
                r = urllib2.urlopen(req, timeout=Downloader.TIMEOUT)
            except BaseException as e:
                logger.error("Something went wrong with urllib :'(: "+str(e))
                pass
            try:
                logger.debug("connection info: "+str(r.info()))
            except:
                logger.error("could not be converted")
                pass
            cookie = ""
            logger.debug("reading...")
            html = r.read()
            headers = r.info()
            if ('Content-Encoding' in headers.keys() and headers['Content-Encoding'] == 'gzip') or ('content-encoding' in headers.keys() and headers['content-encoding'] == 'gzip'):
                logger.debug("Uncompressing content...")
                html = StringIO.StringIO(html)
                gzipper = gzip.GzipFile(fileobj=html)
                html = gzipper.read()
                logger.debug("Done uncompressing content process.")
            logger.debug("cookies...")
            #update cookies
            for key1, value1 in sorted(r.info().items()):
                logger.debug("trace....."+key1)
                if key1.lower()=='set-cookie':
                    value1 = value1.replace("path=/, ","")
                    if value1.find(";")==-1:
                        value1+=";="
                    logger.debug("processing cookie...: "+value1)
                    if value1.find(";")>-1:
                        for values in value1.split(";"):
                            logger.debug(values)
                            if values.find("=")>-1:
                                key = values.split("=")[0]
                                value = values.split("=")[1]
                                logger.debug("key: "+key+", value="+value)
                                if(key.find("PHPSESSID")>-1 or key.find("captcha_keystring")>-1 or key.find("__cfduid")>-1 or key.find("key")):
                                    if value.find(";")>-1:
                                        cookie+=key+"="+value[:value.find(";")]
                                    else:
                                        cookie+=key+"="+value
                                    cookie+=";"
                                    logger.debug("processed cookie: "+key+"="+value)
                elif key1.lower()=='location':
                    logger.info("Location detected: using location: "+value1)
                    location = value1
                else:
                    logger.debug("rejected cookie: "+key1+"->"+value1)
            if len(cookie)>1:
                Downloader.cookie = cookie
                logger.info("Cookie was updated to: "+cookie)
            location = ""
            if cookie!= '':
                Downloader.cookie = cookie
            logger.info("cookie was updated to: "+Downloader.cookie)
            if location != '' and launchLocation:
                if location=="/":
                    location = url
                elif location.find("/")==0:
                    location = "http://"+host+location
                logger.info("launching redirection to: "+location)
                html = Downloader.getContentFromUrl(location,data,Downloader.cookie,url)
        else:
            logger.debug("launching POST...")
            req = urllib2.Request(url, data, headers)
            r = urllib2.urlopen(req, timeout=Downloader.TIMEOUT)
            logger.debug(str(r.info()))
            logger.debug("reading...")
            html = r.read()
            headers = r.info()
            if ('Content-Encoding' in headers.keys() and headers['Content-Encoding'] == 'gzip') or ('content-encoding' in headers.keys() and headers['content-encoding'] == 'gzip'):
                html = StringIO.StringIO(html)
                gzipper = gzip.GzipFile(fileobj=html)
                html = gzipper.read()
            logger.debug("cookies...")
            cookie = "" #update cookies
            for key1, value1 in sorted(r.info().items()):
                logger.debug("trace....."+key1)
                if key1.lower()=='set-cookie':
                    value1 = value1.replace("path=/, ","")
                    if value1.find(";")==-1:
                        value1+=";="
                    logger.debug("processing cookie...: "+value1)
                    if value1.find(";")>-1:
                        for values in value1.split(";"):
                            logger.debug(values)
                            if values.find("=")>-1:
                                key = values.split("=")[0]
                                value = values.split("=")[1]
                                logger.debug("key: "+key+", value="+value)
                                if(key.find("PHPSESSID")>-1 or key.find("captcha_keystring")>-1 or key.find("__cfduid")>-1 or key.find("key")):
                                    if value.find(";")>-1:
                                        cookie+=key+"="+value[:value.find(";")]
                                    else:
                                        cookie+=key+"="+value
                                    cookie+=";"
                                    logger.debug("processed cookie: "+key+"="+value)
                else:
                    logger.debug("rejected cookie: "+key1+"->"+value1)
            if len(cookie)>1:
                Downloader.cookie = cookie
                logger.info("Cookie was updated to: "+cookie)
        return html

    @staticmethod
    def getHeaders(iframeReferer=''):
        headers = ""
        if iframeReferer is not None and iframeReferer!='':
            headers += "Referer="+urllib.quote_plus(iframeReferer)+"&"
        headers += "User-Agent="+urllib.quote_plus(Downloader.USER_AGENT)
        headers += "&Accept-Language="+urllib.quote_plus("en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3")
        headers += "&Accept="+urllib.quote_plus("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        #headers += "&Connection="+urllib.quote_plus("keep-alive")
        headers += "&Accept-Encoding="+urllib.quote_plus('gzip, deflate')
        headers += "&DNT=1"
        #headers += "&Icy-MetaData" #Now it's fixed from ffmpeg
        #headers += "&Range"
        return headers

    @staticmethod
    def getSimpleDownload(url):
        response = urllib2.urlopen(url)
        content = response.read()
        response.close()
        return content