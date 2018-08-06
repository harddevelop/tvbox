# -*- coding: utf-8 -*-
import time
from tvboxcore.decoder import Decoder
from tvboxcore import jsunpack
from providers.cricfreetv import Cricfreetv
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Vipracinginfo(Downloader):

    MAIN_URL = "http://vipracing.tv"
    MAIN_URL2 = "http://vipracing.us"
    MAIN_URL3 = "http://vipracing.info"

    @staticmethod
    def getChannels(page):
        x = []
        element = {}
        if str(page) == '0':
            page=Vipracinginfo.MAIN_URL3
            html = Vipracinginfo.getContentFromUrl(page,"",Vipracinginfo.cookie,"")
            #print html
            if html.find("var channels = JSON.parse('")>-1: #it's a list, needs decode
                table = Decoder.extract("var channels = JSON.parse('","'),",html)
                table = table.replace('\u00f3','ó').replace('\u00f1','ñ').replace('\/',"-")#.replace('"',"'")
                x = Vipracinginfo.extractElements(table,Vipracinginfo.MAIN_URL3)
                logger.debug("Vipracing channels logic done!")
            else:
                #change domain to alternative and repeat the same logic
                html = Vipracinginfo.getContentFromUrl(Vipracinginfo.MAIN_URL3,"",Vipracinginfo.cookie,"")
                #print html
                if html.find("var channels = JSON.parse('")>-1: #it's a list, needs decode
                    table = Decoder.extract("var channels = JSON.parse('","'),",html)
                    table = table.replace('\u00f3','ó').replace('\u00f1','ñ').replace('\/',"-")#.replace('"',"'")
                    x = Vipracinginfo.extractElements(table,Vipracinginfo.MAIN_URL3)
                    logger.debug("done with the second loop, detected channels: "+str(len(x)))
        else:
            html = Vipracinginfo.getContentFromUrl(url=page)
            logger.debug("html: " + html)
            logger.debug("launching Vipracing else logic")
            if html.find('http://www.streamlive.to/embed/')>-1:
                link = Decoder.decodeStreamliveto(html,page)
                element["link"] = link
                element["title"] = Decoder.extract("<title>","</title>",html)
                element["permalink"] = True
                x.append(element)
            elif html.find("http://www.janjua.tv")!=-1:
                channel = Decoder.extract(" width=653, height=410, channel='","'",html)
                url2 = "http://www.janjuaplayer.com/embedplayer/"+channel+"/1/653/410"
                html2 = Vipracinginfo.getContentFromUrl(url2,"",Vipracinginfo.cookie,page)
                bruteContent = Decoder.extract("so.addParam('FlashVars', '","');",html2)
                #extract id and pk
                id = bruteContent[0:bruteContent.find("&")]
                pk = bruteContent[bruteContent.find('pk='):]
                # loadbalancer is http://www.janjuapublisher.com:1935/loadbalancer?53346
                ip = Vipracinginfo.getContentFromUrl("http://www.janjuapublisher.com:1935/loadbalancer?"+(id[id.find("=")+1:]),"","","http://www.janjuaplayer.com/resources/scripts/eplayer.swf").replace('redirect=','')
                link = "rtmp://"+ip+"/live"+" swfUrl=http://www.janjuaplayer.com/resources/scripts/eplayer.swf pageUrl="+url2+" flashver=WIN/2019,0,0,226 live=true timeout=11 playpath="+channel+"?"+id+"&"+pk
                link = "rtmp://"+ip+"/live"+channel+"?"+id+"&"+pk+" app=live pageUrl="+url2+" swfUrl=http://www.janjuaplayer.com/resources/scripts/eplayer.swf tcUrl=rtmp://"+ip+"/live playPath="+channel+"?"+id+"&"+pk+" conn=S:OK live=1 flashver=WIN/2019,0,0,226"
                element["link"] = link
                element["title"] = channel
                element["permalink"] = True
                x.append(element)
            else:
                logger.debug("launching Vipracing else ELSE logic (other provider embed - max-deportv)")
                html2 = ""
                if ' SRC="' in html:
                    iframeUrl = Decoder.extract(' SRC="','"',html)
                    html2 = Vipracinginfo.getContentFromUrl(iframeUrl, "", Vipracinginfo.cookie, page)
                elif '<iframe name="vipracing" src="' in html:
                    iframeUrl = Decoder.extract('<iframe name="vipracing" src="','"',html)
                    html2 = Vipracinginfo.getContentFromUrl(iframeUrl)
                logger.debug("html2 is: "+html2)
                if 'http://max-deportv' in html2:
                    logger.debug("using max-deportv way")
                    iframeUrl2 = Decoder.extractWithRegex("http://max-deportv",'"',html2)
                    iframeUrl2 = iframeUrl2[0:len(iframeUrl2)-1]
                    logger.debug("using iframeUrl: "+iframeUrl2)
                    html3 = Vipracinginfo.getContentFromUrl(iframeUrl2,"",Vipracinginfo.cookie,iframeUrl)
                    iframeUrl3 = Decoder.extractWithRegex('http://www.iguide.to/embed/','">',html3)
                    iframeUrl3 = iframeUrl3[:len(iframeUrl3)-1]
                    #extract channelId
                    channelId = Decoder.extract('embed/','&',iframeUrl3)
                    iframeUrl3 = "http://www.iguide.to/embedplayer_new.php?width=650&height=400&channel="+channelId+"&autoplay=true"
                    link = Decoder.decodeIguide(iframeUrl3,iframeUrl2)
                elif 'http://www.streamlive.to' in html2:
                    streamLiveScript = Decoder.extractWithRegex('http://www.streamlive.to','"',html2).replace('"','')
                    link = Decoder.decodeStreamliveto(streamLiveScript, iframeUrl)
                    logger.debug("using streamlive way...")
                elif '<iframe name="vipracing" src="http://vipracing.' in html:
                    logger.debug("detected vipracing embed iframe, other loop...")
                    iframeUrlLoop = Decoder.extract('<iframe name="vipracing" src="','"',html)
                    element2 = Vipracinginfo.getChannels(iframeUrlLoop)[0]
                    link = element2["link"]
                    page = element2["title"]
                elif '247bay.tv/static/scripts/247bay.js' in html:
                    channel = Decoder.extract(", channel='","'",html)
                    url2 = 'http://www.247bay.tv/embedplayer/'+channel+'/2/653/410'
                    link = Decoder.decode247bay(url2,page)
                elif 'castalba.tv/js/embed.js' in html:
                    cid = Decoder.extract(' id="','"',html)
                    link = 'http://www.castalba.tv/embed.php?cid='+cid+'&wh=653&ht=410&d=vipracing.info'
                    link = Decoder.decodeCastalbatv(link, page)
                elif 'http://cricfree.sc/update/' in html:
                    frameUrl = Decoder.extractWithRegex('http://cricfree.sc/update','.php',html)
                    link = Cricfreetv.getChannels(frameUrl)[0]["link"]
                elif 'http://crichd.tv/update/' in html:
                    frameUrl = Decoder.extractWithRegex('http://crichd.tv/update/',".php",html)
                    link = Cricfreetv.getChannels(frameUrl)[0]["link"]
                    #html2 = Downloader.getContentFromUrl(url=frameUrl)
                    #if 'cast4u' in html2:
                    #    url2 = "http://www.cast4u.tv/embedcr.php?v="+Decoder.extract('fid=\'','\'',html2)+"&vw=620&vh=490"
                    #    link = Cricfreetv.extractIframe(url2,frameUrl)[0]["link"]

                else:
                    logger.debug("Nothing done: "+html+", \nhtml2: "+html2)
                element["link"] = link
                element["title"] = page
                element["permalink"] = True
                x.append(element)
        return x

    @staticmethod
    def extractElements(table,domain):
        x = []
        i = 0
        for value in table.split('"name"'):
            if i>0:
                element = {}
                title = Decoder.extract('"','"',value).replace('- ','')
                link = Decoder.extract('shortcut":"','"',value)
                element["title"] = title
                element["link"] = domain+"/channel/"+link+"/frame"
                logger.debug("append: "+title+", link: "+element["link"])
                x.append(element)
            i+=1
        return x