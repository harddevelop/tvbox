import urllib
import os
import re
import base64
from tvboxcore.decoder import Decoder
from tvboxcore import jsunpack
from tvboxcore import logger
from tvboxcore.downloader import Downloader
from providers.cricfreetv import Cricfreetv

class ShowsportTvCom(Downloader):

    MAIN_URL = "http://showsport-tv.com/"

    @staticmethod
    def getChannels(page):
        x = []
        start = False
        if str(page) == '0':
            html = ShowsportTvCom.getContentFromUrl(ShowsportTvCom.MAIN_URL)
            element = {}
            element["link"] = '1'
            element["title"] = 'Display by event'
            x.append(element)
            if html.find('<div id="cssmenu">')>-1: #build channels menu from provider
                cssMenu = Decoder.extract('<div id="cssmenu">','</ul>',html)
                for htmlElement in cssMenu.split('<li class="has-sub">'):
                    if htmlElement.find('<a href="')>-1:
                        element = {}
                        link = Decoder.extract('<a href="','"',htmlElement)
                        if htmlElement.find(' title="')>-1:
                            title = Decoder.extract(' title="','"',htmlElement)
                        img = Decoder.extract('img src="/','"',htmlElement)
                        element["title"] = title
                        element["link"] = ShowsportTvCom.MAIN_URL+link
                        element["thumbnail"] = ShowsportTvCom.MAIN_URL+img
                        logger.debug("found element: "+title+", url: "+element["link"])
                        if title != '':
                            x.append(element)
        elif str(page) == '1': #show by events
            html = ShowsportTvCom.getContentFromUrl(ShowsportTvCom.MAIN_URL)
            html = Decoder.extract('<div class="listmatch">','<div id="right_content">',html)
            for htmlElement in html.split('<div class="leaguelogo column">'):
                if htmlElement.find(' href="')>-1:
                    href = Decoder.extract(' href="','">',htmlElement)
                    timeHtml = Decoder.extract('<div class="date_time column"><span class="','</span></div>',htmlElement)
                    time = ""
                    if timeHtml.find('</span><span')>-1:
                        time = Decoder.extract('>','</span><span',timeHtml)
                        time+= " - "+timeHtml[timeHtml.rfind(">")+1:]
                    name = Decoder.extract('png"><span>','</span></div>',htmlElement)
                    logger.debug("first name is: "+name)
                    if htmlElement.find('px;">')>-1 and htmlElement.find('</span><img')>-1:
                        name += " vs "+Decoder.extract('px;">','</span><img',htmlElement)
                    logger.debug("final name is: "+name)
                    element = {}
                    if time=='':
                        element["title"] = name
                    else:
                        element["title"] = time+" - "+name
                    element["link"] = ShowsportTvCom.MAIN_URL+href
                    logger.debug("appending event: "+element["title"])
                    if element["title"].find(" vs ")>-1:
                        x.append(element)
        else: #open link
            html = ShowsportTvCom.getContentFromUrl(page)
            iframeUrl = ShowsportTvCom.MAIN_URL+Decoder.extract('<iframe frameborder="0" marginheight="0" marginwidth="0" height="450" src="/','"',html)
            logger.debug("iframeUrl is: "+iframeUrl)
            html2 = ShowsportTvCom.getContentFromUrl(iframeUrl,"",ShowsportTvCom.cookie,page)
            if html2.find("http://www.caston.tv/player.php?")>-1:
                id = Decoder.extract("var id = "," ;",html2)
                url2 = "http://www.caston.tv/player.php?id="+id
                html3 = ShowsportTvCom.getContentFromUrl(url2,"id="+id,ShowsportTvCom.cookie,iframeUrl)
                script = Decoder.extract('<script type="text/javascript">\n','</script>',html3)
                if script.find("document.write(unescape('")>-1: #patch
                    scriptContent = Decoder.extract("document.write(unescape('","'));",script)
                    scriptContent = urllib.unquote(scriptContent)
                    script=re.compile('eval\(function\(w,i,s,e\).*}\((.*?)\)').findall(scriptContent)[0]
                finalScriptContent = Decoder.preWise(script)
                logger.debug(finalScriptContent)
                token = Decoder.extract("token:\"","\"",finalScriptContent)
                logger.debug("pre-token is: "+token)
                ajaxContent = dict(token=token, is_ajax=1)
                #logger.debug(html3)
                tokenResponse = ShowsportTvCom.getContentFromUrl("http://www.caston.tv/sssss.php",urllib.urlencode(ajaxContent),ShowsportTvCom.cookie,url2,True)
                logger.debug("token response: "+tokenResponse)
                file = Decoder.extract("file:\"","\"",finalScriptContent)+Decoder.extract('","','",',tokenResponse)+"&e="+Decoder.rExtract(',',']',tokenResponse)+"|Referer=http://p.jwpcdn.com/6/12/jwplayer.flash.swf"
            elif html2.find("http://www.sostart.pw/js/embed.js")>-1:
                fid = Decoder.extract('<script type="text/javascript"> fid="','"',html2)
                url3 = "http://www.sostart.pw/jwplayer6.php?channel="+fid
                html3 = ShowsportTvCom.getContentFromUrl(url3,"",ShowsportTvCom.cookie,iframeUrl)
                if html3.find("http://static.bro.adca.st/broadcast/player.js")>-1:
                    id2 = Decoder.extract("<script type='text/javascript'>id='","';",html3)
                    logger.debug("using id = "+id2)
                    url4 = "http://bro.adcast.site/stream.php?id="+id2+"&width=700&height=450&stretching=uniform"
                    html4 = ShowsportTvCom.getContentFromUrl(url4,"",ShowsportTvCom.cookie,url3)
                    logger.debug("html4: "+html4)
                    curl = Decoder.extract('curl = "','"',html4)
                    token = ShowsportTvCom.getContentFromUrl('http://bro.adcast.site/getToken.php',"",ShowsportTvCom.cookie,url4,True)
                    logger.debug("token: "+token)
                    token = Decoder.extract('":"','"',token)
                    file = base64.decodestring(curl)+token+"|"+Downloader.getHeaders('http://cdn.bro.adcast.site/jwplayer.flash.swf')
                    logger.debug("final url is: "+file)
            elif html2.find("http://www.iguide.to/embed")>-1:
                nextIframeUrl = Decoder.extractWithRegex('http://www.iguide.to/embed','"',html2).replace('"',"")
                file = Decoder.decodeIguide(nextIframeUrl,iframeUrl)
            elif "/embedplayer.php" in html2:
                nextIframeUrl = ShowsportTvCom.MAIN_URL+Decoder.extractWithRegex('/embedplayer.php', "'", html2).replace("'", "")
                logger.debug("next loop will use: "+nextIframeUrl)
                file = ShowsportTvCom.getChannels(nextIframeUrl)
            elif html2.find("adca.st/stream.php")>-1:
                token = False
                if "http://bro.adca.st/stream.php" not in html2:
                    token = True
                    id2 = Decoder.extract("<script type='text/javascript'>id='","';",html2)
                    logger.debug("using id = "+id2)
                    url4 = "http://bro.adcast.site/stream.php?id="+id2+"&width=700&height=450&stretching=uniform"
                else: #it's built, not needed extract id
                    url4 = Decoder.extractWithRegex("http://bro.adca.st/stream.php",'"',html2)
                html4 = ShowsportTvCom.getContentFromUrl(url4,"",ShowsportTvCom.cookie,iframeUrl)
                logger.debug("html4: "+html4)
                curl = Decoder.extract('curl = "','"',html4)

                tokenUrl = "http://bro.adca.st/getToken.php"
                swfUrl = "http://cdn.allofme.site/jw/jwplayer.flash.swf"
                if token:
                    tokenUrl = 'http://bro.adcast.site/getToken.php'
                    swfUrl = 'http://cdn.bro.adcast.site/jwplayer.flash.swf'

                token = ShowsportTvCom.getContentFromUrl(tokenUrl,"",ShowsportTvCom.cookie,url4,True)
                logger.debug("token: "+token)
                token = Decoder.extract('":"','"',token)


                file = base64.decodestring(curl)+token+"|"+Downloader.getHeaders(swfUrl)
                logger.debug("final url is: "+file)
            else:
                logger.debug("trying crickfreetv way...: "+html2)
                file = Cricfreetv.seekIframeScript(html2, page, page)
            logger.debug("final remote url: "+file)
            element = {}
            element["link"] = file
            element["permaLink"] = True
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
                element["title"] = Decoder.extract('alt="','">',fieldHtml)
                element["thumbnail"] = Decoder.extract('src="','" ',fieldHtml)
                logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumbnail: "+element["thumbnail"])
                if len(element["title"])>0:
                    x.append(element)
        return x