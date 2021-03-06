# -*- coding: utf-8 -*-
import urllib
import base64
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader
import re


class Vercanalestv1com(Downloader):

    MAIN_URL = "https://vercanalestv1.com/ver-tve-1-la-1-online-en-directo-gratis-24h-por-internet"

    @staticmethod
    def getChannels(page):
        if str(page) == '0':
            page=Vercanalestv1com.MAIN_URL
        page = urllib.unquote_plus(page)
        html = Vercanalestv1com.getContentFromUrl(page,"",Vercanalestv1com.cookie,referer="https://vercanalestv1.com")
        logger.debug("end FIRST")
        x = []
        if page == Vercanalestv1com.MAIN_URL:
            table = Decoder.extract('<center><table><tbody><tr>',"</center>",html)
            for fieldHtml in table.split('<a'):
                element = {}
                element["link"] = Decoder.extract('href="','"',fieldHtml)
                element["title"] = Decoder.extract('alt="','nline',fieldHtml)
                if '"' in element["title"]:
                    element["title"]=element["title"][:element["title"].find('"')]
                element["title"]=element["title"][:element["title"].rfind(' ')]
                element["thumbnail"] = Decoder.extract('<img src="','"',fieldHtml)
                if "http" not in element["thumbnail"]:
                    element["thumbnail"]="https:"+element["thumbnail"]
                element["permaLink"] = True
                logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                if "http" in element["link"]:
                    x.append(element)
        else:
            logger.debug("extracting channel...")
            x.append(Vercanalestv1com.extractChannel(html,page))
            logger.debug("extracted channel!")
        return x

    @staticmethod
    def extractChannel(html,page="https://vercanalestv1.com"):
        element = {}
        if '<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" allowfullscreen width="650" height="400" src="' in html:
            url = Decoder.extract('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" allowfullscreen width="650" height="400" src="','"',html)
            if "http" not in url:
                url = "https://vercanalestv1.com"+url
            html = Vercanalestv1com.getContentFromUrl(url=url,referer=page)
            page = url
            url = "https:"+Decoder.extract('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" allowfullscreen width="650" height="400" src="','"',html)
            html = Vercanalestv1com.getContentFromUrl(url=url,referer=page)
            page = url
            logger.debug("HTML NEW IS: %s"%html)
            key = Decoder.extract('" name="','"',html) #manzana66 key
            formData = key+"=12345"
            logger.debug("FORM DATA IS: %s"%formData)
            html4 = Vercanalestv1com.getContentFromUrl(url=url,data=formData,referer=url)
            if "source: '" in html4:
                #change
                originalLink = Vercanalestv1com.extractLastLink(html4)
                lastUrl = "https:"+originalLink+"|User-Agent=Mozilla%2F5.0+%28X11%3B+Linux+x86_64%3B+rv%3A68.0%29+Gecko%2F20100101+Firefox%2F68.0&amp;Referer="+urllib.quote_plus(url)
            elif ".php" in html4:
                scriptUrl = url
                newScriptUrl = "https:"+Decoder.rExtractWithRegex('//','.php',html4)
                html5 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,referer=scriptUrl)
                key = Decoder.extract('" name="','"',html5) #manzana66 key
                formData = key+"=12345"
                html6 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,data=formData,referer=scriptUrl)
                logger.debug("html66 is: "+html6)
                if "source: '" in html6:
                    originalLink = Vercanalestv1com.extractLastLink(html6)
                    lastUrl = "https:"+originalLink+"|User-Agent=Mozilla%2F5.0+%28X11%3B+Linux+x86_64%3B+rv%3A68.0%29+Gecko%2F20100101+Firefox%2F68.0&amp;Referer="+urllib.quote_plus(newScriptUrl)
            logger.debug("decoded link is: "+lastUrl)
            element["title"] = page
            element["link"] = lastUrl
        if ' allowfullscreen src="' in html:
            logger.debug("allowfullscreen found!")
            try:
                script = Decoder.extract(' allowfullscreen src="','"',html)
                if 'http' not in script:
                    script = "https://vercanalestv1.com"+script
                scriptUrl = script
                logger.debug("trying first fix... "+script)
                html2 = Vercanalestv1com.getContentFromUrl(url=scriptUrl,referer=page)

                logger.debug("HTML: %s"%html2)

                logger.debug("DONE fix")
                if "source: '" not in html2 and '/embed.js' not in html2 and '12345' not in html2:
