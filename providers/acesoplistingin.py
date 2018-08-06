# -*- coding: utf-8 -*-
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Acesoplistingin(Downloader):

    MAIN_URL = "http://acesoplisting.in/"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            html = Acesoplistingin.getContentFromUrl(url=Acesoplistingin.MAIN_URL)
            table = Decoder.extract('<table id="listing" ','</table></div>',html)
            x = Acesoplistingin.extractElements(table)
            logger.debug("appending "+str(len(x))+" elements")
        return x

    @staticmethod
    def extractElements(table):
        x = []
        i = 0
        for value in table.split('<td colspan="2" class="text-center">'):
            if i>0 and " href=" in value:
                element = {}
                title = Decoder.extract(' title="','"',value) #provisional
                logger.debug("provisional title: "+title)
                #time = Decoder.extract('<td colspan="2" class="text-center">', '</td>', value)
                time = value[:value.find("<")]
                date = Decoder.extract('<td class="xsmall text-muted text-center">', '</td>', value)
                game = Decoder.extract('<td class="text-center" style="text-transform:uppercase;">', '</td>', value)
                teams = Decoder.extract('<td colspan="2">', '</td>', value)
                #date = "[" + time + "][" + date + "]-"
                j=0
                for content in value.split("href="):
                    if j>0:
                        #time = Decoder.extract('<td colspan="2" class="text-center">', '</td>', content)
                        link = Decoder.extract('"','"',content)
                        language = Decoder.extract('alt="','"',content)
                        title2 = language
                        title2 = title2[:title2.find("<")]
                        title2 = title2.replace("<br />","").replace("\n","")
                        language = language[language.find("Language ")+len("Language "):]
                        title2 = time+"|"+language+"|"+title2+" || "+date
                        logger.debug("time: "+time)
                        logger.debug("date: " + date)
                        #if len(date)<20 and len(date)>0:
                        #    title2 = language+date+teams+" - "+game
                        #else:
                        #    title2 = language+"-"+title
                        element["title"] = title2
                        element["link"] = link
                        logger.debug(language+" - append: "+title2+", link: "+link)
                        x.append(element)
                    j+=1
            i+=1
        return x