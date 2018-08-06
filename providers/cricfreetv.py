import urllib
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore import jsunpack
from providers.filmoncom import Filmoncom
from providers.live9net import Live9net
from tvboxcore.downloader import Downloader

class Cricfreetv(Downloader):

    cookie = ""
    MAIN_URL = "http://cricfree.sc/"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == "0":
            html = Cricfreetv.getContentFromUrl(Cricfreetv.MAIN_URL)
            logger.debug("total html is: "+html)
            element = {}
            element["link"] = '1'
            element["title"] = 'Display by event'
            x.append(element)
            if html.find("<div id='cssmenu'>")>-1:
                cssMenu = Decoder.extract("<div id='cssmenu'>",'</ul>',html)
                logger.debug("html menu: "+cssMenu)
                for htmlElement in cssMenu.split('<li'):
                    if htmlElement.find('<a href="')>-1:
                        element = {}
                        link = Decoder.extract('<a href="','" target="_parent"',htmlElement)
                        if htmlElement.find('<span class="channels-icon ')>-1:
                            title = Decoder.extract('<span class="channels-icon ','"></span>',htmlElement)
                        elif htmlElement.find('<span class="chclass3">')>-1:
                            title = Decoder.extract('<span class="chclass3">','</span>',htmlElement)
                        element["title"] = title
                        element["link"] = link
                        logger.debug("found element: "+title+", url: "+link)
                        if title != 'ch1toch20' and title != 'No Stream':
                            x.append(element)
        elif str(page) == '1': #event
            html = Cricfreetv.getContentFromUrl(Cricfreetv.MAIN_URL)
            html = Decoder.extract('<div class="panel-body">',"</section>",html)
            logger.debug("using html for menu: "+html)
            for htmlElement in html.split('<span class="sport-icon'):
                if htmlElement.find('<td>')>-1:
                    name = Decoder.extract('<td>',"</td>",htmlElement).replace("<br>"," - ")
                    event = Decoder.extract(' target="_blank">','</a></td>',htmlElement)
                    time = Decoder.extract('px">',"</td>",htmlElement)
                    href = Decoder.extract(' href="','"',htmlElement)
                    element = {}
                    element["title"] = time+" - "+name+" - "+event
                    element["link"] = href
                    logger.debug("time: "+time)
                    logger.debug("name: "+name)
                    logger.debug("event: "+event)
                    if "http" in href:
                        logger.debug("appending: "+element["title"]+", link: "+href)
                        x.append(element)
        else:
            html = Cricfreetv.getContentFromUrl(page)
            logger.debug(html)
            x.append(Cricfreetv.extractIframe(html,page))
        return x

    @staticmethod
    def extractIframe(html,referer):
        iframeUrl = ''
        if '<iframe frameborder="0" marginheight="0" allowfullscreen="true" marginwidth="0" height="555" src="' in html:
            iframeUrl = Decoder.extract('<iframe frameborder="0" marginheight="0" allowfullscreen="true" marginwidth="0" height="555" src="','"',html)
        elif '<iframe frameborder="0" marginheight="0" marginwidth="0" height="490" src="' in html:
            iframeUrl = Decoder.extract('<iframe frameborder="0" marginheight="0" marginwidth="0" height="490" src="','"',html)
        if "'" in iframeUrl:
            iframeUrl = iframeUrl[0:iframeUrl.find("'")]
        if "/update/" in iframeUrl:
            #get all urls and check if they hasn't /update/
            for content in html.split(".php"):
                link = content[content.rfind('"')+1:]+".php"
                if "http://" in link and "/update/" not in link and "/update/" in iframeUrl:
                    logger.debug("link has been updated from: "+iframeUrl+", to: "+link)
                    iframeUrl = link
        logger.debug("level 1, iframeUrl: "+iframeUrl+", cookie: "+Cricfreetv.cookie)
        if iframeUrl!='':
            html = Cricfreetv.getContentFromUrl(iframeUrl,"",Cricfreetv.cookie,referer)
        file = Cricfreetv.seekIframeScript(html,referer,iframeUrl)
        item = {}
        item["title"] = referer
        item["link"] = file
        return item

    @staticmethod
    def launchScriptLogic(scriptRegex,html,referer,iframeUrl):
        logger.debug("processing pre level 2... url: "+scriptRegex)
        firstScriptUrl = Decoder.extractWithRegex(scriptRegex,".js",html)
        if firstScriptUrl.find('"')>-1:
            firstScriptUrl = firstScriptUrl[0:firstScriptUrl.find('"')]
        if "'" in firstScriptUrl:
            firstScriptUrl = firstScriptUrl[0:firstScriptUrl.find("'")]
        scriptUrl = Cricfreetv.extractScriptIframeUrl(html,firstScriptUrl,referer)
        logger.debug("level 2, scriptUrl: "+scriptUrl+", cookie: "+Cricfreetv.cookie)
        lastIframeHtml = Cricfreetv.getContentFromUrl(scriptUrl,"",Cricfreetv.cookie,iframeUrl)
        logger.debug("html in level2 is: "+lastIframeHtml)
        file = Cricfreetv.seekIframeScript(lastIframeHtml,iframeUrl,scriptUrl)
        logger.debug("script logic finished!")
        return file

    @staticmethod
    def seekIframeScript(html,referer, iframeUrl):
        lastIframeHtml = html
        file = ""
        logger.debug("seek iframe logic... ")
        if html.find("http://theactionlive.com/live")>-1:
            file = Cricfreetv.launchScriptLogic("http://theactionlive.com/live",html,referer,iframeUrl)
        elif html.find('http://biggestplayer.me/play')>-1:
            file = Cricfreetv.launchScriptLogic("http://biggestplayer.me/play",html,referer,iframeUrl)
        elif html.find("http://www.yotv.co/play")>-1:
            file = Cricfreetv.launchScriptLogic("http://www.yotv.co/play",html,referer,iframeUrl)
        elif html.find("http://www.yocast.tv/embed")>-1:
            file = Cricfreetv.launchScriptLogic("http://www.yocast.tv/embed",html,referer,iframeUrl)
        elif html.find("http://www.rocktv.co/play")>-1:
            file = Cricfreetv.launchScriptLogic("http://www.rocktv.co/play",html,referer,iframeUrl)
        elif html.find("http://miplayer.net/embed")>-1:
            file = Cricfreetv.launchScriptLogic("http://miplayer.net/embed",html,referer,iframeUrl)
        elif html.find("http://www.cast4u.tv/embed")>-1:
            file = Cricfreetv.launchScriptLogic("http://www.cast4u.tv/embed",html,referer,iframeUrl)
        elif html.find("http://www.cast4u.tv/Player")>-1:
            file = Cricfreetv.launchScriptLogic("http://www.cast4u.tv/Playercr", html, referer, iframeUrl)
        elif html.find("http://www.topcast.live/embed")>-1:
            file = Cricfreetv.launchScriptLogic("http://www.topcast.live/embed", html, referer, iframeUrl)
        elif 'http://www.webtv.ws/player' in html:
            file = Cricfreetv.launchScriptLogic("http://www.webtv.ws/player", html, referer, iframeUrl)
        elif "http://www.hdcast.info/embed.js" in html:
            id = Decoder.extract('fid="','"',html)
            scriptUrl = "http://www.hdcast.info/embed.php?live="+id+"&vw=620&vh=490"
            logger.debug("using script url: "+scriptUrl)
            lastIframeHtml = Cricfreetv.getContentFromUrl(scriptUrl, "", Cricfreetv.cookie, iframeUrl)
            logger.debug("html is: "+lastIframeHtml)
            lastIframeHtml = Decoder.rExtract("<body","</body>",lastIframeHtml)
            file = Cricfreetv.seekIframeScript(lastIframeHtml, iframeUrl, scriptUrl)
        elif html.find("http://violadito.biggestplayer.me/playercr.js")>-1:
            id = Decoder.extract("<script type='text/javascript'>id='","'",html)
            logger.debug("violadito id="+id)
            #newUrl = "http://lqgq.biggestplayer.me/streamcr.php?id="+id+"&width=620&height=460"
            jsLogic = Cricfreetv.getContentFromUrl('http://violadito.biggestplayer.me/playercr.js',"",Cricfreetv.cookie,iframeUrl)
            try:
                jsLogic = jsunpack.unpack(jsLogic)
                logger.debug("jsLogic: "+jsLogic)
                newUrl = Decoder.extractWithRegex('http://','"',jsLogic).replace("\\'+id+\\'",str(id))
            except:
                logger.debug("could not use unpack from jsunpack, using new method...")
                logger.debug("jsLogic is: " + jsLogic)
                newUrl = Decoder.extract(' src="', '"', jsLogic).replace("'+id+'", id)
                pass
            logger.debug("using referer: "+iframeUrl)
            html2 = Cricfreetv.getContentFromUrl(newUrl,"",Cricfreetv.cookie,iframeUrl)
            logger.debug("extracting file from "+newUrl)
            if html2.find('file: "')>-1:
                file = Decoder.extract('file: "','"',html2)
            logger.debug("obtained file: "+file)
        elif 'file: "rtmp:' in html:  # found final link
            logger.debug("detected rtmp link...")
            rtmp = "rtmp:" + Decoder.extract('file: "rtmp:', '"', html)
            swfJS = Decoder.extract('<script src="','"',html[html.find('<div id="myElement">'):])
            jsContent = Downloader.getContentFromUrl(url=swfJS,referer=referer)
            swfUrl = Decoder.extract('"flashplayer": "','"',jsContent)
            if "http:" not in swfUrl:
                swfUrl = "http:"+swfUrl
            logger.debug("swfUrl is: "+swfUrl)
            logger.debug("iframeUrl is: "+iframeUrl)
            logger.debug("referer is: " + referer)

            link = rtmp+" swfUrl="+swfUrl+" pageUrl="+iframeUrl
            logger.debug("final rtmp link built is: "+link)
            file = link
        elif 'file: "http' in html:  # found final link
            logger.debug("using http file extractor...")
            file = "http" + Decoder.extract('file: "http', '"', html)
            file += "|" + Downloader.getHeaders(iframeUrl) #TODO review this part
            logger.debug("found final link: " + file)
        elif html.find("http://www.filmon.com/tv/")>-1:
            url = Decoder.extractWithRegex("http://www.filmon.com/tv/",'"',html).replace('"',"")
            logger.debug("using first filmon.com url from provider, url: "+url+", r: "+referer)
            file = Filmoncom.launchScriptLogic(url,referer)[0]["url"]
        elif html.find('return(["r","t","m","p"')>-1: #changed order to build final url first
            logger.debug("launching array logic for rtmp link...")
            swfUrl = "http://cdn.ibrod.tv/player/jwplayer.flash.swf"
            if 'cast4u.tv' in html:
                swfUrl = "http://cast4u.tv/jwplayer/jwplayer.flash.swf"
            elif 'http://www.hdcast.info/video-js/video-js.swf' in html:
                swfUrl = "http://www.hdcast.info/video-js/video-js.swf"

            if '<script type="text/javascript">\nvar' in html:
                scriptSplit = '<script type="text/javascript">\nvar'
            elif '<script type="text/javascript">\n\nvar' in html:
                scriptSplit = '<script type="text/javascript">\n\nvar'

            bruteData = Decoder.extract(scriptSplit,"</script>",html)

            rtmp = ""
            file = Decoder.extract('file: ','}],',bruteData).replace(' ','')
            logger.debug("file form is: "+file)
            playpath = ""
            for functionName in file.split('+'):
                if functionName.find("/")==-1:
                    logger.debug("using function: "+functionName)
                    bruteData2 = Decoder.extract('function '+functionName+' {',"}",bruteData)
                    line = Decoder.extract('return([',');',bruteData2)
                    #now begin the fix
                    for linePart in line.split("+"):
                        if '].join' in linePart:
                            linePart = linePart[:linePart.find('].join')]
                            linePart2 = linePart.replace('","',"").replace('"','').replace('\\',"").replace(",","")
                            logger.debug("at this moment linePart1 is: "+linePart2)
                            rtmp+=linePart2
                            if '/' not in linePart2:
                                playpath = linePart2
                        elif 'document.getElementById' in linePart:
                            #extract id and get content
                            idSpan = Decoder.extract('(',')',linePart).replace("\"","").replace("'","")
                            content = Decoder.extract(' id='+idSpan+'>','</span>',html)
                            logger.debug("at this moment linePart2 is: " + content)
                            rtmp+=content
                        elif 'join("")' in linePart:
                            #array to join with a replace like first condition
                            idArrayVar = linePart.replace('.join("")','').replace(' ','')
                            content = Decoder.extract('var '+idArrayVar+" = [","];",bruteData).replace(",","").replace('"','')
                            logger.debug("at this moment linePart3 is: " + content)
                            rtmp+=content
                else:
                    rtmp+="/"
                logger.debug("at this moment final rtmp is: " + rtmp)
            '''
            token = ""

            if bruteData.find('securetoken: ')>-1:
                token = Decoder.extract('securetoken: ','\n',bruteData)
                swfUrlJS = 'http://cast4u.tv/jwplayer/jwplayer.js?v=3.3'
                htmlToken = Cricfreetv.getContentFromUrl(url=swfUrlJS)
                token = Decoder.extract('var '+token+' = "','"',htmlToken)

            logger.debug("Fresh token is: "+token)
            '''
            if "/live" in rtmp:
                app = 'live'+Decoder.extract('/live','==/',rtmp)+"==/"
            else: #/hd
                app = 'hd' + Decoder.extract('/hd', '==/', rtmp) + "==/"

            file = rtmp+" app="+app+" playpath="+playpath+r" token=%XB00(nKH@#. flashver=WIN\2021,0,0,182 timeout=30 live=1 swfUrl="+swfUrl+" pageUrl="+iframeUrl+""

            logger.debug("Built a rtmp with data: "+file)
        elif html.find('securetoken:')>-1:
            logger.debug("building final link from html: "+html)
            file = Decoder.extract('file: "','"',html)
            securetoken = Decoder.extract('securetoken: "','"',html)
            #logger.debug(html)
            flashPlayer = 'http://p.jwpcdn.com/6/12/jwplayer.flash.swf'
            tokenString = ""
            if "html>" not in securetoken:
                tokenString = " token="+securetoken
            else:
                jsUrl = Decoder.rExtract('<script type="text/javascript" src="','" ></script>',html)
                jsContent = Cricfreetv.getContentFromUrl(url=jsUrl)
                var = Decoder.extract('securetoken: ',"\n",html)
                logger.debug("seeking var: "+var)
                tokenString = Decoder.extract('var '+var+" = \"",'";',jsContent)
                logger.debug("new token string is: "+tokenString)
                tokenString = " token="+tokenString
            rtmpUrl = file[0:file.rfind('/')+1]+" playpath="+file[file.rfind('/')+1:]+tokenString+" swfUrl="+flashPlayer+" live=1 timeout=13 pageUrl="+iframeUrl
            logger.debug("found final link: "+rtmpUrl)
            file = rtmpUrl
        elif html.find("eval(unescape('")>-1:
            logger.debug("eval unescape js logic...")
            html = Cricfreetv.decodeContent(html).lower()
        elif html.find('<a href="http://sports4u.tv/channel')>-1 or html.find('http://sports4u.tv/embed/')>-1:
            logger.debug("embed link logic...")
            if html.find('http://sports4u.tv/embed/')>-1:
                urlLink = Decoder.extractWithRegex('http://sports4u.tv/embed/','"',html).replace('"',"")
                logger.debug("seek new iframe url with: "+urlLink)
                html2 = Cricfreetv.getContentFromUrl(urlLink,"",Cricfreetv.cookie,iframeUrl)
                file = Cricfreetv.seekIframeScript(html2,iframeUrl,urlLink)
            elif html.find('<a href="http://sports4u.tv/channel')>-1:
                logger.debug("urlLink...")
                urlLink = Decoder.extractWithRegex('<a href="http://sports4u.tv/channel','/"',html)
                logger.debug("urlLink2..."+urlLink)
                urlLink = urlLink[urlLink.find('"')+1:urlLink.rfind('"')]
                logger.debug("urlLinkFinal..."+urlLink)
                if urlLink != iframeUrl:
                    urlLink = urlLink.replace(".tv/",".pw/")
                    html2 = Cricfreetv.getContentFromUrl(url=urlLink,cookie=Cricfreetv.cookie,referer=iframeUrl)
                    logger.debug("html2 is: "+html2)
                    file = Cricfreetv.seekIframeScript(html2,iframeUrl,urlLink)
                    if file=='':
                        #extract iframe value
                        iframe = Decoder.extract('<iframe frameborder="0" marginheight="0" marginWidth="0" height="490" id="iframe" src="','" id="',html).replace('"',"")
                        file = Cricfreetv.extractIframeValue(iframe,html,referer)
        elif ' src="http://cricfree.sx/' in html:
            logger.debug("native cricfree.sx logic")
            #it's a cricfree.sx native page, so launch this logic
            urlLink = Decoder.extractWithRegex('http://cricfree.sx/', '"', html).replace('"', "")
            logger.debug("seek new http://cricfree.sx/ iframe url with: " + urlLink)
            html2 = Cricfreetv.getContentFromUrl(urlLink, "", Cricfreetv.cookie, iframeUrl)
            file = Cricfreetv.seekIframeScript(html2, iframeUrl, urlLink)
        elif 'http://sports4u.pw/embed/' in html:
            logger.debug("repeating proccess...")
            newOldUrl = Decoder.extractWithRegex('http://sports4u.pw/embed/','"',html).replace('"','')
            logger.debug("new old url is: "+newOldUrl)
            html2 = Cricfreetv.getContentFromUrl(url=newOldUrl, referer=iframeUrl)
            logger.debug("html is: " + html2)
            file = Cricfreetv.seekIframeScript(html2, iframeUrl, newOldUrl)
        else:
            logger.debug("enterring to ELSE logic")
            if html.find('<iframe id="player" scrolling="no" width="620" height="490" allowtransparency="no" frameborder="0" src="') > -1:
                iframe = Decoder.extract('<iframe id="player" scrolling="no" width="620" height="490" allowtransparency="no" frameborder="0" src="','"', html)
                file = Cricfreetv.extractIframeValue(iframe, html, referer)
            elif html.find('<iframe ') > -1:  # brute method forced
                logger.debug("brute method launched...")
                logger.debug("referer is: "+referer)
                logger.debug("iframeUrl is: " + iframeUrl)
                iframe = Decoder.rExtract('<iframe ', '</iframe>', html)
                iframe = Decoder.extract('src="', '"', iframe)
                if iframe == referer or iframe == iframeUrl:
                    logger.debug("is the same page so needs to be changed!")
                    logger.debug("html is: " + html)
                    for content in html.split(".php"):
                        link = content[content.rfind('"') + 1:] + ".php"
                        logger.debug("target ELSE link is: " + link)
                        if "http://" in link and "/update/" not in link and "/update/" in iframeUrl:
                            logger.debug("ELSE link has been updated from: " + iframeUrl + ", to: " + link)
                            iframe = link
                    if iframe != referer and iframe != iframeUrl:
                        logger.debug("fixed the same url, continue...")
                        file = Cricfreetv.extractIframeValue(iframe, html, referer)
                    else:
                        logger.debug("NOT fixed the same url, stopping...")
                else:
                    file = Cricfreetv.extractIframeValue(iframe, html, referer)
            else:
                logger.debug(html)
        return file

    @staticmethod
    def extractIframeValue(iframe,html,referer):
        file = ""
        if iframe.find("http:")!=0:
            iframe = Decoder.extract("<iframe src='","' ",html).replace("'","") #take into account .lower() characters, so is not ' SRC=
            if iframe.find("http:")!=0:
                iframe = Decoder.extract(' src="','"',html).replace('"',"")
        logger.debug("using iframeUrl: "+iframe)
        if iframe.find("filmon.")>-1: # i prefer this fix to change all logic, really, I boried about this provider and is a 'silly' provider
            logger.debug("Detected exceptional filmon.com|tv provider: "+iframe)
            file = Filmoncom.launchScriptLogic(iframe,referer)[0]["url"]
        else:
            html2 = Cricfreetv.getContentFromUrl(iframe,"",Cricfreetv.cookie,referer)
            #print html2
            if html2.find("http://www3.sawlive.tv/embed/")>-1:
                iframe2 = Decoder.extractWithRegex("http://www3.sawlive.tv/embed/",'"',html2).replace('"',"")
                logger.debug("detected a sawlive: "+iframe2+", from: "+iframe)
                #file = Live9net.getChannels(iframe2) #Live9net has the sawlive decoder, so it decodes target link
                file = Decoder.extractSawlive(iframe2,Cricfreetv.cookie,iframe)
            else:
                file = Cricfreetv.seekIframeScript(html2,referer,iframe)
        return file

    @staticmethod
    def decodeContent(html): #This method is used to fix a "probably" encoding/decoding problem from provider
        #new encoded iframe method
        logger.debug("trying new method for encrypted javascript code...")
        html2 = Decoder.extractWithRegex("eval(unescape('","'));",html)
        html3 = Decoder.rExtractWithRegex("eval(unescape('","'));",html)
        html3 = html3.replace("eval(","").replace("unescape(","").replace(" + ","").replace(")","").replace("'","").replace(";","")
        logger.debug("extracted code is: "+html3)
        decodedHtml = urllib.unquote(html2[:html2.find(";")+1]).decode('utf8')
        logger.debug("decypter function in javascript is: "+decodedHtml)
        encryptedCall = urllib.unquote(html3).decode('utf8')
        #encryptedCall = html3
        logger.debug("final html is: "+encryptedCall)
        #now extract encrypted string
        encryptedCall = Decoder.extract("('","'));",encryptedCall)
        splitter = Decoder.extract('s.split("','");',decodedHtml)
        logger.debug("splitter: "+splitter)
        subfixer = Decoder.extract('tmp[1] + "','");',decodedHtml)
        logger.debug("subfixer: "+subfixer)
        s = encryptedCall.split(splitter)[0]
        k = encryptedCall.split(splitter)[1]+subfixer
        xorDiff = int(Decoder.extract("charCodeAt(i))+",");",decodedHtml))
        #logger.debug(xorDiff)
        r = ""
        i = 0
        logger.debug("starting loop decoder, s: "+s+", k: "+k)
        '''
        r += String.fromCharCode((parseInt(k.charAt(i%k.length))^s.charCodeAt(i))+-2);
        '''
        CORRECTION = 16 #I don't know why but this convert it to legible character (most cases)
        mode = 0
        while i<len(s): #GO TO HELL, REALLY, I HAVE NO IDEA HOW THERE IS PEOPLE IN THE WORLD DOING THIS THING, DO YOU KNOW AN STANDARD ENCODING? YOU DOOOON'T!!!!
            seed = k[(i%len(k))]
            #logger.debug("seed: "+seed)
            primitive = ord(seed)^ord(s[i])
            #logger.debug("xorted: "+str(primitive))
            if len(r)==0 and str(primitive)!= '<':
                #tryes to check what fix is neccesary
                if str(primitive)=='15':
                    mode = 1
                elif str(primitive)=='14':
                    mode = 2
                elif str(primitive)=='4':
                    mode = 3
                elif str(primitive)=='7':
                    mode = 4
                elif str(primitive)=='9':
                    mode = 5
                else:
                    logger.debug("detected new start value: "+str(primitive)+", probably needs new encoding method")
            #mode 1 and mode 2
            if (str(primitive) == '1' and mode==1) or (mode==2 and str(primitive)=='0'):
                r += "."
            elif (str(primitive) == '2' and mode==1) or (mode==2 and (str(primitive)=='1' or str(primitive)=='113')):
                r += "/"
            elif (str(primitive) == '15' and mode==1) or (mode==2 and str(primitive)=='14') or (mode==3 and str(primitive)=='4') or (mode==4 and str(primitive)=='7') or (mode==5 and str(primitive)=='9'):
                r += "<"
            elif (str(primitive) == '112' and mode==1) or (mode==2 and str(primitive)=='15') or (str(primitive) == '5' and mode==3) or (str(primitive) == '8' and mode==4) or (mode==5 and str(primitive)=='10'):
                r += "="
            elif (str(primitive) == '113' and mode==1) or (mode==2 and str(primitive)=='112') or (str(primitive) == '6' and mode==3) or (str(primitive) == '9' and mode==4) or (mode==5 and str(primitive)=='11'):
                r += ">"
            elif (str(primitive) == '13' and mode==1) or (mode==2 and str(primitive)=='12') or (str(primitive) == '2' and mode==3) or (str(primitive) == '5' and mode==4) or (mode==5 and str(primitive)=='7'):
                r += ":"
            elif (int(str(primitive))-3<10 and mode==1):
                r += str(int(str(primitive))-3)
            elif (int(str(primitive))-2<10 and mode==2):
                r += str(int(str(primitive))-2)
            #mode 3
            elif (str(primitive) == '1' and mode==3) or (str(primitive) == '4' and mode==4):
                r += "9"
            elif (str(primitive) == '1' and mode==4) or (str(primitive) == '3' and mode==5):
                r += "6"
            elif (str(primitive) == '110' and mode==3):
                r += "f"
            elif (str(primitive) == '105' and mode==3) or (str(primitive) == '108' and mode==4) or (mode==5 and str(primitive)=='110'):
                r += "a"
            elif (str(primitive) == '109' and mode==3):
                r += "e"
            elif (str(primitive) == '40' and mode==3) or (str(primitive) == '43' and mode==4) or (mode==5 and str(primitive)=='45'):
                r += " "
            elif (str(primitive) == '108' and mode==3):
                r += "d"
            elif (str(primitive) == '42' and mode==3) or (str(primitive) == '45' and mode==4) or (mode==5 and str(primitive)=='47'):
                r += '"'
            elif (str(primitive) == '111' and mode==3):
                r += 'g'
            elif (str(primitive) == '81' and mode==3):
                r += 'i'
            elif (str(primitive) == '107' and mode==3) or (str(primitive) == '110' and mode==4):
                r += 'c'
            elif ((str(primitive) == '10' or str(primitive) == '106') and mode==3) or (str(primitive) == '109' and mode==4) or (mode==5 and str(primitive)=='111'):
                r += 'b'
            #mode 4
            elif mode==4 and str(primitive)=='105':
                r += 'a'
            elif  (str(primitive) == '111' and mode==4):
                r += 'd'
            #mode 5
            elif (mode==5 and str(primitive)=='1'):
                r += '4'
            elif (mode==5 and str(primitive)=='5'):
                r += '8'
            elif (mode==5 and str(primitive)=='108'):
                r += '_'
            elif (mode==5 and str(primitive)=='12'):
                r += '?'
            else:
                integer = primitive+xorDiff
                #logger.debug("new value: "+chr(integer+CORRECTION))
                r += chr(integer+CORRECTION)
            #logger.debug("r is now: "+r)
            i+=1
        logger.debug("loop decoder finished at: "+str(i)+" loop")
        logger.debug("final decoded value is: "+r)
        return r


    @staticmethod
    def extractScriptIframeUrl(html,scriptUrl,referer):
        iframeUrl = ""
        scriptContent = Cricfreetv.getContentFromUrl(scriptUrl,"",Cricfreetv.cookie,referer)
        logger.debug("script content is: "+scriptContent)
        iframeUrl = Decoder.extract('src="','"',scriptContent)
        if iframeUrl.find("id='+id+'")>-1: #search id in html
            id = Decoder.extract("<script type='text/javascript'>id='","';",html)
            iframeUrl = iframeUrl[0:iframeUrl.find('?id=')+len('?id=')]+id+Cricfreetv.getWidthAndHeightParams(html)+"&stretching="
        elif iframeUrl.find("live=")>-1 or '+ fid +' in iframeUrl:
            if html.find("<script type='text/javascript'>fid='")>-1:
                id = Decoder.extract("<script type='text/javascript'>fid='","';",html)
            elif html.find("<script type='text/javascript'>fid=\"")>-1:
                id = Decoder.extract("<script type='text/javascript'>fid=\"","\";",html)
            else:
                id = Decoder.extract('<script>fid="','";',html)
            if iframeUrl.find("live=")>-1:
                iframeUrl = iframeUrl[0:iframeUrl.find('?live=')+len('?live=')]+id+Cricfreetv.getWidthAndHeightParams(html)
            else:
                iframeUrl = iframeUrl[0:iframeUrl.find('?v=') + len('?v=')] + id + Cricfreetv.getWidthAndHeightParams(html)
        else:
            iframeUrl = Decoder.extract("<iframe src='","' ",scriptContent)
        return iframeUrl

    @staticmethod
    def getWidthAndHeightParams(html):
        subUrl = ""
        if html.find("; width='")>-1:
            width = Decoder.extract("; width='","'",html)
            height = Decoder.extract("; height='","'",html)
            subUrl = "&width="+width+"&height="+height
        elif html.find("; v_height=")>-1:
            width = Decoder.extract("; v_width=",";",html)
            height = Decoder.extract("; v_height=",";",html)
            subUrl = "&vw="+width+"&vh="+height
        return subUrl