#                    newScriptUrl = "https:"+Decoder.rExtractWithRegex('//','.php',html2)
#                    html3 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,referer=scriptUrl)
#                    key = Decoder.extract('" name="','"',html3) #manzana66 key
#                    formData = key+"=12345"
#                    html4 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,data=formData,referer=scriptUrl)
                    lastUrl = Vercanalestv1com.decodeChannel(html2,scriptUrl,page)
                elif "source: '" in html2:
                    logger.debug("second if")
                    originalLink = Vercanalestv1com.extractLastLink(html2)
                    lastUrl = "https:"+originalLink+"|User-Agent=Mozilla/5.0"
                elif 'embed.js' in html2:
                    logger.debug("third 3333333333333333333333 if")
                    domain = Decoder.rExtract("//","/embed.js",html2)
                    if ", id='" in html2:
                        id = Decoder.extract(", id='","'",html2)
                    else:
                        id = Decoder.extract(">id='","'",html2)
                    newScriptUrl = "http://"+domain+"/embed/"+id
                    html3 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,referer=scriptUrl)
                    if 'file: "' in html3:
                        lastUrl = Decoder.extract('file: "','"',html3)+"|User-Agent=Mozilla/5.0"
                    else:
                        logger.debug("decoding channel (loop)")
                        #lastUrl = Vercanalestv1com  .decodeChannel(html3,newScriptUrl)
                else: #premier league
                    #key = Decoder.extract('" name="','"',html3) #manzana66 key
                    #formData = key+"=12345"
                    #html4 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,data=formData,referer=scriptUrl)
                    lastUrl = Vercanalestv1com.decodeChannel(html2,scriptUrl,page)

                logger.debug("decoded link is: "+lastUrl)
                element["title"] = page
                element["link"] = lastUrl
            except Exception as ex:
                logger.debug("Ex: "+str(ex))
        return element

    @staticmethod
    def extractLastLink(html6):
        #originalLink = re.search("(?=(//([a-zA-Z])+[0-9](.+)+[0-9]))", html6, flags=0).group(1).replace("'","")
        originalLink = Decoder.extract('<script src="/player/player.js"></script>',"',",html6)
        originalLink = originalLink[originalLink.find("source: '")+len("source: '"):]
        #originalLink = Decoder.extract("'","'",html6)
        return originalLink

    @staticmethod
    def decodeChannel(html4,scriptUrl,page):

        lastUrl = ""
        logger.debug("first if %s"%html4)

        if "source: '" in html4:
            originalLink = Vercanalestv1com.extractLastLink(html4)
            lastUrl = "https:"+originalLink+"|User-Agent=Mozilla/5.0"
        elif ".php" in html4:
            newScriptUrl = "https:"+Decoder.rExtractWithRegex('//','.php',html4)
            html5 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,referer=scriptUrl)
            key = Decoder.extract('" name="','"',html5) #manzana66 key
            formData = key+"=12345"
            html6 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,data=formData,referer=scriptUrl)
            logger.debug("html6 is: "+html6)
            if "source: '" in html6:
                originalLink = Vercanalestv1com.extractLastLink(html6)
                lastUrl = "https:"+originalLink+"|User-Agent=Mozilla%2F5.0+%28X11%3B+Linux+x86_64%3B+rv%3A68.0%29+Gecko%2F20100101+Firefox%2F68.0&amp;Referer="+urllib.quote_plus(newScriptUrl)
            elif 'embed.js' in html6:
                logger.debug("third 1111111111111111111 if")
                domain = Decoder.rExtract("//","/embed.js",html6).replace("embed.","")
                #id = Decoder.extract(", id='","'",html6)
                if ", id='" in html6:
                    id = Decoder.extract(", id='","'",html6)
                else:
                    id = Decoder.extract(">id='","'",html6)
                newScriptUrl = "http://"+domain+"/embed/"+id+".html"
                html3 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,referer=scriptUrl)
                #logger.debug("ELSE HTML! special dev. %s"%html3)
                #lastUrl = Decoder.extract('file: "','"',html3)+"|User-Agent=Mozilla/5.0"
                if 'file: "' in html3:
                    lastUrl = Decoder.extract('file: "','"',html3)+"|User-Agent=Mozilla/5.0"
                else:
                    logger.debug("decoding channel (loop)")
                    lastUrl = Vercanalestv1com.extractLaliga(html3,newScriptUrl,scriptUrl)
                    #lastUrl = Vercanalestv1com .decodeChannel(html3,newScriptUrl,scriptUrl)
            else:
                logger.debug("ELSEEEEE url=%s"%scriptUrl)
                scriptUrl = newScriptUrl #backup referer
                newScriptUrl = "https:"+Decoder.extractWithRegex('//','.php',html6)
                html7 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,referer=scriptUrl)
                logger.debug("ELSEEEEE 2 url=%s"%newScriptUrl)
                logger.debug(html7)
                key = Decoder.extract('" name="','"',html7) #manzana66 key
                formData = key+"=12345"
                html8 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,data=formData,referer=scriptUrl)
                logger.debug("launching new decode channel process with url: %s"%newScriptUrl)
                lastUrl = Vercanalestv1com.decodeChannel(html8,newScriptUrl,scriptUrl)
        else:
            logger.debug("ELSE HTML! special dev. %s"%html4)
            domain = Decoder.rExtract("//","/embed.js",html4).replace("embed.","")
            id = Decoder.extract("id='","'",html4)
            newScriptUrl = "http://"+domain+"/embed/"+id+".html"
            logger.debug("new script url is: %s"%newScriptUrl)
            html5 = Vercanalestv1com.getContentFromUrl(url=newScriptUrl,referer=scriptUrl)
            #logger.debug("last content has HTML: %s"%html5)
            if 'file: "' in html5:
                lastUrl = Decoder.extract('file: "','"',html5)+"|User-Agent=Mozilla/5.0"
            else: #laliga
                #extract eval packer
                lastUrl = Vercanalestv1com.extractLaliga(html5,newScriptUrl,scriptUrl)

        return lastUrl

    @staticmethod
    def extractLaliga(html5,newScriptUrl,scriptUrl):
        packer = "eval("+Decoder.extract("eval(",",{}))",html5)+',{}))'
        #logger.debug("packer: %s"%packer)
        from tvboxcore import jsunpackOld
        packer = jsunpackOld.unpack(packer)
        #logger.debug("unpacked: %s"%packer)
        vars = Decoder.extract('doThePIayer("",',",location",packer)
        var1 = vars[:vars.find(",")]
        var2 = vars[vars.find(",")+1:]
        var1 = Decoder.extract(var1+'=window.atob(',')',packer)
        var2 = ""
        logger.debug("var1 %s "%var1)
        value1 = Decoder.extract(var1+'="','"',packer)
        value2 = "JnRva2Vu"+Decoder.extract('JnRva2Vu','"',packer)
        logger.debug("value1 %s value2 %s"%(value1,value2))
        lastUrl = str(base64.b64decode(value1))
        logger.debug("lastUrl %s"%lastUrl)
        hmac = str(base64.b64decode(value2))
        logger.debug("hmac %s"%hmac)
        lastUrl = lastUrl + hmac
        lastUrl = "https:"+lastUrl
        oldDomain = Decoder.extract("//","/",lastUrl)
        newDomain = Decoder.extract("//","/",newScriptUrl)
        lastUrl = lastUrl.replace(oldDomain,newDomain)
        logger.debug("link is: %s. Sum headers to kodi..."%lastUrl)
        lastUrl = lastUrl+"|User-Agent=Mozilla%2F5.0+%28X11%3B+Linux+x86_64%3B+rv%3A68.0%29+Gecko%2F20100101+Firefox%2F68.0&amp;Referer="+urllib.quote_plus(newScriptUrl)
        #lastUrl = ""
        return lastUrl
